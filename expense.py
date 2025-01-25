import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# File to store expenses
CSV_FILE = "expenses.csv"

# Load or create DataFrame
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(CSV_FILE)
        df["Date"] = pd.to_datetime(df["Date"]).dt.date  # Ensure Date is treated as date (not datetime)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# Streamlit UI
st.title("Expense Tracker 💸")

# Sidebar: Add new expense
with st.sidebar:
    st.header("Add Expense")
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Transport", "Rent", "Entertainment", "Other"])
    amount = st.number_input("Amount ($)", min_value=0.0, step=5.0)
    description = st.text_input("Description")
    if st.button("Add Expense"):
        new_expense = {
            "Date": date,
            "Category": category,
            "Amount": amount,
            "Description": description
        }
        df = load_data()
        df = pd.concat([df, pd.DataFrame([new_expense])], ignore_index=True)
        save_data(df)
        st.success("Expense added!")

# Main area: Visualizations
df = load_data()

if not df.empty:
    # Summary stats
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Expenses", f"${df['Amount'].sum():.2f}")
    col2.metric("Most Spent On", df["Category"].mode()[0])
    col3.metric("Avg Daily Spend", f"${df.groupby('Date')['Amount'].sum().mean():.2f}")

    # Date range filter
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    start_date, end_date = st.date_input(
        "Filter by Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    filtered_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

    # Charts
    st.subheader("Visualizations")
    tab1, tab2 = st.tabs(["By Category", "Over Time"])

    with tab1:
        fig, ax = plt.subplots()
        filtered_df.groupby("Category")["Amount"].sum().plot.pie(
            autopct="%1.1f%%", ax=ax, startangle=90
        )
        ax.set_ylabel("")
        st.pyplot(fig)

    with tab2:
        fig, ax = plt.subplots()
        filtered_df.groupby("Date")["Amount"].sum().plot.bar(ax=ax)
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount ($)")
        st.pyplot(fig)

    # Raw data table
    st.subheader("All Expenses")
    st.dataframe(filtered_df.sort_values("Date", ascending=False))

else:
    st.info("No expenses added yet. Start by adding one in the sidebar!")