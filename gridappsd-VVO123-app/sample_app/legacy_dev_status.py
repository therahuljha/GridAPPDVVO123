# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 11:17:12 2019

@author: spoudel
"""
import json

class LEGACY_DEV(object):
    """
    WSU VVO
    """
    def __init__(self, msr_mrids_cap, msr_mrids_reg, sim_output):
        self.meas_c = msr_mrids_cap
        self.meas_r = msr_mrids_reg
        self.output = sim_output
        
    def cap_(self):
        data1 = self.meas_c

        data2 = self.output
        #data2 = json.loads(data2.replace("\'",""))
        data2 = data2["message"]["measurements"]

        # Find interested mrids. We are only interested in position of Capacitors
        ms_id = []
        eq_id = []
        for d1 in data1['data']: 
            if d1['type'] == "Pos":
                ms_id.append(d1['measid'])
                eq_id.append(d1['eqid'])

        # Store the Capacitor status and location
        store = []
        cap_loc = []
        for k, v in data2.items():
            if (v['measurement_mrid']) in ms_id:
                store.append(v['value'])
                cap_loc.append(v['measurement_mrid'])

        # Find which bus has capacitor
        cap_bus = []
        for d1 in data1['data']: 
            if d1['measid'] in cap_loc:
                cap_bus.append(d1['bus'])

        # print(cap_bus)
        return store

    def reg_(self):
        data1 = self.meas_r

        data2 = self.output
        #data2 = json.loads(data2.replace("\'",""))
        data2 = data2["message"]["measurements"]

        # Find interested mrids. We are only interested in position of Capacitors
        ms_id = []
        eq_id = []
        for d1 in data1['data']: 
            if d1['type'] == "Pos":
                ms_id.append(d1['measid'])
                eq_id.append(d1['eqid'])

        
        # Store the Capacitor status and location
        store = []
        reg_loc = []
        for k, v in data2.items():
            if (v['measurement_mrid']) in ms_id:
                store.append(v['value'])
                reg_loc.append(v['measurement_mrid'])
                # print(v['measurement_mrid'], v['value'])
                
        # Find which bus has reg
        reg_bus = []
        for d1 in data1['data']: 
            if d1['measid'] in reg_loc:
                reg_bus.append(d1['bus'])
        # print(reg_bus)
        return store
        
