#!/bin/bash

while getopts 'p:' OPTION; do
  # Base paths to root files on /dpm
  photon_base_path='root://polgrid4.in2p3.fr//dpm/in2p3.fr/home/cms/trivcat/store/user/lportale/DoublePhoton_FlatPt-1To100/GammaGun_Pt1_100_PU200_HLTSummer20ReRECOMiniAOD_2210_BCSTC-FE-studies_v3-29-1_realbcstc4/221102_143035/0000/'
  electron_base_path='root://polgrid4.in2p3.fr//dpm/in2p3.fr/home/cms/trivcat/store/user/lportale/DoubleElectron_FlatPt-1To100/ElectronGun_Pt1_100_PU200_HLTSummer20ReRECOMiniAOD_2210_BCSTC-FE-studies_v3-29-1_realbcstc4/221102_102633/0000/'

  # List of root files
  photon_files=`gfal-ls $photon_base_path`
  electron_files=`gfal-ls $electron_base_path`

  # Output path
  out_path='/data_CMS/cms/ehle/L1HGCAL'

  # Output names
  photon_out='photon_200PU_bc_stc_hadd.root'
  electron_out='electron_200PU_bc_stc_hadd.root'
  
  case "$OPTION" in
    p)

      if [ "$OPTARG" == "photon" ]
      then

        # Combine files into one.
        # Options: -k = Skip corrupt or non-existent files, do not exit
        #          -j = Parallelize the execution in multiple processes
        photon_comm="hadd -k -j ${out_path}/${photon_out}"

        echo "Combining $OPTARG files to be placed into: ${out_path}/${photon_out}."

        for file in $photon_files
        do
          photon_comm+=" ${photon_base_path}${file}"
        done

        photon_command=`$photon_comm`
        echo $photon_command

      elif [ "$OPTARG" == "electron" ]
      then

        electron_comm="hadd -k ${out_path}/${electron_out}"

        echo "Combining $OPTARG files to be placed into: ${out_path}/${electron_out}."
        
        for file in $electron_files
        do
          electron_comm+=" ${electron_base_path}${file}"
        done

        electron_command=`$electron_comm`
        echo $electron_command

      else
        echo "Particle options are electron and photon."
      fi
     
      echo "Files have been combined."
      ;;
    ?)
      echo "script usage: $(basename \$0) [-p electron/photon]" >&2
      exit 1
      ;;
  esac
done
shift "$((OPTIND -1))"
