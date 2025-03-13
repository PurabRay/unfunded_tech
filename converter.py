import csv
import json

input_file = "reddit.csv"  # Change this to your actual CSV file name
output_file = "reddit2.csv"

with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", newline="", encoding="utf-8") as outfile:
    reader = csv.DictReader(infile)
    fieldnames = ["query", "title", "url", "score", "comments"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        query = row["query"]
        results = row["results"]

        try:
            # Convert the JSON-like string into a Python list of dictionaries
            parsed_results = json.loads(results.replace("'", '"'))  # Replace single quotes with double quotes
            if not isinstance(parsed_results, list):  # Ensure it's a list
                parsed_results = [parsed_results]

            # Write each result with the associated query
            for result in parsed_results:
                writer.writerow({
                    "query": query,
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "score": result.get("score", ""),
                    "comments": result.get("comments", ""),
                })
        
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON for query '{query}': {e}")

print("CSV file formatted successfully.")
