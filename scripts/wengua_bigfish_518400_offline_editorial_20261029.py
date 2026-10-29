#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wengua x BigFish -- one relationship, 518400 four-pillar scenario rows.

Put this file beside local_batch.py inside the INSTALLED WenguaBigFishLocal folder.
Run `python3 wengua_518400.py`; edit RELATIONSHIP below to run the next actor.

This enumerates the abstract combinatorial space year(60) x month branch(12)
x day(60) x hour branch(12), deriving the permitted month/hour STEMS via
Five-Tiger/Five-Rat rules. It DOES NOT invent a Gregorian instant: each month
branch has two alternative solar terms. Both are separately cast, calculated,
and retained in one row. A real date/time is needed before one variant can be
used as a real-world actual cast. V8/V10.2 and data resources stay untouched.

Actual BigFish original compiled TypeScript builds each distinct physical base
board. It is cached by (yin/yang, ju 1..9, actual hour Ganzhi), never rebuilt
as a fake independent board for each calendar/person condition. For EVERY row
and BOTH JieQi alternatives, the unchanged frozen Python V8 analyzer runs
with its distinct person/month/day/hour calendar context. The research-only
source gate does not alter any original V8 score/strength/text logic.

OUTPUT: per-relationship resume SQLite + Excel-compatible CSV and genuine XLSX
files, 5000 rows/file, and shared physical base charts JSON for audit. Output
files, once exported, are NEVER overwritten, so manual/GPT edits are retained.
First execution AUTOMATICALLY installs official SHA256-verified Node LTS
if missing on macOS, then pinned BigFish + frozen Wengua via Git/npm in this Python process. No .command is needed; first installation
requires internet. Subsequent bulk computation has no GPT API/network calls.
"""
from __future__ import annotations

# ===== THESE ARE THE ONLY SETTINGS YOU NORMALLY CHANGE =====
RELATIONSHIP = 'father'       # father -> mother -> younger_sibling -> ...
PATIENT_SEX = None           # 弟弟可设 'male'；姐妹或妈妈已知女可设 'female'
PATIENT_AGE_BAND = None      # 只有确定为年轻人时填 'young'；否则保持None
BIRTH_ORDER = None           # 只有真正知道排行时填 eldest/middle/youngest
PATIENT_BIRTH_GANZHI = None  # 后来知道真实出生年干支才填完整六十甲子，如'乙丑'；与问测年柱不同
CONSULTATION_CONTEXT = None   # None=本人direct_self/别人direct_proxy；仅确实为闻讯事件可按原书设置'event_news'
MAX_NEW_ROWS = 0             # 0 = 剩余全部518400行；想小试时改20
ROWS_PER_EXCEL = 5000        # 104 numbered CSV / XLSX workbooks per person
COMMIT_EVERY = 10            # committed records surviving power loss
PRINT_EVERY = 100            # print progress every 100 newly completed rows
GENERATE_XLSX = True        # actual .xlsx (uses Python standard library only)
AUTO_INSTALL = True        # 首次运行自动安装 GitHub 固定源码与 TypeScript；只需联网一次
AUTO_INSTALL_NODE = True   # Mac 缺 Node 时自动下载官方 LTS 到本项目 toolchain，无 sudo / .command
INSTALL_ONLY = False       # 改 True 时仅安装/校验，不开始 518400 批量
STOP_IF_FIRST_ROW_FAILS = False # 缺人物用神时仅保留失败，继续生成可断的其它场景
DEFER_UNRESOLVED_JIA = False # 2026-10-29用户核准完整来源柱六甲遁仪；不再跳过甲年/月/日
MAX_CONSECUTIVE_UNEXPECTED_FAILURES = 3 # 未预先识别的双节气失败到门槛就停止并保留所有失败
# ==========================================================

import csv
import shutil
import hashlib
import json
import os
import platform
import re
import ssl
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import local_batch as base  # installed, pinned BigFish, frozen V8 resources

STEMS = tuple('甲乙丙丁戊己庚辛壬癸')
BRANCHES = tuple('子丑寅卯辰巳午未申酉戌亥')
CYCLE60 = tuple(STEMS[i % 10] + BRANCHES[i % 12] for i in range(60))
MONTH_ORDER = tuple('寅卯辰巳午未申酉戌亥子丑')
# Month-branch two possible ACTIVE 24 terms -- both must be evaluated.
TERM_BY_MONTH = {
    '寅': ('立春', '雨水'), '卯': ('惊蛰', '春分'),
    '辰': ('清明', '谷雨'), '巳': ('立夏', '小满'),
    '午': ('芒种', '夏至'), '未': ('小暑', '大暑'),
    '申': ('立秋', '处暑'), '酉': ('白露', '秋分'),
    '戌': ('寒露', '霜降'), '亥': ('立冬', '小雪'),
    '子': ('大雪', '冬至'), '丑': ('小寒', '大寒'),
}
# 五虎遁: 甲己年丙寅、乙庚年戊寅、丙辛年庚寅、丁壬年壬寅、戊癸年甲寅
MONTH_START = {'甲':'丙','己':'丙','乙':'戊','庚':'戊','丙':'庚','辛':'庚',
               '丁':'壬','壬':'壬','戊':'甲','癸':'甲'}
# 五鼠遁: 甲己日甲子、乙庚日丙子、丙辛日戊子、丁壬日庚子、戊癸日壬子
HOUR_START = {'甲':'甲','己':'甲','乙':'丙','庚':'丙','丙':'戊','辛':'戊',
              '丁':'庚','壬':'庚','戊':'壬','癸':'壬'}
N_CASES = 60 * 12 * 60 * 12  # 518400 ABSTRACT scenarios, not real timestamps
PIPELINE_VERSION = 'bigfish_518400_two_terms_sixjia_all_source_pillars_v3_earth_tomb_parity'
SIX_JIA_APPROVED_WENGUA_SHA = 'a288d127883157cb2bea96b676d2c86a45c2ab12' # user-approved Jia and earth-tomb parity; V8 math and 200/81 unchanged
SIX_JIA_BATCH_SUBDIR = '六甲全柱来源_20261029_v3_地盘墓核验'
SIX_JIA_SOURCES_ACTIVATED = False
# Old v1 vendor/, frozen/, father SQLite and manually edited Excel remain read-only.

# == One-time, Python-only pinned local installation (does not touch App/V8 code) ==
BIGFISH_REPO = 'https://github.com/perfhelf/bigfishmarquis-qimen.git'
WENGUA_REPO = 'https://github.com/turnupmason/WenguaApp.git'
FROZEN_SOURCES = {
    'reading_template.json':'data/templates/health_severity_vnext/reading_template.json',
    'health_energy_200.json':'data/mobile/health_vnext/health_energy_200.json',
    '81_pairs.tsv':'data/knowledge/health_81_excel_20261025/81_pairs.tsv',
    'actor_profiles.json':'data/knowledge/phrase_library/health_v20/actor_profiles.json',
}


def command(cmd, *, cwd=None, desc=None):
    """Use installed executables; never execute fetched shell scripts."""
    if desc:
        print('[首次安装]', desc, flush=True)
    try:
        subprocess.run([str(x) for x in cmd], cwd=cwd, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError(f'缺少执行程序: {cmd[0]}。请先安装 Git 和 Node.js（含 npm），然后重试 PyCharm Run。') from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f'首次安装步骤失败：{desc or cmd[0]}（退出码 {exc.returncode}）。首次运行需要联网；检查 GitHub/npm 网络后重新 Run，可续装，不会删除输出。') from exc


def checkout_pinned(repo_url, dest, sha, label):
    if not (dest / '.git').exists():
        if dest.exists() and any(dest.iterdir()):
            raise RuntimeError(f'已存在非 Git 目录 {dest}，为防止覆盖文件自动安装停止。请手动检查。')
        if dest.exists():
            dest.rmdir()
        command(['git', 'clone', '--quiet', repo_url, str(dest)], desc='下载'+label+'固定版本源码（只首次联网）')
    head = subprocess.run(['git','rev-parse','HEAD'],cwd=dest,
                          text=True,capture_output=True,check=True).stdout.strip()
    if head == sha:
        return
    dirty = subprocess.run(['git','status','--porcelain'],cwd=dest,
                           text=True,capture_output=True,check=True).stdout.strip()
    if dirty:
        raise RuntimeError(f'{label} 本地 Git 源有未提交改动，不能自动切换固定版本：{dest}')
    has_sha = subprocess.run(['git','cat-file','-e',sha+'^{commit}'],cwd=dest,
                             capture_output=True).returncode == 0
    if not has_sha:
        command(['git','fetch','--quiet','origin',sha],cwd=dest,
                desc='抓取'+label+'指定固定提交')
    command(['git','checkout','--quiet','--detach',sha],cwd=dest,
            desc=label+'固定到审核提交 '+sha[:12])



def _extend_macos_tool_path():
    """PyCharm started from Finder may not inherit nvm/brew/fnm/mise PATH."""
    home = Path.home()
    fixed = [
        HERE / 'toolchain' / 'node_runtime' / 'bin',
        Path('/opt/homebrew/bin'), Path('/opt/homebrew/opt/node/bin'),
        Path('/usr/local/bin'), Path('/usr/local/opt/node/bin'),
        home / '.volta/bin', home / '.fnm/aliases/default/bin',
        home / '.local/share/mise/shims', home / '.asdf/shims',
        Path('/usr/bin'), Path('/bin'),
    ]
    for globpat in ('.nvm/versions/node/v*/bin', '.local/share/mise/installs/node/*/bin',
                    '.local/share/fnm/node-versions/v*/installation/bin'):
        fixed.extend(sorted(home.glob(globpat), reverse=True))
    existing = os.environ.get('PATH', '').split(os.pathsep)
    paths = [str(x) for x in [*fixed, *map(Path, existing)] if str(x) and x.is_dir()]
    os.environ['PATH'] = os.pathsep.join(dict.fromkeys(paths))


def _verified_https_context() -> ssl.SSLContext:
    """Always verify HTTPS; supplement python.org macOS Python's missing CA bundle.

    python.org macOS 3.11 may not have run `Install Certificates.command`.
    `certifi` is a well maintained Mozilla root CA bundle if installed in the
    current venv. macOS SystemRoot keychain is the other authoritative source.
    Neither path turns off TLS verification or accepts untrusted certificates.
    """
    context = ssl.create_default_context()
    try:
        import certifi
        ca = certifi.where()
        if ca and Path(ca).is_file():
            context.load_verify_locations(cafile=ca)
    except (ImportError, OSError, ssl.SSLError):
        # certifi is optional; try Apple's trusted root keychain below.
        pass

    if platform.system() == 'Darwin':
        roots = Path('/System/Library/Keychains/SystemRootCertificates.keychain')
        security = Path('/usr/bin/security')
        if roots.is_file() and security.is_file():
            try:
                export = subprocess.run(
                    [str(security), 'find-certificate', '-a', '-p', str(roots)],
                    capture_output=True, text=True, check=True, timeout=25)
                if '-----BEGIN CERTIFICATE-----' in export.stdout:
                    context.load_verify_locations(cadata=export.stdout)
            except (OSError, subprocess.CalledProcessError,
                    subprocess.TimeoutExpired, ssl.SSLError, ValueError):
                # Never degrade to SSL_CERT_NONE / unverified HTTP.
                pass
    return context


def _official_url(url: str, *, max_bytes: int) -> bytes:
    """Download verified official HTTPS data with a bounded response size."""
    if not url.startswith('https://nodejs.org/dist/'):
        raise ValueError('Node下载地址不在 nodejs.org 官方发布目录')
    req = urllib.request.Request(url, headers={'User-Agent':'WenguaMacNodeBootstrap/1.1'})
    try:
        # Critical: python.org Mac Python often lacks its default CA bundle.
        # This explicit SSLContext still enforces hostname and issuer checks.
        with urllib.request.urlopen(req, timeout=65, context=_verified_https_context()) as reply:
            chunks, size = [], 0
            while True:
                block = reply.read(1024*1024)
                if not block:
                    break
                size += len(block)
                if size > max_bytes:
                    raise RuntimeError('Node官方下载超出安全大小上限，停止安装')
                chunks.append(block)
        return b''.join(chunks)
    except urllib.error.URLError as exc:
        root = exc.reason
        if isinstance(root, (ssl.SSLCertVerificationError, ssl.SSLError)) and (
                isinstance(root, ssl.SSLCertVerificationError) or
                'CERTIFICATE_VERIFY_FAILED' in str(root)):
            raise RuntimeError(
                'macOS Python 3.11无法验证 nodejs.org HTTPS 证书链。'
                '请先在 Mac 终端执行：\n'
                'open \"/Applications/Python 3.11/Install Certificates.command\"\n'
                '如果你使用公司网络代理，需要安装其受信任的CA证书；'
                '绝不能关闭SSL证书校验。修好后回 PyCharm 重新运行。'
            ) from exc
        raise


def _extract_node_release(archive: Path, dst: Path, prefix: str):
    """Do not extract arbitrary upstream paths/links; only Node and bundled npm."""
    with tarfile.open(archive, 'r:gz') as package:
        have_node = have_npm = False
        for member in package:
            parts = member.name.split('/')
            if not parts or parts[0] != prefix or any(x in ('', '.', '..') for x in parts):
                continue
            relative = Path(*parts[1:])
            key = relative.as_posix()
            if key != 'bin/node' and not key.startswith('lib/node_modules/npm/'):
                continue
            if not member.isfile():
                # Symlinks and hardlinks are deliberately excluded.
                continue
            target = dst / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            fileobj = package.extractfile(member)
            if fileobj is None:
                raise RuntimeError('Node官方tar文件内容缺失: ' + key)
            with fileobj, target.open('wb') as out:
                shutil.copyfileobj(fileobj, out)
            if key == 'bin/node':
                target.chmod(0o755)
                have_node=True
            if key == 'lib/node_modules/npm/bin/npm-cli.js':
                have_npm=True
        if not have_node or not have_npm:
            raise RuntimeError('Node官方包缺少node或npm程序，拒绝假装安装成功')
    npm=dst/'bin/npm'
    npm.write_text('#!/bin/sh\nexec "$(dirname "$0")/node" "$(dirname "$0")/../lib/node_modules/npm/bin/npm-cli.js" "$@"\n',encoding='utf-8')
    npm.chmod(0o755)


def _install_node_official_lts():
    """Mac, no admin: verified official archive, local runtime, atomic install."""
    if platform.system() != 'Darwin':
        raise RuntimeError('自动安装Node只支持macOS；其他系统请先安装Node.js LTS')
    machine=platform.machine().lower()
    arch={'arm64':'arm64','aarch64':'arm64','x86_64':'x64','amd64':'x64'}.get(machine)
    if arch is None:
        raise RuntimeError('不支持的Mac处理器架构: '+machine+'；请手动安装Node.js LTS')
    toolchain=HERE/'toolchain'
    toolchain.mkdir(parents=True, exist_ok=True)
    root=toolchain/'node_runtime'
    if root.exists():
        raise RuntimeError('本地Node目录已存在但不可用，拒绝覆盖: '+str(root)+
                           '。请先检查此目录；也可用 brew install node')
    print('[首次安装] PyCharm找不到Node/npm，正在从 nodejs.org 下载官方LTS（只首次联网）...',flush=True)
    index=json.loads(_official_url('https://nodejs.org/dist/index.json',max_bytes=4_000_000))
    suffix='osx-'+arch+'-tar'
    release=next((x for x in index if x.get('lts') and suffix in x.get('files',()) and
                  re.fullmatch(r'v\d+\.\d+\.\d+',x.get('version',''))),None)
    if release is None:
        raise RuntimeError('Node官方版本表没有可用的macOS LTS tar包')
    version=release['version']
    filename=f'node-{version}-darwin-{arch}.tar.gz'
    baseurl=f'https://nodejs.org/dist/{version}/'
    shas=_official_url(baseurl+'SHASUMS256.txt',max_bytes=250_000).decode('utf-8')
    candidates={cols[1]:cols[0] for line in shas.splitlines()
                if len(cols:=line.strip().split())==2}
    wanted=candidates.get(filename)
    if not wanted or not re.fullmatch('[a-f0-9]{64}',wanted):
        raise RuntimeError('Node官方SHA256清单没有目标安装包: '+filename)
    print(f'[首次安装] 官方Node {version}，Mac {arch}，校验SHA256...',flush=True)
    with tempfile.TemporaryDirectory(prefix='.node_verified_',dir=toolchain) as td:
        temp=Path(td)
        archive=temp/filename
        archive.write_bytes(_official_url(baseurl+filename,max_bytes=180_000_000))
        actual=hashlib.sha256(archive.read_bytes()).hexdigest()
        if actual!=wanted:
            raise RuntimeError('Node官方文件SHA256不匹配，拒绝安装')
        stage=temp/'stage'
        stage.mkdir()
        _extract_node_release(archive,stage,filename.removesuffix('.tar.gz'))
        node_version=subprocess.run([str(stage/'bin/node'),'--version'],text=True,
                                    capture_output=True,check=True,timeout=15).stdout.strip()
        npm_version=subprocess.run([str(stage/'bin/npm'),'--version'],text=True,
                                   capture_output=True,check=True,timeout=20).stdout.strip()
        if node_version != version or not npm_version:
            raise RuntimeError('官方Node/npm本地运行校验失败')
        (stage/'NODE_SOURCE_SHA256.txt').write_text(filename+'\n'+wanted+'\n',encoding='utf-8')
        stage.rename(root)
    _extend_macos_tool_path()
    print(f'[首次安装] 官方Node {version} / npm {npm_version} 已安装到 {root}。无需管理员权限。',flush=True)


def ensure_node_available():
    """Prefer already installed Node; otherwise verified project-local LTS."""
    _extend_macos_tool_path()
    node=shutil.which('node')
    npm=shutil.which('npm')
    if node and npm:
        version=subprocess.run([node,'--version'],text=True,capture_output=True,timeout=10)
        if version.returncode==0 and re.fullmatch(r'v\d+\.\d+\.\d+',version.stdout.strip()):
            major=int(version.stdout.strip()[1:].split('.')[0])
            if major>=20:
                print('[首次安装] 已找到Node '+version.stdout.strip()+'，npm: '+npm,flush=True)
                return
    if not AUTO_INSTALL_NODE:
        raise RuntimeError('缺少可用Node.js (20+) 或npm。Mac终端执行 brew install node，重启PyCharm；'+
                           '或设 AUTO_INSTALL_NODE=True 让Python自动安装。')
    _install_node_official_lts()
    if not shutil.which('node') or not shutil.which('npm'):
        raise RuntimeError('Node下载完成但PATH仍不可用；请检查toolchain/node_runtime/bin')


def activate_six_jia_sources():
    """Side-by-side pin the new user-approved role binding source.

    The Mac package's original pinned Wengua SHA and local_batch.py remain
    physically unchanged; only this running adapter points at a new checkout.
    """
    global SIX_JIA_SOURCES_ACTIVATED
    if SIX_JIA_SOURCES_ACTIVATED:
        return
    base.WENGUA_SHA = SIX_JIA_APPROVED_WENGUA_SHA
    base.SOURCE = HERE / 'vendor' / 'WenguaApp_sixjia_source_v2'
    base.FROZEN = HERE / 'frozen_sixjia_source_v2'
    SIX_JIA_SOURCES_ACTIVATED = True


def ensure_install():
    """Idempotent: install only absent components and verify frozen SHA.

    Network is confined to this bootstrap stage. Dataset and scoring sources
    are byte-for-byte the original pinned versions; existing output is untouched.
    """
    # PyCharm/Finder often omits Homebrew/nvm paths. This MUST run even when
    # frozen sources are already installed: the Node worker starts afterwards.
    # The former fast-path returned before Node was put on PATH, causing Popen
    # FileNotFoundError despite successful source/resource checks.
    _extend_macos_tool_path()
    ensure_node_available()
    try:
        return base.check_install()
    except (RuntimeError, FileNotFoundError, OSError, ValueError, KeyError) as why:
        if not AUTO_INSTALL:
            raise RuntimeError(f'本地依赖缺失：{why}。设置 AUTO_INSTALL=True 后重新在 PyCharm Run。') from why
        print('首次依赖检查：', why, flush=True)
        print('正在通过 Python 自动完成一次性安装（无需 .command）。', flush=True)
    _extend_macos_tool_path()
    if not shutil.which('git'):
        raise RuntimeError('缺少Git。请先在Mac终端执行 xcode-select --install 安装命令行工具，或用 brew install git。')
    ensure_node_available()
    base.UPSTREAM.parent.mkdir(parents=True, exist_ok=True)
    base.FROZEN.mkdir(parents=True, exist_ok=True)
    base.OUTPUT.mkdir(parents=True, exist_ok=True)
    checkout_pinned(BIGFISH_REPO, base.UPSTREAM, base.BIGFISH_SHA, 'BigFish')
    checkout_pinned(WENGUA_REPO, base.SOURCE, base.WENGUA_SHA, 'Wengua V8.0')
    toolchain = HERE / 'toolchain'
    toolchain.mkdir(exist_ok=True)
    tsc = toolchain / 'node_modules' / '.bin' / 'tsc'
    version = subprocess.run([str(tsc),'--version'],text=True,capture_output=True).stdout.strip() if tsc.is_file() else ''
    if version != 'Version 5.8.3':
        command(['npm','--prefix',str(toolchain),'install','--no-save',
                 '--save-exact','typescript@5.8.3'],
                desc='安装固定版本 TypeScript 5.8.3')
    compiled = base.COMPILED / 'engines' / 'shijia.js'
    if not compiled.exists():
        base.COMPILED.mkdir(parents=True, exist_ok=True)
        files=['shijia.ts','chaibuquju.ts','maoshan.ts','zhirun.ts']
        command([str(tsc),'--module','commonjs','--target','es2020',
                 '--moduleResolution','node','--lib','es2020,dom',
                 '--skipLibCheck','--rootDir',str(base.UPSTREAM/'src'),
                 '--outDir',str(base.COMPILED),
                 *[str(base.UPSTREAM/'src/engines'/f) for f in files]],
                desc='编译 BigFish 原始 TypeScript 引擎（不改源码）')
    manifest = {
        'scope':'V8.0 frozen scoring / V10.2 reading, do not modify',
        'bigfish_sha':base.BIGFISH_SHA,
        'wengua_sha':base.WENGUA_SHA,
        'files':{},
    }
    for name, rel in FROZEN_SOURCES.items():
        source = base.SOURCE / rel
        dest = base.FROZEN / name
        if not source.is_file():
            raise RuntimeError('GitHub 固定源码缺少规则资源：'+str(source))
        expected = hashlib.sha256(source.read_bytes()).hexdigest()
        if dest.is_file() and hashlib.sha256(dest.read_bytes()).hexdigest()!=expected:
            raise RuntimeError('发现冻结资源已被修改，为保护用户文件不自动覆盖：'+str(dest))
        if not dest.is_file():
            shutil.copy2(source, dest)
        manifest['files'][name]={'source':rel,'sha256':expected}
    mfile=base.FROZEN/'FREEZE_MANIFEST.json'
    if mfile.exists():
        old=json.loads(mfile.read_text('utf-8'))
        if old!=manifest:
            raise RuntimeError('已有 FREEZE_MANIFEST.json 内容与固定版本不同，拒绝静默覆盖：'+str(mfile))
    else:
        mfile.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    verified=base.check_install()
    print('[首次安装] BigFish TS + Wengua V8 + 4份冻结资源均已校验。以后可离线运行。',flush=True)
    return verified


# Same independent single-process gate as candidate_source_gate.py in the
# original Mac package, embedded so PyCharm needs no extra helper .py.
_SOURCE_KEY='perfhelf/bigfishmarquis-qimen@'+base.BIGFISH_SHA
_GUA={1:'坎',2:'坤',3:'震',4:'巽',5:'中',6:'乾',7:'兑',8:'艮',9:'离'}
_STARS={'天蓬星','天芮星','天冲星','天辅星','天心星','天柱星','天任星','天英星','天禽星'}
_DOORS={'休门','生门','伤门','杜门','景门','死门','惊门','开门'}
_GODS={'值符','螣蛇','太阴','六合','白虎','玄武','九地','九天'}
_STEMS=set('戊己庚辛壬癸丁丙乙')


def validate_bigfish_board(chart):
    from src.wengua.casting_shenqi import xun_shou, SIX_JIA
    if chart.get('school_id')!='shijia_zhuanpan' or chart.get('casting_variant')!='bigfish_shijia_chaibu_pilot':
        raise ValueError('Only original BigFish direct shiJiaGenerate board can pass')
    if chart.get('source_key')!=_SOURCE_KEY or chart.get('status')!='bigfish_unapproved_candidate':
        raise ValueError('Untrusted source identity/status')
    if chart.get('dun') not in ('yang','yin') or type(chart.get('ju')) is not int or not 1<=chart['ju']<=9:
        raise ValueError('Invalid original bureau')
    xun, steps, hidden=xun_shou(chart.get('hour_ganzhi',''))
    if (chart.get('xun_shou'),chart.get('hidden_stem'))!=(xun,hidden) or SIX_JIA[xun]!=hidden:
        raise ValueError('Wrong hour xun hidden carrier')
    palaces=chart.get('palaces')
    if not isinstance(palaces,dict) or set(palaces)!={str(i) for i in range(1,10)}:
        raise ValueError('Nine palaces required')
    stars=[];doors=[];gods=[];earth=[]
    for i in range(1,10):
        p=palaces[str(i)]
        if p.get('palace')!=i or p.get('gua')!=_GUA[i]:
            raise ValueError('Incorrect physical palace')
        e=p.get('earth_stem')
        if e not in _STEMS:
            raise ValueError('Invalid physical earth plate stem')
        earth.append(e)
        if i==5:
            if p['heaven_stars'] or p['door'] is not None or p['deity'] is not None:
                raise ValueError('Middle five may not have ordinary stars/doors/gods')
            continue
        for star in p.get('heaven_stars',()):
            if star.get('star') not in _STARS or star.get('carried_stem') not in _STEMS:
                raise ValueError('Missing true heaven star or stem')
            stars.append(star['star'])
        if p.get('door') not in _DOORS or p.get('deity') not in _GODS:
            raise ValueError('Missing eight ordinary doors/deities')
        doors.append(p['door']);gods.append(p['deity'])
    if len(set(earth))!=9 or len(stars)!=9 or set(stars)!=_STARS or len(set(doors))!=8 or len(set(gods))!=8:
        raise ValueError('Source missing or duplicate real nine-palace factor')
    if chart.get('value_star') not in _STARS or chart.get('value_door') not in _DOORS:
        raise ValueError('Wrong source value signifier')
    if chart.get('value_star_palace') not in range(1,10) or chart.get('value_door_palace') not in range(1,10):
        raise ValueError('Wrong actual value position')
    return chart


@contextmanager
def bigfish_candidate_only(chart):
    validate_bigfish_board(chart)
    from src.wengua import health_severity_v22
    old=health_severity_v22._validate_chart
    def scoped_gate(incoming):
        if incoming is not chart:
            raise ValueError('Old Wengua source substitution forbidden')
        return validate_bigfish_board(incoming)
    health_severity_v22._validate_chart=scoped_gate
    try:
        yield
    finally:
        health_severity_v22._validate_chart=old



def month_ganzhi(year_gz: str, month_branch: str) -> str:
    if year_gz not in CYCLE60 or month_branch not in MONTH_ORDER:
        raise ValueError('Invalid year Ganzhi or month branch')
    start = STEMS.index(MONTH_START[year_gz[0]])
    return STEMS[(start + MONTH_ORDER.index(month_branch)) % 10] + month_branch


def hour_ganzhi(day_gz: str, hour_branch: str) -> str:
    if day_gz not in CYCLE60 or hour_branch not in BRANCHES:
        raise ValueError('Invalid day Ganzhi or hour branch')
    start = STEMS.index(HOUR_START[day_gz[0]])
    return STEMS[(start + BRANCHES.index(hour_branch)) % 10] + hour_branch


def scenario(index: int) -> dict:
    if not 0 <= index < N_CASES:
        raise IndexError(index)
    h = index % 12
    d = (index // 12) % 60
    m = (index // (12 * 60)) % 12
    y = index // (12 * 60 * 12)
    yg, mb, dg, hb = CYCLE60[y], MONTH_ORDER[m], CYCLE60[d], BRANCHES[h]
    return {'year': yg, 'month': month_ganzhi(yg, mb),
            'day': dg, 'hour': hour_ganzhi(dg, hb)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def canonical(data) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def key_for(index: int, term: str) -> str:
    return sha_text(canonical((PIPELINE_VERSION, base.BIGFISH_SHA,
                               base.WENGUA_SHA, RELATIONSHIP, index, term)))[:24]


BRIDGE = r'''"use strict";
// Original BigFish compiled TypeScript ONLY. One long-running Node worker.
const rl=require('node:readline');
const path=require('node:path');
const root=path.resolve(process.argv[2]);
const {shiJiaGenerate}=require(path.join(root,'engines/shijia.js'));
const {chaiBuJuByGanZhi}=require(path.join(root,'engines/chaibuquju.js'));
function gz(s){return {gan:s[0],zhi:s[1]};}
const four0={year:gz('甲子'),month:gz('丙寅'),day:gz('甲子'),hour:gz('甲子')};
const input=rl.createInterface({input:process.stdin,crlfDelay:Infinity});
input.on('line',line=>{
 try{
   const a=JSON.parse(line);
   let result;
   if(a.action==='bureau') {
     result=chaiBuJuByGanZhi(a.term,a.day[0],a.day[1]);
   }else if(a.action==='layout'){
     if(!['yang','yin'].includes(a.dun)||!(a.ju>=1&&a.ju<=9))throw Error('Invalid bureau');
     const four={...four0,hour:gz(a.hour)};
     result=shiJiaGenerate(a.hour[0],a.hour[1],a.ju,a.dun,four,a.term);
   }else throw Error('Invalid BigFish worker request');
   process.stdout.write(JSON.stringify({ok:true,result})+'\n');
 }catch(e){process.stdout.write(JSON.stringify({ok:false,error:String(e.stack||e)})+'\n');}
});
'''


class BigFishWorker:
    """One Node process; physical arrangements cached by TRUE 1080-key."""
    def __init__(self, out_dir: Path):
        out_dir.mkdir(parents=True, exist_ok=True)
        js_file = out_dir / '_bigfish_worker.cjs'
        # This generated source is static and cannot modify original TS.
        if not js_file.exists() or js_file.read_text('utf-8') != BRIDGE:
            js_file.write_text(BRIDGE, encoding='utf-8')
        node_executable = shutil.which('node')
        if not node_executable:
            raise RuntimeError('BigFish启动需要Node.js：未找到node可执行文件。'
                               '请先安装Node.js 20+（含npm），或检查PyCharm运行环境PATH；'
                               '本脚本的ensure_install应自动准备Node。')
        self.error_file=(out_dir / '_bigfish_node_errors.log').open('a',encoding='utf-8')
        self.p = subprocess.Popen([node_executable, str(js_file), str(base.COMPILED)],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=self.error_file, text=True, bufsize=1)
        self.bureaus = {}                 # (actual 24 solar term, real day GZ)
        self.physical = {}                # (dun, ju, actual hour GZ)
        self.physical_dir = out_dir / 'physical_1080'
        self.physical_dir.mkdir(parents=True, exist_ok=True)
        self.out_dir = out_dir

    def ask(self, req: dict):
        if self.p.poll() is not None:
            raise RuntimeError('BigFish Node worker exited unexpectedly; see '+str(self.out_dir / '_bigfish_node_errors.log'))
        self.p.stdin.write(canonical(req) + '\n')
        self.p.stdin.flush()
        line = self.p.stdout.readline()
        if not line:
            raise RuntimeError('No response from real compiled BigFish TypeScript; see '+str(self.out_dir / '_bigfish_node_errors.log'))
        response = json.loads(line)
        if not response.get('ok'):
            raise RuntimeError('BigFish TypeScript failed: ' + str(response.get('error'))[:2000])
        return response['result']

    def bureau(self, term: str, day: str):
        key = (term, day)
        if key not in self.bureaus:
            b = self.ask({'action':'bureau','term':term,'day':day})
            if not 1 <= b['juNumber'] <= 9 or type(b['isYangDun']) is not bool:
                raise ValueError('Invalid BigFish source bureau')
            self.bureaus[key] = b
        return self.bureaus[key]

    def chart(self, bureau: dict, hour: str, term: str):
        dun = 'yang' if bureau['isYangDun'] else 'yin'
        ju = bureau['juNumber']
        key = (dun, ju, hour)
        if key not in self.physical:
            true_chart = self.ask({'action':'layout','dun':dun,'ju':ju,
                                   'hour':hour,'term':term})
            # Original upstream shiJiaGenerate doesn't inject JieQi bureau yuan;
            # same as production bigfish_cast.cjs, attach the REAL bureau result.
            true_chart['yuan'] = bureau['yuan']
            # BigFish had been passed placeholder year/day/month ONLY to
            # establish the physical board; never label those as true clock.
            raw = {'chart':true_chart,'method':'chaibu','bureau_raw':bureau}
            parsed = base.normalize_bigfish({'chart':true_chart,
                                              'method':'chaibu','bureau':bureau})
            if parsed['dun']!=dun or parsed['ju']!=ju:
                raise ValueError('BigFish physical chart bureau mismatch')
            atlas_id = f'{dun}-{ju:02d}-{hour}'
            stable_data = {
                'physical_id':atlas_id,'source_commit':base.BIGFISH_SHA,
                'hour_ganzhi':hour,'dun':dun,'ju':ju,
                'palaces':parsed['palaces'], 'value_star':parsed['value_star'],
                'value_door':parsed['value_door'],
                'value_star_palace':parsed['value_star_palace'],
                'value_door_palace':parsed['value_door_palace'],
                'source_original_raw':raw,
                'not_a_real_calendar_instant':True,
            }
            path = self.physical_dir / f'{atlas_id}.json'
            if not path.exists():
                path.write_text(json.dumps(stable_data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            self.physical[key] = stable_data
        return self.physical[key]

    def close(self):
        if self.p.poll() is None:
            self.p.stdin.close()
            try:self.p.wait(timeout=4)
            except subprocess.TimeoutExpired:self.p.kill()
        self.error_file.close()


HEADERS = [
 '序号','人物ID','人物名称','年柱','月柱','日柱','时柱',
 '节气甲','起局甲','等级甲','V8原始分甲(内部)','状态甲','断词甲','盘式编号甲','证据SHA甲','失败原因甲',
 '节气乙','起局乙','等级乙','V8原始分乙(内部)','状态乙','断词乙','盘式编号乙','证据SHA乙','失败原因乙',
 '校验状态','真实公历日期','人工修改甲','人工修改乙','GPT修订甲','GPT修订乙','人工审核状态','数据来源',
 '主用神来源甲','主用神干甲','主用神宫甲','年命是否参与甲','年命宫甲',
 '主用神来源乙','主用神干乙','主用神宫乙','年命是否参与乙','年命宫乙',
]


def initialize_db(db_path: Path, config: dict) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=FULL')
    conn.execute('CREATE TABLE IF NOT EXISTS settings (name TEXT PRIMARY KEY, value TEXT NOT NULL)')
    conn.execute('''CREATE TABLE IF NOT EXISTS cases (
        idx INTEGER PRIMARY KEY, case_id TEXT UNIQUE NOT NULL,
        pillars_json TEXT NOT NULL,
        result_jie_json TEXT NOT NULL, result_qi_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    )''')
    current = conn.execute("SELECT value FROM settings WHERE name='config'").fetchone()
    config_string = canonical(config)
    if current and current[0]!=config_string:
        raise RuntimeError('This results DB belongs to a DIFFERENT frozen config/actor; never overwrite it')
    if not current:
        conn.execute('INSERT INTO settings VALUES (?,?)',('config',config_string))
        conn.commit()
    return conn


def literal_excel(value):
    s = '' if value is None else str(value)
    # CSV formula-injection guard: Excel should treat human/GPT text as data.
    if s.lstrip().startswith(('=', '+', '-', '@')) or s.startswith(('\t','\r')):
        return "'" + s
    return s


def excel_ref(i):
    s=''
    while i:
        i,v=divmod(i-1,26)
        s=chr(65+v)+s
    return s


def clean_xml(s):
    # XML 1.0 cannot include control chars even when CSV can.
    text=literal_excel(s)
    text=''.join(c for c in text if ord(c)>=32 or c in '\t\r\n')
    return xml_escape(text, {'"':'&quot;'})


def write_xlsx(path: Path, rows):
    """Write an Excel-compatible .xlsx ZIP in bounded memory, no pip deps.

    Inline strings prevent formula execution and avoid costly shared-string
    tables for millions of distinct classical Chinese reading cells.
    """
    path.parent.mkdir(parents=True,exist_ok=True)
    temp = path.with_suffix('.xlsx.incomplete')
    with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED, compresslevel=6,
                         allowZip64=True) as z:
        z.writestr('[Content_Types].xml',
          '<?xml version="1.0" encoding="UTF-8"?>'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
          '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
          '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
          '</Types>')
        z.writestr('_rels/.rels',
          '<?xml version="1.0" encoding="UTF-8"?>'
          '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
          '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
          '</Relationships>')
        z.writestr('xl/workbook.xml',
          '<?xml version="1.0" encoding="UTF-8"?>'
          '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
          ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
          '<sheets><sheet name="逐时辰条件候选" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels',
          '<?xml version="1.0" encoding="UTF-8"?>'
          '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
          '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
          '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
          '</Relationships>')
        z.writestr('xl/styles.xml',
          '<?xml version="1.0" encoding="UTF-8"?>'
          '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
          '<fonts count="2"><font><sz val="11"/><name val="Arial"/></font>'
          '<font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Arial"/></font></fonts>'
          '<fills count="3"><fill><patternFill patternType="none"/></fill>'
          '<fill><patternFill patternType="gray125"/></fill>'
          '<fill><patternFill patternType="solid"><fgColor rgb="FF143653"/><bgColor indexed="64"/></patternFill></fill></fills>'
          '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
          '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
          '<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
          '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFill="1" applyFont="1"/>'
          '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1">'
          '<alignment vertical="top" wrapText="1"/></xf></cellXfs>'
          '</styleSheet>')
        with z.open('xl/worksheets/sheet1.xml', 'w') as f:
            def write(text):f.write(text.encode('utf-8'))
            max_col=excel_ref(len(HEADERS))
            write('<?xml version="1.0" encoding="UTF-8"?>'
                  '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                  '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
                  '<sheetFormatPr defaultRowHeight="22"/>'
                  '<cols>')
            for k in range(1,len(HEADERS)+1):
                width=60 if k in (13,22) else 22 if k in (16,25,27,28,29,30) else 16
                write(f'<col min="{k}" max="{k}" width="{width}" customWidth="1"/>')
            write('</cols><sheetData>')
            def row_xml(row_idx, values):
                write(f'<row r="{row_idx}">')
                for j,val in enumerate(values,1):
                    cell=f'{excel_ref(j)}{row_idx}'
                    style='1' if row_idx==1 else ('2' if j in (13,22) else '0')
                    # XL cells at most 32767 Unicode chars. Full text is still
                    # retained in SQLite and CSV without this Excel UI limit.
                    v=clean_xml(str(val)[:32767])
                    write(f'<c r="{cell}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{v}</t></is></c>')
                write('</row>')
            row_xml(1,HEADERS)
            count=1
            for count, values in enumerate(rows,2):
                row_xml(count, values)
            write('</sheetData>')
            write(f'<autoFilter ref="A1:{max_col}{count}"/>')
            write('</worksheet>')
    os.replace(temp,path)


def format_part(result: dict):
    return [result.get('term',''),result.get('bureau',''),result.get('grade',''),
            result.get('score',''),result.get('status',''),result.get('text',''),
            result.get('base_id',''),result.get('evidence_sha',''),result.get('error','')]


def make_row(idx, pillars, jie, qi, labels):
    return ([idx+1, RELATIONSHIP, labels.get(RELATIONSHIP,RELATIONSHIP),
             pillars['year'],pillars['month'],pillars['day'],pillars['hour']]
            +format_part(jie)+format_part(qi)
            +['抽象四柱条件候选 / 未绑定真实公历时刻','', '', '', '', '',
              '待人工审核','BigFish原TS起盘 + Wengua V8.0/V10.2现有Python断案链(未核实公历时刻)']
            + [value for result in (jie,qi) for value in (
                result.get('source_fact_lock',{}).get('person_binding',{}).get('role_via',''),
                result.get('source_fact_lock',{}).get('person_binding',{}).get('stem',''),
                result.get('source_fact_lock',{}).get('person_binding',{}).get('palace',''),
                result.get('source_fact_lock',{}).get('person_binding',{}).get('natal_active',False),
                result.get('source_fact_lock',{}).get('person_binding',{}).get('natal_palace',''),
              )])


def export_completed_chunks(db, folder, labels, *, completed_only=True):
    """Snapshot only COMPLETED chunks. Never overwrite human-edited files."""
    outputs=folder/'Excel_CSV_可直接打开'
    outputs.mkdir(parents=True,exist_ok=True)
    n=int(db.execute('SELECT COUNT(*) FROM cases').fetchone()[0])
    # Sequential run, and intentional stop at MAX_NEW_ROWS in a partial chunk.
    end = min(N_CASES, (n // ROWS_PER_EXCEL) * ROWS_PER_EXCEL) if completed_only else n
    exported=0
    for start in range(0,end,ROWS_PER_EXCEL):
        stop=min(start+ROWS_PER_EXCEL,end)
        csv_path=outputs/f'{RELATIONSHIP}_{start+1:06d}-{stop:06d}.csv'
        xlsx_path=outputs/f'{RELATIONSHIP}_{start+1:06d}-{stop:06d}.xlsx'
        jsonl_path=outputs/f'{RELATIONSHIP}_{start+1:06d}-{stop:06d}_待审事实包.jsonl'
        if csv_path.exists() and (not GENERATE_XLSX or xlsx_path.exists()) and jsonl_path.exists():
            continue
        originals=list(db.execute('''SELECT idx,pillars_json,result_jie_json,result_qi_json
                                    FROM cases WHERE idx BETWEEN ? AND ? ORDER BY idx''',(start,stop-1)))
        if len(originals)!=(stop-start) or [r[0] for r in originals]!=list(range(start,stop)):
            continue   # Never export incomplete chunk as if complete.
        data=[make_row(i,json.loads(p),json.loads(j),json.loads(q),labels) for i,p,j,q in originals]
        if not csv_path.exists():
            tmp=csv_path.with_suffix('.csv.incomplete')
            with tmp.open('w',encoding='utf-8-sig',newline='') as f:
                writer=csv.writer(f)
                writer.writerow(HEADERS)
                writer.writerows([[literal_excel(v) for v in row] for row in data])
            os.replace(tmp,csv_path)
        if GENERATE_XLSX and not xlsx_path.exists():
            write_xlsx(xlsx_path,data)
        export_editorial_jsonl(jsonl_path,originals,relationship=RELATIONSHIP)
        exported+=1
    return exported


def export_editorial_jsonl(path: Path, originals, *, relationship: str):
    """One auditable original for each of the TWO term branches per row.

    No API calls, no rewriting. Writes source/fact lock + blank reviewer fields.
    An existing file is never overwritten (human/GPT edits remain intact).
    """
    if path.exists():
        return False
    tmp=path.with_suffix('.jsonl.incomplete')
    with tmp.open('w',encoding='utf-8') as out:
        for index,p,j,q in originals:
            four=json.loads(p)
            for source_variant,item in (('甲',json.loads(j)),('乙',json.loads(q))):
                identity={'relationship':relationship,'index':index+1,
                          'four_pillars':four,'term':item.get('term'),
                          'source_version':PIPELINE_VERSION,
                          'wengua_sha':base.WENGUA_SHA,'bigfish_sha':base.BIGFISH_SHA}
                payload={
                    'schema':'wengua_v80_v102_bigfish_editorial_precompute_v1',
                    'case_id':sha_text(canonical(identity))[:32],
                    'immutable_identity':identity,
                    'branch':source_variant,
                    'source_type':'abstract_four_pillars_two_term_conditional_not_real_instant',
                    'original_result':{
                        'status':item.get('status'), 'grade':item.get('grade'),
                        'score_internal':item.get('score'), 'bureau':item.get('bureau'),
                        'physical_board_id':item.get('base_id'),
                        'physical_board_json':('physical_1080/'+item['base_id']+'.json') if item.get('base_id') else None,
                        'original_text':item.get('text',''),
                        'original_text_sha256':item.get('original_text_sha256',''),
                        'sections':item.get('sections',[]),
                        'frozen_fact_lock':item.get('source_fact_lock',{}),
                        'source_evidence_sha256':item.get('evidence_sha',''),
                        'failure_reason':item.get('error',''),
                    },
                    'editorial':{
                        'first_screen_draft':None,
                        'detailed_rewrite_sections':None,
                        'repetition_issues':[],
                        'human_comments':None,
                        'review_state':'等待原文核对' if item.get('text') else '源断案失败_不得补写',
                        'approved_for_app':False,
                    },
                }
                out.write(canonical(payload)+'\n')
    os.replace(tmp,path)
    return True


def actor_catalog() -> dict:
    """Use the actual SHA-verified actor profile JSON; no copied signifier rules."""
    path=base.FROZEN/'actor_profiles.json'
    data=json.loads(path.read_text('utf-8'))
    return data


def catalog_relation_labels() -> dict:
    return {p['id']:p['label'] for p in actor_catalog()['profiles']}


def validate_actor_settings(profiles: dict) -> dict:
    """Fail before 518400 rows if the user wrote an unsupported/ignored role parameter."""
    mapping={p['id']:p for p in profiles['profiles']}
    if RELATIONSHIP not in mapping:
        raise ValueError('未知人物ID '+repr(RELATIONSHIP)+'；有效人物: '+', '.join(mapping))
    role=mapping[RELATIONSHIP]
    if not role.get('references'):
        raise ValueError('此人物没有经源确认的专用取用引用，不作完整成功断词: '+RELATIONSHIP)
    if PATIENT_SEX is not None and PATIENT_SEX not in ('male','female'):
        raise ValueError("PATIENT_SEX只能是None、'male'、'female'")
    fixed={'father':'male','mother':'female','grandfather':'male','grandmother':'female',
           'wife':'female','husband':'male','son':'male','daughter':'female',
           'animal_hen':'female','animal_rooster':'male'}
    expected=fixed.get(RELATIONSHIP)
    if expected and PATIENT_SEX not in (None,expected):
        raise ValueError(f'人物 {RELATIONSHIP} 的已知性别 {expected} 与PATIENT_SEX={PATIENT_SEX}冲突')
    if RELATIONSHIP in ('spouse','parent') and PATIENT_SEX is None:
        raise ValueError('配偶或父母合称必须先明确PATIENT_SEX；建议明确选 wife/husband 或 father/mother')
    if PATIENT_AGE_BAND is not None and PATIENT_AGE_BAND not in ('young',):
        raise ValueError("年龄条件目前仅有源规则 'young'，否则保持 None，勿添加未审年龄分支")
    if PATIENT_AGE_BAND is not None and RELATIONSHIP!='younger_sibling':
        raise ValueError('当前冻结版仅 younger_sibling 使用 PATIENT_AGE_BAND=young，别的角色不要填无效条件')
    if BIRTH_ORDER is not None and BIRTH_ORDER not in ('eldest','middle','youngest'):
        raise ValueError("BIRTH_ORDER只能是'eldest'、'middle'、'youngest'或None")
    if BIRTH_ORDER is not None and RELATIONSHIP not in ('child','son','daughter','nephew'):
        raise ValueError('冻结人物选择目前仅对孩子/儿子/女儿/侄子使用出生排行；兄弟姐妹勿误填该字段')
    if BIRTH_ORDER is not None and PATIENT_SEX is None and not expected:
        raise ValueError('需同时知道患者性别，才能依据排行选择真实辅助宫')
    if PATIENT_BIRTH_GANZHI is not None and PATIENT_BIRTH_GANZHI not in CYCLE60:
        raise ValueError('PATIENT_BIRTH_GANZHI必须是患者真实出生年六十甲子，如"乙丑"；不能只写出生公历年或甲一个字')
    context=CONSULTATION_CONTEXT or ('direct_self' if RELATIONSHIP=='self' else 'direct_proxy')
    if context not in ('direct_self','direct_proxy','event_news'):
        raise ValueError('CONSULTATION_CONTEXT只可为 None/direct_self/direct_proxy/event_news')
    if RELATIONSHIP=='self' and context!='direct_self':
        raise ValueError('本人问自己必须用 direct_self')
    if RELATIONSHIP!='self' and context=='direct_self':
        raise ValueError('代问其他人不能用 direct_self')
    if context=='event_news' and RELATIONSHIP not in profiles.get('event_news_override',{}).get('eligible',[]):
        raise ValueError('此人物未在原著 event_news 来源适用名单中，不能强行用闻讯事件日干')
    return {'profile':role,'context':context,'reference':role['references'][0]}


def build_inquiry(validation:dict)->dict:
    inquiry={'intent':'severity','relationship':RELATIONSHIP,
             'consultation_context':validation['context']}
    for key,value in (('patient_sex',PATIENT_SEX),('patient_age_band',PATIENT_AGE_BAND),
                      ('birth_order',BIRTH_ORDER),('patient_birth_ganzhi',PATIENT_BIRTH_GANZHI)):
        if value is not None:inquiry[key]=value
    return inquiry


def actor_output_folder() -> Path:
    """Keep no-option old 20 rows resumable; never mix natal or sex variants."""
    root=base.OUTPUT/'full_518400'/RELATIONSHIP
    if SIX_JIA_SOURCES_ACTIVATED:
        root=root/SIX_JIA_BATCH_SUBDIR
    extra={'birth':PATIENT_BIRTH_GANZHI,'sex':PATIENT_SEX,'age':PATIENT_AGE_BAND,
           'order':BIRTH_ORDER,'context':CONSULTATION_CONTEXT}
    if any(v is not None for v in extra.values()):
        # Changing any input uses its OWN checkpoint, not a misleading overwritten Excel.
        suffix=sha_text(canonical(extra))[:10]
        label=('年命_'+PATIENT_BIRTH_GANZHI) if PATIENT_BIRTH_GANZHI else '人物条件'
        return root/(label+'_'+suffix)
    return root


def verify_actual_role(chart:dict, inquiry:dict, calendar:dict, source_reference:dict)->dict:
    """Double-check the REAL Wengua role binder, not a copied actor selection."""
    from src.wengua.health_dynamic_v21 import bind_patient
    role=bind_patient(chart,inquiry,calendar)
    kind=role['role_via']
    if inquiry['consultation_context']!='event_news' and kind!=source_reference['kind']:
        raise ValueError('人物取用种类与actor_profiles原表不符：'+str((kind,source_reference['kind'])))
    expected={'day_stem':calendar['day_ganzhi'][0],
              'casting_day_stem':calendar['day_ganzhi'][0],
              'casting_year_stem':calendar['year_ganzhi'][0],
              'casting_month_stem':calendar['month_ganzhi'][0],
              'casting_hour_stem':calendar['hour_ganzhi'][0]}
    if kind in expected and role['stem']!=expected[kind]:
        raise ValueError('人物取用来源柱与最终天干不同，拒绝错误稿：'+str((kind,role['stem'],expected[kind])))
    if kind=='spouse_gender_harmony':
        sex=inquiry.get('patient_sex')
        if inquiry['relationship']=='wife':sex='female'
        if inquiry['relationship']=='husband':sex='male'
        if role['stem']!=('乙' if sex=='female' else '庚'):
            raise ValueError('配偶乙/庚取用未按实际性别绑定')
    if role['stem']=='甲' and kind in (
        'day_stem','casting_day_stem','casting_year_stem',
        'casting_month_stem','casting_hour_stem'):
        from src.wengua.casting_shenqi import SIX_JIA
        source_col={
            'day_stem':'day_ganzhi','casting_day_stem':'day_ganzhi',
            'casting_year_stem':'year_ganzhi',
            'casting_month_stem':'month_ganzhi',
            'casting_hour_stem':'hour_ganzhi'}[kind]
        own=calendar[source_col]
        expected_carrier=SIX_JIA.get(own)
        if not expected_carrier or role.get('source_ganzhi')!=own or role.get('carrier_stem')!=expected_carrier:
            raise ValueError('六甲用神没有按自己的完整来源柱定位：'+str(
                (kind,own,role.get('source_ganzhi'),role.get('carrier_stem'))))
    patient=role.get('main_cell')
    if patient is None:
        raise ValueError('实际患者主用神未落宫：'+str(role['role_name']))
    if patient['palace'] not in (1,2,3,4,6,7,8,9):
        raise ValueError('患者主用神不可被伪造在无普通星门神的中五宫')
    natal=inquiry.get('patient_birth_ganzhi')
    # Optional true birth-Ganzhi, if ever activated later, resolves by its
    # OWN full pillar. Current batch always leaves PATIENT_BIRTH_GANZHI=None.
    natal_cell=role.get('birth_cell')
    if natal and natal_cell is None:
        raise ValueError('已提供真实年命'+natal+'，但独立年命符号实际落宫未核定；不得假称年命已参与')
    if natal and natal_cell['palace'] not in (1,2,3,4,6,7,8,9):
        raise ValueError('年命实际落宫不能伪造为普通中五宫')
    return {
        'relationship':role['relationship'],'label':role['label'],
        'consultation_context':role['context'],
        'role_via':kind,'role_source':role['source_rule'],
        'role_status':role['status'],'role_confidence':role['confidence'],
        'stem':role['stem'],'palace':patient['palace'],
        'source_ganzhi':role.get('source_ganzhi'),
        'carrier_stem':role.get('carrier_stem'),
        'role_name':role['role_name'],
        'auxiliary_palaces':[c['palace'] for c in role.get('extra_cells',[])],
        'natal_year':natal,'natal_active':bool(natal_cell) if natal else False,
        'natal_stem':natal[0] if natal else None,
        'natal_palace':natal_cell['palace'] if natal_cell else None,
        'natal_note':role['birth_note'],
    }


def source_chart_from_base(src: dict, pillars: dict, term: str, bureau: dict):
    """Return original BigFish physical facts, NEVER reference old Wengua board."""
    from src.wengua.casting_shenqi import xun_shou
    hour=pillars['hour']
    assert src['hour_ganzhi']==hour
    xun,_,hidden=xun_shou(hour)
    chart={
      'school_id':'shijia_zhuanpan',
      'source_key':'perfhelf/bigfishmarquis-qimen@'+base.BIGFISH_SHA,
      'casting_variant':'bigfish_shijia_chaibu_pilot',
      'status':'bigfish_unapproved_candidate',
      'dun':src['dun'],'ju':src['ju'], 'hour_ganzhi':hour,
      'xun_shou':xun,'hidden_stem':hidden,
      'value_star':src['value_star'],
      'value_door':src['value_door'],
      'value_star_palace':src['value_star_palace'],
      'value_door_palace':src['value_door_palace'],
      'palaces':src['palaces'],
    }
    if bureau['juNumber']!=src['ju'] or (("yang" if bureau['isYangDun'] else "yin")!=src['dun']):
        raise ValueError('A distinct source board was mixed into this case')
    return chart


def compute_variant(worker, pillars, term, inquiry, *, include_evidence=True):
    """Use ORIGINAL BigFish board and EXACT repository V8/V10.2 report route.

    Same analyze_health_severity_review entry used by the repo's own
    scripts/preview_20261028_twoclocks_six_relatives_v80.py. No second score
    implementation and no GPT rewriting here. Unresolved source signifiers
    are marked as retained failures, not invented personal palaces.
    """
    result={'term':term,'status':'pending','grade':'','score':'','text':'',
            'base_id':'','evidence_sha':'','bureau':'','error':'',
            'sections':[], 'source_fact_lock':{},'original_text_sha256':''}
    try:
        bureau=worker.bureau(term,pillars['day'])
        physical=worker.chart(bureau,pillars['hour'],term)
        result['base_id']=physical['physical_id']
        result['bureau']=('阳' if bureau['isYangDun'] else '阴') + str(bureau['juNumber'])+'局'+bureau['yuan']+'元'
        board=source_chart_from_base(physical,pillars,term,bureau)
        from src.wengua.health_severity_vnext_review import analyze_health_severity_review
        from src.wengua.health_text_pipeline import DEFAULT_DB
        cal={'year_ganzhi':pillars['year'],'month_ganzhi':pillars['month'],
             'day_ganzhi':pillars['day'],'hour_ganzhi':pillars['hour'],
             'month_branch':pillars['month'][1]}
        with bigfish_candidate_only(board):
            profiles=actor_catalog()
            lookup={p['id']:p for p in profiles['profiles']}
            source_reference=lookup[inquiry['relationship']]['references'][0]
            person_audit=verify_actual_role(board,inquiry,cal,source_reference)
            report=analyze_health_severity_review(chart=board,inquiry=inquiry,
                         calendar=cal,db_path=DEFAULT_DB)
        quant=report['full_health_role_strength_network']['candidate_five_grade_quantization']
        roles=quant.get('roles',{})
        if roles.get('patient',{}).get('palace')!=person_audit['palace']:
            raise ValueError('封存V8评分的患者宫与人物绑定主宫不一致')
        if person_audit['natal_year']:
            if roles.get('natal',{}).get('palace')!=person_audit['natal_palace']:
                raise ValueError('患者真实年命已给出但冻结V8未按独立年命宫参与，不能输出伪完整判断')
        elif 'natal' in roles:
            raise ValueError('用户未提供年命，却生成了年命评分宫')
        elder_aux={'father':6,'grandfather':6,'mother':2,'grandmother':2}
        expected_aux=elder_aux.get(inquiry['relationship'])
        if expected_aux and roles.get('gender',{}).get('palace')!=expected_aux:
            raise ValueError('冻结V8未按原人物条件选正确的长辈乾/坤辅助宫')
        if not expected_aux and inquiry['relationship'] not in ('parent','older_relative') and 'gender' in roles:
            raise ValueError('非符合条件的长辈被误套乾坤辅助宫')
        if person_audit['stem']=='甲':
            from src.wengua.casting_shenqi import SIX_JIA
            carrier=person_audit['carrier_stem']
            expected=SIX_JIA[person_audit['source_ganzhi']]
            cell=board['palaces'][str(person_audit['palace'])]
            if carrier != expected or not any(
                sky['carried_stem']==carrier for sky in cell['heaven_stars']
            ):
                raise ValueError('真正天盘未含该角色六甲所遁六仪，拒绝假成绩')
        summary=quant['summary']
        score=summary['score']
        if score not in base.GRADE:
            raise ValueError('封存V8未返回有效的 -5 到 +5 等级')
        text=report['reading_text']
        sections=report['sections']
        if not text or not sections or not all(isinstance(s,dict) and s.get('id') and s.get('text') for s in sections):
            raise ValueError('封存V10.2中文原文或章节缺失')
        lock={
            'four_pillars':pillars,'source_term':term,
            'person_binding':person_audit,
            'birth_year_was_explicit':bool(inquiry.get('patient_birth_ganzhi')),
            'consultation_context':inquiry['consultation_context'],
            'bigfish_source_sha':base.BIGFISH_SHA,'wengua_source_sha':base.WENGUA_SHA,
            'original_physical_board_id':physical['physical_id'],
            'selected_roles':{
                name:{k: v for k,v in role.items() if k in ('palace','kind','symbol','strength','fact_id','month_stage')}
                for name,role in report['full_health_role_strength_network']['nodes'].items()
            },
            'quant_summary':summary,
            'role_effectiveness_gates':quant.get('role_effectiveness_gates',{}),
            'role_group_reviews':report['full_health_role_strength_network'].get('role_group_reviews',{}),
            'verdict':report.get('verdict',{}),
            'macro_fuyin_fanyin':report.get('macro_fuyin_fanyin',{}),
            'first_stage_macro':report.get('first_stage_macro',{}),
            'source_confidence':report.get('audit',{}).get('role_confidence'),
        }
        result.update(status='原始断词_待润色和人工审核',grade=base.GRADE[score],score=score,
                      text=text,sections=sections,source_fact_lock=lock,
                      original_text_sha256=sha_text(text),
                      evidence_sha=sha_text(canonical({'facts':lock,'sections':sections})))
    except Exception as ex:
        result['status']='失败_保留原样'
        result['error']=str(ex)[:1500]
        # No reference Shenqi layout, no fake personal signifier, no score fallback.
    return result



def deferred_source_jia(pillars:dict, validation:dict) -> str | None:
    """Historical v1-only switch; disabled for the approved six-Jia v2.

    The source-kind independent resolution is verified per variant downstream.

    This is a scheduler decision, NOT a fabricated 六甲 carrier or score.
    A real Jia HOUR is handled by the existing frozen binder; independent
    year/month/day Jia source pillars require a separately verified rule.
    """
    kind=(validation["reference"]["kind"] if validation["context"]!="event_news"
          else "day_stem")
    key={"day_stem":"day","casting_day_stem":"day",
         "casting_year_stem":"year","casting_month_stem":"month"}
    column=key.get(kind)
    if column and pillars[column][0]=="甲":
        return (f"独立来源甲待核：{kind}={pillars[column]}；"
                "不能借用本次小时旬首。保留已有旧失败，等待独立书证/新版本重算")
    return None


def export_new_batch(db, root:Path, labels:dict, indices:list[int]) -> str | None:
    """Always deliver NEW noncontiguous results as a separate snapshot.

    Previously exported Excel / reviewer edits are immutable. Older output
    exporter requires contiguous 0..N-1 and cannot export a resumed range
    after deferred Jia indexes; this path never pretends a gap is completed.
    """
    if not indices:
        return None
    indices=sorted(set(indices))
    first,last=indices[0]+1,indices[-1]+1
    version=sha_text(canonical((PIPELINE_VERSION, RELATIONSHIP, indices)))[:12]
    name=f"{RELATIONSHIP}_本轮新增_{first:06d}-{last:06d}_{version}"
    outputs=root/"Excel_CSV_可直接打开"
    outputs.mkdir(parents=True,exist_ok=True)
    csv_path=outputs/(name+".csv")
    xlsx_path=outputs/(name+".xlsx")
    jsonl_path=outputs/(name+"_待审事实包.jsonl")
    originals=[]
    for idx in indices:
        item=db.execute(
            "SELECT idx,pillars_json,result_jie_json,result_qi_json FROM cases WHERE idx=?",
            (idx,)).fetchone()
        if item is None:
            raise RuntimeError(f"Export missing committed result idx={idx}")
        originals.append(item)
    data=[make_row(i,json.loads(p),json.loads(j),json.loads(q),labels)
          for i,p,j,q in originals]
    if not csv_path.exists():
        temp=csv_path.with_suffix(".csv.incomplete")
        with temp.open("w",encoding="utf-8-sig",newline="") as f:
            writer=csv.writer(f)
            writer.writerow(HEADERS)
            writer.writerows([[literal_excel(v) for v in row] for row in data])
        os.replace(temp,csv_path)
    if GENERATE_XLSX and not xlsx_path.exists():
        write_xlsx(xlsx_path,data)
    export_editorial_jsonl(jsonl_path,originals,relationship=RELATIONSHIP)
    return str(xlsx_path if GENERATE_XLSX else csv_path)


def run():
    if ROWS_PER_EXCEL<1 or ROWS_PER_EXCEL>30000:raise ValueError('ROWS_PER_EXCEL must be 1..30000')
    if COMMIT_EVERY<1 or PRINT_EVERY<1:raise ValueError('commit/report cadence must be positive')
    # The previous father/ output had 1100 retained FAILS; NEVER reuse it.
    # Switch only the CURRENT Python process to a new verified rule checkout.
    activate_six_jia_sources()
    # Verify both source Git HEADs and frozen template/data hash BEFORE looping.
    manifest=ensure_install()
    if INSTALL_ONLY:
        print("仅安装模式完成：下次把 INSTALL_ONLY=False 即开始计算。", flush=True)
        return
    profiles=actor_catalog()
    validation=validate_actor_settings(profiles)
    labels=catalog_relation_labels()
    inquiry=build_inquiry(validation)
    root=actor_output_folder()
    root.mkdir(parents=True,exist_ok=True)
    info={
        'version':PIPELINE_VERSION,'relationship':RELATIONSHIP,
        'bigfish_commit':base.BIGFISH_SHA, 'wengua_commit':base.WENGUA_SHA,
        'compiled_typescript_sha256':{f:hashlib.sha256((base.COMPILED/'engines'/f).read_bytes()).hexdigest()
                                     for f in ('shijia.js','chaibuquju.js')},
        'freeze_file_sha256':{k:v['sha256'] for k,v in manifest['files'].items()},
        'rows':N_CASES,'term_selection':'both_real_possible_term_names_per_month_branch',
        'calendar_binding':'none; abstract four-pillar matrix; do not assert actual instant',
        'patient_sex':PATIENT_SEX, 'patient_age_band':PATIENT_AGE_BAND,
        'birth_order':BIRTH_ORDER, 'patient_birth_ganzhi':PATIENT_BIRTH_GANZHI,
        'person_natal':'optional_explicit_only_no_inference','source_method':'BigFish original shiJiaGenerate/ChaiBu',
        'score_method':'frozen Wengua V8.0 and V10.2 text, single-thread research gate',
    }
    if CONSULTATION_CONTEXT is not None:
        info['consultation_context']=validation['context']
    db=initialize_db(root/f'{RELATIONSHIP}_断点进度.sqlite3',info)
    (root/'源版本与条件说明.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    done=int(db.execute('SELECT COUNT(*) FROM cases').fetchone()[0])
    if MAX_NEW_ROWS<0:raise ValueError('MAX_NEW_ROWS must be >=0')
    print('人物:',RELATIONSHIP,labels[RELATIONSHIP],flush=True)
    print('封存用神来源:',validation['reference']['kind'],
          '原始来源:',validation['reference']['source'],
          '人物辅助宫:',validation['profile'].get('palaces',[]),flush=True)
    print('本次问事方式:',validation['context'],'问测年月日时按本次每行四柱计算，绝不替换成患者出生年',flush=True)
    print('真实出生年命:',PATIENT_BIRTH_GANZHI or '未提供：不参与',
          '；已知年命将另列独立宫与能量',flush=True)
    print('当前独立存储目录:',root,flush=True)
    (root/'人物用神与年命配置核对.json').write_text(
        json.dumps({'relationship_id':RELATIONSHIP,'profile':validation['profile'],
                    'consultation_context':validation['context'],
                    'real_birth_year_ganzhi_if_known':PATIENT_BIRTH_GANZHI,
                    'sex':PATIENT_SEX,'age_band':PATIENT_AGE_BAND,
                    'birth_order':BIRTH_ORDER,
                    'main_signifier_source_column':validation['reference']['kind'],
                    'note':'按每行真实四柱选主用神；年命是额外身份，只在真实提供并能实际落宫时加入。'},
                    ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('现有SQLite内已处理（含失败）会按原状跳过，绝不会用新版覆盖旧断词/人工改稿。',flush=True)
    print('理论组合:',N_CASES,'每行两个可能节气；已完成:',done,flush=True)
    print('注意：这是条件组合研究库，非518400个已核实的真实公历时刻。',flush=True)
    sys.path.insert(0,str(base.SOURCE))
    worker=BigFishWorker(root)
    current=0;pending=0;failed=0
    deferred=0; consecutive_failures=0
    newly_added=[]; newest_export=None
    if DEFER_UNRESOLVED_JIA:
        print("仅旧版本模式：独立甲来源暂缓",flush=True)
    else:
        print("现行六甲全柱规则：甲子戊/甲戌己/甲申庚/甲午辛/甲辰壬/甲寅癸",flush=True)
        print("按来源年/月/日/时干支独立找真实天盘宫；旧失败与人工稿另目录保留。",flush=True)
    try:
        # Reuse the EXACT preflight inquiry for every per-term cast.
        for idx in range(N_CASES):
            if MAX_NEW_ROWS and current>=MAX_NEW_ROWS:break
            if db.execute('SELECT 1 FROM cases WHERE idx=?',(idx,)).fetchone():
                continue
            pillars=scenario(idx)
            why=deferred_source_jia(pillars,validation) if DEFER_UNRESOLVED_JIA else None
            if why:
                deferred+=1
                if deferred==1:
                    print("[暂缓而非失败] 第一个待核组合",idx+1,pillars,why,flush=True)
                continue
            term1,term2=TERM_BY_MONTH[pillars['month'][1]]
            r1=compute_variant(worker,pillars,term1,inquiry)
            r2=compute_variant(worker,pillars,term2,inquiry)
            if current<3:
                for term_result in (r1,r2):
                    binding=term_result.get('source_fact_lock',{}).get('person_binding',{})
                    print('[首条用神复核]',idx+1,term_result['term'],
                          '问测',pillars,'主取',binding.get('role_via','未核定'),
                          binding.get('stem',''), '来源',binding.get('source_ganzhi',''),
                          '遁仪',binding.get('carrier_stem',''),
                          '宫',binding.get('palace',''),
                          '年命', ('参与'+str(binding.get('natal_palace'))+'宫'
                                     if binding.get('natal_active') else '未参与'),
                          '状态',term_result['status'],
                          ('错误='+term_result['error'][:140] if term_result.get('error') else ''),flush=True)
            failed+=int(r1['status'].startswith('失败'))+int(r2['status'].startswith('失败'))
            case_id=sha_text(canonical((RELATIONSHIP,idx,base.BIGFISH_SHA,base.WENGUA_SHA)))[:28]
            db.execute('INSERT INTO cases VALUES (?,?,?,?,?,?)',
                (idx,case_id,canonical(pillars),canonical(r1),canonical(r2),
                 datetime.now(timezone.utc).isoformat()))
            current+=1;pending+=1
            newly_added.append(idx)
            if r1['status'].startswith('失败') and r2['status'].startswith('失败'):
                consecutive_failures+=1
            else:
                consecutive_failures=0
            if consecutive_failures>=MAX_CONSECUTIVE_UNEXPECTED_FAILURES:
                db.commit();pending=0
                raise RuntimeError(
                    "非甲来源连续三行两节气均失败，已保存错误并停止以免再产生成千空白："
                    +r1.get('error','')[:250]+" / "+r2.get('error','')[:250])
            # Early source/data failures are never silently recast or amplified
            # into hundreds of thousands of bogus "successful" outputs.
            if STOP_IF_FIRST_ROW_FAILS and current==1 and (
                r1['status'].startswith('失败') and r2['status'].startswith('失败')):
                db.commit();pending=0
                raise RuntimeError('第1组双节气候选计算均失败，已记录原始失败并停止，'
                                   '请修复后再决定是否从下一组继续。\n'
                                   '节气甲：'+r1['error']+'\n节气乙：'+r2['error'])
            if pending>=COMMIT_EVERY:
                db.commit();pending=0
            if current%PRINT_EVERY==0:
                db.commit();pending=0
                print(f'新增 {current:,} 行，全球序号 {idx+1:,}/{N_CASES:,}；'
                      f'新增失败分支 {failed:,}；已生成原盘 {len(worker.physical)}，'
                      f'缓存节气局数 {len(worker.bureaus)}',flush=True)
            # Export full CSV/XLSX chunks, not partial/existing edited files.
            if len(newly_added)>=ROWS_PER_EXCEL:
                db.commit();pending=0
                newest_export=export_new_batch(db,root,labels,newly_added)
                print("真实新增数据已导出",newest_export,flush=True)
                newly_added.clear()
            if (idx+1)%ROWS_PER_EXCEL==0:
                db.commit();pending=0
                count=export_completed_chunks(db,root,labels)
                if count:print('导出完整连续分卷',count,flush=True)
    except KeyboardInterrupt:
        print('手动停止：正在保存全部已计算记录，重新运行自动续接。',flush=True)
    finally:
        db.commit()
        if newly_added:
            newest_export=export_new_batch(db,root,labels,newly_added)
            print("本轮新增可打开的Excel/CSV",newest_export,flush=True)
        print("独立甲用神未核候选（本次遍历跳过）",deferred,flush=True)
        # Export the last incomplete chunk too: first 20 test cases stay visible.
        # Filenames include ending index; previously edited exports remain untouched.
        exported=export_completed_chunks(db,root,labels,completed_only=False)
        total=int(db.execute('SELECT COUNT(*) FROM cases').fetchone()[0])
        print(f'总进度 {total:,}/{N_CASES:,}; 新增 {current:,}; 失败分支 {failed:,}; 新导出分卷 {exported};',flush=True)
        if total==N_CASES:
            print('全人物循环结束，518400行均已有状态和结果。',flush=True)
        print('文件目录:',root/'Excel_CSV_可直接打开',flush=True)
        print('原始断词、失败与人工编辑栏见CSV/XLSX；按节气分别供GPT润色的事实包见同目录 *_待审事实包.jsonl。',flush=True)
        print('2026-10-29现规则：六甲全柱独立遁仪定位，保留旧v1所有失败和人工稿。',flush=True)
        print('未跑完的组合不称成功；条件四柱不等同真实公历时刻。',flush=True)
        db.close()
        worker.close()


if __name__=='__main__':
    run()
