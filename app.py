import streamlit as st
from dotenv import load_dotenv
import os
from income import generate_profit_and_loss_statement
from classify import classify_trial_balance, segregate_financial_statements
from balance_sheet import generate_balance_sheet  # Assuming it's in balance.py
import tempfile

load_dotenv()

st.set_page_config(page_title="Financial Statement Generator", layout="wide")

st.title("📊 Trial Balance Analyzer - P&L & Balance Sheet Generator")

api_key = os.getenv('MISTRAL_API_KEY')

uploaded_file = st.file_uploader("📂 Upload Trial Balance Excel File", type=["xlsx", "xls"])

if uploaded_file and api_key:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    with st.spinner("🔍 Processing trial balance..."):
        try:
            # Step 1
            st.info("🚀 Step 1: Classifying Trial Balance using LLM...")
            classified_data = classify_trial_balance(api_key, file_path)
            st.success("✅ Step 1 Complete: Classification done.")

            # Step 2
            st.info("🧩 Step 2: Segregating data into Balance Sheet and P&L sections...")
            balance_sheet, pnl = segregate_financial_statements(classified_data)
            st.success("✅ Step 2 Complete: Data segregated successfully.")

            # Step 3
            st.info("📈 Step 3: Generating Profit & Loss Statement...")
            pnl_statement, net_profit = generate_profit_and_loss_statement(api_key, pnl)
            st.success("✅ Step 3 Complete: P&L generated.")

            # Step 4
            st.info("📊 Step 4: Generating Balance Sheet...")
            bs_statement = generate_balance_sheet(api_key, balance_sheet, net_profit)
            st.success("✅ Step 4 Complete: Balance Sheet generated.")

            st.success("✅ Financial statements generated successfully!")
            
            # Split and display P&L
            pnl_parts = pnl_statement.split("Explanation:")
            pnl_text = pnl_parts[0].strip()
            pnl_explanation = pnl_parts[1].strip() if len(pnl_parts) > 1 else ""

            with st.expander("🧾 View Profit & Loss Statement", expanded=True):
                st.markdown(pnl_text)
                if pnl_explanation:
                    st.markdown(f"**ℹ️ Explanation:**\n\n{pnl_explanation}")

            # Split and display Balance Sheet
            bs_parts = bs_statement.split("### Explanation:")
            bs_text = bs_parts[0].strip()
            bs_explanation = bs_parts[1].strip() if len(bs_parts) > 1 else ""

            with st.expander("📑 View Balance Sheet", expanded=True):
                st.markdown(bs_text)
                if bs_explanation:
                    st.markdown(f"**ℹ️ Explanation:**\n\n{bs_explanation}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
