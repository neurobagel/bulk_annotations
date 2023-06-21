#!/usr/bin/bash

# make sure we're up to date
docker pull neurobagel/bagelcli:latest

ldin=inputs/openneuro-jsonld/
ldout=outputs/openneuro-jsonld/

ds="$1"
ds_name="$2"
ds_portal=https://openneuro.org/datasets/${ds}
workdir=`realpath ${ldin}/$ds`
out=(${ldout}/${ds}.jsonld)

if [ "$ds_name" == "None" ]; then
    ds_name=$ds
fi

if [ ! -e ${ldout} ]; then
    mkdir -p ${ldout}
fi

echo $ds "$ds_name"
if [ ! -e ${out} ]; then


    echo bagel pheno --pheno ${workdir}/participants.tsv --dictionary ${workdir}/participants.json --output ${workdir} --name "$ds_name" --portal $ds_portal
    docker run -v ${workdir}:${workdir} neurobagel/bagelcli:latest pheno --pheno ${workdir}/participants.tsv --dictionary ${workdir}/participants.json --output ${workdir} --name "$ds_name" --portal $ds_portal
    docker run -v ${workdir}:${workdir} neurobagel/bagelcli:latest bids --jsonld-path ${workdir}/pheno.jsonld  --bids-dir ${workdir} --output ${workdir}

    cp ${workdir}/pheno_bids.jsonld ${out}
fi
