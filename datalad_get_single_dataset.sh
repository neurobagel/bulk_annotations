#!/bin/bash

#step1
ds_id=$1

ds_portal="https://github.com/OpenNeuroDatasets-JSONLD/${ds_id}.git"
ds_git="git@github.com:OpenNeuroDatasets-JSONLD/${ds_id}"

ldin="inputs/openneuro-jsonld/"
mkdir -p $ldin
ldout="outputs/openneuro-jsonld/"
mkdir -p $ldout

workdir=$(realpath ${ldin}${ds_id})
out="${ldout}${ds_id}.jsonld"

datalad clone ${ds_git} ${workdir}
datalad get -d $workdir "${workdir}/participants.tsv"
datalad get -d $workdir "${workdir}/participants.json"
datalad get -d $workdir "${workdir}/dataset_description.json"

ds_name=$(python extract_bids_dataset_name.py --ds $workdir)
if [ "$ds_name" == "None" ] ; then ds_name=$ds_id ; else ds_name=$ds_name ; fi

#step2
docker run --rm -v ${workdir}:${workdir} neurobagel/bagelcli pheno --pheno ${workdir}/participants.tsv --dictionary ${workdir}/participants.json --output ${workdir} --name "$ds_name" --portal $ds_portal
docker run --rm -v ${workdir}:${workdir} neurobagel/bagelcli bids --jsonld-path ${workdir}/pheno.jsonld  --bids-dir ${workdir} --output ${workdir}
cp ${workdir}/pheno_bids.jsonld ${out}
