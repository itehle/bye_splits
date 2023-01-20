#!/bin/bash

# Working Directory
work_dir='/grid_mnt/vol_home/llr/cms/ehle/git/bye_splits_new/'
prod_dir=${work_dir}'bye_splits/production/'

data_dir="/data_CMS/cms/ehle/L1HGCAL/"
photon_base_path="${data_dir}photon/"
electron_base_path="${data_dir}electron/"

cd $work_dir

export PATH=$PATH:$work_dir:$prod_dir

while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --batch)
    IFS=' ' read -r -a BATCH <<< "$2"
    shift 2
    ;;
    --particle)
    PARTICLE="$2"
    shift 2
    ;;
esac
done

# Skim ntuples
for path in "${BATCH[@]}"
do
  file=$(basename $path)
  if [ $PARTICLE == "photon" ]; then
    skimmed_file="${photon_base_path}skim_${PARTICLE}_${file}"
    if ! [ -f $skimmed_file ]; then # Check that skimmed file doesn't already exist
      ./t3_produce.exe --infile $path --particle photon
    fi
  elif [ $PARTICLE == "electron" ]; then
    skimmed_file="${electron_base_path}skim_${PARTICLE}_${file}"
    if ! [ -f $skimmed_file ]; then
      ./t3_produce.exe --infile $path --particle electron
    fi
  else
    echo "${PARTICLE} is not currently supported for the --particle argument. The options are 'photon' and 'electron'."
  fi
  if ! [ -f $matched_file ]; then # Check that matched file doesn't already exist
    python bye_splits/production/new_match.py --infile $skimmed_file
  fi
done
