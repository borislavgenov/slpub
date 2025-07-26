import streamlit as st
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Break-Even & Campaign ROI Simulator", layout="wide", initial_sidebar_state="collapsed")
st.title("🎯 Break-Even & Campaign ROI Simulator")

#inputs and options
campaign_cost = st.number_input("📢 Total Campaign Budget (BGN)", min_value=0.0, value=2000.0, step=100.0)

st.subheader("📦 Per-Conversion Costs")
production_cost = st.number_input("Production Cost per Unit", 0.0, value=5.0, step=0.1)
packaging_cost = st.number_input("Packaging Cost", 0.0, value=0.88, step=0.1)
delivery_cost = st.number_input("Delivery Cost", 0.0, value=6.0, step=0.1)
marketing_cost = st.number_input("Marketing Cost per Conversion", 0.0, value=2.0, step=0.1)
platform_fee = st.number_input("Platform Fee (%)", 0.0, 20.0, value=2.9, step=0.1)

st.subheader("🎁 Promotion Strategy")
promo_type = st.selectbox("Promotion Type", ["None", "Flat % Discount", "Buy 2 Get 1 Free"])
unit_price = st.number_input("Selling Price per Unit", 0.01, value=20.0, step=0.1)

discount_percent = 0
adjusted_price = unit_price
adjusted_production = production_cost

if promo_type == "Flat % Discount":
    discount_percent = st.slider("Discount %", 0, 100, 15)
    adjusted_price = unit_price * (1 - discount_percent / 100)
elif promo_type == "Buy 2 Get 1 Free":
    adjusted_price = unit_price * 2
    adjusted_production = production_cost * 3

st.subheader("🔢 Adjusted Values")
col1, col2 = st.columns(2)
col1.metric("🛠 Production Cost (Unit => Adjusted)", f"{production_cost:.2f} BGN => {adjusted_production:.2f} BGN")
col2.metric("💰 Selling Price (Unit => Adjusted)", f"{unit_price:.2f} BGN => {adjusted_price:.2f} BGN")

#calculate
platform_fee_cost = (platform_fee / 100) * adjusted_price
total_cost = adjusted_production + packaging_cost + delivery_cost + marketing_cost + platform_fee_cost
net_profit = adjusted_price - total_cost

break_even_conversions = campaign_cost / net_profit if net_profit > 0 else float('inf')
max_spend_conversion = campaign_cost / break_even_conversions if break_even_conversions != 0 else 0

st.header("📊 Break-Even Results")
col1, col2 = st.columns(2)
col1.metric("Net Profit per Conversion", f"{net_profit:.2f} BGN")
col2.metric("Break-Even Conversions", f"{break_even_conversions:.0f}")
st.metric("📏 Max Spend per Conversion", f"{max_spend_conversion:.2f} BGN")

if net_profit <= 0:
    st.error("⚠️ You're not making profit per conversion.")

#forecast
st.markdown("---")
st.subheader("📈 Optional Forecast")

show_forecast = st.checkbox("Estimate based on expected conversions")
expected_conversions = None
expected_total_profit = None
roi_percent = None
target_cost = None

if show_forecast:
    expected_conversions = st.number_input("Expected Number of Conversions", min_value=10, step=10, value=1000)
    expected_total_profit = (net_profit * expected_conversions) - campaign_cost
    roi_percent = (expected_total_profit / campaign_cost * 100) if campaign_cost > 0 else 0

    st.metric("📈 Forecasted Net Profit", f"{expected_total_profit:.2f} BGN")
    st.metric("💸 ROI", f"{roi_percent:.2f}%")

    target_cost = adjusted_price - ((expected_total_profit + campaign_cost) / expected_conversions)
    st.metric("📏 Max Cost per Conversion to Hit Target", f"{target_cost:.2f} BGN")

    if total_cost > target_cost:
        st.error("⚠️ Too expensive to reach your goal.")
    else:
        st.success("✅ Your cost structure supports your profit target.")

#pdf download
st.markdown("---")
st.subheader("Download Summary as PDF")

if st.button("📥 Generate PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    def write_line(label, value=""):
        pdf.cell(0, 10, f"{label} {value}", ln=True)

    pdf.set_title("Campaign ROI & Break-Even Report")
    pdf.set_font("Arial", 'B', 14)
    write_line("Campaign ROI Report")
    pdf.set_font("Arial", size=12)
    write_line(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    pdf.ln(5)

    write_line("Campaign Budget:", f"{campaign_cost:.2f} BGN")
    write_line("Promotion Type:", promo_type)
    if promo_type == "Flat % Discount":
        write_line("Discount %:", f"{discount_percent}%")

    pdf.ln(3)
    write_line("Production Cost:", f"{production_cost:.2f} BGN => {adjusted_production:.2f} BGN")
    write_line("Selling Price:", f"{unit_price:.2f} BGN => {adjusted_price:.2f} BGN")

    pdf.ln(3)
    write_line("Packaging:", f"{packaging_cost:.2f} BGN")
    write_line("Delivery:", f"{delivery_cost:.2f} BGN")
    write_line("Marketing:", f"{marketing_cost:.2f} BGN")
    write_line("Platform Fee:", f"{platform_fee:.2f}% => {platform_fee_cost:.2f} BGN")

    pdf.ln(5)
    write_line("Net Profit per Conversion:", f"{net_profit:.2f} BGN")
    write_line("Break-Even Conversions:", f"{break_even_conversions:.0f}")
    write_line("Max Spend per Conversion:", f"{max_spend_conversion:.2f} BGN")

    if show_forecast:
        pdf.ln(5)
        write_line("Forecasted Conversions:", f"{expected_conversions}")
        write_line("Forecasted Profit:", f"{expected_total_profit:.2f} BGN")
        write_line("ROI:", f"{roi_percent:.2f}%")
        write_line("Max Cost per Conversion for Goal:", f"{target_cost:.2f} BGN")

    pdf_path = r"D:\Gamaselect\Лични\Uni\Diplomna\DiscountMargins\roi_report.pdf"
    pdf.output(pdf_path)

    with open(pdf_path, "rb") as f:
        st.download_button("📥 Download PDF", f, file_name="campaign_report.pdf", mime="application/pdf")
