# Customer Segmentation & Retention Analysis — Design

## Intent

Create a portfolio-ready data science project that demonstrates how transactional retail data can be converted into customer segments, retention insight, and concrete marketing actions. The audience is recruiters, hiring managers, and peers reviewing the project on GitHub or locally.

## Goals

- Use the real UCI Online Retail dataset and retain clear source provenance.
- Build a reproducible Python analysis that validates and cleans transaction data.
- Segment customers through Recency, Frequency, and Monetary (RFM) measures.
- Show repeat-purchase behavior and monthly cohort retention without treating immature cohorts as zero retention.
- Provide a polished Streamlit dashboard with filterable results, neutral chart titles, readable KPI cards, a revenue trend, segment composition, retention heatmap, and recommended actions.
- Document the work in a README with methodology, key findings, limitations, and resume-ready language.

## Non-goals

- No unsupported causal claims or predictions of individual churn.
- No automated marketing campaign execution or customer outreach.
- No fabrication of values: every final KPI and chart derives from the downloaded dataset.
- No deployment or cloud hosting in this scope.

## Data and analytical assumptions

- Source: UCI Machine Learning Repository's Online Retail dataset, a transaction-level UK-based non-store retailer dataset covering 2010-12-01 through 2011-12-09.
- A valid purchase has a positive quantity, positive unit price, non-null customer ID, and invoice number not starting with `C` (cancelled invoices).
- Revenue is `Quantity × UnitPrice` in pounds sterling.
- The analysis population is customers with at least one valid purchase; returns/cancellations are excluded from customer-value metrics.
- RFM recency is calculated relative to the day after the final transaction date. Frequency is distinct valid invoices; monetary value is net positive purchase revenue.
- RFM scores use dataset-relative quintiles when enough unique values exist, with a rank-based fallback to avoid duplicate-bin errors.
- Segment labels use these transparent business rules: **Champions** (R≥4, F≥4, M≥4), **Loyal Customers** (F≥4 and R≥3, excluding Champions), **Potential Loyalists** (R≥4 and F 2–3), **At Risk** (R≤2 and F≥3), **Lost Customers** (R=1 and F≤2), and **Needs Attention** (all remaining customers). These rules prioritize mutually exclusive labels and make the at-risk population auditable.
- Cohorts are defined by the calendar month of each customer's first valid purchase. A cohort-month retention rate is active customers divided by its original cohort size. Future/unobserved cohort periods remain missing.
- A repeat buyer is a customer with two or more distinct valid invoices. This measures repeat ordering rather than multiple line items within one order.

## Approaches considered

1. **Notebook only.** Easiest to reproduce, but less accessible for a recruiter who wants to explore the outcomes quickly.
2. **Dashboard only.** Strong visual presentation, but weaker evidence of methodology and reproducibility.
3. **Notebook plus dashboard (selected).** Keeps calculations transparent and delivers a quick interactive portfolio surface. This adds a small amount of code but best meets the stated portfolio goal.

## Solution outline

The project will contain a download/data-prep pipeline, shared analytical functions, a Jupyter notebook, a Streamlit dashboard, generated analysis outputs, automated tests for core calculations, and a README. The pipeline caches the source workbook locally, makes a clean transaction table, derives customer-level RFM and cohort tables, and writes compact CSV outputs used by the dashboard. The dashboard loads only these prepared outputs and filters segment-level views by country and segment.

## Dashboard experience

The dashboard follows the approved mockup: a clear title and source scope; KPI cards for customers, revenue, repeat buyers, and at-risk customers; a monthly revenue trend; a ranked segment-revenue view; a cohort-retention heatmap; and an action panel. Country and segment filtering will recompute customer metrics from the selected transactions so that the displayed measures stay internally consistent. The selected portfolio audience favors clear explanation over excessive controls.

## Constraints and quality checks

- Python 3.9+ with pandas, numpy, matplotlib/seaborn, Streamlit, and openpyxl.
- Store raw data under `data/raw/` and generated, versionable aggregates under `data/processed/`; keep the source download URL and retrieval date in the README.
- Keep raw downloaded data out of version control because of its size; preserve a short download script and source link instead.
- Test invoice filtering, revenue calculation, RFM output, cohort calculation, and missing future cohort behavior.
- Execute the notebook top to bottom, run the test suite, and smoke-test the dashboard locally.

## Builder choices

- Streamlit is selected for a compact local dashboard because it pairs naturally with the Python analysis and is easy for a reviewer to run.
- Use static Matplotlib/Seaborn visuals in the notebook and Plotly only where interactivity helps dashboard filtering.
- Use UCI's original source rather than an authentication-gated data mirror.

## Open items

None. The project will be a local, portfolio-ready artifact; deployment and machine-learning churn prediction are deliberately out of scope.
