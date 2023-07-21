#!/bin/bash

#step1
ds_id="ds004107"
GIT="git@github.com:OpenNeuroDatasets-JSONLD/${ds_id}"
OUTDIR="/home/maellef/DataBase/NeuroBagel_test/"

OUTPATH=${OUTDIR}${ds_id}

datalad clone ${GIT} ${OUTPATH}
datalad get -d $OUTPATH "${OUTPATH}/participants.tsv"
datalad get -d $OUTPATH "${OUTPATH}/participants.json"
datalad get -d $OUTPATH "${OUTPATH}/dataset_description.json"

ds_name=$(python extract_bids_dataset_name.py --ds $OUTPATH)
if [ "$ds_name" == "None" ] ; then ds_name=$ds_id ; else ds_name=$ds_name ; fi

#step2
echo ./run_bagel_cli.sh $ds_id \"$ds_name\"
