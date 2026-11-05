"""Install the reviewed chapter delta, append a source database and activate CPU RAG."""
import argparse,gzip,hashlib,json,os,re,zipfile
from pathlib import Path
from src.wengua import book_rag as r,course_delivery_v1 as delivery

RELEASE=r.ROOT/'data/knowledge/jinhan/zongxu_20261105/release.json'
REGISTRY=r.ROOT/'local/wengua_rag/reviewed_sources.json'


def extract_checked(archive,destination,release):
    destination=r.private(destination);archive=Path(archive)
    if r.digest(archive.read_bytes())!=release['archive_sha256']:raise ValueError('Chapter archive checksum differs')
    if destination.exists():
        for name,digest in release['files'].items():
            if r.digest((destination/name).read_bytes())!=digest:raise ValueError('Existing chapter changed; preserved')
        return destination
    pending=destination.with_name(destination.name+'.pending')
    if pending.exists():raise ValueError('Incomplete chapter installation preserved')
    with zipfile.ZipFile(archive) as z:
        if len(z.namelist())!=len(set(z.namelist())) or set(z.namelist())!=set(release['files']):raise ValueError('Wrong archive members')
        if any(Path(n).is_absolute() or '..' in Path(n).parts or '\\' in n for n in z.namelist()):raise ValueError('Unsafe archive member')
        # Authenticate all members before creating an installation directory.
        payload={name:z.read(name) for name in z.namelist()}
        if any(r.digest(payload[n])!=h for n,h in release['files'].items()):raise ValueError('Chapter member checksum differs')
        pending.mkdir(parents=True)
        for name,raw in payload.items():
            target=pending/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    pending.rename(destination);return destination


def portable_decrypt(key,iv,cipher):
    if os.name=='nt':return delivery.windows_decrypt(key,iv,cipher)
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
        from cryptography.hazmat.primitives import padding
    except ImportError as error:raise RuntimeError('On Mac use Python with cryptography installed, or restore on Windows first') from error
    decryptor=Cipher(algorithms.AES(key),modes.CBC(iv)).decryptor();padded=decryptor.update(cipher)+decryptor.finalize()
    unpad=padding.PKCS7(128).unpadder();return unpad.update(padded)+unpad.finalize()


def restore(release,master):
    manifest=r.read(r.ROOT/release['delivery_manifest']);blob=(r.ROOT/manifest['file']).read_bytes()
    if r.digest(blob)!=manifest['ciphertext_sha256']:raise ValueError('Encrypted source changed')
    archive=delivery.install(blob,master,Path.home()/'Downloads'/release['archive_name'],
        expected_sha256=release['archive_sha256'],decrypt=portable_decrypt)
    return extract_checked(archive,r.ROOT/release['installed_directory'],release)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,default=RELEASE)
    p.add_argument('--key');p.add_argument('--key-file',type=Path);a=p.parse_args(argv)
    if a.key and a.key_file:p.error('Choose one key input')
    value=a.key or (a.key_file.read_text(encoding='utf-8-sig') if a.key_file else input('粘贴此前V4/V5.1教材口令（输入可见，回车确认）：'))
    value=value.strip()
    if not re.fullmatch(r'[0-9a-fA-F]{64}',value):raise ValueError('Expected the same 64-character delivery key')
    master=bytes.fromhex(value);release=r.read(a.release);directory=restore(release,master)
    from scripts.wengua_rag import DEFAULT_DATA,install,verify_sources,load_library
    if not DEFAULT_DATA.exists():
        prior=r.read(r.ROOT/'data/knowledge/book_rag_v1/release.json');m=r.read(r.ROOT/'data/delivery/book_rag_v1/manifest.json')
        blob=(r.ROOT/m['file']).read_bytes()
        if r.digest(blob)!=m['ciphertext_sha256']:raise ValueError('Prior encrypted library changed')
        archive=delivery.install(blob,master,Path.home()/'Downloads'/prior['archive_name'],expected_sha256=prior['archive_sha256'],decrypt=portable_decrypt)
        install(archive)
    verify_sources(DEFAULT_DATA)
    entries=r.read(REGISTRY)['libraries'] if REGISTRY.exists() else [{'path':str(DEFAULT_DATA/'sources.json.gz'),'sha256':r.digest((DEFAULT_DATA/'sources.json.gz').read_bytes())}]
    delta=directory/'sources.json.gz';entry={'path':str(delta),'sha256':r.digest(delta.read_bytes())}
    if not any(x['path']==entry['path'] for x in entries):entries.append(entry)
    if any(r.digest(r.private(x['path']).read_bytes())!=x['sha256'] for x in entries):raise ValueError('Registered source changed')
    libraries=[load_library(x['path']) for x in entries];expected=r.merge_libraries(libraries)
    index=r.private(r.ROOT/release['index_path'])
    if not index.exists():report=r.build_index(libraries,index)
    else:
        with r.Index(index) as prior:
            hashes=json.loads(prior.db.execute("SELECT value FROM meta WHERE key='source_libraries'").fetchone()[0])
            if hashes!=expected['source_libraries']:raise ValueError('Existing index belongs to a different source set')
            report=prior.coverage
    active=r.ROOT/'local/wengua_rag/active_index.json'
    if active.exists():
        with r.Index(r.active_index()) as previous:
            old={x[0] for x in previous.db.execute('SELECT id FROM documents')};new={d['id'] for d in expected['documents']}
            if not old.issubset(new):raise ValueError('Update would drop active sources; register all prior libraries first')
    from src.wengua.book_rag_editorial import append_database
    database=r.private(r.ROOT/release['database_path']);receipt=database.with_suffix('.receipt.json')
    if r.digest((r.ROOT/release['parent_database']).read_bytes())!=release['parent_database_sha256']:raise ValueError('Parent source database differs')
    if not database.exists():
        proof=append_database(r.ROOT/release['parent_database'],database,load_library(delta),r.read(directory/'review_units.json'))
        r.write(receipt,proof|{'chapter_library_sha256':entry['sha256']})
    else:
        proof=r.read(receipt)
        if proof['output_database_sha256']!=r.digest(database.read_bytes()) or proof['chapter_library_sha256']!=entry['sha256']:raise ValueError('Existing database/receipt differs')
    r.write(REGISTRY,{'libraries':entries});r.activate_index(index)
    print('本批书稿已安装；原贴、清理版、逐项校订和Excel在：'+str(directory))
    print('累计检索库：'+r.dumps(report));print('来源数据库：'+str(database))
    print('CPU更新完成；未加载模型，未改当前V5.1训练或起盘程序。')
    return 0


if __name__=='__main__':raise SystemExit(main())
