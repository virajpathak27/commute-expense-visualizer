import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import os

st.set_page_config(page_title="Commute & Expense Visualizer", layout="wide")
st.title("🚌 Local Commute & Student Expense Visualizer")
st.caption("B.Tech AI & Data Science — Exploratory Data Analysis (EDA) Project")

DATA_FILE = "commute_expense_log.csv"

# Load data
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=[
        "Date", "Day", "Mode", "Departure_Slot", "Scheduled_Mins",
        "Actual_Mins", "Delay_Reason", "Transit_Cost_INR", "Food_Cost_INR", "Academic_Misc_INR"
    ])

df = load_data()

# Sidebar: Log a New Day
st.sidebar.header("➕ Log Today's Commute & Spend")
with st.sidebar.form("entry_form", clear_on_submit=True):
    log_date = st.date_input("Date", date.today())
    mode = st.selectbox("Transport Mode", ["MSRTC Bus", "Two-Wheeler", "Private Share/Auto"])
    slot = st.selectbox("Departure Slot", ["07:00 AM", "07:15 AM", "07:30 AM", "08:00 AM", "08:30 AM"])
    sched_mins = st.number_input("Scheduled Duration (Mins)", value=45, min_value=15, max_value=120)
    actual_mins = st.number_input("Actual Duration (Mins)", value=50, min_value=15, max_value=180)
    reason = st.text_input("Delay / Route Note", "Normal traffic")
    
    st.markdown("**Daily Expenses (₹)**")
    t_cost = st.number_input("Direct Transit / Fuel Cost (₹)", value=0, min_value=0)
    f_cost = st.number_input("Canteen / Food Cost (₹)", value=40, min_value=0)
    m_cost = st.number_input("Printouts / Stationery / Misc (₹)", value=0, min_value=0)
    
    submitted = st.form_submit_button("Save Entry")
    if submitted:
        new_row = pd.DataFrame([{
            "Date": str(log_date),
            "Day": log_date.strftime("%A"),
            "Mode": mode,
            "Departure_Slot": slot,
            "Scheduled_Mins": sched_mins,
            "Actual_Mins": actual_mins,
            "Delay_Reason": reason,
            "Transit_Cost_INR": t_cost,
            "Food_Cost_INR": f_cost,
            "Academic_Misc_INR": m_cost
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.cache_data.clear()
        st.rerun()

# Feature Engineering: Delay & Total Daily Spend
df["Delay_Mins"] = df["Actual_Mins"] - df["Scheduled_Mins"]
df["Total_Spend_INR"] = df["Transit_Cost_INR"] + df["Food_Cost_INR"] + df["Academic_Misc_INR"]

# Top KPI Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Days Logged", len(df))
col2.metric("Avg One-Way Commute", f"{df['Actual_Mins'].mean():.1f} mins")
col3.metric("Avg Daily Delay", f"+{df['Delay_Mins'].mean():.1f} mins")
col4.metric("Total Variable Spend", f"₹{df['Total_Spend_INR'].sum():,.0f}")

st.divider()

# Interactive Charts
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("⏱️ Commute Time & Delay by Mode")
    fig_commute = px.bar(
        df, x="Date", y=["Scheduled_Mins", "Delay_Mins"],
        color_discrete_sequence=["#2563eb", "#ef4444"],
        title="Scheduled Duration vs. Delay Minutes",
        labels={"value": "Minutes", "variable": "Metric"},
        barmode="stack"
    )
    st.plotly_chart(fig_commute, use_container_width=True)

with right_col:
    st.subheader("💸 Expense Breakdown by Category")
    expense_totals = df[["Transit_Cost_INR", "Food_Cost_INR", "Academic_Misc_INR"]].sum().reset_index()
    expense_totals.columns = ["Category", "Amount"]
    fig_expense = px.pie(
        expense_totals, names="Category", values="Amount",
        hole=0.4, title="Where Your Money Goes"
    )
    st.plotly_chart(fig_expense, use_container_width=True)

# Raw Data Inspector
with st.expander("📋 View & Filter Raw Dataset"):
    st.dataframe(df, use_container_width=True)