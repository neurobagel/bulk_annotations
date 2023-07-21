#!/bin/bash

#step1
ds_id=$1

ds_portal="https://github.com/OpenNeuroDatasets-JSONLD/${ds_id}.git"
GIT="git@github.com:OpenNeuroDatasets-JSONLD/${ds_id}"

bagel_dir="inputs/openneuro-jsonld/"
mkdir -p $bagel_dir
ldout="outputs/openneuro-jsonld/"
mkdir -p $ldout

workdir="${bagel_dir}${ds_id}"
out="${ldout}${ds_id}.jsonld"

datalad clone ${GIT} ${workdir}
datalad get -d $workdir "${workdir}/participants.tsv"
datalad get -d $workdir "${workdir}/participants.json"
datalad get -d $workdir "${workdir}/dataset_description.json"

ds_name=$(python extract_bids_dataset_name.py --ds $workdir)
if [ "$ds_name" == "None" ] ; then ds_name=$ds_id ; else ds_name=$ds_name ; fi

#step2
bagel pheno --pheno ${workdir}/participants.tsv --dictionary ${workdir}/participants.json --output ${workdir} --name "$ds_name" --portal $ds_portal
bagel bids --jsonld-path ${workdir}/pheno.jsonld  --bids-dir ${workdir} --output ${workdir}
cp ${workdir}/pheno_bids.jsonld ${out}
