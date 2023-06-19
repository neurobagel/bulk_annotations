#!/bin/bash

for ds in inputs/openneuro-jsonld/*; do
    ds=$(basename $ds)
    if [ ! -e outputs/openneuro-jsonld/${ds}.jsonld ]; then
        echo $ds
    fi
    
# Now run this in parallel with -j 8 jobs
done | parallel -j 8 ./run_bagel_cli.sh {}

