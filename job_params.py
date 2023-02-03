home_dir = "/grid_mnt/vol_home/llr/cms/ehle/"

work_dir = "{}git/bye_splits_new/".format(home_dir)
submit_dir = "{}bye_splits/production/submit_scripts/".format(work_dir)

pile_up = "PU0"

local = False
if local:
    data_dir = "/data_CMS/cms/ehle/L1HGCAL/"
else:
    data_dir = "/eos/user/i/iehle/data/{}/".format(pile_up)

phot_out_path="{}photon/".format(data_dir)
el_out_path="{}electron/".format(data_dir)
pion_out_path="{}pion/".format(data_dir)

# The setup script saves the file paths on /dpm to .txt files
phot_files = "{}photon_ntuples.txt".format(phot_out_path)
el_files = "{}electron_ntuples.txt".format(el_out_path)

files_electrons = el_files
files_photons = phot_files
files_pions = []

files_per_batch_elec = 10
files_per_batch_phot = 10
files_per_batch_pion = 10

