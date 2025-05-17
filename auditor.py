import json
import re
import pandas as pd
from mistralai import Mistral
from extract import extract_account_fields_from_file, clean_with_llm


def process_accounts_from_excel(cleaned, api_key):
    # # Read the Excel file
    # df = pd.read_excel(file_path)

    # # Select and rename required columns
    # selected_columns = {
    #     "G/L Account": "G/L Account",
    #     "G/L Account.1": "Account Name",
    #     "Ending Balance in Company Code Currency": "Ending Balance"
    # }
    
    # df_selected = df[list(selected_columns.keys())].rename(columns=selected_columns)

    # # Extract numeric part from 'G/L Account'
    # df_selected["Account Number"] = df_selected["G/L Account"].astype(str).str.extract(r'/(\d+)$')

    # # Drop the original 'G/L Account' column
    # df_selected = df_selected.drop(columns=["G/L Account"])

    # # Convert DataFrame to JSON
    # json_data = df_selected.to_dict(orient="records")  # Ensures proper JSON structure

    # # Save the JSON (Optional)
    # with open("filtered_accounts.json", "w") as json_file:
    #     json.dump(json_data, json_file, indent=4)
    # print(json_data)
    
    # Step 1: Transform keys to match expected input format
    transformed_input = [
        {
            "Account Number": record["account_number"],
            "Account Name": record["account_name"],
            "Ending Balance": record["closing_balance"]
        }
        for record in cleaned
    ]

    # Step 2: Convert to JSON string
    json_data = json.dumps(transformed_input, indent=4)

    # Initialize Mistral LLM
    model = "mistral-small-latest"
    client = Mistral(api_key=api_key)

    # Define structured prompt explicitly
    prompt = f"""
    Your task is to process a JSON array of financial accounts and transform it into a new format.

    **Processing Instructions:**
    - Extract "Account Number", "Account Name", and "Ending Balance".
    - Create a new object with:
      - "Account Number": same as input.
      - "Account Name": same as input.
      - "Debit": If "Ending Balance" > 0, use "Ending Balance", else 0.
      - "Credit": If "Ending Balance" < 0, use absolute value, else 0.

    **Input JSON:**
    ```json
    {json.dumps(json_data, indent=4)}
    ```

    **Expected Output Format:**
    ```json
    [
        {{
            "Account Number": "1001",
            "Account Name": "Cash",
            "Debit": 5000,
            "Credit": 0
        }},
        {{
            "Account Number": "2001",
            "Account Name": "Accounts Payable",
            "Debit": 0,
            "Credit": 3000
        }}
    ]
    ```

    **Return only the transformed JSON. No explanations.**
    """


    # Step 6: Send request to Mistral LLM
    chat_response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        
    )

    # Extract response text
    response_text = chat_response.choices[0].message.content.strip()
    
    # Step 7: Extract JSON correctly
    match = re.search(r"```json\n(.*?)\n```", response_text, re.DOTALL)
    if match:
        json_data = match.group(1)  # Extract JSON portion
    else:
        json_data = response_text  # Assume whole response is JSON

    # Step 8: Convert JSON string to Python dictionary
    try:
        categorized_data = json.loads(json_data)
        print("✅ 3. Successfully parsed JSON response of auditor file.")
    except json.JSONDecodeError as e:
        print("❌ Error decoding JSON:", e)
        categorized_data = {}

    # Convert output to formatted JSON string
    trail = json.dumps(categorized_data, indent=4)
    # print("auditor_data: ",trail)

    return trail


# # Example usage
# file_path = "TRIAL_BALANCE_1710.xlsx"  # Replace with your actual file
# api_key = "YrEG1WcKWgMEPnQIDA9bxVV5dhjjlkBO"  # Replace with your actual API key
# result = extract_account_fields_from_file(file_path, api_key)
# print(result)
# cleaned_json = clean_with_llm(file_path, result, api_key)
# print(cleaned_json)
# formatted_json = process_accounts_from_excel(cleaned_json, api_key)

