#!/usr/bin/env python

# Simple script for testing the launching of bash scripts and job submission on the t3 clusters
import os
import sys
from datetime import datetime

parent_dir = os.path.abspath(__file__ + 3*'../')
sys.path.insert(0, parent_dir)

import subprocess
import optparse

# Specify t3 machine and proxy certificate
proxy = "~/.t3/proxy.cert"
queue = "short"

# Submit command
sub_comm = ["/opt/exp_soft/cms/t3/t3submit"]

home_dir = "/grid_mnt/vol_home/llr/cms/ehle/"

work_dir = "{}git/bye_splits_final/".format(home_dir)
submit_dir = "{}bye_splits/production/submit_scripts/".format(work_dir)

data_dir = "/data_CMS/cms/ehle/L1HGCAL/"

phot_out_path="{}photon/".format(data_dir)
el_out_path="{}electron/".format(data_dir)

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

def prepare_configs(batches, data_dir):
    for i in range(len(batches)):
        config_file_name = '{0}configs/{1}_cfg.py'.format(data_dir, i)
        if os.path.exists(config_file_name):
            os.remove(config_file_name)
        with open(config_file_name, 'w') as param:
            print('files={}\n'.format(batches[i]), file=param)
            print('output_file_name="{0}{1}.txt"'.format(data_dir, i), file=param)

def prepare_submit(particle, batches, data_dir):
    for i, batch in enumerate(batches):
        batch_str = ' '.join(batch)
        sub_file_name = '{0}jobs/skim_match_{1}.sub'.format(data_dir, i)
        config_file_name = '{0}_cfg.py'.format(i)
        if os.path.exists(sub_file_name):
            os.remove(sub_file_name)
        with open(sub_file_name, 'w') as sub_file:
            print('#! /bin/bash', file=sub_file)
            print('Universe=grid', file=sub_file)
            print('uname -a', file=sub_file)
            print('python --version', file=sub_file)
            print('which python', file=sub_file)
            print('cd', data_dir+'logs', file=sub_file)
            print('conda init bash',file=sub_file)
            print('bash -c source {}.bashrc'.format(home_dir),file=sub_file)
            print('conda activate ByeSplitEnv',file=sub_file)
            print("export PYTHONPATH=/home/llr/cms/ehle/anaconda3/envs/ByeSplitEnv/bin/python", file=sub_file)
            print('getenv=true', file=sub_file)
            print('T3Queue=${}'.format(queue), file=sub_file)
            print('WNTag=el7', file=sub_file)
            print("export X509_CERT_FILE={}".format(proxy), file=sub_file)
            print("bash {0}skim_match.sh --batch '{1}' --particle {2} &> skim_match_{3}.log".format(submit_dir, batch_str, particle, i), file=sub_file)

        st=os.stat(sub_file_name)
        os.chmod(sub_file_name, st.st_mode | 0o744)

def prepare_jobs(param, batches_phot, batches_elec, batches_pion):
    files_photons = param.files_photons
    files_electrons = param.files_electrons
    files_pions = param.files_pions

    data_dir = param.data_dir

    phot_dir=param.phot_out_path
    elec_dir=param.el_out_path
    pion_dir=param.pion_out_path

    if not os.path.exists(phot_dir+'configs'):
        os.makedirs(phot_dir+'configs')
        os.makedirs(phot_dir+'jobs')
        os.makedirs(phot_dir+'logs')

        os.makedirs(elec_dir+'configs')
        os.makedirs(elec_dir+'jobs')
        os.makedirs(elec_dir+'logs')

    if len(files_pions)>0:
        os.makedirs(pion_dir+'configs')
        os.makedirs(pion_dir+'jobs')
        os.makedirs(pion_dir+'logs')

    prepare_configs(batches_phot, phot_dir)
    prepare_submit('photon', batches_phot, phot_dir)

    prepare_configs(batches_elec, elec_dir)
    prepare_submit('electron', batches_elec, elec_dir)
    if len(files_pions)>0:
        prepare_configs(batches_pion, pion_dir)
        prepare_submit('pion', batches_pion, pion_dir)
    
    return phot_dir, elec_dir, pion_dir

def launch_jobs(particle, out_dir, batches, queue=queue, proxy=proxy, local=True):
    if local==True:
        machine='local'
    else:
        machine = "llrt3.in2p3.fr"

    if not local:
        print ('\nSending {0} {1} jobs on {2}'.format(len(batches), particle, queue+'@{}'.format(machine)))
        print ('===============')
        print("\n")

    for i, batch in enumerate(batches):
        sub_args = []
        if not local:
            sub_args.append("-{}".format(queue))
        sub_file_name = "{0}jobs/skim_match_{1}.sub".format(out_dir, i)
        sub_args.append(sub_file_name)

        if local:
            comm = sub_args
        else:
            comm = sub_comm+sub_args
        print(str(datetime.now()), ' '.join(comm))
        status = subprocess.run(comm)

def main(parameters_file):
    import importlib
    import sys
    sys.path.append(work_dir)
    parameters_file=parameters_file.replace("/",".").replace(".py","")

    parameters=importlib.import_module(parameters_file)
    local = parameters.local
    files_electrons = parameters.files_electrons
    files_photons = parameters.files_photons
    files_pions = parameters.files_pions
    files_per_batch_elec = parameters.files_per_batch_elec
    files_per_batch_phot = parameters.files_per_batch_phot
    files_per_batch_pion = parameters.files_per_batch_pion

    batches_elec = setup_batches(files_electrons, files_per_batch_elec)
    batches_phot = setup_batches(files_photons, files_per_batch_phot)
    batches_pion = []

    if len(files_pions) > 0:
        batches_pion = setup_batches(files_pions, files_per_batch_pion)

    phot_dir, elec_dir, pion_dir = prepare_jobs(parameters, batches_phot, batches_elec, batches_pion)

    launch_jobs('photon', phot_dir, batches_phot, local=local)
    launch_jobs('electron', elec_dir, batches_elec, local=local)

    if len(files_pions) > 0:
        launch_jobs('pion', pion_dir, batches_pion, local=local)

if __name__=='__main__':
    parser = optparse.OptionParser()
    parser.add_option("--cfg", type="string", dest="param_file", help="select the parameter file")
    (opt, args) = parser.parse_args()
    parameters=opt.param_file
    main(parameters)

