import json
import networkx as nx 
import numpy as np
from pulp import *
import math


# start = time.clock()


class WSUVVO123VCQ(object):
    """
    This code is for solving the VVO for  test cases. The planning model is used as
    input and real time load data is required.
    """
    def __init__(self):
        """
        Inputs:
           LinePar
           LoadData
           Graph =  G (V,E)
        """
        pass        
   
    def VVO123(self, Linepar, LoadData):    
        
        # Find Tree and Planning model using Linepar
        G = nx.Graph()
        

        for l in Linepar:
            G.add_edge(l['from_br'], l['to_br'])
        T = list(nx.bfs_tree(G, source = '150').edges())
        Nodes = list(nx.bfs_tree(G, source = '150').nodes())
        
       

        # parameters
        nNodes = G.number_of_nodes()
        nEdges = G.number_of_edges() 
        fr, to = zip(*T)
        fr = list(fr)
        to = list(to) 
        bigM = 15000   
        CVRP = 1.0
        CVRQ = 1.0
        # CVRP = 0.4
        # CVRQ = 0.4
        tap_r1 = 33
        loadmult = 1
        bkva = 1000.0
            
        # Different variables for optimization function
        si = LpVariable.dicts("s_i", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')
        vi = LpVariable.dicts("v_i", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')
        xij = LpVariable.dicts("x_ij", ((i) for i in range(nEdges) ), lowBound=0, upBound=1, cat='Binary')
        Pija = LpVariable.dicts("xPa", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Pijb = LpVariable.dicts("xPb", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Pijc = LpVariable.dicts("xPc", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Qija = LpVariable.dicts("xQa", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Qijb = LpVariable.dicts("xQb", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Qijc = LpVariable.dicts("xQc", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Via = LpVariable.dicts("xVa", ((i) for i in range(nNodes) ), lowBound=0.9025, upBound=1.1025, cat='Continous')
        Vib = LpVariable.dicts("xVb", ((i) for i in range(nNodes) ), lowBound=0.9025, upBound=1.1025, cat='Continous')
        Vic = LpVariable.dicts("xVc", ((i) for i in range(nNodes) ), lowBound=0.9025, upBound=1.1025, cat='Continous')
        QPVa = LpVariable.dicts("xQPVa", ((i) for i in range(nNodes) ), lowBound=1, upBound=1, cat='Continous')
        QPVb = LpVariable.dicts("xQPVb", ((i) for i in range(nNodes) ), lowBound=1, upBound=1, cat='Continous')
        QPVc = LpVariable.dicts("xQPVc", ((i) for i in range(nNodes) ), lowBound=1, upBound=1, cat='Continous')
        tapi1 = LpVariable.dicts("xtap1", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi2 = LpVariable.dicts("xtap2", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi3 = LpVariable.dicts("xtap3", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi4 = LpVariable.dicts("xtap4", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi5 = LpVariable.dicts("xtap5", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi6 = LpVariable.dicts("xtap6", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        swia = LpVariable.dicts("xswa", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')
        swib = LpVariable.dicts("xswb", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')
        swic = LpVariable.dicts("xswc", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')


    
        # Optimization problem objective definitions
        # Minimize the power flow from feeder        
             
        prob = LpProblem("CVRSW",LpMinimize)
        prob += Pija[0]+Pijb[0]+Pijc[0] 
        # prob += 0


        # Constraints (v_i==1)
        for k in range(nNodes):
            prob += vi[k] == 1
        
        # Constraints (s_i<=1)
        for k in range(nNodes):
            prob += si[k] == 1
        

        # Real power flow equation for Phase A, B, and C
        #Phase A   
        for i in range(nEdges):    
            node = to[i]     
            indb = Nodes.index(node)
            ch = [n for n, e in enumerate(fr) if e == node]
            pa = [n for n, e in enumerate(to) if e == node]
            M = range(len(ch))
            N = range(len(pa))
            demandP = 0.
            demandQ = 0.
            demandQc = 0.
            demandPpv = 0.
            demandSpv = 0.
            for d in LoadData:
                if node == d['bus'] and d['Phase'] == 'A':
                    demandP += d['kW']/bkva
                    demandQ += d['kVaR']/bkva
                    demandQc += d['kVaR_C']/bkva
                    demandPpv += d['kW_pv']/bkva
                    demandSpv += d['kVA_pv']/bkva

            prob += lpSum(Pija[pa[j]] for j in N) - loadmult*(demandP)*(CVRP/2)*Via[indb] == \
                    lpSum(Pija[ch[j]] for j in M) + loadmult*(demandP)*(1-CVRP/2) + demandPpv

            prob += lpSum(Qija[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Via[indb] == \
                    lpSum(Qija[ch[j]] for j in M) + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swia[indb]  

            # prob += lpSum(Qija[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Via[indb] == \
            #         lpSum(Qija[ch[j]] for j in M) + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swia[indb]  + (np.sqrt(demandSpv**2 - demandPpv**2))*QPVa[indb]


        # Phase B
        for i in range(nEdges):    
            node = to[i]     
            indb = Nodes.index(node)
            ch = [n for n, e in enumerate(fr) if e == node]
            pa = [n for n, e in enumerate(to) if e == node]
            M = range(len(ch))
            N = range(len(pa))
            demandP = 0.
            demandQ = 0.
            demandQc = 0.
            demandPpv = 0.
            demandSpv = 0.

            for d in LoadData:
                if node == d['bus'] and d['Phase'] == 'B':
                    demandP += d['kW']/bkva
                    demandQ += d['kVaR']/bkva
                    demandQc += d['kVaR_C']/bkva
                    demandPpv += d['kW_pv']/bkva
                    demandSpv += d['kVA_pv']/bkva

            prob += lpSum(Pijb[pa[j]] for j in N) - loadmult*(demandP)*(CVRP/2)*Vib[indb] == \
                    lpSum(Pijb[ch[j]] for j in M) + loadmult*(demandP)*(1-CVRP/2) + demandPpv

            prob += lpSum(Qijb[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Vib[indb] == \
                    lpSum(Qijb[ch[j]] for j in M)  + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swib[indb] 


            # prob += lpSum(Qijb[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Vib[indb] == \
            #         lpSum(Qijb[ch[j]] for j in M)  + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swib[indb] + (np.sqrt(demandSpv**2 - demandPpv**2))*QPVb[indb]


        # Phase C
        for i in range(nEdges):    
            node = to[i]     
            indb = Nodes.index(node)
            ch = [n for n, e in enumerate(fr) if e == node]
            pa = [n for n, e in enumerate(to) if e == node]
            M = range(len(ch))
            N = range(len(pa))
            demandP = 0.
            demandQ = 0.
            demandQc = 0.
            demandPpv = 0.
            demandSpv = 0. 
            for d in LoadData:
                if node == d['bus'] and d['Phase'] == 'C':
                    demandP += d['kW']/bkva
                    demandQ += d['kVaR']/bkva
                    demandQc += d['kVaR_C']/bkva
                    demandPpv += d['kW_pv']/bkva
                    demandSpv += d['kVA_pv']/bkva

            prob += lpSum(Pijc[pa[j]] for j in N) - loadmult*(demandP)*(CVRP/2)*Vic[indb] == \
                    lpSum(Pijc[ch[j]] for j in M) + loadmult*(demandP)*(1-CVRP/2) + demandPpv
            
            prob += lpSum(Qijb[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Vib[indb] == \
                    lpSum(Qijb[ch[j]] for j in M)  + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swib[indb] 


            # prob += lpSum(Qijc[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Vic[indb] == \
            #         lpSum(Qijc[ch[j]] for j in M)  + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swic[indb] + (np.sqrt(demandSpv**2 - demandPpv**2))*QPVc[indb]


        # Voltage constraints by coupling with switch variable
        base_Z = 2.4**2
        M = 4
        unit = 1.

        ## regulator index
        indr  = [126,127,128]

        # Phase A
        for m, l in enumerate(Linepar):
            k = l['index']
            n1 = l['from_br'] 
            n2 = l['to_br']    
            ind1 = Nodes.index(n1)
            ind2 = Nodes.index(n2)   
            length = l['length']
            Rmatrix =  l['r']
            Xmatrix =  l['x']
            r_aa,x_aa,r_ab,x_ab,r_ac,x_ac = Rmatrix[0], Xmatrix[0], Rmatrix[1], Xmatrix[1], Rmatrix[2], Xmatrix[2]
            if l['is_Switch'] == 0 and l['index'] not in indr:
                prob += Via[ind1]-Via[ind2] - \
                2*r_aa*length/(unit*base_Z*1)*Pija[k]- \
                2*x_aa*length/(unit*base_Z*1)*Qija[k]+ \
                (r_ab+np.sqrt(3)*x_ab)*length/(unit*base_Z*1)*Pijb[k] +\
                (x_ab-np.sqrt(3)*r_ab)*length/(unit*base_Z*1)*Qijb[k] +\
                (r_ac-np.sqrt(3)*x_ac)*length/(unit*base_Z*1)*Pijc[k] +\
                (x_ac+np.sqrt(3)*r_ac)*length/(unit*base_Z*1)*Qijc[k] == 0


        # indr  = [13,38,70]

       # Phase A
        # for m, l in enumerate(Linepar):
        #     k = l['index']
        #     n1 = l['from_br'] 
        #     n2 = l['to_br']    
        #     ind1 = Nodes.index(n1)
        #     ind2 = Nodes.index(n2)   
        #     length = l['length']
        #     Rmatrix =  l['r']
        #     Xmatrix =  l['x']
        #     r_aa,x_aa,r_ab,x_ab,r_ac,x_ac = Rmatrix[4], Xmatrix[4], Rmatrix[1], Xmatrix[1], Rmatrix[6], Xmatrix[6]
        #     # Write voltage constraints
        #     if l['is_Switch'] == 0 and l['index'] not in indr :
        #         prob += Via[ind1]-Via[ind2] - \
        #         2*r_aa*length/(unit*base_Z*1)*Pija[k]- \
        #         2*x_aa*length/(unit*base_Z*1)*Qija[k]+ \
        #         (r_ab+np.sqrt(3)*x_ab)*length/(unit*base_Z*1)*Pijb[k] +\
        #         (x_ab-np.sqrt(3)*r_ab)*length/(unit*base_Z*1)*Qijb[k] +\
        #         (r_ac-np.sqrt(3)*x_ac)*length/(unit*base_Z*1)*Pijc[k] +\
        #         (x_ac+np.sqrt(3)*r_ac)*length/(unit*base_Z*1)*Qijc[k] == 0

        # Phase B
        for m, l in enumerate(Linepar):
            k = l['index']
            n1 = l['from_br'] 
            n2 = l['to_br']    
            ind1 = Nodes.index(n1)
            ind2 = Nodes.index(n2)   
            length = l['length']
            Rmatrix =  l['r']
            Xmatrix =  l['x']
            r_bb,x_bb,r_ba,x_ba,r_bc,x_bc = Rmatrix[4], Xmatrix[4], Rmatrix[3], Xmatrix[3], Rmatrix[5], Xmatrix[5]
            # Write voltage constraints
            if l['is_Switch'] == 0 and l['index'] not in indr :
                prob += Vib[ind1]-Vib[ind2] - \
                2*r_bb*length/(unit*base_Z*1)*Pijb[k]- \
                2*x_bb*length/(unit*base_Z*1)*Qijb[k]+ \
                (r_ba+np.sqrt(3)*x_ba)*length/(unit*base_Z*1)*Pija[k] +\
                (x_ba-np.sqrt(3)*r_ba)*length/(unit*base_Z*1)*Qija[k] +\
                (r_bc-np.sqrt(3)*x_bc)*length/(unit*base_Z*1)*Pijc[k] +\
                (x_bc+np.sqrt(3)*r_bc)*length/(unit*base_Z*1)*Qijc[k] == 0

                

        # Phase C
        for m, l in enumerate(Linepar):
            k = l['index']
            n1 = l['from_br'] 
            n2 = l['to_br']    
            ind1 = Nodes.index(n1)
            ind2 = Nodes.index(n2)   
            length = l['length']
            Rmatrix =  l['r']
            Xmatrix =  l['x']
            r_cc,x_cc,r_ca,x_ca,r_cb,x_cb = Rmatrix[8], Xmatrix[8], Rmatrix[6], Xmatrix[6], Rmatrix[7], Xmatrix[7]
            # Write voltage constraints
            if l['is_Switch'] == 0 and l['index'] not in indr:
                prob += Vic[ind1]-Vic[ind2] - \
                2*r_cc*length/(unit*base_Z*1)*Pijc[k]- \
                2*x_cc*length/(unit*base_Z*1)*Qijc[k]+ \
                (r_ca+np.sqrt(3)*x_ca)*length/(unit*base_Z*1)*Pija[k] +\
                (x_ca-np.sqrt(3)*r_ca)*length/(unit*base_Z*1)*Qija[k] +\
                (r_cb-np.sqrt(3)*x_cb)*length/(unit*base_Z*1)*Pijb[k] +\
                (x_cb+np.sqrt(3)*r_cb)*length/(unit*base_Z*1)*Qijb[k] == 0
                
        
        # Initialize source bus at 1.05 p.u. V^2 = 1.1025
        prob += Via[0] == 1.1025
        prob += Vib[0] == 1.1025
        prob += Vic[0] == 1.1025
        # prob += Via[0] == 1.0
        # prob += Vib[0] == 1.0
        # prob += Vic[0] == 1.0


        ## tap1+tap2+....tap33 ==1 only one tap position will be 1 , other 0
        
    
        prob += lpSum([tapi1[i] for i in range(tap_r1)]) == 1  
        prob += lpSum([tapi2[i] for i in range(tap_r1)]) == 1  
        prob += lpSum([tapi3[i] for i in range(tap_r1)]) == 1 
        prob += lpSum([tapi4[i] for i in range(tap_r1)]) == 1  
        prob += lpSum([tapi5[i] for i in range(tap_r1)]) == 1  
        prob += lpSum([tapi6[i] for i in range(tap_r1)]) == 1  
        
       
        # # ## v2 - tap^2*v1 ==0
      
        M = 10
        tapk = np.arange(0.9, 1.1, 0.00625)
        for k in range(0,33):
            prob += Via[14] - tapk[k]**2*Via[12] - M*(1-tapi1[k]) <= 0
            prob += Via[14] - tapk[k]**2*Via[12] + M*(1-tapi1[k]) >= 0
           
            prob += Via[39] - tapk[k]**2*Via[34] - M*(1-tapi2[k]) <= 0    
            prob += Via[39] - tapk[k]**2*Via[34] + M*(1-tapi2[k]) >= 0

            prob += Vic[39] - tapk[k]**2*Vic[34] - M*(1-tapi3[k]) <= 0
            prob += Vic[39] - tapk[k]**2*Vic[34] + M*(1-tapi3[k]) >= 0
           
            prob += Via[71] - tapk[k]**2*Via[62] - M*(1-tapi4[k]) <= 0
            prob += Via[71] - tapk[k]**2*Via[62] + M*(1-tapi4[k]) >= 0

            prob += Vib[71] - tapk[k]**2*Vib[62] - M*(1-tapi5[k]) <= 0
            prob += Vib[71] - tapk[k]**2*Vib[62] + M*(1-tapi5[k]) >= 0

            prob += Vic[71] - tapk[k]**2*Vic[62] - M*(1-tapi6[k]) <= 0
            prob += Vic[71] - tapk[k]**2*Vic[62] + M*(1-tapi6[k]) >= 0



  



        print ('Solving the VVO problem..........')
        # Call solver 
        # prob.solve()
        print("using Pulp solver")
        prob.solve(pulp.PULP_CBC_CMD(msg=True))
            # prob.solve()
        prob.writeLP("Check.lp")


        for i in range(tap_r1):
            if tapi1[i].varValue >= 0.9:
                # print(tapi1[i])
                tap1 = (i-17)

        for i in range(tap_r1):
            if tapi2[i].varValue >= 0.9:
                tap2 = (i-17)
        
        for i in range(tap_r1):
            if tapi3[i].varValue >= 0.9:
                tap3 = (i-17)

        for i in range(tap_r1):
            if tapi4[i].varValue >= 0.9:
                tap4 = (i-17)

        for i in range(tap_r1):
            if tapi5[i].varValue >= 0.9:
                tap5 = (i-17)

        for i in range(tap_r1):
            if tapi6[i].varValue >= 0.9:
                tap6 = (i-17)

        status_c = [swia[121].varValue,swib[121].varValue,swic[121].varValue, swia[103].varValue,swib[110].varValue,swic[118].varValue]
        status_r = [tap1, tap2, tap3, tap4, tap5, tap6]


        Qpvcontrol = []
        # for i in range(nEdges):
        #     node = to[i]
        #     indb = Nodes.index(node)
        #     demandPpv = 0.
        #     demandSpv = 0.
        #     for d in LoadData:
        #         if node == d['bus'] and d['Phase'] == 'A' :
        #             demandPpv += d['kW_pv']/bkva
        #             demandSpv += d['kVA_pv']/bkva
        #             if QPVa[indb].varValue != None and QPVa[indb].varValue != 0:
        #                 value = (np.sqrt(demandSpv**2 - demandPpv**2))*(QPVa[indb].varValue)*bkva*1000
        #                 # print(value)
        #                 message = dict(bus = d['bus'],
        #                                 mrid = 'abc',
        #                                 val = value)
        #                 Qpvcontrol.append(message)

        #         if node == d['bus'] and d['Phase'] == 'B' :
        #             demandPpv += d['kW_pv']/bkva
        #             demandSpv += d['kVA_pv']/bkva
        #             if QPVb[indb].varValue != None and QPVb[indb].varValue != 0:
        #                 value = (np.sqrt(demandSpv**2 - demandPpv**2))*(QPVb[indb].varValue)*bkva*1000
        #                 message = dict(bus = d['bus'],
        #                                 mrid = 'abc',
        #                                 val = value)
        #                 Qpvcontrol.append(message)

        #         if node == d['bus'] and d['Phase'] == 'C' :
        #             demandPpv += d['kW_pv']/bkva
        #             demandSpv += d['kVA_pv']/bkva
        #             if QPVc[indb].varValue != None and QPVc[indb].varValue != 0:
        #                 value = (np.sqrt(demandSpv**2 - demandPpv**2))*(QPVc[indb].varValue)*bkva*1000
        #                 message = dict(bus = d['bus'],
        #                                 mrid = 'abc',
        #                                 val = value)
        #                 Qpvcontrol.append(message)

        return Qpvcontrol, status_c, status_r