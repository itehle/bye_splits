#!/bin/bash

# Base paths to root files on /dpm
photon_base_path='root://polgrid4.in2p3.fr//dpm/in2p3.fr/home/cms/trivcat/store/user/lportale/DoublePhoton_FlatPt-1To100/GammaGun_Pt1_100_PU200_HLTSummer20ReRECOMiniAOD_2210_BCSTC-FE-studies_v3-29-1_realbcstc4/221102_143035/0000/'
electron_base_path='root://polgrid4.in2p3.fr//dpm/in2p3.fr/home/cms/trivcat/store/user/lportale/DoubleElectron_FlatPt-1To100/ElectronGun_Pt1_100_PU200_HLTSummer20ReRECOMiniAOD_2210_BCSTC-FE-studies_v3-29-1_realbcstc4/221102_102633/0000/'

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

# Skim ntuples
echo  "Skimming files."
for file in $BATCH
do
  if [ $PARTICLE == "photon" ]
    file_path="${photon_base_path}${file}"
    ./t3_produce.exe --infile $file_path --particle photon
  elif [ $PARTICLE == "electron" ]
    file_path="${electron_base_path}${file}"
    ./t3_produce.exe --infile $file_path --particle electron
  else
    echo "${PARTICLE} is not currently supported for the --particle argument. The options are 'photon' and 'electron'."
  fi
done