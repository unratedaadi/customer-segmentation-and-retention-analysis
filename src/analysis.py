from __future__ import annotations

import numpy as np
import pandas as pd


def _score(series: pd.Series, reverse: bool = False) -> pd.Series:
    """Return 1–5 RFM scores without splitting identical values across bins."""
    if series.nunique(dropna=True) <= 1:
        return pd.Series(3, index=series.index, dtype=int)
    percentile = series.rank(method="average", pct=True, ascending=not reverse)
    return (percentile.mul(5).apply(np.ceil).clip(1, 5)).astype(int)


def build_customer_rfm(transactions: pd.DataFrame, reference_date: pd.Timestamp | None = None) -> pd.DataFrame:
    reference_date = pd.Timestamp(reference_date) if reference_date is not None else transactions["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)
    customer = transactions.groupby("CustomerID", as_index=False).agg(
        LastPurchase=("InvoiceDate", "max"), Frequency=("InvoiceNo", "nunique"), Monetary=("Revenue", "sum")
    )
    customer["Recency"] = (reference_date - customer["LastPurchase"].dt.normalize()).dt.days
    customer["R_Score"] = _score(customer["Recency"], reverse=True)
    customer["F_Score"] = _score(customer["Frequency"])
    customer["M_Score"] = _score(customer["Monetary"])
    return assign_segments(customer)


def assign_segments(rfm: pd.DataFrame) -> pd.DataFrame:
    result = rfm.copy()
    r, f, m = result["R_Score"], result["F_Score"], result["M_Score"]
    rules = [
        (r >= 4) & (f >= 4) & (m >= 4),
        (f >= 4) & (r >= 3),
        (r >= 4) & f.between(2, 3),
        (r <= 2) & (f >= 3),
        (r == 1) & (f <= 2),
    ]
    labels = ["Champions", "Loyal Customers", "Potential Loyalists", "At Risk", "Lost Customers"]
    result["Segment"] = np.select(rules, labels, default="Needs Attention")
    return result


def build_kpis(transactions: pd.DataFrame) -> dict[str, float | int]:
    per_customer = transactions.groupby("CustomerID")["InvoiceNo"].nunique()
    return {
        "customers": int(per_customer.size),
        "revenue": float(transactions["Revenue"].sum()),
        "orders": int(transactions["InvoiceNo"].nunique()),
        "repeat_buyers": int((per_customer >= 2).sum()),
        "repeat_buyer_rate": float((per_customer >= 2).mean()) if len(per_customer) else 0.0,
    }


def monthly_revenue(transactions: pd.DataFrame) -> pd.DataFrame:
    result = transactions.assign(Month=transactions["InvoiceDate"].dt.to_period("M").dt.to_timestamp()).groupby("Month", as_index=False)["Revenue"].sum()
    return result.sort_values("Month")


def build_cohort_retention(transactions: pd.DataFrame, max_periods: int | None = None) -> tuple[pd.DataFrame, pd.Series]:
    data = transactions[["CustomerID", "InvoiceDate"]].drop_duplicates().copy()
    data["CohortMonth"] = data.groupby("CustomerID")["InvoiceDate"].transform("min").dt.to_period("M").dt.to_timestamp()
    data["OrderMonth"] = data["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    data["Period"] = (data["OrderMonth"].dt.year - data["CohortMonth"].dt.year) * 12 + (data["OrderMonth"].dt.month - data["CohortMonth"].dt.month)
    active = data.groupby(["CohortMonth", "Period"])["CustomerID"].nunique().unstack("Period").sort_index()
    cohort_sizes = active[0].copy()
    periods = range(max_periods) if max_periods is not None else range(int(data["Period"].max()) + 1)
    matrix = active.reindex(columns=periods).div(cohort_sizes, axis=0)
    latest_month = data["OrderMonth"].max()
    for cohort in matrix.index:
        observed = (latest_month.year - cohort.year) * 12 + (latest_month.month - cohort.month)
        matrix.loc[cohort, [p for p in matrix.columns if p > observed]] = np.nan
    return matrix, cohort_sizes


def filter_transactions(transactions: pd.DataFrame, country: str | None = None, segment: str | None = None) -> pd.DataFrame:
    result = transactions.copy()
    if country and country != "All":
        result = result[result["Country"] == country]
    if segment and segment != "All" and not result.empty:
        customer_segments = build_customer_rfm(result)[["CustomerID", "Segment"]]
        result = result.merge(customer_segments, on="CustomerID", how="inner")
        result = result[result["Segment"] == segment].drop(columns="Segment")
    return result
