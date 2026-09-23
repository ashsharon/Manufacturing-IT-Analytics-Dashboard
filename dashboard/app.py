"""
Manufacturing IT Analytics Dashboard
-------------------------------------
An interactive dashboard for reviewing production KPIs derived from
SAP-style PP/MM export data (production orders, downtime logs, material
and work center masters). Built to resemble a client-facing deliverable
a manufacturing IT consultant might present during a digitalization
project review.

Run:
    pip install streamlit pandas plotly
    streamlit run app.py
"""
import sys
import os
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "analysis"))
from kpi_analysis import (
    load_data,
    scrap_rate_by_material,
    schedule_variance_by_work_center,
    downtime_pareto,
    oee_proxy_by_work_center,
)

st.set_page_config(page_title="Manufacturing IT Analytics", layout="wide")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

st.title("🏭 Manufacturing IT Analytics Dashboard")
st.caption(
    "Production KPIs derived from SAP-style PP/MM export data "
    "(production orders, downtime log, material & work center master)."
)

orders, downtime, work_centers, materials = load_data(DATA_DIR)

# --- Filters -----------------------------------------------------------
with st.sidebar:
    st.header("Filters")
    wc_options = ["All"] + sorted(orders["WorkCenter"].unique().tolist())
    selected_wc = st.selectbox("Work Center", wc_options)
    date_min, date_max = orders["OrderDate"].min(), orders["OrderDate"].max()
    date_range = st.date_input("Order date range", (date_min, date_max))

filtered_orders = orders.copy()
if selected_wc != "All":
    filtered_orders = filtered_orders[filtered_orders["WorkCenter"] == selected_wc]
if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_orders = filtered_orders[
        (filtered_orders["OrderDate"] >= start) & (filtered_orders["OrderDate"] <= end)
    ]
filtered_order_nos = filtered_orders["OrderNo"]
filtered_downtime = downtime[downtime["OrderNo"].isin(filtered_order_nos)]

# --- KPI summary row -----------------------------------------------------
oee_df = oee_proxy_by_work_center(orders, downtime, work_centers)
avg_oee = oee_df["OEE"].mean()
total_scrap_pct = (filtered_orders["ScrapQty"].sum() / filtered_orders["PlannedQty"].sum() * 100) if len(filtered_orders) else 0
avg_variance = ((filtered_orders["ActualHours"].sum() - filtered_orders["PlannedHours"].sum())
                 / filtered_orders["PlannedHours"].sum() * 100) if filtered_orders["PlannedHours"].sum() else 0
total_downtime_hrs = filtered_downtime["DurationMin"].sum() / 60

c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg. OEE (all work centers)", f"{avg_oee:.1f}%")
c2.metric("Scrap rate (filtered)", f"{total_scrap_pct:.1f}%")
c3.metric("Schedule variance (filtered)", f"{avg_variance:.1f}%")
c4.metric("Downtime hours (filtered)", f"{total_downtime_hrs:.1f} h")

st.divider()

# --- Charts ---------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("OEE by Work Center")
    fig_oee = px.bar(
        oee_df, x="WorkCenter", y="OEE", color="OEE",
        color_continuous_scale="RdYlGn", range_color=(50, 100),
        text="OEE",
    )
    fig_oee.update_traces(texttemplate="%{text}%", textposition="outside")
    st.plotly_chart(fig_oee, use_container_width=True)

with col2:
    st.subheader("Downtime Pareto")
    pareto = downtime_pareto(filtered_downtime if len(filtered_downtime) else downtime)
    fig_pareto = px.bar(pareto, x="Reason", y="DurationMin", text="SharePct")
    fig_pareto.update_traces(texttemplate="%{text}%", textposition="outside")
    st.plotly_chart(fig_pareto, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Scrap Rate by Material")
    scrap = scrap_rate_by_material(filtered_orders if len(filtered_orders) else orders)
    fig_scrap = px.bar(scrap, x="MaterialDesc", y="ScrapRatePct", text="ScrapRatePct")
    fig_scrap.update_traces(texttemplate="%{text}%", textposition="outside")
    st.plotly_chart(fig_scrap, use_container_width=True)

with col4:
    st.subheader("Planned vs. Actual Hours by Work Center")
    variance = schedule_variance_by_work_center(filtered_orders if len(filtered_orders) else orders)
    fig_var = px.bar(
        variance, x="WorkCenter", y=["PlannedHours", "ActualHours"],
        barmode="group",
    )
    st.plotly_chart(fig_var, use_container_width=True)

st.divider()
st.subheader("Production Orders (filtered)")
st.dataframe(filtered_orders, use_container_width=True)

st.caption(
    "Data is synthetically generated to resemble SAP PP (production orders) "
    "and MM (material master) module exports for demonstration purposes."
)
