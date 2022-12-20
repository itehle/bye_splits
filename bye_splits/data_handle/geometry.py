# coding: utf-8

_all_ = [ 'GeometryData' ]

import os
from pathlib import Path
import sys
parent_dir = os.path.abspath(__file__ + 2 * '/..')
sys.path.insert(0, parent_dir)

import yaml
import uproot as up
import pandas as pd

from utils import params, common
from data_handle.base import BaseData

class GeometryData(BaseData):
    def __init__(self, inname=''):
        super().__init__(inname, 'geom')
        self.dname = 'tc'
        with open(params.viz_kw['CfgEventPath'], 'r') as afile:
            cfg = yaml.safe_load(afile)
            self.var = common.dot_dict(cfg['varGeometry'])

        self.readvars = list(self.var.values())
        self.readvars.remove('waferv_shift')
        self.readvars.remove('color')

    def provide(self):
        if not os.path.exists(self.outpath):
            self.store()
        with pd.HDFStore(self.outpath, mode='r') as s:
            res = s[self.dname]
        return res

    def select(self):
        with up.open(self.inpath) as f:
            tree = f[ os.path.join('hgcaltriggergeomtester', 'TreeTriggerCells') ]
            #print(tree.show())
            data = tree.arrays(self.readvars)
            sel = (data.zside==1) & (data.subdet==1)
            fields = data[sel].fields
            for v in (self.var.side, self.var.subd):
                fields.remove(v)
            data = data[sel][fields]
            breakpoint()
            data = data.loc[~data.layer.isin(params.disconnectedTriggerLayers)]
            #data = data.drop_duplicates(subset=[self.var.cu, self.var.cv, self.var.l])
            data[self.var.wv] = data.waferv
            data[self.var.wvs] = -1 * data.waferv
            data[self.var.c] = "#8a2be2"
            
        return data

    def store(self):
        data = self.select()
        ak.to_parquet(data, self.tag + '.parquet')
