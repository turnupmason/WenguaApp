"""Import first-chapter abstract facts/procedures into local SQLite, immutably.

Only files from this repository's approved metadata layout are read.
The user's original chapter is a separate LOCAL sections record and
is never uploaded to a public Git remote.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

from .database import connect, initialize, import_section, ROOT

DEFAULT_CHAPTER = ROOT/"data/knowledge/shenqi/shijia_qiju"

def _hex(obj:dict)->tuple[str,str]:
    canonical=json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    return canonical,hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def _load_json(path:Path)->dict:
    obj=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj,dict):
        raise ValueError(f"Expected JSON object: {path.name}")
    return obj

def register_chapter_knowledge(db_path, folder=DEFAULT_CHAPTER, *, source_file=None):
    folder=Path(folder)
    manifest=_load_json(folder/"chapter_manifest.json")
    if (manifest.get("book_id")!="shenqi"
        or manifest.get("section_key")!="shijia_qiju"
        or len(manifest.get("source_sha256",""))!=64
        or manifest.get("source_storage") != "user_chat_attachment_and_local_private_sqlite_not_public_github"):
        raise ValueError("Unexpected chapter identity and provenance")
    expected_digest=manifest["source_sha256"]
    source_status="metadata_only_original_not_in_db"
    if source_file is not None:
        p=Path(source_file)
        raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected_digest:
            raise ValueError("Provided source bytes do not match chapter SHA256")
        # Legal access remains local; never put this original text in public Git.
        import_section(db_path,"shenqi","shijia_qiju",manifest["title"],raw.decode("utf-8"))
        source_status="original_text_verified_locally"
    initialize(db_path)
    pieces = (
        ("foundation","entries",folder/"foundation.json"),
        ("casting_procedure","entries",folder/"casting_rules.json"),
        ("casting_example","cases",folder/"casting_examples.json"),
    )
    candidates=[]
    seen=set()
    sizes={}
    for category,property_name,path in pieces:
        data=_load_json(path)
        if data.get("source_sha256")!=expected_digest:
            raise ValueError("Chapter part points to different source text")
        rows=data.get(property_name)
        if not isinstance(rows,list):
            raise ValueError(f"{path.name}: entries must be list")
        sizes[category]=len(rows)
        for row in rows:
            key=row.get("id") if category!="casting_example" else row.get("case_id")
            if not isinstance(key,str) or not key or key in seen:
                raise ValueError("Missing/duplicate entry identity")
            if (category == "casting_procedure" and row.get("kind")!="casting_procedure"):
                raise ValueError("Casting knowledge mislabeled")
            seen.add(key)
            payload,digest=_hex(row)
            candidates.append((key,category,payload,digest))
    if (sizes!={"foundation":12,"casting_procedure":17,"casting_example":3}
            or len(candidates)!=32):
        raise ValueError("First-chapter reviewed extraction count changed unexpectedly")
    chapter_key="shenqi/shijia_qiju/v1"
    with connect(db_path) as con:
        old=con.execute("SELECT book_id,source_sha256,knowledge_version FROM chapter_knowledge WHERE chapter_key=?",
                        (chapter_key,)).fetchone()
        if old is None:
            con.execute("""INSERT INTO chapter_knowledge
                (chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
                VALUES (?,?,?,?,?,?,?)""",
                (chapter_key,"shenqi",manifest["title"],expected_digest,
                 manifest["source_utf8_bytes"],"1","draft"))
        elif old!=("shenqi",expected_digest,"1"):
            raise ValueError("Immutable chapter metadata changed")
        for key,category,payload,digest in candidates:
            prior=con.execute("SELECT category,payload_sha256 FROM casting_knowledge_entries WHERE chapter_key=? AND entry_id=?",
                              (chapter_key,key)).fetchone()
            if prior:
                if prior!=(category,digest):
                    raise ValueError("Existing casting rule differs; version migration required")
                continue
            con.execute("""INSERT INTO casting_knowledge_entries
               (chapter_key,entry_id,category,payload_json,payload_sha256,approval_state)
               VALUES (?,?,?,?,?,'draft')""",(chapter_key,key,category,payload,digest))
        local_count=con.execute("""SELECT COUNT(*) FROM sections
            WHERE book_id='shenqi' AND section_key='shijia_qiju' AND sha256=?""",
            (expected_digest,)).fetchone()[0]
        if local_count:
            source_status="original_text_verified_locally"
        total=con.execute("SELECT COUNT(*) FROM casting_knowledge_entries WHERE chapter_key=?",
                          (chapter_key,)).fetchone()[0]
    return {
        "chapter_key":chapter_key,"source_status":source_status,
        "extracted_counts":sizes,"stored_entries":total,
        "approved_casting_rules":0,"approved_prediction_rules":0,
        "review_state":"draft_source_extracted_not_professional_app_accepted"
    }
