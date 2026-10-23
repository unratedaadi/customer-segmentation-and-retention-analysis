import pandas as pd

from src.analysis import assign_segments, build_cohort_retention, build_customer_rfm, build_kpis


def test_rfm_and_repeat_buyer_kpi_use_distinct_invoices():
    transactions = pd.DataFrame(
        {
            "CustomerID": [1, 1, 1, 2],
            "InvoiceNo": ["A", "A", "B", "C"],
            "InvoiceDate": pd.to_datetime(["2021-01-01", "2021-01-01", "2021-02-01", "2021-01-15"]),
            "Revenue": [10.0, 5.0, 15.0, 20.0],
            "Country": ["UK"] * 4,
        }
    )
    rfm = build_customer_rfm(transactions, reference_date=pd.Timestamp("2021-03-01"))
    assert rfm.loc[rfm.CustomerID == 1, "Frequency"].iloc[0] == 2
    assert build_kpis(transactions)["repeat_buyers"] == 1


def test_segments_are_exclusive_and_cohort_future_month_is_missing():
    scored = pd.DataFrame({"R_Score": [5, 1, 3], "F_Score": [5, 4, 1], "M_Score": [5, 4, 1]})
    assert assign_segments(scored)["Segment"].notna().all()
    transactions = pd.DataFrame(
        {"CustomerID": [1, 1, 2], "InvoiceDate": pd.to_datetime(["2021-01-02", "2021-02-03", "2021-02-05"])}
    )
    matrix, _ = build_cohort_retention(transactions, max_periods=3)
    assert pd.isna(matrix.loc[pd.Timestamp("2021-02-01"), 1])


def test_rfm_scores_keep_tied_values_together_and_support_one_customer():
    tied = pd.DataFrame(
        {
            "CustomerID": [1, 2, 3],
            "InvoiceNo": ["A", "B", "C"],
            "InvoiceDate": pd.to_datetime(["2021-01-01"] * 3),
            "Revenue": [10.0, 10.0, 10.0],
        }
    )
    scored = build_customer_rfm(tied, reference_date=pd.Timestamp("2021-02-01"))
    assert scored["F_Score"].nunique() == 1
    assert scored["M_Score"].nunique() == 1
    assert len(build_customer_rfm(tied.iloc[:1], reference_date=pd.Timestamp("2021-02-01"))) == 1
