from src.config import PROCESSED_DATA_DIR, RAW_DATA_PATH, UCI_DATA_URL, ensure_directories


def test_project_paths_and_source_are_declared():
    ensure_directories()
    assert RAW_DATA_PATH.parent.exists()
    assert PROCESSED_DATA_DIR.exists()
    assert UCI_DATA_URL.startswith("https://")
