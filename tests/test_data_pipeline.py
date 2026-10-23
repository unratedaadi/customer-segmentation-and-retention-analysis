import pandas as pd

from src.data_pipeline import clean_transactions


def test_clean_transactions_keeps_only_valid_paid_orders():
    raw = pd.DataFrame(
        {
            "InvoiceNo": ["10001", "C10002", "10003", "10004", "10005"],
            "StockCode": ["A", "B", "C", "D", "E"],
            "Description": ["Item"] * 5,
            "Quantity": [2, 1, -2, 1, 1],
            "InvoiceDate": ["2011-01-01"] * 5,
            "UnitPrice": [10.0, 10.0, 10.0, 0.0, 10.0],
            "CustomerID": [12345, 12345, 12345, 12345, None],
            "Country": ["United Kingdom"] * 5,
        }
    )
    result = clean_transactions(raw)
    assert result["InvoiceNo"].tolist() == ["10001"]
    assert result["Revenue"].tolist() == [20.0]
    assert str(result["CustomerID"].dtype) == "Int64"
