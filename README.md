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
