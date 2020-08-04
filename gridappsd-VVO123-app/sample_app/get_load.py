# @author: rjha
# """
import json
import numpy as np
import math
import networkx as nx 

class PowerData(object):
    """
    WSU VVO, Get load data from feeder
    """
    # def __init__(self, msr_mrids_load, sim_output, LineData):

    def __init__(self, msr_mrids_load, sim_output, obj_msr_inv, LineData, nodev):
        self.meas_load = msr_mrids_load
        self.output = sim_output        
        self.LineData = LineData
        self.obj_msr_inv = obj_msr_inv
        self.nodev = nodev
        
        
    def demand(self):
        data1 = self.meas_load
        data2 = self.output
        data3 = self.obj_msr_inv 
        datanodev = self.nodev
      
        meas_value = data2['message']['measurements']     
        timestamp = data2["message"] ["timestamp"]

        datav = datanodev['data']
        # print(data2)
        # print(data3)

       
        data1 = data1['data']
        ds = [d for d in data1 if d['type'] != 'PNV']

        ### for the VR and C control
        # Demand = []
        # for d1 in ds:         
        #     if d1['measid'] in meas_value:
        #         v = d1['measid']
        #         pq = meas_value[v]
        #         # Check phase of load in 123 node based on last letter
        #         loadbus = d1['bus']
        #         phase = loadbus[-1].upper()
        #         phi = (pq['angle'])*math.pi/180
        #         message = dict(bus = d1['bus'],
        #                         VA = [pq['magnitude'], pq['angle']],
        #                         Phase = phase,
        #                         kW = 0.001 * pq['magnitude']*np.cos(phi),
        #                         kVaR = 0.001* pq['magnitude']*np.sin(phi),
        #                         kW_pv = 0.,
        #                         kVAr_pv = 0,
        #                         kVA_pv = 0,
        #                         kVaR_C = 0.)
        #         Demand.append(message) 

        ### end of VR and C control

        Demand = []
        primloadnode = ['35', '47', '48', '65', '76']

        for d1 in ds:         
            if d1['measid'] in meas_value:
                v = d1['measid']
                pq = meas_value[v]
                # print(pq)
                # Check phase of load in secondary of the 123 node based on last letter
                loadbus = d1['bus']
                # print(loadbus)
                # if loadbus == '76':
                #     phase = d1['phases']     
                #     print(phase)
                # elif loadbus == '65':
                #     phase = d1['phases']     
                #     print(phase)
                # elif loadbus == '48':
                #     phase = d1['phases']     
                #     print(phase)
                # elif loadbus == '47':
                #     phase = d1['phases']     
                #     print(phase)
                # elif loadbus == '35':
                #     phase = d1['phases']     
                #     print(phase)
                # else:
                #     phase = loadbus[-1].upper()
                # if loadbus != '35' or '47' or '48' or '65' or '76':
                #     phase = loadbus[-1].upper()
                if d1['bus'] == '35' or d1['bus'] == '47' or d1['bus'] == '48' or d1['bus'] == '65' or d1['bus'] == '76':
                    phase = d1['phases']
                else:   
                    phase = loadbus[-1].upper()    
                #     print(phase)
                phi = (pq['angle'])*math.pi/180
                message = dict(bus = d1['bus'],
                                VA = [pq['magnitude'], pq['angle']],
                                Phase = phase,
                                kW = 0.001 * pq['magnitude']*np.cos(phi),
                                kVaR = 0.001* pq['magnitude']*np.sin(phi),
                                kW_pv = 0.,
                                kVAr_pv = 0,
                                kVA_pv = 0,
                                kVaR_C = 0.)
                Demand.append(message)    

        # print(Demand)
        # print(r)

        Demand_update = {}
        for i, row in enumerate(Demand):
            if row['bus'] not in primloadnode:
            # if row['bus']  !=  '47' and row['phase']  ==  'A' or row['bus']  !=  '47' and row['phase']  ==  'B' or row['bus'] != '48' or row['bus'] != '65' or row['bus'] != '76':
                if row['bus'] in Demand_update.keys():
                    Demand_update[row['bus']]['kW'] += row['kW']
                    Demand_update[row['bus']]['kVaR'] += row['kVaR']
                    Demand_update[row['bus']]['kW_pv'] += row['kW_pv']
                    Demand_update[row['bus']]['kVAr_pv'] += row['kVAr_pv']
                    Demand_update[row['bus']]['kVA_pv'] += row['kVAr_pv']
                    Demand_update[row['bus']]['kVaR_C'] += row['kVaR_C']
                else:
                    Demand_update[row['bus']] = row

            else:
                Demand_update[row['bus']+'_'+str(i)] = row


        Demand = []
        for d in Demand_update.items():
            message = dict(bus = d[1]['bus'],
                                VA = d[1]['VA'],
                                Phase = d[1]['Phase'],
                                kW = d[1]['kW'],
                                kVaR = d[1]['kVaR'],
                                kW_pv =d[1]['kW_pv'],
                                kVAr_pv =d[1]['kVAr_pv'],
                                kVA_pv = d[1]['kVA_pv'],
                                kVaR_C = d[1]['kVaR_C'])

            Demand.append(message) 

        # print(Demand_update)
        # print(type(Demand_update))
        # print(r)
        # data3 = data3['data']
        # dspv = [d for d in data3 if d['type'] != 'PNV']


        # print(Demand)
        # print(r)

        pv_out = []
        for d1 in data3:
            if d1['measid'] in meas_value:
                v = d1['measid']
                # print(d1)
                pq = meas_value[v]
                # print(pq)
                loadbus = d1['bus']
                phase = d1['phases']
                # phase = loadbus[-1].upper()
                phi = (pq['angle'])*math.pi/180
                # print(d1)
                # print(r)
                message = dict(bus = 's'+d1['bus']+phase.lower(),
                                VA = [pq['magnitude'], pq['angle']],
                                Phase = phase,
                                kW_pv = 0.001 * pq['magnitude']*np.cos(phi),
                                kVAr_pv = 0.001* pq['magnitude']*np.sin(phi),
                                kVA_pv = 1*d1['Srated'])
                # print(message)
                pv_out.append(message)    
        

        with open('pvoutput.json', 'w') as json_file:
            json.dump(pv_out, json_file)

        for p in pv_out:
            pv_bus = p['bus']
            # print(pv_bus)
            # for d in Demand_update.items():
                # print(d[1]['bus'])
                # print(R)
                # if pv_bus == d[1]['bus']:
            for d in Demand:
                if pv_bus == d['bus']:
                    # d[1]['kW_pv'] = p['kW_pv']
                    # d[1]['kVAr_pv'] = p['kVAr_pv']
                    # d[1]['kVA_pv'] = p['kVA_pv']
                    d['kW_pv'] = p['kW_pv']
                    d['kVAr_pv'] = p['kVAr_pv']
                    d['kVA_pv'] = p['kVA_pv']


        node = ['35','47','48', '65', '76']
        for d in Demand:
            if d['bus'] not in node:
                d['bus'] = repr(d['bus'])[2:-2]
                   
        # print(Demand)
        # print(r)

        sP = 0
        sQ = 0
        sPVp = 0
        for d in Demand:
            sP += d['kW']
            sQ += d['kVaR']
            sPVp += d['kW_pv']
                        
        print('The total real and reactive demand and PV active power  is:', sP, sQ, sPVp)

        cap_bus_ind = ['83', '88' , '90' , '92' ]
        cap_bus_phase = ['C','A', 'B', 'C']
        cap_kvar_value = [200, 50, 50, 50]
        capacitor = []
        for k in range(4):
            message = dict(bus = cap_bus_ind[k],
                            Phase = cap_bus_phase[k],
                            kVaR_C = cap_kvar_value[k])
            capacitor.append(message)


        for p in capacitor:
            for d in Demand:
                if p['bus'] == d['bus']:
                    d['kVaR_C'] = p['kVaR_C']
                    d['Phase'] = p['Phase']
                    # d['kVAr_pv'] = p['kVAr_pv']
                    # d['kVA_pv'] = p['kVA_pv']

        cap_bus_ind1 = ['83', '83']
        cap_bus_phase1 = ['A', 'B']
        cap_kvar_value1 = [200, 200]

        for i in range(2):
            cap1 = dict(
                bus = cap_bus_ind1[i],
                Phase = cap_bus_phase1[i],
                kW = 0,
                kVaR = 0,
                kW_pv = 0,
                kVAr_pv = 0,
                kVA_pv = 0,
                kVaR_C = cap_kvar_value1[i])
            Demand.append(cap1) 



        # print(Demand)
        # print(r)
        with open('Demand.json', 'w') as json_file:
            json.dump(Demand, json_file)

        return Demand