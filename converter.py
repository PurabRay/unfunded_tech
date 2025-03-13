import csv
import json
from tabulate import tabulate

input_file = "reddit.csv"   # Your input CSV file
output_file = "reddit2.csv" # Output file where the table will be stored

rows = []

# Read and parse the CSV file
with open(input_file, "r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        query = row["query"]
        results = row["results"]
        try:
            # Replace single quotes with double quotes to make it valid JSON
            parsed_results = json.loads(results.replace("'", '"'))
            if not isinstance(parsed_results, list):
                parsed_results = [parsed_results]
            for result in parsed_results:
                rows.append({
                    "query": query,
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "score": result.get("score", ""),
                    "comments": result.get("comments", "")
                })
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON for query '{query}': {e}")

# Create a grid-formatted table with clear lined columns using 'fancy_grid'
table_string = tabulate(rows, headers="keys", tablefmt="fancy_grid")

# Write the formatted table to the output file
with open(output_file, "w", encoding="utf-8") as outfile:
    outfile.write(table_string)

print(f"Formatted table stored in {output_file}.")
