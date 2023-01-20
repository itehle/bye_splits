#!/bin/bash

# Working Directory
work_dir='/grid_mnt/vol_home/llr/cms/ehle/git/bye_splits_new/'
prod_dir=${work_dir}'bye_splits/production/'

cd $work_dir

export PATH=$PATH:$work_dir
export PATH=$PATH:$prod_dir

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
    IFS=' ' read -r -a BATCH <<< "$2"#
    shift 2
    ;;
    --particle)
    PARTICLE="$2"
    shift 2
    ;;
esac
done

echo "Matching photon files."
for path in "${BATCH[@]}"
do
  file=$(basename $path)
  echo -e "\nMatching file: ${phot_out_path}skim_${PARTICLE}_${file}"
  if [ $PARTICLE == "photon" ]; then
    file_path="${phot_out_path}skim_${PARTICLE}_${file}"
  elif [ $PARTICLE == "electron" ]; then
    file_path="${el_out_path}skim_${PARTICLE}_${file}"
  else
    echo "${PARTICLE} is not currently supported for the --particle argument. The options are 'photon' and 'electron'."
  fi
  python bye_splits/production/new_match.py --infile $file_path
done