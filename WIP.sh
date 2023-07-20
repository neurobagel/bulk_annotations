#!/bin/bash

#step1
ID="ds004393"
GIT="git@github.com:OpenNeuroDatasets-JSONLD/${ID}"

OUTDIR="/home/maellef/DataBase/NeuroBagel_test/"
OUTPATH=${OUTDIR}${ID}

datalad clone ${GIT} ${OUTPATH}
#datalad get "${OUTPATH}/participants.json"
ds_name=$(python extract_bids_dataset_name.py --ds $OUTPATH)
if [ $ds_name == "None" ] ; then ds_name=$ID ; fi

echo ${ds_name}

#step2