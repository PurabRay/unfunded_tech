import csv
import json
from tabulate import tabulate

input_file = "reddit.csv"  # Your input CSV file
output_file = "reddit2.csv"  # Output file to store the formatted table

rows = []

# Read and parse the CSV
with open(input_file, "r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        query = row["query"]
        results = row["results"]
        try:
            # Replace single quotes with double quotes for valid JSON and parse it
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

# Use tabulate to create a grid-format table as a string
table_string = tabulate(rows, headers="keys", tablefmt="grid")

# Write the table string to the output file
with open(output_file, "w", encoding="utf-8") as outfile:
    outfile.write(table_string)

print(f"Formatted output has been stored in {output_file}.")
