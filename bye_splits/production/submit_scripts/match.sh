#!/bin/bash

# Project Directory
cd /home/llr/cms/ehle/git/bye_splits_new

# Output path for skimmed, matched, and combined files
out_path='/data_CMS/cms/ehle/L1HGCAL/'

# Output paths for skimmed ntuples
phot_out_path="${out_path}photon/"
el_out_path="${out_path}electron/"

while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --batch)
    shift # past argument
    shift # past value
    ;;
    --particle)
    shift
    shift
    ;;
esac
done

BATCH = "${batch}"
PARTICLE = "${particle}"

echo "Matching photon files."
for file in $BATCH
do
  if [ $PARTICLE == "photon" ]
    file_path="${phot_out_path}${file}"
    python bye_splits/production/new_match.py --infile $file_path
  elif [ $PARTICLE == "electron" ]
    file_path="${el_out_path}${file}"
    python bye_splits/production/new_match.py --infile $file_path
  else
    echo "${PARTICLE} is not currently supported for the --particle argument. The options are 'photon' and 'electron'."
  fi
done