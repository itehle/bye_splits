#!/bin/bash

# Working Directory
work_dir='/grid_mnt/vol_home/llr/cms/ehle/git/bye_splits_new/'
prod_dir=${work_dir}'bye_splits/production/'

data_dir="/data_CMS/cms/ehle/L1HGCAL/"
photon_base_bath="${data_dir}photon/"
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
for file in "${BATCH[@]}"
do

  if [ $PARTICLE == "photon" ]; then
    file_path="${photon_base_bath}${file}"
    ./t3_produce.exe --infile $file --particle photon
  elif [ $PARTICLE == "electron" ]; then
    file_path="${electron_base_path}${file}"
    ./t3_produce.exe --infile $file --particle electron
  else
    echo "${PARTICLE} is not currently supported for the --particle argument. The options are 'photon' and 'electron'."
  fi

done
