from classify import classify_trial_balance, segregate_financial_statements
import json
from mistralai import Mistral
import re


def generate_profit_and_loss_statement(api_key, pnl):
    """
    Extracts expenses, revenue, and their totals from the classified trial balance data,
    and generates a formatted Profit and Loss statement using the Mistral LLM.

    Parameters:
    - api_key (str): Mistral API key.
    - classified_data_json (str): JSON string returned by the classify_trial_balance function.

    Returns:
    - str: The formatted Profit and Loss statement, Net Profit.
    """
    # Initialize Mistral client
    model = "mistral-small-latest"
    client = Mistral(api_key=api_key)
    

    # Parse the JSON data
    try:
        classified_data = json.loads(pnl)
    except json.JSONDecodeError as e:
        return f"❌ Error decoding JSON: {e}"

    # Extract expenses and revenue details
    expenses = classified_data.get('expenses', [])
    revenue = classified_data.get('revenue', [])

    # Extract totals
    totals = classified_data.get('totals', {})
    total_expenses = totals.get('expenses', 0)
    total_revenue = totals.get('revenue', 0)
    # Calculate net profit
    net_profit = total_revenue - total_expenses
    # print(type(net_profit))

    # Organize the extracted data
    financial_data = {
        'expenses': expenses,
        'revenue': revenue,
        'total_expenses': total_expenses,
        'total_revenue': total_revenue,
        'net_profit': net_profit
    }
    print("✅ 7. Financial data extracted successfully for profit and loss statement.")
    # Define the prompt for the LLM
    prompt = f"""
    # Profit and Loss Statement Generation Task

    Your task is to create a formal Profit and Loss statement using the JSON data provided. The JSON contains categorized financial data including revenue, expenses, and their respective totals.

    **Input Data:**
    {json.dumps(financial_data, indent=2)}

    **Output Requirements:**
    Generate a clear, properly formatted Profit and Loss statement with the following specifications:

    - Use the exact table structure provided below
    - Present revenue on the top side and expenses below
    - Include subtotals for each group and a grand total for net profit
    - Format all currency values in Indian Rupees (₹)
    - Use the following computed net profit: ₹{net_profit:,.2f}


    **Profit and Loss Statement Format:**
    | **Revenue**               | **Amount (₹)**     |
    |---------------------------|--------------------|
    | Revenue Account 1         | [value]            |
    | Revenue Account 2         | [value]            |
    | ...                       | ...                |
    | **Total Revenue**         | **₹{total_revenue:,.2f}**        |

    | **Expenses**              | **Amount (₹)**     |
    |---------------------------|--------------------|
    | Expense Account 1         | [value]            |
    | Expense Account 2         | [value]            |
    | ...                       | ...                |
    | **Total Expenses**        | **₹{total_expenses:,.2f}**        |

    | **Net Profit**             | **Amount (₹)**     |
    |---------------------------|--------------------|
    |                           | **₹{net_profit:,.2f}**  |

    **Important Notes:**

    - Replace placeholder text in square brackets with actual account names and values from the JSON.
    - Include all revenue and expense accounts within their respective categories.
    - Align numeric values properly for readability.
    - Format currency values consistently (e.g., with commas as thousand separators).
    """

    # Send the prompt to the Mistral model
    response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Extract and return the generated P&L statement
    pnl_statement = response.choices[0].message.content
    # print("profit and loss statement: ",pnl_statement)
    # print(pnl_statement)

   
            
    return pnl_statement, net_profit


# Example usage
# Set Mistral API key
# api_key = "YrEG1WcKWgMEPnQIDA9bxVV5dhjjlkBO"
# file_path = "TRIAL_BALANCE_1710.xlsx" 
# result = extract_account_fields_from_file(file_path, api_key)
# print(result)
# cleaned_json = clean_with_llm(file_path, result, api_key)
# print(cleaned_json)
# classified_data=classify_trial_balance(api_key, cleaned_json)
# balance_sheet, pnl = segregate_financial_statements(classified_data)
# pnl_statement, net_profit = generate_profit_and_loss_statement(api_key, pnl)

