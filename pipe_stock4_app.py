import pandas as pd
import streamlit as st
import os
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Pipe Stock Search Tool", layout="wide")
st.title("🛠 Pipe Stock Search Tool")

# --- Load Latest Excel Stock File ---
excel_files = [f for f in os.listdir() if f.lower().endswith('.xlsx')]
if not excel_files:
    st.error("❌ No Excel stock file found in this folder!")
    st.stop()

# Optional: Pick latest file (assuming filenames contain dates or chronological order)
excel_files.sort(reverse=True)
stock_file = excel_files[0]

# Show stock file date (optional)
file_date = stock_file.split('.')[0]  # filename without extension
st.info(f"📦 Loading stock data from: {stock_file} (Date: {file_date})")

try:
    df_stock = pd.read_excel(stock_file)
except Exception as e:
    st.error(f"❌ Failed to read {stock_file}: {e}")
    st.stop()

# --- Validate Columns ---
expected_cols = ["Pipe Category", "Pipe Size (OD)", "Thickness (mm)", "Weight (kg)", "Quantity"]
if not all(col in df_stock.columns for col in expected_cols):
    st.error(f"❌ Excel file must contain columns: {expected_cols}")
    st.stop()

# --- Clean and Standardize Data ---
df_stock["Pipe Category"] = df_stock["Pipe Category"].astype(str).str.strip()
df_stock["Pipe Size (OD)"] = df_stock["Pipe Size (OD)"].astype(str).str.strip()
df_stock["Thickness (mm)"] = pd.to_numeric(df_stock["Thickness (mm)"], errors='coerce')
df_stock["Weight (kg)"] = pd.to_numeric(df_stock["Weight (kg)"], errors='coerce')
df_stock["Quantity"] = pd.to_numeric(df_stock["Quantity"], errors='coerce')

# --- Search Options ---
st.subheader("🔎 Search Pipe")
pipe_category = st.selectbox("Pipe Category", ["All"] + sorted(df_stock["Pipe Category"].unique()))
pipe_size = st.selectbox("Pipe Size (OD)", ["All"] + sorted(df_stock["Pipe Size (OD)"].unique()))
thickness = st.selectbox("Thickness (mm)", ["All"] + sorted(df_stock["Thickness (mm)"].unique()))
quantity_required = st.number_input("Enter Quantity Required", min_value=1, step=1)

# --- Filter Data ---
df_filtered = df_stock.copy()
if pipe_category != "All":
    df_filtered = df_filtered[df_filtered["Pipe Category"] == pipe_category]
if pipe_size != "All":
    df_filtered = df_filtered[df_filtered["Pipe Size (OD)"] == pipe_size]
if thickness != "All":
    df_filtered = df_filtered[df_filtered["Thickness (mm)"] == thickness]

# --- Display Filtered Pipes ---
st.subheader("📋 Matching Pipes")
if df_filtered.empty:
    st.warning("No pipes found with selected criteria.")
else:
    st.dataframe(df_filtered.reset_index(drop=True))

# --- Check Availability & Weight ---
if st.button("Check Availability"):
    if df_filtered.empty:
        st.warning("No pipe selected.")
    else:
        results = []
        for i, row in df_filtered.iterrows():
            available_qty = row["Quantity"]
            weight_per_pipe = row["Weight (kg)"]
            total_weight = weight_per_pipe * quantity_required
            available = "Yes" if quantity_required <= available_qty else "No"
            stock_info = available_qty if available == "Yes" else f"Only {available_qty} available"
            results.append({
                "Pipe Category": row["Pipe Category"],
                "Pipe Size (OD)": row["Pipe Size (OD)"],
                "Thickness (mm)": row["Thickness (mm)"],
                "Quantity Requested": quantity_required,
                "Available": available,
                "Stock Quantity": stock_info,
                "Total Weight (kg)": total_weight
            })
        df_results = pd.DataFrame(results)
        st.subheader("✅ Availability & Weight")
        st.dataframe(df_results)

# --- Refresh Information ---
st.markdown("---")
st.info("📌 Daily stock data will be automatically picked from the latest Excel file in this folder. Refresh the app daily to update.")
