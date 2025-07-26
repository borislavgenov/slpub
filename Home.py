import streamlit as st

st.set_page_config(page_title="Home", layout="centered", initial_sidebar_state="collapsed")
st.title("Welcome to Business-Helper Dashboard")

st.markdown("Use the buttons below or the sidebar to navigate between tools.")

# prices 
st.header("🛒 E-Commerce Tools and Pricing Tools")
st.page_link("pages/Discount_and_Pricing_Strategy_Assistant.py", label="Discount & Pricing Strategy Assistant", icon="📊")
st.page_link("pages/Bulk_margin.py", label="Bulk Profit Analyzer", icon="📁")
st.page_link("pages/Break_even.py", label="Break-Even ROI Simulator", icon="📉")

# pharmacies
st.header("🏥 Pharmacy Management")
st.page_link("pages/pharmacy_terms.py", label="Pharmacy Terms", icon="📋")
st.page_link("pages/priority_products.py", label="Sell-out/Priority Products", icon="⭐")

st.page_link("pages/Natural_Rabatte_Calculator.py", label=" Natural Rabatte Calculator", icon="💰")
st.page_link("pages/Retail_Price_calculator.py", label="Retail Price Calculator", icon="🛍️")
st.page_link("pages/Marketing_Activities.py", label="Marketing Activities", icon="📢️")

# administration
st.header("🗂️ Administrative Tasks")
st.page_link("pages/Invoice_Tracking.py", label="Invoice Tracking", icon="📑")
st.page_link("pages/products.py", label="Product List", icon="📦")