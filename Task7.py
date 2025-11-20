import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, datetime

DB_PATH = "workouts.db"

# ---------- DB -------------------------------------------------

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    sql = (
        "CREATE TABLE IF NOT EXISTS workouts ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "entry_date TEXT NOT NULL,"
        "exercise TEXT NOT NULL,"
        "sets INTEGER NOT NULL,"
        "reps INTEGER NOT NULL,"
        "weight REAL NOT NULL,"
        "notes TEXT,"
        "created_at TEXT NOT NULL"
        ")"
    )
    conn = get_conn()
    conn.execute(sql)
    conn.commit()
    conn.close()


def add_workout(entry_date, exercise, sets, reps, weight, notes=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO workouts (entry_date, exercise, sets, reps, weight, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (entry_date, exercise, sets, reps, weight, notes, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def delete_workout(entry_id):
    conn = get_conn()
    conn.execute("DELETE FROM workouts WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()


def fetch_df():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM workouts ORDER BY entry_date DESC, id DESC", conn)
    conn.close()
    if not df.empty:
        df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
    return df


# ---------- Analytics -----------------------------------------

def add_volume_column(df):
    if df.empty:
        return df
    df = df.copy()
    df["volume"] = df["sets"] * df["reps"] * df["weight"]
    return df


def weekly_trend(df, exercise=None, end_date=None):
    if df.empty:
        return pd.DataFrame()
    df = add_volume_column(df)
    if end_date is None:
        end_date = date.today()
    else:
        end_date = pd.to_datetime(end_date).date()

    start = end_date - pd.Timedelta(days=13)  # 14-day trend for smoother view
    mask = (df["entry_date"] >= start) & (df["entry_date"] <= end_date)
    dfw = df.loc[mask]
    if exercise:
        dfw = dfw[dfw["exercise"] == exercise]
    if dfw.empty:
        return pd.DataFrame()
    agg = dfw.groupby("entry_date").agg({"volume": "sum"}).reindex(pd.date_range(start, end_date), fill_value=0)
    agg.index = agg.index.date
    return agg


# ---------- UI ------------------------------------------------

def minimal_css():
    st.markdown(
        "<style>"
        "body {font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;}"
        ".stApp { max-width: 900px; margin: 0 auto; }"
        "</style>"
        , unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="Gym Logger — Minimal", layout="centered")
    minimal_css()

    init_db()

    st.title("Gym Logger")
    st.caption("Minimal, fast logging — stores locally in workouts.db")

    # Sidebar: quick add + controls
    with st.sidebar:
        st.header("Quick log")
        with st.form("quick_form", clear_on_submit=True):
            d = st.date_input("Date", value=date.today())
            ex = st.text_input("Exercise", value="Squat")
            sets = st.number_input("Sets", min_value=1, value=3, step=1)
            reps = st.number_input("Reps", min_value=1, value=8, step=1)
            weight = st.number_input("Weight (kg)", min_value=0.0, value=60.0, step=0.5)
            notes = st.text_area("Notes", value="", height=70)
            if st.form_submit_button("Add"):
                if not ex.strip():
                    st.warning("Enter exercise name")
                else:
                    add_workout(d.isoformat(), ex.strip(), int(sets), int(reps), float(weight), notes.strip())
                    st.success("Saved")
                    st.rerun()

        st.markdown("---")
        st.header("Filters")
        df = fetch_df()
        exercises = ["All"] + sorted(df["exercise"].unique().tolist()) if not df.empty else ["All"]
        selected_ex = st.selectbox("Exercise", options=exercises)
        end_date = st.date_input("End date", value=date.today())

        if st.button("Export CSV"):
            if df.empty:
                st.info("No data to export")
            else:
                csv = df.to_csv(index=False)
                st.download_button("Download CSV", data=csv, file_name="workouts.csv", mime="text/csv")

        if st.button("Clear all"):
            if st.confirm("Delete ALL entries? This cannot be undone."):
                conn = get_conn()
                conn.execute("DELETE FROM workouts")
                conn.commit()
                conn.close()
                st.success("Cleared")
                st.rerun()

    # Main area
    st.subheader("Recent entries")
    df = fetch_df()
    if df.empty:
        st.info("No workouts logged yet — use the sidebar to add a quick entry.")
    else:
        display_df = df[["id", "entry_date", "exercise", "sets", "reps", "weight", "notes"]].rename(columns={"entry_date":"date"})
        st.dataframe(display_df, use_container_width=True)

        # allow deleting single entry
        st.write(" ")
        with st.expander("Delete an entry"):
            ids = df["id"].tolist()
            sel = st.selectbox("Select entry id", options=ids)
            if st.button("Delete selected"):
                delete_workout(sel)
                st.success(f"Deleted {sel}")
                st.rerun()

    # Trend chart
    st.subheader("Volume trend")
    if df.empty:
        st.info("No data to chart")
    else:
        ex_filter = None if selected_ex == "All" else selected_ex
        trend = weekly_trend(df, exercise=ex_filter, end_date=end_date)
        if trend.empty:
            st.info("No data in the selected range")
        else:
            fig, ax = plt.subplots(figsize=(8, 3))
            ax.plot(trend.index, trend["volume"], marker="o", linewidth=2)
            ax.set_ylabel("Volume")
            ax.set_xlabel("Date")
            ax.set_title(f"14-day volume{' — ' + ex_filter if ex_filter else ''}")
            ax.grid(alpha=0.25)
            plt.tight_layout()
            st.pyplot(fig)

    # Summary
    st.subheader("Summary")
    if not df.empty:
        dfv = add_volume_column(df)
        total = dfv["volume"].sum()
        st.metric("Total logged volume", f"{int(total)}")
        top = dfv.groupby("exercise").agg({"volume": "sum"}).sort_values("volume", ascending=False).reset_index()
        st.table(top.head(6))

    st.markdown("---")
    st.caption("Run: `streamlit run gym_workout_logger.py` — Dependencies: streamlit, pandas, matplotlib")


if __name__ == "__main__":
    main()
