#!/bin/bash

#step1
ID="ds004107"
GIT="git@github.com:OpenNeuroDatasets-JSONLD/${ID}"
OUTDIR="/home/maellef/DataBase/NeuroBagel_test/"

OUTPATH=${OUTDIR}${ID}

datalad clone ${GIT} ${OUTPATH}
datalad get -d $OUTPATH "${OUTPATH}/participants.tsv"
datalad get -d $OUTPATH "${OUTPATH}/participants.json"
datalad get -d $OUTPATH "${OUTPATH}/dataset_description.json"

ds_name=$(python extract_bids_dataset_name.py --ds $OUTPATH)
if [ "$ds_name" == "None" ] ; then ds_name=$ID ; else ds_name=$ds_name ; fi

echo $ds_name

#step2

