from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.config import PROCESSED_DATA_DIR, RAW_DATA_PATH, ensure_directories


def load_raw_transactions(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    return pd.read_excel(path, engine="openpyxl")


def clean_transactions(raw: pd.DataFrame) -> pd.DataFrame:
    transactions = raw.copy()
    transactions["InvoiceNo"] = transactions["InvoiceNo"].astype("string").str.strip()
    transactions["InvoiceDate"] = pd.to_datetime(transactions["InvoiceDate"], errors="coerce")
    transactions["CustomerID"] = pd.to_numeric(transactions["CustomerID"], errors="coerce").astype("Int64")
    transactions["Quantity"] = pd.to_numeric(transactions["Quantity"], errors="coerce")
    transactions["UnitPrice"] = pd.to_numeric(transactions["UnitPrice"], errors="coerce")
    valid = (
        transactions["CustomerID"].notna()
        & transactions["InvoiceDate"].notna()
        & ~transactions["InvoiceNo"].str.startswith("C", na=True)
        & (transactions["Quantity"] > 0)
        & (transactions["UnitPrice"] > 0)
    )
    transactions = transactions.loc[valid].copy()
    transactions["Revenue"] = (transactions["Quantity"] * transactions["UnitPrice"]).round(2)
    return transactions.sort_values(["InvoiceDate", "InvoiceNo", "CustomerID"]).reset_index(drop=True)


def prepare_transactions(source_path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    return clean_transactions(load_raw_transactions(source_path))


def save_clean_transactions(transactions: pd.DataFrame) -> Path:
    ensure_directories()
    destination = PROCESSED_DATA_DIR / "transactions_clean.csv"
    transactions.to_csv(destination, index=False)
    return destination
