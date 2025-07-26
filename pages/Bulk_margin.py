import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bulk Profit Calculator", layout="wide", initial_sidebar_state="collapsed")
st.title("📤 Upload Spreadsheet & Calculate Profit per Conversion")

uploaded_file = st.file_uploader("Upload your product file", type=["csv", "xlsx"])

df = None

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        sheet_names = pd.ExcelFile(uploaded_file).sheet_names
        selected_sheet = st.selectbox("Select a sheet", sheet_names)
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

    if df is not None:
        st.success("✅ File loaded successfully!")

        st.subheader("🧩 Match Columns to Fields")

        columns = ["Not included"] + df.columns.tolist()

        col_product = st.selectbox("Product Name column", columns, index=1 if "Product" in df.columns else 0)
        col_production = st.selectbox("Production Cost column", columns, index=1 if "Production" in df.columns else 0)
        col_selling = st.selectbox("Selling Price column", columns, index=1 if "Selling" in df.columns else 0)
        col_packaging = st.selectbox("Packaging Cost column", columns)
        col_delivery = st.selectbox("Delivery Cost column", columns)
        col_marketing = st.selectbox("Marketing Cost column", columns)
        col_platform = st.selectbox("Platform Fee (%) column", columns)

        if st.button("💡 Calculate Profit per Conversion"):
            result_df = pd.DataFrame()

            result_df["Product"] = df[col_product] if col_product != "Not included" else "Unnamed Product"
            result_df["Selling Price"] = df[col_selling] if col_selling != "Not included" else 0.0

            production = df[col_production] if col_production != "Not included" else 0.0
            packaging = df[col_packaging] if col_packaging != "Not included" else 0.0
            delivery = df[col_delivery] if col_delivery != "Not included" else 0.0
            marketing = df[col_marketing] if col_marketing != "Not included" else 0.0
            platform_fee = df[col_platform] if col_platform != "Not included" else 0.0

            result_df["Total Cost"] = (
                production +
                packaging +
                delivery +
                marketing +
                (platform_fee / 100 * result_df["Selling Price"])
            )

            result_df["Net Profit"] = result_df["Selling Price"] - result_df["Total Cost"]
            result_df["Profit Margin (%)"] = (result_df["Net Profit"] / result_df["Selling Price"] * 100).round(2)

            result_df["Max Marketing Budget (2x ROAS)"] = (result_df["Net Profit"] / 3 ).round(2)
            result_df["Max Marketing Budget (3x ROAS)"] = (result_df["Net Profit"] / 4 ).round(2)
            
            
            average_row = {
                "Product": "Average",
                "Selling Price": result_df["Selling Price"].mean(),
                "Total Cost": result_df["Total Cost"].mean(),
                "Net Profit": result_df["Net Profit"].mean(),
                "Profit Margin (%)": result_df["Profit Margin (%)"].mean(),
                "Max Marketing Budget (2x ROAS)": result_df["Max Marketing Budget (2x ROAS)"].mean(),
                "Max Marketing Budget (3x ROAS)": result_df["Max Marketing Budget (3x ROAS)"].mean()
            }
            result_df = pd.concat([result_df, pd.DataFrame([average_row])], ignore_index=True)

            def style_rows(row):
                if row["Product"] == "Average":
                    return ['background-color: yellow'] * len(row)
                elif row["Profit Margin (%)"] < 25:
                    return ['background-color: #ffcccc'] * len(row)
                else:
                    return [''] * len(row)

            styled_df = result_df.style.apply(style_rows, axis=1)

            st.subheader("📊 Results (with Styling)")
            st.dataframe(styled_df, use_container_width=True)

            csv_download = result_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Results as CSV", csv_download, file_name="profit_results.csv", mime="text/csv")
