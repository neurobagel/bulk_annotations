""'Transform the JSON of OpenNeuro assessment instances into a table that can be uploaded to the annotation tool"""

import json


def convert_to_table(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
        
    # Extract the labels for the header (one column per assessment)
    headers = ["participant"] + [assessment["Label"] for assessment in data["nb:Assessment"]]
    
    # Extract the values for the row
    # Here we use a single row with all the assessment term URLs so we can easily replace them later with terms from the new vocabulary
    row = ["sub-01"] + [assessment["TermURL"] for assessment in data["nb:Assessment"]]
    
    # Write to the TSV file
    with open(output_file, 'w') as f:
        f.write("\t".join(headers) + "\n")
        f.write("\t".join(row) + "\n")
    

if __name__ == "__main__":
    INPUT_FILE = "outputs/assessments.json"
    OUTPUT_FILE = "outputs/assessments.tsv"
    convert_to_table(INPUT_FILE, OUTPUT_FILE)