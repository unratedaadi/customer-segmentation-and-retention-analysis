# Customer Segmentation & Retention Analysis

A portfolio-ready data science project that turns real retail transactions into customer segments, retention patterns, and practical marketing actions.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)

## Business question

Which customers create the most value, which groups are becoming inactive, and how well do customer cohorts return after their first purchase?

## What this project delivers

- Rigorous cleaning of transaction-level retail data
- RFM customer segmentation: **Champions**, **Loyal Customers**, **Potential Loyalists**, **At Risk**, **Lost Customers**, and **Needs Attention**
- Monthly revenue and repeat-purchase analysis
- Cohort-retention analysis that preserves unobserved future periods as missing rather than incorrectly treating them as 0% retention
- An interactive Streamlit dashboard with country and segment filters
- A reproducible Jupyter notebook with charts and methodology
- Unit tests for cleaning, RFM, repeat-buying, segment assignment, and cohort logic

## Dataset

The analysis uses the [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail): transaction-level data from a UK-based non-store retailer from **1 December 2010 to 9 December 2011**. Source retrieved on **24 October 2026**. The original workbook is downloaded locally and is intentionally excluded from version control.

## Observed results

After cleaning invalid orders, the dataset contains **4,338 identifiable customers** and **£8.91M in positive purchase revenue**.

- **947 Champions** generated approximately **£5.75M**, making them the core value segment.
- **658 At-Risk customers** represented roughly **£821K** in prior revenue and are a practical priority for re-engagement.
- **2,845 customers** placed at least two distinct valid orders.
- Revenue peaked in **November 2011 (£1.16M)**, showing strong end-of-year seasonality.

These are descriptive findings from this dataset, not causal estimates of campaign impact.

## Methodology

### 1. Clean transactions

Records are included only when they have:

- A non-null customer ID
- A positive quantity and unit price
- A valid date
- An invoice number that does not start with `C` (cancelled invoices)

Revenue is calculated as `Quantity × UnitPrice` in GBP.

### 2. Segment customers with RFM

- **Recency:** days since the last purchase, measured from the day after the final transaction
- **Frequency:** number of distinct valid invoices
- **Monetary:** total positive purchase revenue

Each metric is scored in quintiles; a rank-based fallback prevents duplicate-value binning issues. Segment rules are intentionally explicit and mutually exclusive.

### 3. Measure retention

Customers are assigned to the month of their first purchase. Retention is the share of original cohort customers who are active in each subsequent month.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

PYTHONPATH=. python scripts/download_data.py
PYTHONPATH=. python scripts/build_outputs.py
streamlit run app/dashboard.py
```

To execute the notebook:

```bash
PYTHONPATH=. jupyter nbconvert --execute --to notebook --inplace notebooks/customer_segmentation_retention.ipynb
```

## Project structure

```text
├── app/                 # Streamlit dashboard
├── data/raw/            # Downloaded source workbook (ignored by Git)
├── data/processed/      # Reproducible summary outputs
├── notebooks/           # Executed analytical notebook
├── scripts/             # Download and build commands
├── src/                 # Cleaning and analytical functions
└── tests/               # Unit tests
```

## Resume-ready description

> Built an end-to-end customer segmentation and retention analysis using real UCI retail transaction data. Processed 500K+ raw order lines, created RFM customer segments, measured cohort retention, and developed a Streamlit dashboard to identify high-value and at-risk customers; uncovered £5.75M in revenue from Champion customers and £821K associated with At-Risk customers.

## Limitations

- The source data has no marketing-exposure, acquisition-channel, or customer-demographic data, so it cannot establish why a customer churned.
- Cancellation/return records are excluded from positive-purchase customer-value metrics; a separate returns analysis would be a useful extension.
- The project does not train a churn model because no future-labelled churn outcome is provided.

## License

MIT. See [LICENSE](LICENSE).
