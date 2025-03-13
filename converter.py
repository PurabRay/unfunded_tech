import pandas as pd
import json
import csv

def extract_list_from_dict(data_dict):
    """
    If the JSON data is a dict, try to extract a list from one of its values.
    If more than one key contains a list, or none do, return None.
    """
    list_values = [value for value in data_dict.values() if isinstance(value, list)]
    if len(list_values) == 1:
        return list_values[0]
    return None

def convert_json_to_csv(input_json_file, output_csv_file):
    # Load JSON data from file
    with open(input_json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # If data is a dict, try to extract a list from it, else convert dict to a list.
    if isinstance(data, dict):
        extracted = extract_list_from_dict(data)
        if extracted is not None:
            data = extracted
        else:
            # If no list found, treat the dict as a single record.
            data = [data]
    
    # Check if the resulting data is a list.
    if not isinstance(data, list):
        print(f"Error: Expected a list after processing {input_json_file}, got {type(data)} instead.")
        return
    
    # Handle list of dictionaries
    if all(isinstance(entry, dict) for entry in data):
        # Get all unique keys from the JSON to use as column names
        all_keys = set()
        for entry in data:
            all_keys.update(entry.keys())
        # Create DataFrame using the union of keys
        structured_df = pd.DataFrame(data, columns=sorted(all_keys))
    
    # Handle list of strings
    elif all(isinstance(entry, str) for entry in data):
        # Create a DataFrame with a single column "value"
        structured_df = pd.DataFrame(data, columns=["value"])
    
    else:
        print(f"Error: The list in {input_json_file} contains mixed or unsupported types.")
        return

    # Save the DataFrame to CSV with all columns quoted
    structured_df.to_csv(output_csv_file, index=False, quoting=csv.QUOTE_ALL)
    print(f"CSV file saved as {output_csv_file}")

# Example usage for multiple files:
file_mappings = [
    ("reddit_scraped_data.json", "reddit2.csv"),
    ("factordaily_results.json", "factordaily2.csv"),
    ("techcrunch_articles_checkpoint.json", "techcrunch2.csv"),
    ("yourstory_funders_companies_results.json", "yourstory2.csv"),
]

for input_json, output_csv in file_mappings:
    convert_json_to_csv(input_json, output_csv)
