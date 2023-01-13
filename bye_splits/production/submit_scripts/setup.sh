#!/bin/bash

# Project Directory
cd /home/llr/cms/ehle/git/bye_splits_new

# Base paths to root files on /dpm
photon_base_path='root://polgrid4.in2p3.fr//dpm/in2p3.fr/home/cms/trivcat/store/user/lportale/DoublePhoton_FlatPt-1To100/GammaGun_Pt1_100_PU200_HLTSummer20ReRECOMiniAOD_2210_BCSTC-FE-studies_v3-29-1_realbcstc4/221102_143035/0000/'
electron_base_path='root://polgrid4.in2p3.fr//dpm/in2p3.fr/home/cms/trivcat/store/user/lportale/DoubleElectron_FlatPt-1To100/ElectronGun_Pt1_100_PU200_HLTSummer20ReRECOMiniAOD_2210_BCSTC-FE-studies_v3-29-1_realbcstc4/221102_102633/0000/'

# List of root files
photon_files=`gfal-ls $photon_base_path`
electron_files=`gfal-ls $electron_base_path`

# Output path for skimmed, matched, and combined files
out_path='/data_CMS/cms/ehle/L1HGCAL/'

# Output paths for skimmed ntuples
phot_out_path="${out_path}photon/"
el_out_path="${out_path}electron/"

for file in $photon_files
do
    file_path="${photon_base_path}${file}"
    printf "$file_path\n" >> "${phot_out_path}photon_ntuples.txt"
done

for file in $electron_files
do
    file_path="${electron_base_path}${file}"
    printf "$file_path\n" >> "${el_out_path}electron_ntuples.txt"
done