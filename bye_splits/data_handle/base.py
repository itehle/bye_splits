# coding: utf-8

_all_ = [ ]

import os
from pathlib import Path
import sys
parent_dir = os.path.abspath(__file__ + 2 * '/..')
sys.path.insert(0, parent_dir)

import abc
import awkward as ak

from utils import params, common

class BaseData(abc.ABC):
    def __init__(self, inname, outname, tag):
        self.inpath = Path('/data_CMS/cms/ehle/L1HGCAL/') / inname
        self.outpath = Path('/data_CMS/cms/ehle/L1HGCAL/') / outname
        self.tag = tag
        self.dname = 'tc'
        self.var = common.dot_dict({})
        self.newvar = common.dot_dict({})

    @property
    def variables(self):
        return self.var

    @abc.abstractmethod
    def select(self):
        raise NotImplementedError()
    