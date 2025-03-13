import csv
import json

# Define input and output files
input_file = "reddit.csv"  # Change this to your actual file
output_file = "reddit2.csv"

# Open the input file and process it
with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", newline="", encoding="utf-8") as outfile:
    reader = csv.DictReader(infile)

    # Define the column headers for the output file
    fieldnames = ["query", "title", "url", "score", "comments"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        query = row["query"]
        results = row["results"]

        try:
            # Convert the JSON-like string into a proper list of dictionaries
            parsed_results = json.loads(results.replace("'", '"'))  # Replacing single quotes with double quotes

            # Ensure it's a list
            if not isinstance(parsed_results, list):
                parsed_results = [parsed_results]

            # Write each result as a separate row
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

print(f"Formatted CSV saved as {output_file}.")
