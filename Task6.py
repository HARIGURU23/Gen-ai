# app.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

DATA_FILE = "water_log.csv"
DAILY_GOAL = 3000  # ml

# ---------------- Helper Functions ---------------- #

def init_file():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["date", "water_ml"])
        df.to_csv(DATA_FILE, index=False)

def read_logs():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["date", "water_ml"])
    df = pd.read_csv(DATA_FILE, parse_dates=["date"])
    df["water_ml"] = pd.to_numeric(df["water_ml"], errors="coerce").fillna(0).astype(int)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

def write_logs(df: pd.DataFrame):
    df_out = df.copy()
    df_out["date"] = df_out["date"].astype(str)
    df_out.to_csv(DATA_FILE, index=False)

def add_water(amount_ml: int, date=None):
    if date is None:
        date = datetime.now().date()
    df = read_logs()
    if date in df["date"].values:
        df.loc[df["date"] == date, "water_ml"] += amount_ml
    else:
        df = pd.concat([df, pd.DataFrame([{"date": date, "water_ml": amount_ml}])], ignore_index=True)
    df = df.sort_values("date").reset_index(drop=True)
    write_logs(df)

def get_today_amount() -> int:
    df = read_logs()
    today = datetime.now().date()
    row = df[df["date"] == today]
    return int(row["water_ml"].iloc[0]) if not row.empty else 0

def prepare_weekly():
    df = read_logs()
    today = datetime.now().date()
    week = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    week_df = pd.DataFrame({"date": week})
    merged = week_df.merge(df, on="date", how="left").fillna(0)
    merged["water_ml"] = merged["water_ml"].astype(int)
    merged["label"] = merged["date"].apply(lambda d: d.strftime("%a\n%d-%b"))
    return merged


# ---------------- Streamlit UI ---------------- #

st.set_page_config(page_title="Water Intake Tracker 💧", page_icon="💧", layout="centered")
init_file()

st.title("Water Intake Tracker 💧")
st.markdown("Log daily water (ml) and track your progress toward a **3 L (3000 ml)** goal.")

# Input row
col1, col2, col3 = st.columns([2, 2, 3])
with col1:
    add_amount = st.number_input("Add water (ml)", min_value=1, value=250, step=50)
with col2:
    add_btn = st.button("Add")
with col3:
    st.write("")  # spacing

# Optional date override
with st.expander("Log for a different date (optional)"):
    chosen_date = st.date_input("Date", value=datetime.now().date())
    if chosen_date != datetime.now().date():
        st.caption("Logging for chosen date instead of today.")

if add_btn:
    date_to_use = chosen_date if "chosen_date" in locals() else datetime.now().date()
    add_water(int(add_amount), date=date_to_use)
    st.success(f"Logged {add_amount} ml for {date_to_use}")
    st.rerun()   # <-- NEW

# Today's progress
today_amount = get_today_amount()
pct = min(today_amount / DAILY_GOAL, 1.0)

st.subheader("Today's Progress")
st.metric(
    label=str(datetime.now().date()),
    value=f"{today_amount} ml",
    delta=f"{int(pct*100)}% of goal"
)
st.progress(pct)

# Quick buttons
col_a, col_b, col_c = st.columns(3)

with col_a:
    if st.button("Quick +250 ml"):
        add_water(250)
        st.rerun()

with col_b:
    if st.button("Quick +500 ml"):
        add_water(500)
        st.rerun()

with col_c:
    if st.button("Reset today"):
        df = read_logs()
        today = datetime.now().date()
        df = df[df["date"] != today]
        write_logs(df)
        st.rerun()

# Weekly chart
st.subheader("Weekly Hydration Chart (last 7 days)")
weekly = prepare_weekly()

# Show table
st.dataframe(
    weekly[["date", "water_ml"]].rename(columns={"date": "Date", "water_ml": "Water (ml)"}),
    height=200
)

# Matplotlib chart
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.plot(weekly["label"], weekly["water_ml"], marker="o", linewidth=2)
ax.set_ylabel("Water (ml)")
ax.set_ylim(0, max(max(weekly["water_ml"].max(), DAILY_GOAL) * 1.1, DAILY_GOAL + 200))
ax.axhline(DAILY_GOAL, linestyle="--", linewidth=1)
ax.set_title("Last 7 days")

for i, v in enumerate(weekly["water_ml"]):
    ax.text(i, v + 20, str(v), ha="center", va="bottom", fontsize=8)

ax.grid(axis="y", linestyle=":", alpha=0.6)
st.pyplot(fig)

st.markdown("---")
st.write("CSV storage:", DATA_FILE)
st.download_button("Download logs CSV", data=open(DATA_FILE, "rb"), file_name=DATA_FILE)
