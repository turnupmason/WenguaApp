"""Shenqi legal-dispute source importer, additive-only versioned private/research DB.

The full build is delegated to the single audited stdlib builder so importing a
chapter never mutates the caller's baseline snapshot or overwrites prior chapters.
"""
from __future__ import annotations
from pathlib import Path
from scripts.build_shenqi_15_from_14 import main as build_full_snapshot

def import_litigation_chapter(base_db_path, source_path, output_db_path, *, index_dir=None):
    folder=Path(index_dir) if index_dir is not None else Path(__file__).resolve().parents[2]/'data/knowledge/shenqi/litigation_prediction_ch11'
    result=build_full_snapshot(['--base',str(base_db_path),'--source',str(source_path),'--output',str(output_db_path),'--index-dir',str(folder)])
    if result!=0:
        raise RuntimeError('Unsuccessful lossless chapter builder')
    return Path(output_db_path)
