from src.config import PROCESSED_DATA_DIR, ensure_directories
from src.data_pipeline import prepare_transactions, save_clean_transactions
from src.analysis import build_cohort_retention, build_customer_rfm, monthly_revenue


if __name__ == "__main__":
    ensure_directories()
    transactions = prepare_transactions()
    print(save_clean_transactions(transactions))
    rfm = build_customer_rfm(transactions)
    rfm.to_csv(PROCESSED_DATA_DIR / "customer_rfm.csv", index=False)
    rfm.groupby("Segment", as_index=False).agg(Customers=("CustomerID", "nunique"), Revenue=("Monetary", "sum")).to_csv(PROCESSED_DATA_DIR / "segment_summary.csv", index=False)
    monthly_revenue(transactions).to_csv(PROCESSED_DATA_DIR / "monthly_revenue.csv", index=False)
    retention, sizes = build_cohort_retention(transactions)
    retention.to_csv(PROCESSED_DATA_DIR / "cohort_retention.csv")
    sizes.rename("CohortSize").to_csv(PROCESSED_DATA_DIR / "cohort_sizes.csv")
