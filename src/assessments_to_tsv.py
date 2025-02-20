import json


def convert_to_table(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
        
    # Extract the labels for the header
    headers = ["participant"] + [assessment["Label"] for assessment in data["nb:Assessment"]]
    
    # Extract the values for the row
    row = ["sub-01"] + [assessment["TermURL"] for assessment in data["nb:Assessment"]]
    
    # Write to the TSV file
    with open(output_file, 'w') as f:
        f.write("\t".join(headers) + "\n")
        f.write("\t".join(row) + "\n")
    

if __name__ == "__main__":
    INPUT_FILE = "assessments.json"
    OUTPUT_FILE = "assessments.tsv"
    convert_to_table(INPUT_FILE, OUTPUT_FILE)