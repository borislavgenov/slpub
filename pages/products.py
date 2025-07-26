import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Product Manager", layout="wide", initial_sidebar_state="collapsed")
st.title("📦 Product List Manager")


conn = sqlite3.connect("pharmacy.db")
cursor = conn.cursor()


st.subheader("➕ Add or Update a Product")

with st.form("product_form"):
    name = st.text_input("Product Name")
    division = st.selectbox("Division", ["Other", "LecoVita", "AdiPharm"])
    production_cost = st.number_input("Production Cost (BGN)", min_value=0.0, step=0.01)
    packaging_cost = st.number_input("Packaging Cost (BGN)", min_value=0.0, step=0.01)
    delivery_cost = st.number_input("Delivery Cost (BGN)", min_value=0.0, step=0.01)
    platform_fee_pct = st.number_input("Platform Fee (%)", min_value=0.0, step=0.1)
    notes = st.text_area("Notes")

    submitted = st.form_submit_button("💾 Save Product")
    if submitted:
        cursor.execute("SELECT id FROM products WHERE name = ?", (name,))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE products
                SET division = ?, production_cost = ?, packaging_cost = ?, delivery_cost = ?, platform_fee_pct = ?, notes = ?
                WHERE name = ?
            """, (division, production_cost, packaging_cost, delivery_cost, platform_fee_pct, notes, name))
            st.success("✅ Product updated successfully.")
        else:
            cursor.execute("""
                INSERT INTO products (name, division, production_cost, packaging_cost, delivery_cost, platform_fee_pct, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, division, production_cost, packaging_cost, delivery_cost, platform_fee_pct, notes))
            st.success("✅ New product added.")
        conn.commit()


st.markdown("---")
st.subheader("📋 Current Product List")

filter_division = st.selectbox("Filter by Division", ["All", "LecoVita", "PharmaPlus"])

if filter_division != "All":
    query = """
        SELECT name, division, production_cost, packaging_cost,
               delivery_cost, platform_fee_pct, notes
        FROM products
        WHERE division = ?
        ORDER BY name
    """
    products = cursor.execute(query, (filter_division,)).fetchall()
else:
    query = """
        SELECT name, division, production_cost, packaging_cost,
               delivery_cost, platform_fee_pct, notes
        FROM products
        ORDER BY name
    """
    products = cursor.execute(query).fetchall()

df = pd.DataFrame(products, columns=[
    "Product", "Division", "Production Cost", "Packaging", "Delivery", "Platform Fee (%)", "Notes"
])

st.dataframe(df, use_container_width=True)

st.markdown("---")
st.subheader("✏️ Edit Existing Product")


product_names = [row[0] for row in products]
selected_product = st.selectbox("Select a product to edit", product_names)


cursor.execute("""
    SELECT name, division, production_cost, packaging_cost, delivery_cost, platform_fee_pct, notes
    FROM products
    WHERE name = ?
""", (selected_product,))
prod = cursor.fetchone()

if prod:
    with st.form("edit_form"):
        new_name = st.text_input("Product Name", value=prod[0])
        new_div = st.selectbox("Division", ["Other", "LecoVita", "AdiPharm"], index=["Other", "LecoVita", "AdiPharm"].index(prod[1]) if prod[1] in ["Other", "LecoVita", "AdiPharm"] else 0)
        new_prod = st.number_input("Production Cost (BGN)", min_value=0.0, step=0.01, value=prod[2])
        new_pack = st.number_input("Packaging Cost (BGN)", min_value=0.0, step=0.01, value=prod[3])
        new_del = st.number_input("Delivery Cost (BGN)", min_value=0.0, step=0.01, value=prod[4])
        new_fee = st.number_input("Platform Fee (%)", min_value=0.0, step=0.1, value=prod[5])
        new_notes = st.text_area("Notes", value=prod[6])

        save_changes = st.form_submit_button("💾 Save Changes")
        if save_changes:
            cursor.execute("""
                UPDATE products
                SET name = ?, division = ?, production_cost = ?, packaging_cost = ?, delivery_cost = ?, platform_fee_pct = ?, notes = ?
                WHERE name = ?
            """, (new_name, new_div, new_prod, new_pack, new_del, new_fee, new_notes, selected_product))
            conn.commit()
            st.success("✅ Product updated.")
            st.rerun()
