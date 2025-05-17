import pandas as pd
import json
import re
from mistralai import Mistral
from extract import extract_account_fields_from_file, clean_with_llm
from auditor import process_accounts_from_excel



def classify_trial_balance(api_key, cleaned_json):
    """
    This function reads a trial balance file, processes the data using process_accounts_from_excel, and then uses the Mistral LLM to classify accounts into the five fundamental accounting categories: Assets, Liabilities, Equity, Expenses, and Revenue.
    """
    model = "mistral-small-latest"
    client = Mistral(api_key=api_key)

    # Step 1: Process trial balance file using the provided function
    trial_balance_json = process_accounts_from_excel(cleaned_json, api_key)

    # Step 2: Save JSON for reference
    json_file = "trial_balance.json"
    with open(json_file, "w") as f:
        json.dump(trial_balance_json, f, indent=4)

    print(f"✅ 4. Trial balance data saved to {json_file} from auditor file.")

    # Step 3: Define prompt for LLM with JSON data
    prompt = f"""
    You are a financial accounting expert tasked with categorizing trial balance data into the five fundamental accounting categories.

    INPUT FORMAT:
    {json.dumps(trial_balance_json, indent=2)}

    The input will be a JSON array of trial balance entries, where each entry has the following structure:
    {{
    "accountNumber": "string",
    "accountName": "string",
    "debit": number,  // will be null/0 if this is a credit entry
    "credit": number  // will be null/0 if this is a debit entry
    }}

    TASK:
    Categorize each account from the trial balance into one of these 5 categories:
    1. Assets (Debit balance)
    2. Liabilities (Credit balance)
    3. Equity (Credit balance)
    4. Expenses (Debit balance)
    5. Revenue (Credit balance)

    ACCOUNTING CLASSIFICATION RULES:
    - Accounts starting with 1xxx typically represent Assets (normal balance: Debit)
    - Accounts starting with 2xxx typically represent Liabilities (normal balance: Credit)
    - Accounts starting with 3xxx typically represent Equity (normal balance: Credit)
    - Accounts starting with 4xxx typically represent Revenue (normal balance: Credit)
    - Accounts starting with 5xxx-6xxx typically represent Expenses (normal balance: Debit)

    OUTPUT FORMAT:
    Return only a valid JSON object without extra text, with this structure:

    {{
    "assets": [
        {{
        "accountNumber": "string",
        "accountName": "string",
        "amount": number,
        "balanceType": "string" // "Dr." or "Cr."
        }}
    ],
    "liabilities": [
        {{
        "accountNumber": "string",
        "accountName": "string",
        "amount": number,
        "balanceType": "string" // "Dr." or "Cr."
        }}
    ],
    "equity": [
        {{
        "accountNumber": "string",
        "accountName": "string",
        "amount": number,
        "balanceType": "string" // "Dr." or "Cr."
        }}
    ],
    "expenses": [
        {{
        "accountNumber": "string",
        "accountName": "string",
        "amount": number,
        "balanceType": "string" // "Dr." or "Cr."
        }}
    ],
    "revenue": [
        {{
        "accountNumber": "string",
        "accountName": "string",
        "amount": number,
        "balanceType": "string" // "Dr." or "Cr."
        }}
    ],
    "totals": {{
        "assets": number,
        "liabilities": number,
        "equity": number,
        "expenses": number,
        "revenue": number,
        "debits": number,
        "credits": number
    }}
    }}

    Ensure your categorization follows accounting principles and the account numbering conventions. The totals section should include the sum of amounts for each category and verification that total debits equal total credits.

    VERIFICATION:
    After categorizing, verify that:
    1. The total of Assets (debit) equals the sum of Liabilities + Equity (credit) + (Revenue - Expenses)
    2. Total Debits = Total Credits across all categories
    """

    # Step 4: Send request to Mistral LLM
    chat_response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract response text
    response_text = chat_response.choices[0].message.content
    # print("Raw response text:", response_text)

    # Step 5: Extract JSON using regex
    match = re.search(r"```json\n(.*?)\n```", response_text, re.DOTALL)

    if match:
        json_data = match.group(1)  # Extract JSON portion
    else:
        json_data = response_text  # Assume whole response is JSON

    # Step 6: Convert JSON string to Python dictionary
    try:
        categorized_data = json.loads(json_data)
        print("✅ 5. Successfully parsed JSON response after classification. ")
    except json.JSONDecodeError as e:
        print("❌ Error decoding JSON:", e)
        categorized_data = {}
    classified = json.dumps(categorized_data, indent=4)
    # print("classified data: ",classified)
    
    return classified



def segregate_financial_statements(classified_json_str):
    """
    Segregates the classified trial balance JSON into balance sheet and P&L components.

    Parameters:
    - classified_json_str (str): JSON string returned from classify_trial_balance

    Returns:
    - tuple: (balance_sheet_json_str, profit_and_loss_json_str)
    """
    try:
        classified_data = json.loads(classified_json_str)
    except json.JSONDecodeError as e:
        print("❌ Failed to parse classified JSON:", e)
        return None, None

    # Extract relevant parts
    balance_sheet = {
        "assets": classified_data.get("assets", []),
        "liabilities": classified_data.get("liabilities", []),
        "equity": classified_data.get("equity", []),
        "totals": {
            "assets": classified_data.get("totals", {}).get("assets", 0),
            "liabilities": classified_data.get("totals", {}).get("liabilities", 0),
            "equity": classified_data.get("totals", {}).get("equity", 0)
        }
    }

    profit_and_loss = {
        "expenses": classified_data.get("expenses", []),
        "revenue": classified_data.get("revenue", []),
        "totals": {
            "expenses": classified_data.get("totals", {}).get("expenses", 0),
            "revenue": classified_data.get("totals", {}).get("revenue", 0)
        }
    }

    # Convert both to JSON strings
    balance_sheet_json = json.dumps(balance_sheet, indent=4)
    pnl_json = json.dumps(profit_and_loss, indent=4)
    
    print("✅ 6. Successfully segregated balance sheet and P&L data.")
    print("Balance Sheet JSON: ", balance_sheet_json)
    print("Profit and Loss JSON: ", pnl_json)

    return balance_sheet_json, pnl_json


# file_path = "TRIAL_BALANCE_1710.xlsx"
# api_key = "YrEG1WcKWgMEPnQIDA9bxVV5dhjjlkBO"
# file_path = "TRIAL_BALANCE_1710.xlsx"
# result = extract_account_fields_from_file(file_path, api_key)
# print(result)
# cleaned_json = clean_with_llm(file_path, result, api_key)
# print(cleaned_json)
# classified_json_str=classify_trial_balance(api_key, cleaned_json)
# segregate_financial_statements(classified_json_str)


