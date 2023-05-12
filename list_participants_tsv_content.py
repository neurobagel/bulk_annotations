import pandas as pd
from rich import print
from pathlib import Path


datalad_superdataset = Path("/home/remi/datalad/datasets.datalad.org")
openneuro = datalad_superdataset / "openneuro"

datasets = pd.read_csv(Path(__file__).resolve().parent / "openneuro.tsv", sep="\t")

for dataset_name in datasets.name:
    mask = datasets.name == dataset_name
    if datasets[mask].has_mri.values[0] and datasets[mask].has_participant_tsv.values[0]:  
        print(dataset_name)
        participants = pd.read_csv(openneuro / dataset_name / "participants.tsv", sep="\t")
