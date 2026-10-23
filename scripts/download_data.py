from __future__ import annotations

import argparse
from pathlib import Path
from urllib.request import urlretrieve

from src.config import RAW_DATA_PATH, UCI_DATA_URL, ensure_directories


def download_source(url: str = UCI_DATA_URL, destination: Path = RAW_DATA_PATH, force: bool = False) -> Path:
    ensure_directories()
    if destination.exists() and not force:
        return destination
    urlretrieve(url, destination)
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download the UCI Online Retail workbook.")
    parser.add_argument("--force", action="store_true", help="Replace an existing local source workbook.")
    args = parser.parse_args()
    print(download_source(force=args.force))
