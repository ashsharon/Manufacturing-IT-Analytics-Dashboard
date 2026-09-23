# Manufacturing IT Analytics Dashboard

An analytics dashboard for reviewing shop-floor KPIs derived from **SAP-style
PP (Production Planning) and MM (Materials Management) export data** —
production orders, work centers, material master, and machine downtime logs.

Built as a hands-on way to explore the kind of data and KPIs a manufacturing
IT / MES-CAQ consultant works with day to day: translating raw ERP export
data into decision-ready insights for a client review.

## What it does

- **Generates realistic synthetic data** shaped like typical SAP table
  exports (production orders, material master, work center master, downtime
  events) — see `data/generate_data.py`.
- **Calculates core manufacturing KPIs** in `analysis/kpi_analysis.py`:
  - OEE proxy (Availability × Performance × Quality) per work center
  - Downtime Pareto analysis (which causes eat the most hours)
  - Scrap rate by material
  - Planned vs. actual hours / schedule adherence
- **Visualizes everything in an interactive dashboard** (`dashboard/app.py`)
  built with Streamlit and Plotly, with filters by work center and date
  range — the kind of client-facing view used in project reviews or
  digitalization workshops.

## Why this project

This project was built to bridge into manufacturing IT consulting: applying
data analysis skills to the kind of ERP/MES data structures, KPIs (OEE,
downtime, scrap), and client-review deliverables that come up when
supporting a company's production digitalization (e.g. SAP PP/MM, MES, CAQ
systems). The data schema and field naming intentionally mirror common SAP
tables (production orders ~ AFKO/AFPO, material master ~ MARA, work centers
~ CRHD) so the analysis reads like a real client export.

## Tech stack

Python, pandas, Streamlit, Plotly.

## Running it

```bash
pip install -r requirements.txt

# 1. generate the synthetic dataset
cd data && python generate_data.py && cd ..

# 2. run the KPI calculations from the command line (optional)
cd analysis && python kpi_analysis.py && cd ..

# 3. launch the interactive dashboard
cd dashboard && streamlit run app.py
```

## Project structure

```
sap-manufacturing-analytics/
├── data/
│   ├── generate_data.py       # synthetic SAP-style data generator
│   ├── production_orders.csv
│   ├── material_master.csv
│   ├── work_centers.csv
│   └── downtime_log.csv
├── analysis/
│   └── kpi_analysis.py        # OEE, downtime pareto, scrap rate, variance
├── dashboard/
│   └── app.py                 # Streamlit + Plotly dashboard
├── requirements.txt
└── README.md
```

## Notes

All data is synthetically generated for demonstration purposes and does not
represent a real company or real SAP system.
