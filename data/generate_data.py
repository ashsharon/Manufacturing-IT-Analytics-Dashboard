"""
Generates synthetic manufacturing data shaped like typical SAP PP (Production
Planning) / MM (Materials Management) module exports. Field names loosely
mirror common SAP tables so the dataset reads like a realistic client export:

  - material_master.csv   ~ SAP MARA/MARC style material master
  - work_centers.csv      ~ SAP CRHD style work center master
  - production_orders.csv ~ SAP AFKO/AFPO style production order header+item
  - downtime_log.csv      ~ machine downtime events per work center/order

Run: python generate_data.py
"""
import csv
import random
from datetime import datetime, timedelta

random.seed(42)
OUT_DIR = "."

MATERIALS = [
    ("MAT-1001", "Steel Bracket A", "FERT", "PC", 2.5),
    ("MAT-1002", "Steel Bracket B", "FERT", "PC", 3.1),
    ("MAT-1003", "Motor Housing", "FERT", "PC", 12.4),
    ("MAT-1004", "Control Panel", "FERT", "PC", 18.9),
    ("MAT-1005", "Gearbox Assembly", "FERT", "PC", 45.0),
    ("MAT-2001", "Raw Steel Sheet", "ROH", "KG", 1.2),
    ("MAT-2002", "Circuit Board", "ROH", "PC", 6.7),
]

WORK_CENTERS = [
    ("WC-100", "Cutting Line 1", "Cutting"),
    ("WC-110", "Cutting Line 2", "Cutting"),
    ("WC-200", "Assembly Line A", "Assembly"),
    ("WC-210", "Assembly Line B", "Assembly"),
    ("WC-300", "Quality Inspection", "QA"),
    ("WC-400", "Packaging", "Packaging"),
]

DOWNTIME_REASONS = [
    "Machine breakdown",
    "Material shortage",
    "Changeover / setup",
    "Operator unavailable",
    "Quality hold",
    "Scheduled maintenance",
]


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def gen_material_master():
    rows = [(m[0], m[1], m[2], m[3], m[4]) for m in MATERIALS]
    write_csv(
        f"{OUT_DIR}/material_master.csv",
        ["MaterialNo", "Description", "MaterialType", "BaseUnit", "StdCostPerUnit"],
        rows,
    )


def gen_work_centers():
    rows = [(w[0], w[1], w[2], 8.0) for w in WORK_CENTERS]  # 8h standard shift capacity
    write_csv(
        f"{OUT_DIR}/work_centers.csv",
        ["WorkCenter", "Description", "Category", "ShiftCapacityHrs"],
        rows,
    )


def gen_production_orders(n_orders=180):
    start_date = datetime(2026, 6, 1)
    rows = []
    order_no = 900000
    for i in range(n_orders):
        order_no += 1
        material = random.choice([m for m in MATERIALS if m[2] == "FERT"])
        wc = random.choice(WORK_CENTERS)
        order_date = start_date + timedelta(days=random.randint(0, 110))
        planned_qty = random.choice([50, 100, 150, 200, 300])
        # simulate realistic yield variance
        yield_rate = random.uniform(0.85, 1.0)
        confirmed_qty = int(planned_qty * yield_rate)
        scrap_qty = planned_qty - confirmed_qty
        planned_hours = round(planned_qty * random.uniform(0.05, 0.15), 2)
        # actual hours run somewhat longer than planned (realistic OEE loss)
        actual_hours = round(planned_hours * random.uniform(1.0, 1.35), 2)
        status = random.choices(["CNF", "REL", "TECO"], weights=[0.6, 0.1, 0.3])[0]
        rows.append(
            [
                order_no,
                order_date.strftime("%Y-%m-%d"),
                material[0],
                material[1],
                wc[0],
                planned_qty,
                confirmed_qty,
                scrap_qty,
                planned_hours,
                actual_hours,
                status,
            ]
        )
    write_csv(
        f"{OUT_DIR}/production_orders.csv",
        [
            "OrderNo", "OrderDate", "MaterialNo", "MaterialDesc", "WorkCenter",
            "PlannedQty", "ConfirmedQty", "ScrapQty", "PlannedHours", "ActualHours", "Status",
        ],
        rows,
    )
    return rows


def gen_downtime_log(order_rows, n_events=140):
    rows = []
    event_id = 5000
    for _ in range(n_events):
        event_id += 1
        order = random.choice(order_rows)
        order_date = datetime.strptime(order[1], "%Y-%m-%d")
        event_date = order_date + timedelta(hours=random.randint(0, 20))
        reason = random.choice(DOWNTIME_REASONS)
        duration_min = round(random.uniform(10, 240), 0)
        rows.append(
            [event_id, order[0], order[4], event_date.strftime("%Y-%m-%d %H:%M"), reason, duration_min]
        )
    write_csv(
        f"{OUT_DIR}/downtime_log.csv",
        ["EventID", "OrderNo", "WorkCenter", "EventTimestamp", "Reason", "DurationMin"],
        rows,
    )


if __name__ == "__main__":
    gen_material_master()
    gen_work_centers()
    orders = gen_production_orders()
    gen_downtime_log(orders)
    print("Generated: material_master.csv, work_centers.csv, production_orders.csv, downtime_log.csv")
