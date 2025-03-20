from pathlib import Path
import json

from tqdm import tqdm


def replace_terms(dictionary, map_dict):
    
    updated_dict = {}
    for key, value in dictionary.items():
        if "Annotations" in value and "IsPartOf" in value["Annotations"]:
            cogatlas_id = value["Annotations"]["IsPartOf"]["TermURL"]
            if cogatlas_id in map_dict:
                value["Annotations"]["IsPartOf"]["TermURL"] = map_dict[cogatlas_id]
                updated_dict[key] = value
            else:
                value.pop("Annotations")
                updated_dict[key] = value
        else:
            updated_dict[key] = value
    return updated_dict
        


def parse_dictionaries(work_dir, map_file):
    with open(map_file, 'r') as f:
        my_map = json.load(f)
    
    work_path = Path(work_dir)
    dictionary_files = list(work_path.glob("*.json"))
    
    print(f"Found {len(dictionary_files)} dictionaries")
    
    for dictionary_f in tqdm(dictionary_files, desc="Processing dictionaries"):
        with open(dictionary_f, 'r') as f:
            dictionary = json.load(f)
            
        updated_dict = replace_terms(dictionary, my_map)
        
        with open(dictionary_f, 'w') as f:
            json.dump(updated_dict, f, indent=4)
    

if __name__ == "__main__":
    MAP_FILE = "outputs/vocab_map.json"
    WORK_DIR = "openneuro-annotations"
    parse_dictionaries(work_dir=WORK_DIR, map_file=MAP_FILE)