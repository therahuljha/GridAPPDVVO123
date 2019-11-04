# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 09:35:36 2018
@author: Shiva
"""

import json

class Topology(object):
    """
    WSU Topoloy Analyzer
    """
   
    def __init__(self, msr_mrids, sim_output):
        self.meas = msr_mrids
        self.output = sim_output

    def top_analyzer(self):               
        data1 = self.meas
        data2 = self.output
        with open('ms_value.json', 'w') as json_file:
            json.dump(data2, json_file)
        with open ('ms_value.json') as f:
            d = json.loads(json.JSONDecoder().decode(f.readlines()[0]))
            data2 = d["message"]["measurements"]

        # Find interested mrids. We are only interested in position of switches
        interested = []
        bus = []
        for d1 in data1['data']:
            if d1['type'] == "Pos":
                interested.append(d1['measid'])
                bus.append(d1['bus'])

        open_sw = []
        for k in range(len(data2)):
            a = data2[k]
            if (a['measurement_mrid']) in interested:
                if a['value'] == 0:
                    open_sw.append(a['measurement_mrid'])

        # Find which LineBreakSwitch is opened
        for d1 in data1['data']:
            if d1['measid'] in open_sw:
                print(d1['bus'])
