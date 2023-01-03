#!/usr/bin/env python
import os
import subprocess

# Specify t3 machine and proxy certificate
machine = "llrt3.in2p3.fr"
proxy = "~/.t3/proxy.cert"
queue = "short"

working_dir = "/grid_mnt/vol_home/llr/cms/ehle/git/bye_splits_new/"

# Relative path to submit scripts
submit_dir = "bye_splits/production/submit_scripts/"

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

# This specific command is repeated enough times to write it as a function
def full_command(script, batch, particle):
    return "{0} {1}{2}{3} --batch {4} --particle {5}".format(sub_comm, working_dir, submit_dir, script, batch, particle)

def launch_jobs(phot_files, el_files, queue=queue, proxy=proxy, machine=machine):
    if not os.path.exists(phot_out_path):
        print(subprocess.run(["{}{}setup.sh".format(working_dir,submit_dir), "arguments"], shell=True))

    # Save full paths to ntuple files and break them into batches of size <=10 files each
    with open(phot_files, "r") as Photon, open(el_files, "r") as Electron:
        Phot_Lines = Photon.readlines()
        El_Lines = Electron.readlines()

        phot_batches = strip_trail(my_batches(Phot_Lines, 10))
        el_batches = strip_trail(my_batches(El_Lines, 10))

    # Run the skimming step on each batch; the new, skimmed files will be placed in {particle}_out_path/
    for batch in phot_batches:
        skim_phots = full_command("skim.sh", batch, "photon")
        print(subprocess.run([skim_phots, "arguments"], shell=True))

    for batch in el_batches:
        skim_els = full_command("skim.sh", batch, "electron")
        print(subprocess.run([skim_els, "arguments"], shell=True))

    skimmed_phots = [path for path in os.listdir(phot_out_path) if ".root" in path]
    skimmed_phots = ["{}{}".format(phot_out_path, file) for file in skimmed_phots]

    skimmed_els = [path for path in os.listdir(el_out_path) if ".root" in path]
    skimmed_els = ["{}{}".format(el_out_path, file) for file in skimmed_els]

    skimmed_phot_batches = strip_trail(my_batches(skimmed_phots, 10))
    skimmed_el_batches = strip_trail(my_batches(skimmed_els, 10))

    # Run the matching step on each (skimmed) batch
    for batch in skimmed_phot_batches:
        match_phots = full_command("match.sh", batch, "photon")
        print(subprocess.run([match_phots, "arguments"], shell=True))

    for batch in skimmed_el_batches:
        match_els = full_command("match.sh", batch, "electron")
        print(subprocess.run([match_els, "arguments"], shell=True))

    matched_phots = [path for path in os.listdir(phot_match_out)]
    matched_els = [path for path in os.listdir(el_match_out)]

    # Initialize command for combining skimmed, matched root files
    phot_hadd_comm="hadd -k -j {}photon_skim_match_hadd.root".format(phot_match_out)
    el_hadd_comm="hadd -k -j {}electron_skim_match_hadd.root".format(el_match_out)

    # Each file is appended to the command before it is called, so all are combined at once
    for file in matched_phots:
        phot_hadd_comm += phot_match_out + file
    print(subprocess.run([phot_hadd_comm, "arguments"], shell=True))

    for file in matched_els:
        el_hadd_comm += el_match_out + file
    print(subprocess.run([el_hadd_comm, "arguments"], shell=True))

if __name__=='__main__':
    launch_jobs(phot_files=phot_files, el_files=el_files)