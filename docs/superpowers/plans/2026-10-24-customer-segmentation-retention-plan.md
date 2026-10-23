# Customer Segmentation & Retention Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a reproducible, portfolio-ready customer segmentation and retention project using UCI Online Retail transaction data, a Python notebook, and an interactive Streamlit dashboard.

**Architecture:** A data module downloads and cleans the original workbook, then derives transaction-, customer-, and cohort-level tables. A notebook uses those tables to explain the methodology and static figures, while the Streamlit app loads the same functions/data for an interactive dashboard. Tests lock down the business definitions for valid orders, RFM segmentation, and cohort retention.

**Tech Stack:** Python 3.9+, pandas, numpy, openpyxl, matplotlib, seaborn, plotly, Streamlit, pytest, Jupyter.

**Spec:** `docs/superpowers/specs/2026-10-24-customer-segmentation-retention-design.md`

## Global Constraints

- Source only the UCI Online Retail workbook; preserve its source URL and retrieval date in documentation.
- Valid purchases require a non-null customer ID, positive quantity, positive unit price, and an invoice not beginning with `C`.
- Revenue is `Quantity × UnitPrice` in GBP; no causal or individual-level churn claims.
- RFM uses quintiles with a rank fallback, a day-after-max-date recency reference, distinct valid invoices for frequency, and mutually exclusive documented segment rules.
- A repeat buyer has at least two distinct valid invoices.
- Cohorts use a customer’s first valid-purchase calendar month; unobserved future periods stay null.
- Raw source files stay untracked; all outputs must be reproducible by scripts.

## Review Focus

- Cancellation invoices and negative quantities must never leak into customer spending or retention counts — test in Task 2.
- Customers whose ties make `qcut` fail must still receive reproducible RFM scores — test in Task 3.
- Segment rules must be mutually exclusive and preserve every scored customer — test in Task 3.
- The final incomplete cohort must show unavailable future periods as missing, not 0% — test in Task 4.
- Country-filtered dashboard views must derive all customer KPIs from selected transactions, not pre-filter global values — test in Task 6.

## File Structure

- `src/data_pipeline.py` — source download, cleaning, and reproducible processed-data generation.
- `src/analysis.py` — RFM scoring, segment mapping, KPIs, monthly trends, and cohort functions shared by notebook/app.
- `src/config.py` — paths, source URL, and analysis constants.
- `app/dashboard.py` — Streamlit dashboard and filter wiring.
- `notebooks/customer_segmentation_retention.ipynb` — executed narrative analysis.
- `tests/test_data_pipeline.py` — valid-transaction and revenue tests.
- `tests/test_analysis.py` — RFM, segment, retention, and filter-consistency tests.
- `scripts/download_data.py` — command-line dataset retrieval.
- `scripts/build_outputs.py` — command-line preparation of processed tables and chart-ready output.
- `data/raw/.gitkeep` and `data/processed/.gitkeep` — expected data locations.
- `README.md`, `requirements.txt`, `.gitignore` — setup, methodology, portfolio narrative, and environment control.

### Task 1: Scaffold reproducible project configuration

**Files:**
- Create: `src/__init__.py`
- Create: `src/config.py`
- Create: `scripts/download_data.py`
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `data/raw/.gitkeep`
- Create: `data/processed/.gitkeep`
- Create: `tests/conftest.py`

**Interfaces:**
- Produces: `RAW_DATA_PATH`, `PROCESSED_DATA_DIR`, `UCI_DATA_URL`, and `ensure_directories() -> None` from `src.config`.
- Produces: `download_source(url: str = UCI_DATA_URL, destination: Path = RAW_DATA_PATH) -> Path` from `scripts.download_data`.

- [ ] **Step 1: Write the failing configuration/import smoke test**

```python
from src.config import RAW_DATA_PATH, PROCESSED_DATA_DIR, UCI_DATA_URL, ensure_directories

def test_project_paths_and_source_are_declared():
    ensure_directories()
    assert RAW_DATA_PATH.parent.exists()
    assert PROCESSED_DATA_DIR.exists()
    assert UCI_DATA_URL.startswith("https://")
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_config.py::test_project_paths_and_source_are_declared -v`
Expected: FAIL because `src.config` does not exist.

- [ ] **Step 3: Implement configuration, data directories, dependency list, raw-file ignore rule, and download entry point**

Use `pathlib.Path`; source URL targets the official UCI workbook. The download function must avoid replacing an existing source file unless called with `force=True`.

- [ ] **Step 4: Run the configuration test**

Run: `pytest tests/test_config.py::test_project_paths_and_source_are_declared -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src scripts requirements.txt .gitignore data tests
git commit -m "chore: scaffold retail analysis project"
```

### Task 2: Build and test transaction cleaning

**Files:**
- Create: `src/data_pipeline.py`
- Create: `tests/test_data_pipeline.py`
- Modify: `scripts/build_outputs.py`

**Interfaces:**
- Consumes: `RAW_DATA_PATH` and `ensure_directories()` from `src.config`.
- Produces: `load_raw_transactions(path: Path) -> pd.DataFrame`, `clean_transactions(raw: pd.DataFrame) -> pd.DataFrame`, and `prepare_transactions(source_path: Path = RAW_DATA_PATH) -> pd.DataFrame`.
- Produces: cleaned columns `InvoiceNo`, `InvoiceDate`, `CustomerID`, `Country`, `Quantity`, `UnitPrice`, `Revenue`.

- [ ] **Step 1: Write failing tests for exclusions, standard types, and revenue**

```python
def test_clean_transactions_keeps_only_valid_paid_orders(sample_raw_transactions):
    result = clean_transactions(sample_raw_transactions)
    assert result["InvoiceNo"].tolist() == ["10001"]
    assert result["Revenue"].tolist() == [20.0]
    assert str(result["CustomerID"].dtype) == "Int64"
```

- [ ] **Step 2: Run the data-pipeline test to verify it fails**

Run: `pytest tests/test_data_pipeline.py::test_clean_transactions_keeps_only_valid_paid_orders -v`
Expected: FAIL because `clean_transactions` does not exist.

- [ ] **Step 3: Implement loading, cleaning, and output preparation**

Normalize column names, parse `InvoiceDate`, drop missing customer IDs, remove `C` invoice numbers and non-positive quantity/unit price rows, compute `Revenue`, and return a deterministic sort. `scripts/build_outputs.py` writes `data/processed/transactions_clean.csv`.

- [ ] **Step 4: Run pipeline tests**

Run: `pytest tests/test_data_pipeline.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/data_pipeline.py scripts/build_outputs.py tests/test_data_pipeline.py
git commit -m "feat: clean retail transactions"
```

### Task 3: Derive RFM metrics and customer segments

**Files:**
- Create: `src/analysis.py`
- Create: `tests/test_analysis.py`
- Modify: `scripts/build_outputs.py`

**Interfaces:**
- Consumes: clean transaction DataFrame from `prepare_transactions()`.
- Produces: `build_customer_rfm(transactions: pd.DataFrame, reference_date: pd.Timestamp | None = None) -> pd.DataFrame`, `assign_rfm_scores(rfm: pd.DataFrame) -> pd.DataFrame`, `assign_segments(scored_rfm: pd.DataFrame) -> pd.DataFrame`, and `build_kpis(transactions: pd.DataFrame) -> dict[str, float | int]`.

- [ ] **Step 1: Write failing RFM, rank-fallback, segment-exclusivity, and repeat-buyer tests**

```python
def test_segments_are_exclusive_and_at_risk_requires_low_recency():
    result = assign_segments(scored_fixture)
    assert result["Segment"].notna().all()
    assert set(result.loc[result["Segment"] == "At Risk", "R_Score"]) <= {1, 2}

def test_repeat_buyer_kpi_counts_distinct_invoices():
    metrics = build_kpis(transactions_fixture)
    assert metrics["repeat_buyers"] == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_analysis.py -v`
Expected: FAIL because RFM functions do not exist.

- [ ] **Step 3: Implement customer-level RFM metrics, robust quintile scoring, and segment mapping**

Map scores with the selected design rules in `assign_segments`; use rank-based scoring where quantile edges collide. Extend `scripts/build_outputs.py` to write `customer_rfm.csv` and `segment_summary.csv`.

- [ ] **Step 4: Run analysis tests**

Run: `pytest tests/test_analysis.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/analysis.py scripts/build_outputs.py tests/test_analysis.py
git commit -m "feat: add rfm segmentation metrics"
```

### Task 4: Calculate monthly trends and cohort retention

**Files:**
- Modify: `src/analysis.py`
- Modify: `scripts/build_outputs.py`
- Modify: `tests/test_analysis.py`

**Interfaces:**
- Produces: `monthly_revenue(transactions: pd.DataFrame) -> pd.DataFrame`, `build_cohort_retention(transactions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]`.
- Produces: `monthly_revenue.csv`, `cohort_retention.csv`, and `cohort_sizes.csv` in `data/processed/`.

- [ ] **Step 1: Write failing tests for cohort denominator and unavailable future months**

```python
def test_cohort_retention_keeps_unobserved_future_periods_missing(cohort_fixture):
    matrix, cohort_sizes = build_cohort_retention(cohort_fixture)
    assert matrix.loc[pd.Timestamp("2011-12-01"), 1] != matrix.loc[pd.Timestamp("2011-12-01"), 1]
    assert cohort_sizes.loc[pd.Timestamp("2011-01-01")] == 2
```

- [ ] **Step 2: Run the targeted test to verify it fails**

Run: `pytest tests/test_analysis.py::test_cohort_retention_keeps_unobserved_future_periods_missing -v`
Expected: FAIL because `build_cohort_retention` does not exist.

- [ ] **Step 3: Implement monthly revenue and cohort retention**

Floor dates to month starts, count distinct active customers by cohort and period index, divide by cohort size, and set future/unobserved months to missing rather than zero. Extend the output script with CSV exports.

- [ ] **Step 4: Run all analysis tests**

Run: `pytest tests/test_analysis.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/analysis.py scripts/build_outputs.py tests/test_analysis.py
git commit -m "feat: calculate cohort retention"
```

### Task 5: Acquire real source data and create the executed notebook

**Files:**
- Create: `notebooks/customer_segmentation_retention.ipynb`
- Modify: `scripts/build_outputs.py`
- Create: `outputs/figures/`

**Interfaces:**
- Consumes: data output functions from Tasks 2–4.
- Produces: executed notebook with Summary, Context & Methods, Data, Results, and Takeaways sections; static figures retained in notebook output and `outputs/figures/`.

- [ ] **Step 1: Download the official data and build processed outputs**

Run: `python scripts/download_data.py && python scripts/build_outputs.py`
Expected: source workbook exists under `data/raw/`; processed CSVs have rows and documented schema.

- [ ] **Step 2: Create notebook cells for loading, validation, RFM results, trends, cohort heatmap, and conclusions**

Include visible provenance, filtering rules, caveats, and exact observed values only after execution. Create static, labeled figures for monthly revenue, segment value, and cohort retention.

- [ ] **Step 3: Execute the notebook top to bottom**

Run: `jupyter nbconvert --execute --to notebook --inplace notebooks/customer_segmentation_retention.ipynb --ExecutePreprocessor.timeout=180`
Expected: PASS with rendered outputs and no cell errors.

- [ ] **Step 4: Inspect rendered notebook HTML**

Run: `jupyter nbconvert --to html notebooks/customer_segmentation_retention.ipynb --output /tmp/customer-segmentation.html`
Expected: all charts, labels, summary, and table outputs visibly render.

- [ ] **Step 5: Commit**

```bash
git add notebooks outputs data/processed scripts/build_outputs.py
git commit -m "feat: add executed retention analysis notebook"
```

### Task 6: Build and test interactive Streamlit dashboard

**Files:**
- Create: `app/dashboard.py`
- Create: `app/__init__.py`
- Modify: `src/analysis.py`
- Modify: `tests/test_analysis.py`

**Interfaces:**
- Consumes: cleaned transaction data plus `build_kpis`, `build_customer_rfm`, `assign_segments`, `monthly_revenue`, and `build_cohort_retention`.
- Produces: `filter_transactions(transactions: pd.DataFrame, country: str | None, segment: str | None) -> pd.DataFrame` and dashboard server command `streamlit run app/dashboard.py`.

- [ ] **Step 1: Write failing test for country-filter recomputation**

```python
def test_country_filter_recomputes_customer_metrics_from_selected_orders():
    filtered = filter_transactions(transactions_fixture, country="France", segment=None)
    assert build_kpis(filtered)["customers"] == 1
```

- [ ] **Step 2: Run the targeted test to verify it fails**

Run: `pytest tests/test_analysis.py::test_country_filter_recomputes_customer_metrics_from_selected_orders -v`
Expected: FAIL because `filter_transactions` does not exist.

- [ ] **Step 3: Implement filtered-data helper and dashboard**

Create sidebar country/segment filters; compute all cards and charts from the selected transaction population. Render KPI cards, monthly revenue line chart, segment revenue bar chart, labeled cohort heatmap, and a segment-to-action table. Use direct labels/tooltips and clear empty-state messaging.

- [ ] **Step 4: Run test suite and dashboard smoke test**

Run: `pytest -q && streamlit run app/dashboard.py --server.headless true --server.port 8501`
Expected: tests pass and the local dashboard loads without errors.

- [ ] **Step 5: Commit**

```bash
git add app src/analysis.py tests/test_analysis.py
git commit -m "feat: add interactive retention dashboard"
```

### Task 7: Complete portfolio documentation and final validation

**Files:**
- Create: `README.md`
- Modify: `.gitignore`
- Create: `LICENSE`

**Interfaces:**
- Consumes: observed results from executed notebook/output tables.
- Produces: self-contained project overview, installation/run instructions, source attribution, methodology, limitations, screenshots/figure links, resume bullet, and portfolio description.

- [ ] **Step 1: Write a README from verified outputs only**

Include project goal, source/license, data dictionary, cleaning rules, methods, dashboard launch command, key findings tied to actual outputs, limitations, repo structure, and resume-ready summary.

- [ ] **Step 2: Run full reproducibility checks**

Run: `pytest -q && python scripts/build_outputs.py && jupyter nbconvert --execute --to notebook --inplace notebooks/customer_segmentation_retention.ipynb --ExecutePreprocessor.timeout=180`
Expected: all commands complete successfully with current source data.

- [ ] **Step 3: Review dashboard and notebook at normal reading size**

Verify KPI values, labels, filters, heatmap scale, empty states, and README claims against processed data and executed notebook.

- [ ] **Step 4: Commit**

```bash
git add README.md .gitignore LICENSE notebooks outputs data/processed
git commit -m "docs: finalize portfolio project"
```

## Self-review

- **Spec coverage:** Data source, cleaning, RFM, named segments, repeat buyers, cohort retention, notebook, dashboard, documentation, tests, and validation each have an owning task.
- **Step scan:** Each task moves from a defined test/check to one implementation action and a specific validation command.
- **Type consistency:** DataFrame interfaces and output filenames are introduced before consumers; `filter_transactions` is defined in Task 6 and validated with KPI recomputation.
- **Review focus:** The five most likely analytical errors are represented as targeted tests in Tasks 2–6.
- **Proportion:** The plan specifies decisions and verification without duplicating implementation code.
