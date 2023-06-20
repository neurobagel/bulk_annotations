#!/bin/bash

for ds in inputs/openneuro-jsonld/*; do
    ds_id=$(basename $ds)
    if [ ! -e outputs/openneuro-jsonld/${ds_id}.jsonld ]; then
        # Get human-readable dataset name or "None"
        ds_name=$(python extract_bids_dataset_name.py --ds $ds)
        echo $ds_id $ds_name
    fi

# Now run this in parallel with -j 8 jobs
done | parallel -j 8 ./run_bagel_cli.sh {}
