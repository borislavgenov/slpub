import streamlit as st

st.set_page_config(page_title="Discount and Pricing", layout="wide", initial_sidebar_state="collapsed")

st.title("📦 Discount & Pricing Strategy Assistant")

st.markdown("#### What would you like to calculate?")

#options
goal = st.radio("", [
    "📊 Profit per Conversion",
    "📈 Maximum Marketing Spend",
    "💵 What Should I Sell For?",
    "🎁 Impact of Buy 2 Get 1 Free Promo",
    "📅 Monthly Profit Projection"
], index=0)

st.divider()

#constants
with st.expander("📦 Base Costs (Click to Set or Adjust)", expanded=True):
    product_cost = st.number_input("Product cost (BGN)", min_value=0.0, value=5.0, step=0.1)
    packaging_cost = st.number_input("Packaging cost (BGN)", min_value=0.0, value=0.88, step=0.1)
    delivery_cost = st.number_input("Delivery cost per conversion (BGN)", min_value=0.0, value=6.0, step=0.1)
    platform_fee_percent = st.slider("Platform fee (%)", min_value=0.0, max_value=20.0, value=0.5, step=0.1)

#IFs and calcs
if goal == "📊 Profit per Conversion":
    selling_price = st.number_input("Selling price (BGN)", min_value=0.01, value=20.0, step=0.5)
    marketing_cost = st.number_input("Marketing cost per conversion (BGN)", min_value=0.0, value=5.0, step=0.5)

    total_cost = product_cost + packaging_cost + delivery_cost + marketing_cost + (platform_fee_percent / 100 * selling_price)
    profit = selling_price - total_cost
    profit_margin = (profit / selling_price * 100) if selling_price else 0

    st.subheader("📊 Results")
    st.metric("Net Profit per Conversion", f"{profit:.2f} BGN")
    st.metric("Profit Margin", f"{profit_margin:.2f}%")

elif goal == "📈 Maximum Marketing Spend":
    selling_price = st.number_input("Selling price (BGN)", min_value=0.01, value=20.0, step=0.5)
    desired_profit = st.number_input("Desired profit per conversion (BGN)", min_value=0.0, value=5.0, step=0.5)

    fixed_costs = product_cost + packaging_cost + delivery_cost + (platform_fee_percent / 100 * selling_price)
    max_marketing = selling_price - fixed_costs - desired_profit

    st.subheader("🎯 Result")
    if max_marketing >= 0:
        st.success(f"You can afford to spend up to **{max_marketing:.2f} BGN** on marketing per conversion.")
    else:
        st.error("⚠️ Your target profit is too high for this selling price. Try increasing the price or reducing costs.")

elif goal == "💵 What Should I Sell For?":
    marketing_cost = st.number_input("Marketing cost per conversion (BGN)", min_value=0.0, value=5.0, step=0.5)
    desired_profit = st.number_input("Desired profit per conversion (BGN)", min_value=0.0, value=7.0, step=0.5)

    base_cost = product_cost + packaging_cost + delivery_cost + marketing_cost
    price_required = (base_cost + desired_profit) / (1 - platform_fee_percent / 100)

    st.subheader("💸 Required Selling Price")
    st.success(f"You need to sell at **{price_required:.2f} BGN** per unit to hit your target profit per conversion.")

elif goal == "🎁 Impact of Buy 2 Get 1 Free Promo":
    selling_price = st.number_input("Normal selling price for 1 unit (BGN)", min_value=0.01, value=20.0, step=0.5)
    marketing_cost = st.number_input("Marketing cost per conversion (BGN)", min_value=0.0, value=5.0, step=0.5)

    # In B2G1 promo: sell 3 units for the price of 2
    effective_price = 2 * selling_price
    total_cost = (product_cost * 3) + packaging_cost + delivery_cost + marketing_cost + (platform_fee_percent / 100 * selling_price)
    promo_profit = effective_price - total_cost
    promo_margin = (promo_profit / effective_price * 100) if effective_price else 0

    st.subheader("🎁 Promo Results")
    st.metric("Adjusted Price (per combo)", f"{effective_price:.2f} BGN")
    st.metric("Profit per Unit (after promo)", f"{promo_profit:.2f} BGN")
    st.metric("Profit Margin", f"{promo_margin:.2f}%")

elif goal == "📅 Monthly Profit Projection":
    selling_price = st.number_input("Selling price (BGN)", min_value=0.01, value=20.0, step=0.5)
    marketing_cost = st.number_input("Marketing cost per conversion (BGN)", min_value=0.0, value=5.0, step=0.5)
    monthly_conversions = st.number_input("Estimated monthly conversions", min_value=0, value=5, step=5)

    total_cost = product_cost + packaging_cost + delivery_cost + marketing_cost + (platform_fee_percent / 100 * selling_price)
    profit = selling_price - total_cost
    monthly_profit = profit * monthly_conversions

    st.subheader("📅 Projected Monthly Profit")
    st.metric("Net Profit per Conversion", f"{profit:.2f} BGN")
    st.success(f"📈 Estimated Monthly Profit: {monthly_profit:.2f} BGN")
