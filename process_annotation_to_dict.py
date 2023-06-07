from pathlib import Path
import json

import pandas as pd


MYPATH = Path(__file__).parent


def is_discrete(df: pd.DataFrame) -> bool:
    return  not df.is_row.all()


def is_dropped(df: pd.DataFrame) -> bool:
    """True if the column has been dropped, False otherwise"""
    return (get_col_rows(df)["Decision"] == "drop").item()


def get_ds_path(dataset: str) -> Path:
    return MYPATH / "inputs/openneuro" / dataset


def get_dict_path(dataset: str) -> Path:
    return get_ds_path(dataset) / "participants.json";


def fetch_data_dictionary(dataset: str) -> dict:
    if get_dict_path(dataset).is_file():
        with open(get_dict_path(dataset), "r") as f:
            data_dict = json.load(f)
        return data_dict
    else:
        return {}
    
    
def describe_continuous(df: pd.DataFrame) -> dict:
    return {
        "Annotations": {
            "IsAbout": {
                "TermURL": get_col_rows(df)["controlled_term"].item(),
                "Label": ""
            }
        }
    }
    
    
def get_col_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.query("is_row == True")


def get_level_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.query("is_row == False")

    
def describe_level(level: str, term: str) -> dict:
    return {
            "TermURL": term,
            "Label": ""
        }

    
def describe_discrete(df: pd.DataFrame) -> dict:
    return {
        "Annotations": {
            "IsAbout": {
                "TermURL": get_col_rows(df)["controlled_term"].item(),
                "Label": ""
            },
            "Levels": {
                row.value: describe_level(row.value, row.controlled_term) for _, row in get_level_rows(df).iterrows()
            }
        }
    }
    
    
def write_data_dict(data_dict: dict, path: Path, name: str) -> None:
    with (path / f"{name}.json").open("w") as f:
        json.dump(data_dict, f, indent=2)
    


def main():
    annotated = pd.read_csv(MYPATH / "outputs/annotated_levels.tsv", sep="\t")
    
    # TODO make this work for all datasets
    my_datasets = ["ds000001", "ds001541", "ds000003"]
    for dataset, ds_df in annotated.groupby("dataset"):
        if dataset not in my_datasets:
            continue
        data_dict = fetch_data_dictionary(dataset=dataset)
        
        for col, col_df in ds_df.groupby("column"):
            if is_dropped(col_df):
                continue
            if is_discrete(col_df):
                print(col, "discrete")
                data_dict[col] = describe_discrete(col_df)
                
            else:
                print(col, "continuous")
                data_dict[col] = describe_continuous(col_df)
            
        write_data_dict(data_dict, MYPATH, name=dataset)
    pass
    

if __name__ == "__main__":
    main()
