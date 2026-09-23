"""
KPI calculations for the manufacturing analytics dashboard.

Reads the SAP-style CSV exports and computes:
  - OEE proxy (Availability x Performance x Quality) per work center
  - Downtime Pareto (which reasons cost the most hours)
  - Scrap rate per material
  - Planned vs. actual hours variance (schedule adherence)

These mirror KPIs a manufacturing IT / MES-CAQ consultant would build for a
client review, using data typically sourced from SAP PP/MM tables.
"""
import pandas as pd

DATA_DIR = "../data"


def load_data(data_dir=DATA_DIR):
    orders = pd.read_csv(f"{data_dir}/production_orders.csv", parse_dates=["OrderDate"])
    downtime = pd.read_csv(f"{data_dir}/downtime_log.csv", parse_dates=["EventTimestamp"])
    work_centers = pd.read_csv(f"{data_dir}/work_centers.csv")
    materials = pd.read_csv(f"{data_dir}/material_master.csv")
    return orders, downtime, work_centers, materials


def scrap_rate_by_material(orders: pd.DataFrame) -> pd.DataFrame:
    g = orders.groupby("MaterialDesc").agg(
        PlannedQty=("PlannedQty", "sum"),
        ConfirmedQty=("ConfirmedQty", "sum"),
        ScrapQty=("ScrapQty", "sum"),
    )
    g["ScrapRatePct"] = (g["ScrapQty"] / g["PlannedQty"] * 100).round(2)
    return g.sort_values("ScrapRatePct", ascending=False).reset_index()


def schedule_variance_by_work_center(orders: pd.DataFrame) -> pd.DataFrame:
    g = orders.groupby("WorkCenter").agg(
        PlannedHours=("PlannedHours", "sum"),
        ActualHours=("ActualHours", "sum"),
        Orders=("OrderNo", "count"),
    )
    g["VariancePct"] = ((g["ActualHours"] - g["PlannedHours"]) / g["PlannedHours"] * 100).round(2)
    return g.sort_values("VariancePct", ascending=False).reset_index()


def downtime_pareto(downtime: pd.DataFrame) -> pd.DataFrame:
    g = downtime.groupby("Reason")["DurationMin"].sum().sort_values(ascending=False)
    total = g.sum()
    df = g.reset_index()
    df["SharePct"] = (df["DurationMin"] / total * 100).round(1)
    df["CumulativePct"] = df["SharePct"].cumsum().round(1)
    return df


def oee_proxy_by_work_center(orders: pd.DataFrame, downtime: pd.DataFrame, work_centers: pd.DataFrame) -> pd.DataFrame:
    """
    Simplified OEE proxy per work center:
      Availability = 1 - (downtime hours / planned run hours)
      Performance  = planned hours / actual hours  (capped at 1.0)
      Quality      = confirmed qty / planned qty
      OEE          = Availability x Performance x Quality
    """
    dt_by_wc = downtime.groupby("WorkCenter")["DurationMin"].sum() / 60.0  # -> hours
    rows = []
    for wc in work_centers["WorkCenter"]:
        wc_orders = orders[orders["WorkCenter"] == wc]
        if wc_orders.empty:
            continue
        planned_hours = wc_orders["PlannedHours"].sum()
        actual_hours = wc_orders["ActualHours"].sum()
        planned_qty = wc_orders["PlannedQty"].sum()
        confirmed_qty = wc_orders["ConfirmedQty"].sum()
        downtime_hours = dt_by_wc.get(wc, 0.0)

        availability = max(0.0, 1 - (downtime_hours / planned_hours)) if planned_hours else 0
        performance = min(1.0, planned_hours / actual_hours) if actual_hours else 0
        quality = confirmed_qty / planned_qty if planned_qty else 0
        oee = availability * performance * quality

        rows.append({
            "WorkCenter": wc,
            "Availability": round(availability * 100, 1),
            "Performance": round(performance * 100, 1),
            "Quality": round(quality * 100, 1),
            "OEE": round(oee * 100, 1),
        })
    return pd.DataFrame(rows).sort_values("OEE")


if __name__ == "__main__":
    orders, downtime, work_centers, materials = load_data()

    print("\n=== Scrap Rate by Material ===")
    print(scrap_rate_by_material(orders).to_string(index=False))

    print("\n=== Schedule Variance by Work Center ===")
    print(schedule_variance_by_work_center(orders).to_string(index=False))

    print("\n=== Downtime Pareto ===")
    print(downtime_pareto(downtime).to_string(index=False))

    print("\n=== OEE Proxy by Work Center ===")
    print(oee_proxy_by_work_center(orders, downtime, work_centers).to_string(index=False))
