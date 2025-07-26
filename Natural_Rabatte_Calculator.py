import streamlit as st

st.set_page_config(page_title="Natural Rabatte Calculator", layout="wide", initial_sidebar_state="collapsed")

st.title("📦 Natural Rabatte → Price Discount")
st.markdown("Calculate the real price discount when offering a package deal (for example 5+1).")

st.divider()


col1, col2, col3 = st.columns(3)
with col1:
    buy_qty = st.number_input("You buy (qty):", min_value=1, step=1, value=5)
with col2:
    free_qty = st.number_input("Free addition (qty):", min_value=1, step=1, value=1)


st.divider()

#calcs
total_units = buy_qty + free_qty
effective_unit_price = buy_qty / total_units  # this is what % the partner pays
natural_discount_percent = (1 - effective_unit_price) * 100


natural_rabatte_percentage = (free_qty / buy_qty) * 100


st.subheader("📊 Резултати")
st.markdown(f"""
- 🟢 **Natural Rabatte Percent ({buy_qty}+{free_qty}) = {natural_rabatte_percentage:.2f}% ефективна ценова отстъпка**
- 🟠 **Real Price Discount Percent: {natural_discount_percent:.2f}%**
- 🔵 **Suggested Percent Discount for end consumer (round to 15%, 20%, etc.): {natural_discount_percent - 2:.2f}%**
""")



st.divider()
st.info("💡 Use this tool to determine an acceptable Discount % for the end consumer based on given Natural Rabatte.")
