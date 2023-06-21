#!/bin/bash

ldout=outputs/openneuro-jsonld/

for ds in inputs/openneuro-jsonld/*; do
    ds_id=$(basename $ds)
    if [ ! -e ${ldout}/${ds_id}.jsonld ]; then
        # Get human-readable dataset name or "None"
        ds_name=$(python extract_bids_dataset_name.py --ds $ds)

        echo ./run_bagel_cli.sh $ds_id \"$ds_name\"
    fi

# Now run this in parallel with -j 8 jobs
# and have stderr and output both displayed and appended to a file
done | parallel -j 8 2>&1 | tee -a ${ldout}/log.txt
