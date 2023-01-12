#!/usr/bin/env python
import os
import subprocess

# Specify t3 machine and proxy certificate
machine = "llrt3.in2p3.fr"
proxy = "~/.t3/proxy.cert"
queue = "short"

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

phot_files = "{}photon_ntuples.txt".format(phot_out_path)
el_files = "{}electron_ntuples.txt".format(el_out_path)

def my_batches(files, files_per_batch):
    return [files[i:i + files_per_batch] for i in range(0, len(files), files_per_batch)]

def strip_trail(batches):
    return [[file.rstrip() for file in batch] for batch in batches]

def setup_batches(files, files_per_batch=10):
    with open(files, "r") as File:
        Lines = File.readlines()

        # readlines() keeps the explicit /n character, strip_trail removes this
        batches = strip_trail(my_batches(Lines, files_per_batch))

    return batches

def run_batch(script, batch, particle):
    comm = "{}{}".format(submit_dir, script)
    args = lambda batch, part: "--batch {} --particle {}".format(batch, part)

    print(subprocess.run([comm, args(batch, particle)], shell=True))

def path_batches(directory, files_per_batch=10):
    my_paths = [path for path in os.listdir(directory) if ".root" in path]
    my_paths = ["{}{}".format(directory, file) for file in my_paths]

    stripped_batches = strip_trail(my_batches(my_paths, files_per_batch))

    return stripped_batches

def launch_jobs(phot_files, el_files, queue=queue, proxy=proxy, machine=machine):
    if not os.path.exists(phot_out_path):
        # The setup script will create all of the out directories, so if the photon directory isn't there, neither should the others
        print(subprocess.run(["{}{}setup.sh".format(working_dir,submit_dir)], shell=True))

    # Save full paths to ntuple files and break them into batches (size <=10 files each by default)
    phot_batches = setup_batches(phot_files)
    el_batches = setup_batches(el_files)

    # Run the skimming step on each batch; the new, skimmed files will be placed in {particle}_out_path/
    for batch in phot_batches:
        run_batch("skim.sh", batch, "photon")

    for batch in el_batches:
        run_batch("skim.sh", batch, "electron")

    skimmed_phot_batches = path_batches(phot_out_path)
    skimmed_el_batches = path_batches(el_out_path)

    # Create matching directo
    if not os.path.exists(phot_match_out):
        os.makedirs(phot_match_out)
    if not os.path.exists(el_match_out):
        os.makedirs(el_match_out)

    # Run the matching step on each (skimmed) batch
    for batch in skimmed_phot_batches:
        run_batch("match.sh", batch, "photon")

    for batch in skimmed_el_batches:
        run_batch("match.sh", batch, "electron")

    matched_phots = [path for path in os.listdir(phot_match_out)]
    matched_els = [path for path in os.listdir(el_match_out)]

    # Initialize command for combining skimmed, matched root files
    phot_hadd_comm="hadd -k -j {}photon_skim_match_hadd.root {}".format(phot_match_out, matched_phots[0])
    el_hadd_comm="hadd -k -j {}electron_skim_match_hadd.root {}".format(el_match_out, matched_els[0])

    # Each file is appended to the command before it is called, so all are combined at once
    for file in matched_phots[1:]:
        phot_hadd_comm += " " + phot_match_out + file
    print(subprocess.run([phot_hadd_comm], shell=True))

    for file in matched_els[1:]:
        el_hadd_comm += " " + el_match_out + file
    print(subprocess.run([el_hadd_comm], shell=True))

if __name__=='__main__':
    launch_jobs(phot_files=phot_files, el_files=el_files)