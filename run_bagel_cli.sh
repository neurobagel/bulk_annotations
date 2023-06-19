#!/usr/bin/bash

# make sure we're up to date
docker pull neurobagel/bagelcli:latest

ldin=inputs/openneuro-jsonld/
ldout=outputs/openneuro-jsonld/

ds=$1
workdir=`realpath ${ldin}/$ds`
out=(${ldout}/${ds}.jsonld)

if [ ! -e ${ldout} ]; then
    mkdir -p ${ldout}
fi
 
echo $ds
if [ ! -e ${out} ]; then

    
    echo bagel pheno --pheno ${workdir}/participants.tsv --dictionary ${workdir}/participants.json --output ${workdir} --name $ds
    docker run -v ${workdir}:${workdir} neurobagel/bagelcli:latest pheno --pheno ${workdir}/participants.tsv --dictionary ${workdir}/participants.json --output ${workdir} --name $ds
    docker run -v ${workdir}:${workdir} neurobagel/bagelcli:latest bids --jsonld-path ${workdir}/pheno.jsonld  --bids-dir ${workdir} --output ${workdir}
    
    cp ${workdir}/pheno_bids.jsonld ${out}
fi
