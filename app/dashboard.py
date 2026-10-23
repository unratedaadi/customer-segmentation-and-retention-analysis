from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.analysis import build_cohort_retention, build_customer_rfm, build_kpis, filter_transactions, monthly_revenue
from src.config import PROCESSED_DATA_DIR

st.set_page_config(page_title="Customer Segmentation & Retention", page_icon="📊", layout="wide")


@st.cache_data
def load_transactions() -> pd.DataFrame:
    data = pd.read_csv(PROCESSED_DATA_DIR / "transactions_clean.csv", parse_dates=["InvoiceDate"])
    return data


def money(value: float) -> str:
    return f"£{value / 1_000_000:.2f}M" if value >= 1_000_000 else f"£{value:,.0f}"


st.title("Customer Segmentation & Retention Analysis")
st.caption("UCI Online Retail · 1 Dec 2010–9 Dec 2011 · Valid paid transactions only")

transactions = load_transactions()
with st.sidebar:
    st.header("Filters")
    country = st.selectbox("Country", ["All"] + sorted(transactions["Country"].dropna().unique().tolist()))
    base = filter_transactions(transactions, country=country)
    rfm_options = build_customer_rfm(base)["Segment"].value_counts().index.tolist() if not base.empty else []
    segment = st.selectbox("Customer segment", ["All"] + rfm_options)

selected = filter_transactions(transactions, country=country, segment=segment)
if selected.empty:
    st.warning("No valid transactions match the selected filters.")
    st.stop()

metrics = build_kpis(selected)
rfm = build_customer_rfm(selected)
at_risk = int((rfm["Segment"] == "At Risk").sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers", f"{metrics['customers']:,}")
c2.metric("Revenue", money(metrics["revenue"]))
c3.metric("Repeat buyers", f"{metrics['repeat_buyer_rate']:.1%}")
c4.metric("At-risk customers", f"{at_risk:,}")

left, right = st.columns((1.25, 1))
with left:
    monthly = monthly_revenue(selected)
    chart = px.line(monthly, x="Month", y="Revenue", markers=True, color_discrete_sequence=["#2563eb"])
    chart.update_layout(title="Monthly revenue", yaxis_title="Revenue (GBP)", xaxis_title=None, margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(chart, use_container_width=True)
with right:
    segment_value = rfm.groupby("Segment", as_index=False).agg(Revenue=("Monetary", "sum"), Customers=("CustomerID", "nunique")).sort_values("Revenue", ascending=True)
    chart = px.bar(segment_value, x="Revenue", y="Segment", orientation="h", text_auto=".2s", color="Segment", color_discrete_sequence=px.colors.qualitative.Safe)
    chart.update_layout(title="Revenue by customer segment", showlegend=False, xaxis_title="Revenue (GBP)", yaxis_title=None, margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(chart, use_container_width=True)

retention, sizes = build_cohort_retention(selected)
heatmap = retention.copy()
heatmap.index = heatmap.index.strftime("%b %Y")
fig = px.imshow(heatmap, labels=dict(x="Months since first purchase", y="First-purchase cohort", color="Retention"), color_continuous_scale="Blues", aspect="auto", zmin=0, zmax=1)
fig.update_layout(title="Cohort retention", margin=dict(l=0, r=0, t=50, b=0))
fig.update_coloraxes(colorbar_tickformat=".0%")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Recommended retention actions")
action_map = {
    "Champions": "Protect value with VIP recognition, early-access offers, and referral incentives.",
    "Loyal Customers": "Use cross-sell recommendations and loyalty benefits to deepen repeat behavior.",
    "Potential Loyalists": "Send post-purchase recommendations or a timely second-order incentive.",
    "At Risk": "Prioritize a targeted re-engagement offer; these customers purchased often but have become inactive.",
    "Lost Customers": "Test a low-cost win-back message and suppress non-responders from repeated outreach.",
    "Needs Attention": "Use product/category preferences to improve relevance before discounting.",
}
actions = segment_value[["Segment", "Customers", "Revenue"]].copy()
actions["Recommended action"] = actions["Segment"].map(action_map)
actions["Revenue"] = actions["Revenue"].map(money)
st.dataframe(actions.sort_values("Customers", ascending=False), use_container_width=True, hide_index=True)

with st.expander("Method and definitions"):
    st.markdown("""
    **RFM:** Recency is days since the last purchase, Frequency is distinct valid invoices, and Monetary value is total positive purchase revenue. 
    **Repeat buyer:** a customer with two or more distinct valid invoices. **Retention:** active customers in a calendar month divided by customers in that cohort's first-purchase month. 
    Cancellations, negative quantities, zero prices, and records without customer IDs are excluded.
    """)
