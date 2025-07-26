import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Priority Products", layout="wide", initial_sidebar_state="collapsed")
st.title("⭐ Mark Priority Products per Pharmacy & Month")


conn = sqlite3.connect("pharmacy.db")
cursor = conn.cursor()


def generate_past_months(start="2023-01"):
    start_date = datetime.strptime(start, "%Y-%m")
    current_date = datetime.today()
    months = []
    while current_date >= start_date:
        months.append(current_date.strftime("%Y-%m"))
        current_date -= relativedelta(months=1)
    return months

month_options = generate_past_months()

month = st.selectbox("Month", month_options, index=0)
selected_month = month


cursor.execute("SELECT name FROM products ORDER BY name")
product_list = [row[0] for row in cursor.fetchall()]


cursor.execute("SELECT name FROM pharmacies ORDER BY name")
pharmacy_list = [row[0] for row in cursor.fetchall()]


#inputs
pharmacy = st.selectbox("Pharmacy", pharmacy_list)
product = st.selectbox("Product Name", product_list)

priority_total = st.number_input("Priority Total per Unit (BGN)", min_value=0.0, step=0.1)
pharmacist_share = st.number_input("Pharmacist Share (BGN)", min_value=0.0, step=0.1)
pharmacy_share = st.number_input("Pharmacy Share (BGN)", min_value=0.0, step=0.1)


if st.button("💾 Save Priority Product"):
    if product:
        cursor.execute("""
            INSERT INTO priority_products (
                pharmacy_name, product_name, month,
                priority_total, pharmacist_share, pharmacy_share
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (pharmacy, product, month, priority_total, pharmacist_share, pharmacy_share))
        conn.commit()
        st.success("✅ Priority product saved.")
    else:
        st.error("❌ No product selected.")


st.markdown("---")
st.subheader("📜 Priority Product History")

records = cursor.execute("""
    SELECT id, pharmacy_name, product_name, month,
           priority_total, pharmacist_share, pharmacy_share
    FROM priority_products
    WHERE month = ?
    ORDER BY pharmacy_name
""",(selected_month,)).fetchall()

if records:
    header_cols = st.columns([2, 2, 2, 2, 2, 2, 1])
    headers = ["Pharmacy", "Product", "Month", "Total (BGN)", "Pharmacist Share", "Pharmacy Share", ""]
    for col, header in zip(header_cols, headers):
        col.markdown(f"**{header}**")

    for row in records:
        row_id, pharmacy, product, month, total, pharm_share, phcy_share = row
        cols = st.columns([2, 2, 2, 2, 2, 2, 1])
        cols[0].markdown(f"**{pharmacy}**")
        cols[1].markdown(product)
        cols[2].markdown(month)
        cols[3].markdown(f"{total:.2f} лв")
        cols[4].markdown(f"{pharm_share:.2f} лв")
        cols[5].markdown(f"{phcy_share:.2f} лв")
        with cols[6]:
            with st.form(key=f"delete_form_{row_id}", clear_on_submit=True):
                submit = st.form_submit_button("🗑️")
                if submit:
                    cursor.execute("DELETE FROM priority_products WHERE id = ?", (row_id,))
                    conn.commit()
                    st.warning(f"❌ Deleted entry for {product} ({month})")
                    st.rerun()
else:
    st.info("No priority products saved yet.")

conn.close()