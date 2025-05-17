from mistralai import Mistral
import pandas as pd
import json
import re


def extract_account_fields_from_file(file_path, api_key):
    try:
        # Step 1: Read file
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Only CSV and Excel files are supported.")

        # Step 2: Get column names and sample data
        column_names = df.columns.tolist()
        data_rows = df.head(2).values.tolist()
        table_sample = [dict(zip(column_names, row)) for row in data_rows]

        # Step 3: Build prompt
        prompt = f"""
You are given a table with the following column names and 2 rows of data:
{json.dumps(table_sample, indent=2)}

Your task is to identify:
1. Which column contains the **Account Number**
2. Which column contains the **Account Name**
3. Which column contains the **Closing Balance**

Important guidelines:
- For **Account Number**:
  - It may be prefixed or combined with letters (e.g., "ACC12345", "A/C 98765")
  - Extract the column even if the account number is part of a longer string
  - Look for numeric patterns that could represent account identifiers

- For **Account Name**:
  - Be tolerant of spelling variations and mistakes
  - Ignore case differences (e.g., "SMITH JOHN" = "Smith John")
  - The name could be in various formats (first name first, last name first, etc.)

- For **Closing Balance**:
  - Look for monetary values, especially those labeled as "closing", "ending", or "balance"
  - May include currency symbols like $, €, £, etc.

Return the answer strictly in the following JSON format:
{{
  "account_number_column": "<column_name>",
  "account_name_column": "<column_name>",
  "closing_balance_column": "<column_name>"
}}
"""

        # Step 4: Call Mistral LLM
        model = "mistral-small-latest"
        client = Mistral(api_key=api_key)

        chat_response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = chat_response.choices[0].message.content.strip()

        # Step 5: Extract JSON block from response
        json_match = re.search(r"\{[\s\S]*?\}", response_text)
        if json_match:
            try:
                extract =  json.loads(json_match.group())
                print("✅ 1. Successfully identified columns from give file.")
                return extract
                
            except json.JSONDecodeError:
                return {
                    "account_number_column": None,
                    "account_name_column": None,
                    "closing_balance_column": None,
                    "error": "Invalid JSON in extracted block",
                    "raw_response": response_text
                }
        else:
            return {
                "account_number_column": None,
                "account_name_column": None,
                "closing_balance_column": None,
                "error": "No JSON object found in LLM response",
                "raw_response": response_text
            }

    except Exception as e:
        return {
            "account_number_column": None,
            "account_name_column": None,
            "closing_balance_column": None,
            "error": str(e)
        }



    
    
def clean_with_llm(file_path, extracted_columns, api_key):
    """
    Uses the LLM to clean the columns identified for account number, account name, and closing balance
    directly from the file and returns the cleaned rows as a list of dictionaries.

    Args:
        file_path (str): Path to the Excel or CSV file
        extracted_columns (dict): Dict with 'account_number_column', 'account_name_column', 'closing_balance_column'
        api_key (str): API key for the LLM

    Returns:
        list: List of dicts, each representing a cleaned row
    """

    # Step 1: Load the file
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Only CSV and Excel files are supported.")

    # Extract relevant columns
    account_col = extracted_columns.get("account_number_column")
    name_col = extracted_columns.get("account_name_column")
    balance_col = extracted_columns.get("closing_balance_column")

    if not all([account_col, name_col, balance_col]):
        raise ValueError("One or more required columns are missing from the extracted column names.")

    # Create a sample for the prompt
    try:
        sample_df = df[[account_col, name_col, balance_col]].fillna("").astype(str)
    except KeyError as e:
        raise ValueError(f"Column not found in the dataset: {e}")

    # Format sample data for LLM
    sample_data = sample_df.to_dict(orient="records")

    # Step 2: Build the prompt
    prompt = f"""
You are given sample financial table data with the following columns:
- Account Number Column: "{account_col}"
- Account Name Column: "{name_col}"
- Closing Balance Column: "{balance_col}"

Sample data:
{json.dumps(sample_data, indent=2)}

Your task:
1. Clean the **Account Number** column: Extract only numeric parts if mixed with text (e.g., "A/C 1001" -> "1001").
2. Clean the **Account Name** column: Capitalize names properly and remove extra spaces (e.g., " john doe  " -> "John Doe").
3. Clean the **Closing Balance** column: Extract numeric value and remove currency symbols (e.g., "$1,000.50" -> 1000.50).

Return the cleaned data as a list of dictionaries with the following format:
[
  {{
    "account_number": "1001",
    "account_name": "John Doe",
    "closing_balance": 1000.5
  }},
  ...
]
Only output the JSON block, no additional explanation.
"""

    # Step 3: Call the LLM
    model = "mistral-small-latest"
    client = Mistral(api_key=api_key)

    chat_response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = chat_response.choices[0].message.content.strip()

    # Step 4: Extract the JSON block
    json_match = re.search(r"\[\s*{[\s\S]*?}\s*]", response_text)
    if not json_match:
        raise ValueError(f"No JSON list found in LLM response. Full response:\n{response_text}")

    try:
        cleaned_list = json.loads(json_match.group())
        print("✅ 2. Successfully cleaned the fields")
        return cleaned_list
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in LLM response. Raw response:\n{response_text}")





# Example usage
# if __name__ == "__main__":
#     file_path = "TRIAL_BALANCE_1710.xlsx"  # Replace with your actual file
#     api_key = "YrEG1WcKWgMEPnQIDA9bxVV5dhjjlkBO"  # Replace with your actual API key
#     result = extract_account_fields_from_file(file_path, api_key)
#     print(result)
#     # result = json.dumps(result, indent=2)
#     cleaned_df = clean_with_llm(file_path, result, api_key)
#     # Preview cleaned data
#     print(cleaned_df)

