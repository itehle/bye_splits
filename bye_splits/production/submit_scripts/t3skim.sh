#!/bin/bash

# Working Directory
work_dir='/grid_mnt/vol_home/llr/cms/ehle/git/bye_splits_new/'
prod_dir=${work_dir}'bye_splits/production/'

cd $work_dir

export PATH=$PATH:$work_dir
export PATH=$PATH:$prod_dir

while [[ $# -gt 0 ]]
do
key="$1"

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
done

bar_size=40
bar_char_done="#"
bar_char_todo="-"
bar_percentage_scale=2

function show_progress {
    current="$1"
    total="$2"

    # calculate the progress in percentage 
    percent=$(bc <<< "scale=$bar_percentage_scale; 100 * $current / $total" )
    # The number of done and todo characters
    done=$(bc <<< "scale=0; $bar_size * $percent / 100" )
    todo=$(bc <<< "scale=0; $bar_size - $done" )

    # build the done and todo sub-bars
    done_sub_bar=$(printf "%${done}s" | tr " " "${bar_char_done}")
    todo_sub_bar=$(printf "%${todo}s" | tr " " "${bar_char_todo}")

    # output the bar
    echo -ne "\rProgress : [${done_sub_bar}${todo_sub_bar}] ${percent}%"

    if [ $total -eq $current ]; then
        echo -e "\nDONE"
    fi
}

progress_len=${#BATCH[@]}
# Skim ntuples
echo  "Skimming ${progress_len} files."
for i in "${!BATCH[@]}"
do
  file=${BATCH[$i]}

  if [ $PARTICLE == "photon" ]; then
    ./t3_produce.exe --infile $file --particle photon
  elif [ $PARTICLE == "electron" ]; then
    file_path="${electron_base_path}${file}"
    ./t3_produce.exe --infile $file --particle electron
  else
    echo "${PARTICLE} is not currently supported for the --particle argument. The options are 'photon' and 'electron'."
  fi

  show_progress $i $progress_len
done
