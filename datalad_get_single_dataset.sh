#!/bin/bash

#step1
ds_id="ds004107"
ds_portal="https://openneuro.org/datasets/${ds_id}"
GIT="git@github.com:OpenNeuroDatasets-JSONLD/${ds_id}"
OUTDIR="/home/maellef/DataBase/NeuroBagel_test/"

workdir=${OUTDIR}${ds_id}

datalad clone ${GIT} ${workdir}
datalad get -d $workdir "${workdir}/participants.tsv"
datalad get -d $workdir "${workdir}/participants.json"
datalad get -d $workdir "${workdir}/dataset_description.json"

ds_name=$(python extract_bids_dataset_name.py --ds $workdir)
if [ "$ds_name" == "None" ] ; then ds_name=$ds_id ; else ds_name=$ds_name ; fi

#step2
bagel pheno --pheno ${workdir}/participants.tsv --dictionary ${workdir}/participants.json --output ${workdir} --name "$ds_name" --portal $ds_portal
bagel bids --jsonld-path ${workdir}/pheno.jsonld  --bids-dir ${workdir} --output ${workdir}

