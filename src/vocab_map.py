import json

import pandas as pd


def make_map(input_file, table_file, output_file):
    
    
    my_map = {}
    
    with open(input_file, 'r') as f:
        dictionary = json.load(f)
        
    table = pd.read_csv(table_file, sep="\t")
        
    for key, value in dictionary.items():
        if "Annotations" in value and "IsPartOf" in value["Annotations"]:
            snomed_id = value["Annotations"]["IsPartOf"]["TermURL"]
        else:
            continue
        
        # Look up the cogAtlas ID for the tool name and then map it to the new SNOMED ID
        cogatlas_id = table[key].values[0]
        my_map[cogatlas_id] = snomed_id
        
    with open(output_file, 'w') as f:
        json.dump(my_map, f, indent=4)
    

if __name__ == "__main__":
    DICTIONARY_FILE = "manual_files/assessments_data_dictionary.json"
    TABLE_FILE= "outputs/assessments.tsv"
    OUTPUT_FILE = "outputs/vocab_map.json"
    make_map(DICTIONARY_FILE, TABLE_FILE, OUTPUT_FILE)