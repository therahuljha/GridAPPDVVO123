
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 11:30:52 2019

@author: rjha
with 4 VR, 4 capbank 
"""



import numpy as np
from pulp import *
import time
import Zmatrixa as zma
import Zmatrixb as zmb
import Zmatrixc as zmc

start = time.clock()

## here the 149 node is numbered as 125 node
class WSUVVO(object):
    """
    WSU VVO
    """
    def __init__(self):
        pass

    def VVO(self):
    
    # Parameters
        nNodes = 125
        nEdges = 126
        CVRP = 0.6
        CVRQ = 3.0
        Vs = 1.1
        #Tie_Switches = np.matrix([54, 94], [117, 123]);
        edges = np.loadtxt('edges.txt') 
        demand = np.loadtxt('LoadData.txt') 
        demand = 1.0*demand
        loops = np.loadtxt('cycles.txt')
        LineData = np.loadtxt('Line_Config.txt')
        mult = -1*(demand[:,1]+demand[:,3]+demand[:,5])
        v_i = range(0,nNodes)
        s_i = range(0,nNodes)
        x_ij = range(0,nEdges)
        V_i = range(0,nNodes)
        sw_i=range(0,nNodes);
        tap_r1=range(0,33);
        tap_r2=range(0,33);
        tap_r3=range(0,33);
        tap_r4=range(0,33);
        tap_r5=range(0,33);

                
                # Different variables for optimization function
        assign_vars_vi = LpVariable.dicts("xv", v_i, 0, 1,  LpBinary)
        assign_vars_si = LpVariable.dicts("xs", s_i, 0, 1,  LpBinary)
        assign_vars_xij = LpVariable.dicts("xl", x_ij, 0, 1,  LpBinary)
        assign_vars_xij0 = LpVariable.dicts("xl0", x_ij, 0, 1,  LpBinary)
        assign_vars_xij1 = LpVariable.dicts("xl1", x_ij, 0, 1,  LpBinary)
        assign_vars_Pija = LpVariable.dicts("xPa", x_ij, -10000, 10000)
        assign_vars_Pijb = LpVariable.dicts("xPb", x_ij, -10000, 10000)
        assign_vars_Pijc = LpVariable.dicts("xPc", x_ij, -10000, 10000)
        assign_vars_Qija = LpVariable.dicts("xQa", x_ij, -10000, 10000)
        assign_vars_Qijb = LpVariable.dicts("xQb", x_ij, -10000, 10000)
        assign_vars_Qijc = LpVariable.dicts("xQc", x_ij, -10000, 10000)
        assign_vars_Via = LpVariable.dicts("xVa", V_i, 0.9025, 1.1)
        assign_vars_Vib = LpVariable.dicts("xVb", V_i, 0.9025, 1.1)
        assign_vars_Vic = LpVariable.dicts("xVc", V_i, 0.9025, 1.1)
        assign_vars_swia = LpVariable.dicts("xswa", sw_i, 0, 1,  LpBinary)
        assign_vars_swib = LpVariable.dicts("xswb", sw_i, 0, 1,  LpBinary)
        assign_vars_swic = LpVariable.dicts("xswc", sw_i, 0, 1,  LpBinary)
        assign_vars_tapi1 = LpVariable.dicts("xtap1", tap_r1, 0, 1,  LpBinary)
        assign_vars_tapi2 = LpVariable.dicts("xtap2", tap_r2, 0, 1,  LpBinary)
        assign_vars_tapi3 = LpVariable.dicts("xtap3", tap_r3, 0, 1,  LpBinary)
        assign_vars_tapi4 = LpVariable.dicts("xtap4", tap_r4, 0, 1,  LpBinary)
        assign_vars_tapi5 = LpVariable.dicts("xtap5", tap_r5, 0, 1,  LpBinary)
        #       

        # Optimization problem objective definitions
        prob = LpProblem("CVR",LpMinimize)
        prob += assign_vars_Pija[0]+assign_vars_Pijb[0]+assign_vars_Pijc[0] 
        
                
        # Constraints (v_i<=0)
        for k in range(0,nNodes):
            prob += assign_vars_vi[k] == 1
            
        # Constraints (s_i<=v_i)
        for k in range(0,nNodes):
            prob += assign_vars_si[k] <= assign_vars_vi[k]
                    
                    
        # Real power flow equation for Phase A phase B and Phase C
        fr = edges[:,0]
        to = edges[:,1]
        for k in range(0, nEdges):    
            ed = int(edges[k,1]-1)
            node = edges[k,1]
            line=[edges[k,0], edges[k,1]]
            # Finding the all parent nodes of a particular node
            pa = np.array(np.where(to==edges[k,1]))
            pa = pa.flatten()
            N = range(0,pa.__len__())
            # Finding the all children nodes of a particular node
            ch = np.array(np.where(fr==edges[k,1]))
            ch = ch.flatten()
            M = range(0,ch.__len__()) 
            # The overall power flow equation for Phase A now can be written as,    
            prob += lpSum(assign_vars_Pija[pa[j]] for j in N) - 1.0*demand[ed,1]*assign_vars_Via[int(line[1])-1]*(CVRP/2)== \
            lpSum(assign_vars_Pija[ch[j]] for j in M) +  1.0*demand[ed,1]*(1-CVRP/2)- 0.1*demand[ed,10]
        
        # Phase B
        for k in range(0, nEdges):    
            ed = int(edges[k,1]-1)
            node = edges[k,1]
            line=[edges[k,0], edges[k,1]]
            # Finding the all parent nodes of a particular node
            pa = np.array(np.where(to==edges[k,1]))
            pa = pa.flatten()
            N = range(0,pa.__len__())
            # Finding the all children nodes of a particular node
            ch = np.array(np.where(fr==edges[k,1]))
            ch = ch.flatten()
            M = range(0,ch.__len__()) 
            # The overall power flow equation for Phase B now can be written as,    
            prob += lpSum(assign_vars_Pijb[pa[j]] for j in N) -  1.0*demand[ed,2]*assign_vars_Vib[int(line[1])-1]*(CVRP/2)== \
            lpSum(assign_vars_Pijb[ch[j]] for j in M) + 1.0*demand[ed,2]*(1-CVRP/2) - 0.1*demand[ed,11]
        
        # Phase C    
        for k in range(0, nEdges):    
            ed = int(edges[k,1]-1)
            node = edges[k,1]
            line=[edges[k,0], edges[k,1]]
            # Finding the all parent nodes of a particular node
            pa = np.array(np.where(to==edges[k,1]))
            pa = pa.flatten()
            N = range(0, pa.__len__())
            # Finding the all children nodes of a particular node
            ch = np.array(np.where(fr==edges[k,1]))
            ch = ch.flatten()
            M = range(0, ch.__len__()) 
            # The overall power flow equation for Phase C now can be written as,    
            prob += lpSum(assign_vars_Pijc[pa[j]] for j in N) -  1.0*demand[ed,3]*assign_vars_Vic[int(line[1])-1]*(CVRP/2)== \
            lpSum(assign_vars_Pijc[ch[j]] for j in M) +  1.0*demand[ed,3]*(1-CVRP/2) - 0.1*demand[ed,12]
               
                # Imposing the big-M method to ensure the real-power flowing in open line is zero
                # -M * x_ij0 <= Pij <= x_ij1* M 
        M = 100000
        for k in range(0, nEdges):    
            prob += assign_vars_Pija[k] <= M * assign_vars_xij1[k]
            prob += assign_vars_Pijb[k] <= M * assign_vars_xij1[k] 
            prob += assign_vars_Pijc[k] <= M * assign_vars_xij1[k]     
            prob += assign_vars_Pija[k] >= -M * assign_vars_xij0[k]
            prob += assign_vars_Pijb[k] >= -M * assign_vars_xij0[k] 
            prob += assign_vars_Pijc[k] >= -M * assign_vars_xij0[k] 
                
                ## Now writing the reactive power flow equation for Phase A phase B and Phase C
        fr = edges[:,0]
        to = edges[:,1]
        for k in range(0, nEdges):    
            ed = int(edges[k,1]-1)
            node = edges[k,1]
            line=[edges[k,0], edges[k,1]]
            # Finding the all parent nodes of a particular node
            pa = np.array(np.where(to==edges[k,1]))
            pa = pa.flatten()
            N = range(0, pa.__len__())
            # Finding the all children nodes of a particular node
            ch = np.array(np.where(fr==edges[k,1]))
            ch = ch.flatten()
            M = range(0, ch.__len__()) 
            # The overall power flow equation for Phase A now can be written as,    
            prob += lpSum(assign_vars_Qija[pa[j]] for j in N) -  1.0*demand[ed,4]*assign_vars_Via[int(line[1])-1]*(CVRQ/2)== \
            lpSum(assign_vars_Qija[ch[j]] for j in M) +  1.0*demand[ed,4]*(1-CVRQ/2)- demand[ed,7]*assign_vars_swia[int(line[1])-1] 

        
        # Phase B
        for k in range(0, nEdges):    
            ed = int(edges[k,1]-1)
            node = edges[k,1]
            line=[edges[k,0], edges[k,1]]
            # Finding the all parent nodes of a particular node
            pa = np.array(np.where(to==edges[k,1]))
            pa = pa.flatten()
            N = range(0, pa.__len__())
            # Finding the all children nodes of a particular node
            ch = np.array(np.where(fr==edges[k,1]))
            ch = ch.flatten()
            M = range(0, ch.__len__())  
            # The overall power flow equation for Phase B now can be written as,    
            prob += lpSum(assign_vars_Qijb[pa[j]] for j in N) - 1.0*demand[ed,5]*assign_vars_Vib[int(line[1])-1]*(CVRQ/2)== \
            lpSum(assign_vars_Qijb[ch[j]] for j in M) +  1.0*demand[ed,5]*(1-CVRQ/2)-  demand[ed,8]*assign_vars_swib[int(line[1])-1]

        
        # Phase C   
        for k in range(0, nEdges):    
            ed = int(edges[k,1]-1)
            node = edges[k,1]
            line=[edges[k,0], edges[k,1]];
            # Finding the all parent nodes of a particular node
            pa = np.array(np.where(to==edges[k,1]))
            pa = pa.flatten()
            N = range(0, pa.__len__())
            # Finding the all children nodes of a particular node
            ch =np.array(np.where(fr==edges[k,1]))
            ch = ch.flatten()
            M = range(0, ch.__len__())
            # The overall power flow equation for Phase C now can be written as,    
            prob += lpSum(assign_vars_Qijc[pa[j]] for j in N) - 1.0*demand[ed,6]*assign_vars_Vic[int(line[1])-1]*(CVRQ/2)== \
            lpSum(assign_vars_Qijc[ch[j]] for j in M) +  1.0*demand[ed,6]*(1-CVRQ/2)- demand[ed,9]*assign_vars_swic[int(line[1])-1]
     
               
                # mposing the big-M method to ensure the reactive-power flowing in open line is zero
                # -M * x_ij0 <= Qij <= x_ij1* M
        M = 100000
        for k in range(0, nEdges):    
            prob += assign_vars_Qija[k] <= M * assign_vars_xij[k]
            prob += assign_vars_Qijb[k] <= M * assign_vars_xij[k] 
            prob += assign_vars_Qijc[k] <= M * assign_vars_xij[k] 
            prob += assign_vars_Qija[k] >= -M * assign_vars_xij0[k]
            prob += assign_vars_Qijb[k] >= -M * assign_vars_xij0[k] 
            prob += assign_vars_Qijc[k] >= -M * assign_vars_xij0[k]
         
                # Voltage constraints are written as set of inequality constraints by coupling them with
                # line or switch variable.
        base_Z = 4.16**2
        for k in range(0, 124):
            conf = LineData[k,3]
            len = LineData[k,2]
            # Get the Z matrix for a line
            r_aa,x_aa,r_ab,x_ab,r_ac,x_ac = zma.Zmatrixa(conf)
            line = [LineData[k,0], LineData[k,1]]
            prob += assign_vars_Via[int(line[0])-1]-assign_vars_Via[int(line[1])-1] - \
            2*r_aa*len/(5280*base_Z*1000)*assign_vars_Pija[int(line[1])-1]- \
            2*x_aa*len/(5280*base_Z*1000)*assign_vars_Qija[int(line[1])-1]+ \
            (r_ab+np.sqrt(3)*x_ab)*len/(5280*base_Z*1000)*assign_vars_Pijb[int(line[1])-1] +\
            (x_ab-np.sqrt(3)*r_ab)*len/(5280*base_Z*1000)*assign_vars_Qijb[int(line[1])-1] +\
            (r_ac-np.sqrt(3)*x_ac)*len/(5280*base_Z*1000)*assign_vars_Pijc[int(line[1])-1] +\
            (x_ac+np.sqrt(3)*r_ac)*len/(5280*base_Z*1000)*assign_vars_Qijc[int(line[1])-1] ==0
            
        for k in range(0, 124):
            conf = LineData[k,3]
            len = LineData[k,2]
            # Get the Z matrix for a line
            r_bb,x_bb,r_ba,x_ba,r_bc,x_bc = zmb.Zmatrixb(conf)
            line=[LineData[k,0], LineData[k,1]]
            prob += assign_vars_Vib[int(line[0])-1]-assign_vars_Vib[int(line[1])-1] - \
            2*r_bb*len/(5280*base_Z*1000)*assign_vars_Pijb[int(line[1])-1]- \
            2*x_bb*len/(5280*base_Z*1000)*assign_vars_Qijb[int(line[1])-1]+ \
            (r_ba-np.sqrt(3)*x_ba)*len/(5280*base_Z*1000)*assign_vars_Pija[int(line[1])-1] +\
            (x_ba+np.sqrt(3)*r_ba)*len/(5280*base_Z*1000)*assign_vars_Qija[int(line[1])-1] +\
            (r_bc+np.sqrt(3)*x_bc)*len/(5280*base_Z*1000)*assign_vars_Pijc[int(line[1])-1] +\
            (x_bc-np.sqrt(3)*r_bc)*len/(5280*base_Z*1000)*assign_vars_Qijc[int(line[1])-1] ==0
            
        for k in range(0, 124):
            conf = LineData[k,3]
            len = LineData[k,2]
            # Get the Z matrix for a line
            r_cc,x_cc,r_ca,x_ca,r_cb,x_cb = zmc.Zmatrixc(conf)
            line=[LineData[k,0], LineData[k,1]]
            prob += assign_vars_Vic[int(line[0])-1]-assign_vars_Vic[int(line[1])-1] - \
            2*r_cc*len/(5280*base_Z*1000)*assign_vars_Pijc[int(line[1])-1]- \
            2*x_cc*len/(5280*base_Z*1000)*assign_vars_Qijc[int(line[1])-1]+ \
            (r_ca+np.sqrt(3)*x_ca)*len/(5280*base_Z*1000)*assign_vars_Pija[int(line[1])-1] +\
            (x_ca-np.sqrt(3)*r_ca)*len/(5280*base_Z*1000)*assign_vars_Qija[int(line[1])-1] +\
            (r_cb-np.sqrt(3)*x_cb)*len/(5280*base_Z*1000)*assign_vars_Pijb[int(line[1])-1] +\
            (x_cb+np.sqrt(3)*r_cb)*len/(5280*base_Z*1000)*assign_vars_Qijb[int(line[1])-1] ==0
            
        
        
        Mvr=4    
        prob += lpSum([assign_vars_tapi1[i] for i in tap_r1]) == 1    
        prob += lpSum([assign_vars_tapi2[i] for i in tap_r2]) == 1 
        prob += lpSum([assign_vars_tapi3[i] for i in tap_r3]) == 1 
        prob += lpSum([assign_vars_tapi4[i] for i in tap_r4]) == 1  
        prob += lpSum([assign_vars_tapi5[i] for i in tap_r5]) == 1            
        
        tapk = np.arange(0.9, 1.1, 0.00625)
        tapvs =np.zeros((33,), dtype=float)
        for k in range(0,33):
            tapvs[k] = tapk[k]**2
        
        
        # the VR equations with big M constarints  
            
        M = 10
        tapk = np.arange(0.9, 1.1, 0.00625)
        for k in range(0,33):
           prob += assign_vars_Via[124] - tapk[k]**2*Vs - M*(1-assign_vars_tapi1[k]) <= 0
           prob += assign_vars_Via[124] - tapk[k]**2*Vs + M*(1-assign_vars_tapi1[k]) >= 0
           prob += assign_vars_Vib[124] - tapk[k]**2*Vs - M*(1-assign_vars_tapi1[k]) <= 0
           prob += assign_vars_Vib[124] - tapk[k]**2*Vs + M*(1-assign_vars_tapi1[k]) >= 0
           prob += assign_vars_Vic[124] - tapk[k]**2*Vs - M*(1-assign_vars_tapi1[k]) <= 0
           prob += assign_vars_Vic[124] - tapk[k]**2*Vs + M*(1-assign_vars_tapi1[k]) >= 0
           
           prob += assign_vars_Via[13] - tapk[k]**2*assign_vars_Via[8] - M*(1-assign_vars_tapi2[k]) <= 0    
           prob += assign_vars_Via[13] - tapk[k]**2*assign_vars_Via[8] + M*(1-assign_vars_tapi2[k]) >= 0
           
           prob += assign_vars_Via[25] - tapk[k]**2*assign_vars_Via[24] - M*(1-assign_vars_tapi3[k]) <= 0
           prob += assign_vars_Via[25] - tapk[k]**2*assign_vars_Via[24] + M*(1-assign_vars_tapi3[k]) >= 0
           prob += assign_vars_Vic[25] - tapk[k]**2*assign_vars_Vib[24] - M*(1-assign_vars_tapi4[k]) <= 0
           prob += assign_vars_Vic[25] - tapk[k]**2*assign_vars_Vib[24] + M*(1-assign_vars_tapi4[k]) >= 0
           
           prob += assign_vars_Via[66] - tapk[k]**2*assign_vars_Via[118] - M*(1-assign_vars_tapi5[k]) <= 0
           prob += assign_vars_Via[66] - tapk[k]**2*assign_vars_Via[118] + M*(1-assign_vars_tapi5[k]) >= 0
           prob += assign_vars_Vib[66] - tapk[k]**2*assign_vars_Vib[118] - M*(1-assign_vars_tapi5[k]) <= 0
           prob += assign_vars_Vib[66] - tapk[k]**2*assign_vars_Vib[118] + M*(1-assign_vars_tapi5[k]) >= 0
           prob += assign_vars_Vic[66] - tapk[k]**2*assign_vars_Vic[118] - M*(1-assign_vars_tapi5[k]) <= 0
           prob += assign_vars_Vic[66] - tapk[k]**2*assign_vars_Vic[118] + M*(1-assign_vars_tapi5[k]) >= 0 
            
        
        prob.solve()        
        
        varsdict = {}
        for v in prob.variables():
            varsdict[v.name] = v.varValue

        x1 = LpVariable.dicts("xtap1",range(33))
        for k in range (0,33):
            a=str(x1[k]);
            tap=varsdict[a]
            if tap==1:
                pass
        
        
        taps = []
        x2 = LpVariable.dicts("xtap2",range(33))
        for k in range (0,33):
            a=str(x2[k]);
            tap=varsdict[a]
            if tap==1:
                taps.append(k-17)
          
        #    
        x3 = LpVariable.dicts("xtap3",range(33))
        for k in range (0,33):
            a=str(x3[k]);
            tap=varsdict[a]
            if tap==1:
                taps.append(k-17)
           
                
        x4 = LpVariable.dicts("xtap4",range(33))
        for k in range (0,33):
            a=str(x4[k]);
            tap=varsdict[a]
            if tap==1:
                taps.append(k-17)
            
                
        x5 = LpVariable.dicts("xtap5",range(33))
        for k in range (0,33):
            a=str(x5[k]);
            tap=varsdict[a]
            if tap==1:
                taps.append(k-17)
                taps.append(k-17)
                taps.append(k-17)
               

        status_c = [varsdict['xswa_82'], varsdict['xswb_82'], varsdict['xswc_82'], varsdict['xswa_87'], varsdict['xswb_89'], varsdict['xswc_91'] ]
        status_c = [0,0,1,0]
        status_r = taps
        return status_c, status_r
       
    



