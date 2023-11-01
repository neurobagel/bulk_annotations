# bulk_annotations

Retroactively annotate the phenotypic data of a large number of BIDS datasets at once.

At the moment this focuses on datasets with MRI data only.

This takes as input the datasets that are available on the datalad superdataset.

This may not reflect the latest version of all of the datasets on [openneuro](https://github.com/OpenNeuroDatasets)
and [openneuro derivatives](https://github.com/OpenNeuroDerivatives).

**OpenNeuro datasets:**

Number of datasets: 790 with 34479 subjects including:
- 649 datasets with MRI data
 - with participants.tsv: 450 (450 with more than 'participant_id' column)
 - with phenotype directory: 22
 - with fmriprep: 17 (1877 subjects)
   - with participants.tsv: 16
   - with phenotype directory: 1
 - with freesurfer: 28 (1834 subjects)
   - with participants.tsv: 26
   - with phenotype directory: 1
 - with mriqc: 65 (5664 subjects)
   - with participants.tsv: 57
   - with phenotype directory: 9


**OpenNeuro derivatives datasets:**

Number of datasets: 258 with 10582 subjects including:
- 258 datasets with MRI data
 - with participants.tsv: 189 (189 with more than 'participant_id' column)
 - with phenotype directory: 11
 - with fmriprep: 59 (1789 subjects)
   - with participants.tsv: 45
   - with phenotype directory: 1
 - with freesurfer: 59 (1789 subjects)
   - with participants.tsv: 45
   - with phenotype directory: 1
 - with mriqc: 258 (10582 subjects)
   - with participants.tsv: 189
   - with phenotype directory: 11

## Requirements

- datalad: http://handbook.datalad.org/en/latest/intro/installation.html
- requires make

## Install openneuro and openneuro-derivatives using datalad

openneuro can be installed via (this will take a while):

```bash
make openneuro
```

openneuro derivatives can be installed via (this will take a while):

```bash
make openneuro-derivatives
```

### Update datasets to get the latest version

WIP


## listing datasets contents

run `list_openneuro_dependencies.py`
and it will create TSV file with basic info for each dataset and its derivatives.


### TODO:

- make it able to install on the fly datasets or subdatasets
  (especially `sourcedata/raw` for the openneuro-derivatives)


### listing the content of the participants.tsv files

Run `list_participants_tsv_columns.py.py`
to get a listing of all the columns present in all the participants.tsv files
and a list of all the unique columns across participants.tsv files.

Run `list_participants_tsv_levels.py` to also get a listing of all the levels
in all the columns present in all the participants.tsv files.

## Clone the datasets from OpenNeuro-JSONLD

The [OpenNeuro-JSONLD](https://github.com/OpenNeuroDatasets-JSONLD) org
has augmented openneuro datasets. To clone these effectively,
you can use the below command:

It uses the GH CLI: https://cli.github.com/manual/installation

And make sure to be logged into the CLI

```bash
gh repo list OpenNeuroDatasets-JSONLD --fork -L 500 | awk '{print $1}' | sed 's/OpenNeuroDatasets-JSONLD\///g' | parallel -j 6 git clone git@github.com:OpenNeuroDatasets-JSONLD/{}
```

## Running the `bagel-cli` on bulk annotated data
The following scripts are used:
- `extract_bids_dataset_name.py`
- `add_description.py`
- `run_bagel_cli.sh`
- `parallel_bagel.sh`

### Steps
1. Activate a new Python environment and install the dependencies for this repo with `pip install -r requirements.txt`.

2. Get the latest version of the `bagel-cli` from Docker Hub: `docker pull neurobagel/bagelcli:latest`

3. Create a directory called `inputs` in the repository root that contains all the datasets that will be processed with the CLI.

4. To run the CLI in parallel across the datasets in `inputs/`, double check that the directory paths used by `parallel_bagel.sh` and `run_bagel_cli.sh` are correct, then run:
```bash
./parallel_bagel.sh
```
