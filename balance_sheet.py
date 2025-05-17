import json
from income import generate_profit_and_loss_statement
from classify import classify_trial_balance, segregate_financial_statements
import re
from mistralai import Mistral

def generate_balance_sheet(api_key, balance_sheet, net_profit):
    """
    Extracts assets, liabilities, equity, and net profit, then generates a formatted balance sheet
    using the Mistral LLM.

    Parameters:
    - api_key (str): Mistral API key.
    - classified_data_json (str): JSON string returned by the classify_trial_balance function.
    - Net_profit: float value returned by the generate_profit_and_loss_statement function.

    Returns:
    - str: The formatted balance sheet.
    """
    # Initialize Mistral client
    model = "mistral-small-latest"
    client = Mistral(api_key=api_key)

    # Parse the classified trial balance data
    try:
        classified_data = json.loads(balance_sheet)
    except json.JSONDecodeError as e:
        return f"❌ Error decoding classified trial balance JSON: {e}"


    
    # Extract assets, liabilities, equity, and net profit
    assets = classified_data.get('assets', {})
    liabilities = classified_data.get('liabilities', {})
    equity = classified_data.get('equity', {})
    totals = classified_data.get('totals', {})
    # print(type(net_profit))
    



    # Extract totals from classified data
    total_assets = totals.get('assets', 0)
    total_liabilities = totals.get('liabilities', 0)
    total_equity = totals.get('equity', 0)

    # Organize the extracted data
    financial_data = {
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity,
        'net_profit': net_profit,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity
    }

    print("✅8. Financial data extracted successfully for balance sheet.")
    
    # Define the prompt for the LLM
    prompt = f"""
    # Balance Sheet Generation Task

    Your task is to create a formal balance sheet using the JSON data provided. The JSON contains categorized financial data including assets, liabilities, equity, and their respective totals.

    **Input Data:**
    {json.dumps(financial_data, indent=2)}

    **Output Requirements:**
    Generate a clear, properly formatted balance sheet with the following specifications:

    - Use the exact table structure provided below and show in table format.
    - Present assets on the right side and liabilities & equity on the left side
    - Group accounts by type (current assets, current liabilities, equity)
    - Include subtotals for each group and grand totals
    - Format all currency values in Indian Rupees (₹)
    - Ensure that Total Assets equals Total Liabilities & Equity

    **📊 Balance Sheet Format**
                                               BALANCE SHEET


| **Liabilities & Equity**            | **Amount (₹)** | **Assets**                         | **Amount (₹)** |
|-------------------------------------|----------------|------------------------------------|----------------|
| **Current Liabilities**             |                | **Current Assets**                 |                |
| Short-Term Liability 1              | ₹[Value]       | Current Asset 1                    | ₹[Value]       |
| Short-Term Liability 2              | ₹[Value]       | Current Asset 2                    | ₹[Value]       |
| **Total Current Liabilities**       | ₹[Total]       | **Total Current Assets**           | ₹[Total]       |
| **Non-Current Liabilities**         |                | **Non-Current Assets**             |                |
| Non-Current Liability 1             | ₹[Value]       | Non-Current Asset 1                | ₹[Value]       |
| NOn-current Liability 2             | ₹[Value]       | Non-Current Asset 2                | ₹[Value]       |
| **Total Non-Current Liabilities**   | ₹[Total]       | **Total Non-Current Assets**       | ₹[Total]       |
| **Total Liabilities**               | ₹[Total]       | **Total Assets**                   | ₹[Total]       |
| **Equity**                          |                |                                    |                |
| Owner's Equity                      | ₹[Value]       |                                    |                |
| Retained Earnings                   | ₹[Value]       |                                    |                |
| Net Profit                          | ₹[Value]       |                                    |                |
| **Total Liabilities & Equity**      | ₹[Total]       | **Total Assets**                   | ₹[Total]       |


    Note: " Total liabilities & equity should be equal to Total Assests"
    
    ****Important Notes:****
    
    - Replace placeholder text in square brackets with actual account names and values from the JSON.
    - Include all accounts within each category.
    - Align numeric values properly for readability.
    - Verify that the final balance sheet balances (total assets = total liabilities + total equity). **important requirement**
    - If non-current assets or non-current liabilities exist in the input, include them in the appropriate sections of the balance sheet.
    - Format currency values consistently (e.g., with commas as thousand separators).

    Please generate the balance sheet based on the provided JSON data following these specifications.
    """

    # Send the prompt to the Mistral model
    response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Extract and return the generated balance sheet
    balance_sheet = response.choices[0].message.content
    
    # print("balance sheet: ",balance_sheet)
    
    return balance_sheet




# if __name__ == "__main__":
    # api_key = "YrEG1WcKWgMEPnQIDA9bxVV5dhjjlkBO"
    # file_path = "TRIAL_BALANCE_1710.xlsx" 
    # result = extract_account_fields_from_file(file_path, api_key)
    # cleaned_json = clean_with_llm(file_path, result, api_key)
    # classified_data=classify_trial_balance(api_key, cleaned_json)
    # balance_sheet, pnl = segregate_financial_statements(classified_data)
    # pnl_statement, net_profit = generate_profit_and_loss_statement(api_key, pnl)
    # generate_balance_sheet(api_key, balance_sheet, net_profit)


# prompt = """# Balance Sheet Generation Task
# Your task is to create a formal balance sheet using the JSON data provided from the classify_trial_balance function. The JSON contains categorized financial data including assets, liabilities, equity, and their respective totals.
# Input Format
# The input will be a JSON object with the following structure:
# jsonCopy{
#   "assets": {
#     "current_assets": {...},
#     "non_current_assets": {...}
#   },
#   "liabilities": {
#     "current_liabilities": {...},
#     "non_current_liabilities": {...}
#   },
#   "equity": {...},
#   "totals": {
#     "total_assets": number,
#     "total_liabilities": number,
#     "total_equity": number
#   }
# }
# Output Requirements
# Generate a clear, properly formatted balance sheet with the following specifications:

# -Use the exact table structure provided below
# -Present assets on the right side and liabilities & equity on the left side
# -Group accounts by type (current assets, current liabilities, equity)
# -Include subtotals for each group and grand totals
# -Format all currency values in Indian Rupees (₹)
# -Ensure that Total Assets equals Total Liabilities & Equity

# Balance Sheet Format
#                               BALANCE SHEET
# ---------------------------------------------------------------------------------------------------------------------------------------------

# | **Liabilities & Equity**                      | **Amount (₹)**     | **Assets**                                  | **Amount (₹)**      |  
# |------------------------------------------------|--------------------|---------------------------------------------|---------------------|  
# | **Current Liabilities**                        |                    | **Current Assets**                         |                     |  
# | [Insert Short-Term Liability 1 Name]           | [Insert Value]     | [Insert Current Asset 1 Name]              | [Insert Value]      |  
# | [Insert Short-Term Liability 2 Name]           | [Insert Value]     | [Insert Current Asset 2 Name]              | [Insert Value]      |  
# | [Insert Short-Term Liability 3 Name]           | [Insert Value]     | [Insert Current Asset 3 Name]              | [Insert Value]      |  
# | [Insert Short-Term Liability 4 Name]           | [Insert Value]     | [Insert Current Asset 4 Name]              | [Insert Value]      |  
# | **Total Current Liabilities**                  | [Insert Total]     | **Total Current Assets**                   | [Insert Total]      |  
# | **Non-Current Liabilities**                    |                    | **Non-Current Assets**                     |                     |  
# | [Insert Non-Current Liability 1 Name]          | [Insert Value]     | [Insert Non-Current Asset 1 Name]          | [Insert Value]      |  
# | [Insert Non-Current Liability 2 Name]          | [Insert Value]     | [Insert Non-Current Asset 2 Name]          | [Insert Value]      |  
# |                                                |                    | [Insert Non-Current Asset 3 Name]          | [Insert Value]      |  
# |                                                |                    | [Insert Non-Current Asset 4 Name]          | [Insert Value]      |  
# | **Total Non-Current Liabilities**              | [Insert Total]     | **Total Non-Current Assets**               | [Insert Total]      |  
# | **Total Liabilities**                          | [Insert Total]     | **Total Assets**                           | [Insert Total]      |  
# -----------------------------------------------------------------
# | **Equity**                                     |                    |                                             |                     |  
# | **Owner's Equity**                             | [Insert Value]     |                                             |                     |  
# | **Retained Earnings**                          | [Insert Value]     |                                             |                     |  
# | **Net Profit**                                 | [Insert Value]     |                                             |                     |  
# -----------------------------------------------------------------
# | **Total Liabilities & Equity**                 | [Insert Total]     | **Total Assets **                           | [Insert Total]      |  
# -----------------------------------------------------------------------------------------------------------------------------------------------

# Important Notes

# Replace placeholder text in square brackets with actual account names and values from the JSON
# Include all accounts within each category
# Align numeric values properly for readability
# Verify that the final balance sheet balances (total assets = total liabilities + total equity)
# If non-current assets or non-current liabilities exist in the input, include them in the appropriate sections of the balance sheet
# Format currency values consistently (e.g., with commas as thousand separators)

# Please generate the balance sheet based on the provided JSON data following these specifications."""