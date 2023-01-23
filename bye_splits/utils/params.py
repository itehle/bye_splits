# coding: utf-8

_all_ = [ ]

import os
from os import path as op
from pathlib import Path
import sys

parent_dir = os.path.abspath(__file__ + 3 * '/..')
sys.path.insert(0, parent_dir)

from bye_splits.utils import common

import numpy as np
from glob import glob
import functools
import operator
import re

import warnings
import argparse
from argparse import ArgumentParser, RawTextHelpFormatter
from subprocess import Popen, PIPE
import pickle

# Variables

particle = 'electron'
NbinsRz = 42
NbinsPhi = 216
MinROverZ = 0.076
MaxROverZ = 0.58
MinPhi = -np.pi
MaxPhi = +np.pi
DataFolder = 'data/new_algos'
assert DataFolder in ('data/new_algos', 'data/tc_shift_studies')

# Dictionaries

base_kw = {
    'NbinsRz': NbinsRz,
    'NbinsPhi': NbinsPhi,
    'MinROverZ': MinROverZ,
    'MaxROverZ': MaxROverZ,
    'MinPhi': MinPhi,
    'MaxPhi': MaxPhi,
    'RzBinEdges': np.linspace( MinROverZ, MaxROverZ, num=NbinsRz+1 ),
    'PhiBinEdges': np.linspace( MinPhi, MaxPhi, num=NbinsPhi+1 ),

    'LayerEdges': [0,42],
    'IsHCAL': False,

    'DataFolder': Path(DataFolder),
    'FesAlgos': ['ThresholdDummyHistomaxnoareath20'],
    'BasePath': Path(__file__).parents[2] / DataFolder,
    'OutPath': Path(__file__).parents[2] / 'out',

    'RzBinEdges': np.linspace( MinROverZ, MaxROverZ, num=NbinsRz+1 ),
    'PhiBinEdges': np.linspace( MinPhi, MaxPhi, num=NbinsPhi+1 ),

    'Placeholder': np.nan,
}

# Functions
############################################################################################################################################

def set_dictionary(adict):
    adict.update(base_kw)
    return adict

if len(base_kw['FesAlgos'])!=1:
    raise ValueError('The event number in the cluster task'
                     ' assumes there is only on algo.\n'
                     'The script must be adapted.')

# Make dictionary of coefficients
threshold = 0.05
delta_r_coefs = (0.0,threshold,50)

coefs = [(coef,0)*52 for coef in np.linspace(delta_r_coefs[0], delta_r_coefs[1], delta_r_coefs[2])]
coef_dict = {}
for i,coef in enumerate(coefs):
    coef_key = 'coef_'+str(i)
    coef_dict[coef_key] = coef

ntuple_templates = {'photon': 'Floatingpoint{fe}Genclustersntuple/HGCalTriggerNtuple','pion':'hgcalTriggerNtuplizer/HGCalTriggerNtuple'}
algo_trees = {}
for fe in base_kw['FesAlgos']:
    inner_trees = {}
    for key, val in ntuple_templates.items():
        inner_trees[key] = val.format(fe=fe)
    algo_trees[fe] = inner_trees

def transform(nested_list):
    regular_list=[]
    for ele in nested_list:
        if type(ele) is list:
            regular_list.append(ele)
        else:
            regular_list.append([ele])
    return regular_list


def create_out_names(files,trees):
    output_file_names = {}
    for key in files.keys():
        if isinstance(files[key], str):
            files[key] = [files[key]]
        tree = trees[key]
        #breakpoint()
        output_file_names[key] = ['gen_cl3d_tc_{}_{}_with_pt'.format(base_kw['FesAlgos'][0],re.split('.root|/',file)[-2]) for file in files[key]]
    return output_file_names

files = {'photon': '/data_CMS/cms/alves/L1HGCAL/photon_0PU_truncation_hadd.root', 'pion': glob('/data_CMS_upgrade/sauvan/HGCAL/2210_Ehle_clustering-studies/SinglePion_PT0to200/PionGun_Pt0_200_PU0_HLTSummer20ReRECOMiniAOD_2210_clustering-study_v3-29-1/221018_121053/ntuple*.root')}
gen_trees = {'photon': 'FloatingpointThresholdDummyHistomaxnoareath20Genclustersntuple/HGCalTriggerNtuple', 'pion':'hgcalTriggerNtuplizer/HGCalTriggerNtuple'}

pile_up = True
get_pu_files = False
if pile_up:
    pu_samples = ['DoubleElectron_FlatPt-1To100', 'DoublePhoton_FlatPt-1To100', 'SinglePion_PT0to200']
    if get_pu_files:
        #Fill files dictionary with path to files on /dpm...
        files = {'electron': None, 'photon': None, 'pion': None}
        common.point_to_root_file(pu_samples, files)
        outfile = 'dpm_file_paths.pkl'
        with open(outfile, 'wb') as f:
            pickle.dump(files, f)
    else:
        pu_base = '/data_CMS/cms/ehle/L1HGCAL/skim_'
        name_ext = '200PU_bc_stc_hadd.root'
        files = {'photon': pu_base+'photon'+name_ext, 'electron': pu_base+'electron'+name_ext, 'pion': pu_base+'pion'+name_ext}
        infile = files[particle]

    gen_trees = {'electron': 'FloatingpointMixedbcstcrealsig4DummyHistomaxxydr015GenmatchGenclustersntuple/HGCalTriggerNtuple',
                 'photon':   'FloatingpointMixedbcstcrealsig4DummyHistomaxxydr015GenmatchGenclustersntuple/HGCalTriggerNtuple',
                 'pion':     'FloatingpointMixedbcstcrealsig4DummyHistomaxxydr015GenmatchGenclustersntuple/HGCalTriggerNtuple'}

    algo_trees = {'Mixedbcstcrealsig4DummyHistomaxxydr015Genmatch': gen_trees}

############################################################################################################################################

match_kw = set_dictionary(
    { 'Files': files,
      'GenTrees': gen_trees,
      'AlgoTrees': algo_trees,
      'File': None, # The following four values are chosen from their respective dicts in the matching process
      'GenTree': None,
      'AlgoTree': None,
      'OutFile': None,
      'BestMatch': False,
      'ReachedEE': 2, #0 converted photons; 1: photons that missed HGCAL; 2: photons that hit HGCAL
      'CoeffAlgos': coef_dict,
      'Threshold': threshold}
)
# fill task
file_name_dict = dict.fromkeys(files.keys(), None)
for key in file_name_dict:
    file_name_dict[key] = ["summ_PU200_{}.hdf5".format(key)]

fill_kw = set_dictionary(
    {#'FillInFiles' : create_out_names(files, match_kw['GenTrees']),
     'FillInFiles' : file_name_dict,
     'FillIn'      : None, # To be chosen during the fill process
     'FillOut'     : 'fill',
     'FillOutComp' : 'fill_comp',
     'FillOutPlot' : 'fill_plot' }
     )

# optimization task
opt_kw = set_dictionary(
    { 'Epochs': 99999,
      'KernelSize': 10,
      'WindowSize': 3,
      'InFile': None,
      'OptIn': 'triggergeom_condensed', #Needs to be adjusted because this will change for each starting file
      'OptEnResOut': 'opt_enres',
      'OptPosResOut': 'opt_posres',
      'OptCSVOut': 'stats',
      'FillOutPlot': fill_kw['FillOutPlot'],
      'Pretrained': False,
    }
)

# smooth task
smooth_kw = set_dictionary(
    { #copied from L1Trigger/L1THGCal/python/hgcalBackEndLayer2Producer_cfi.py
        'BinSums': (13,               # 0
                    11, 11, 11,       # 1 - 3
                    9, 9, 9,          # 4 - 6
                    7, 7, 7, 7, 7, 7,  # 7 - 12
                    5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,  # 13 - 27
                    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3  # 28 - 41
                    ),
        'SeedsNormByArea': False,
        'AreaPerTriggerCell': 4.91E-05,
        'SmoothIn': fill_kw['FillOut'],
        'SmoothOut': 'smooth' }
    )

# seed task
seed_kw = set_dictionary(
    { 'SeedIn': smooth_kw['SmoothOut'],
      'SeedOut': 'seed',
      'histoThreshold': 20.,
      'WindowPhiDim': 1}
    )

# cluster task
cluster_kw = set_dictionary(
    { 'ClusterInTC': fill_kw['FillOut'],
      'ClusterInSeeds': seed_kw['SeedOut'],
      'ClusterOutPlot': 'cluster_plot',
      'ClusterOutValidation': 'cluster_validation',
      'CoeffA': ( (0.015,)*7 + (0.020,)*7 + (0.030,)*7 + (0.040,)*7 + #EM
                  (0.040,)*6 + (0.050,)*6 + # FH
                  (0.050,)*12 ), # BH
      'CoeffB': 0,
      'MidRadius': 2.3,
      'PtC3dThreshold': 0.5,
      'ForEnergy': False,
      'EnergyOut': 'cluster_energy',
      'GenPart': fill_kw['FillIn']}
)

# validation task
validation_kw = set_dictionary(
    { 'ClusterOutValidation': cluster_kw['ClusterOutValidation'],
      'FillOutComp' : fill_kw['FillOutComp'],
      'FillOut': fill_kw['FillOut'] }
)

# energy task
energy_kw = set_dictionary(
    { 'ClusterIn': cluster_kw['ClusterOutValidation'],
      'Coeff': cluster_kw['CoeffA'],
      'ReInit': False, # If true, ../scripts/en_per_deltaR.py will create an .hdf5 file containing energy info.
      'Coeffs': delta_r_coefs, #tuple containing (coeff_start, coeff_end, num_coeffs)
      'EnergyIn': cluster_kw['EnergyOut'],
      'EnergyOut': 'energy_out',
      'EnergyPlot': 'plots/energy_plot',
      'BestMatch': True,
      'MatchFile': False,
      'MakePlot': True}
)

disconnectedTriggerLayers = [
    2,
    4,
    6,
    8,
    10,
    12,
    14,
    16,
    18,
    20,
    22,
    24,
    26,
    28
]
