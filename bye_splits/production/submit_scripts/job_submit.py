#!/usr/bin/env python

import os
import subprocess
import time

# Specify t3 machine and proxy certificate
machine = "llrt3.in2p3.fr"
proxy = "~/.t3/proxy.cert"
queue = "short"
local = False

working_dir = "/grid_mnt/vol_home/llr/cms/ehle/git/bye_splits_new/"

# Path to submit scripts
submit_dir = "{}bye_splits/production/submit_scripts/".format(working_dir)

# Output path for skimmed, matched, and combined files
out_path='/data_CMS/cms/ehle/L1HGCAL/'

# Submit command
sub_comm = "/opt/exp_soft/cms/t3/t3submit"

# Output paths for skimmed ntuples
phot_out_path="{}photon/".format(out_path)
el_out_path="{}electron/".format(out_path)

# Output paths for matched ntuples after the skimming has been done
phot_match_out = "{}matched/".format(phot_out_path)
el_match_out = "{}matched/".format(el_out_path)

# The setup script saves the file paths on /dpm to .txt files
phot_files = "{}photon_ntuples.txt".format(phot_out_path)
el_files = "{}electron_ntuples.txt".format(el_out_path)

def my_batches(files, files_per_batch):
    return [files[i:i + files_per_batch] for i in range(0, len(files), files_per_batch)]

def strip_trail(batches):
    return [[file.rstrip() for file in batch] for batch in batches]

def setup_batches(files, files_per_batch=10):
    with open(files, "r") as File:
        Lines = File.readlines()

        # readlines() keeps the explicit "/n" character, strip_trail removes this
        batches = strip_trail(my_batches(Lines, files_per_batch))

    return batches

def run_batch(script, batch, particle, local=local):
    comm = "{}{}".format(submit_dir, script)
    # Create string from list of files, i.e. [file_1, file_2, ...] would become 'file_1 file_2 ...'
    # This string is then parsed by the bash script(s) so that it can process each file individually
    batch_str = ' '.join(batch)

    if not local:
        batch_process = subprocess.run([sub_comm, comm, "--batch", batch_str, "--particle", particle])
    else:
        batch_process = subprocess.run([comm, "--batch", batch_str, "--particle", particle])

def path_batches(directory, files_per_batch=10):
    my_paths = [path for path in os.listdir(directory) if ".root" in path]
    my_paths = ["{}{}".format(directory, file) for file in my_paths]

    stripped_batches = strip_trail(my_batches(my_paths, files_per_batch))

    return stripped_batches

def launch_jobs(phot_files, el_files, queue=queue, proxy=proxy, machine=machine):
    if not os.path.exists(phot_out_path):
        # The setup script will create all of the out directories, so if the photon directory isn't there, neither should the others
        setup_process = subprocess.run(["{}{}setup.sh".format(working_dir,submit_dir)], shell=True)

    # Save full paths to ntuple files and break them into batches (size <=10 files each by default)
    phot_batches = setup_batches(phot_files)
    el_batches = setup_batches(el_files)

    print ('Sending {0} photon jobs on {1}'.format(len(phot_batches), queue+'@{}'.format(machine)))
    print ('---------------')

    # Run the skimming step on each batch; the new, skimmed files will be placed in {particle}_out_path/
    # Ran the first batch locally as a test, so starting from second batch
    for batch in phot_batches:
        run_batch("t3skim.sh", batch, "photon")

    print ('Sending {0} electron jobs on {1}'.format(len(el_batches), queue+'@{}'.format(machine)))
    print ('===============')

    for batch in el_batches:
        run_batch("t3skim.sh", batch, "electron")

    skimmed_phot_batches = path_batches(phot_out_path)
    skimmed_el_batches = path_batches(el_out_path)

    # Create matching directories
    if not os.path.exists(phot_match_out):
        os.makedirs(phot_match_out)
    if not os.path.exists(el_match_out):
        os.makedirs(el_match_out)

    # Run the matching step on each (skimmed) batch
        for batch in skimmed_phot_batches:
            run_batch("match.sh", batch, "photon")

        for batch in skimmed_el_batches:
            run_batch("match.sh", batch, "electron")

    # It's unclear if they will try to run the matching step before the files exist, so this block is written just in case
    ##########################################################################################################################
    ''' while not os.path.exists(phot_match_out+'skim_photon_ntuple_1.root'):
        time.sleep(1)

    if os.path.exists(phot_match_out+'skim_photon_ntuple_1.root'):
        # Run the matching step on each (skimmed) batch
        for batch in skimmed_phot_batches:
            run_batch("match.sh", batch, "photon")

        for batch in skimmed_el_batches:
            run_batch("match.sh", batch, "electron")

        matched_phots = [path for path in os.listdir(phot_match_out)]
        matched_els = [path for path in os.listdir(el_match_out)]'''

    ##########################################################################################################################
    matched_phots = [path for path in os.listdir(phot_match_out) if ".root" in path]
    matched_els = [path for path in os.listdir(el_match_out) if ".root" in path]

    # While the skimming and matching step are broken into batches, i.e. original_list = [list_1=[file_1,file_2,...], list_2=[file_i, file_i+1, ...], ...]
    # The combine step will assume the "batch" is the entire list
    run_batch("combine.sh",matched_phots,"photon")
    run_batch("comine.sh",matched_els,"electron")

if __name__=='__main__':
    launch_jobs(phot_files=phot_files, el_files=el_files)