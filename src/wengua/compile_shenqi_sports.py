"""Public-source sports compiler: versioned immutable-baseline archive."""
from pathlib import Path
from scripts.build_shenqi_16_from_15 import build

def import_sports_chapter(base_db_path, source_path, output_db_path, *, index_dir=None):
    root=Path(__file__).resolve().parents[2]
    folder=Path(index_dir) if index_dir is not None else root/'data/knowledge/shenqi/sports_competition_prediction_ch12'
    migration=root/'schema/migrations/011_sports_source_qualification.sql'
    return build(Path(base_db_path),Path(source_path),Path(output_db_path),folder,migration)
