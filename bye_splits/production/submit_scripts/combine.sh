#!/bin/bash

# Output path for skimmed, matched, and combined batch
out_path='/data_CMS/cms/ehle/L1HGCAL/'

# Output paths for skimmed ntuples
phot_out_path="${out_path}photon/"
el_out_path="${out_path}electron/"

# Output paths for matched ntuples after the skimming has been done
phot_match_out="${phot_out_path}matched/"
el_match_out="${el_out_path}matched/"

phot_hadd_comm="hadd -k -j ${phot_match_out}skim_photon_match_hadd.root"
el_hadd_comm="hadd -k -j ${el_match_out}skim_electron_match_hadd.root"

case $key in
    --batch)
    IFS=' ' read -r -a BATCH <<< "$2"
    shift # past argument
    shift # past value
    ;;
    --particle)
    PARTICLE="$2"
    shift
    shift
    ;;
esac

run_hadd() {
    if [ $PARTICLE == "photon" ]; then
        for file in "${BATCH[@]}"
        do
            phot_hadd_comm+=" ${file}"
        done
    elif [ $PARTICLE == "electron" ]; then
        for file in "${BATCH[@]}"
        do
            el_hadd_comm+=" $file}"
        done
    else
        echo "Usage: combine.sh --batch <space_seperated_string_of_batch> --particle <particle_name>"
        exit 0
    fi
}

run_hadd

