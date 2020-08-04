# -*- coding: utf-8 -*-
"""
Created on nov 22 11:17:12 2019
@author: rjha
"""

class MODEL_EQ(object):
    """
    WSU VVO. Mapping Switch MRIDs
    """
    def __init__(self, gapps, model_mrid, topic):
        self.gapps = gapps
        self.model_mrid = model_mrid
        self.topic = topic
        
    def meas_mrids(self):

       # Get measurement MRIDS for DERs. The measid for DERs are not returning any results so using AC line segment
        message = {
        "modelId": self.model_mrid,
        "requestType": "QUERY_OBJECT_MEASUREMENTS",
        "resultFormat": "JSON",
        "objectType": "ACLineSegment"}     
        obj_msr_sync = self.gapps.get_response(self.topic, message, timeout=180)   
        obj_msr_sync = obj_msr_sync['data']
      
        # # Get measurement MRIDS for Inverters
        message = {
        "modelId": self.model_mrid,
        "requestType": "QUERY_OBJECT_MEASUREMENTS",
        "resultFormat": "JSON",
        "objectType": "PowerElectronicsConnection"}     
        obj_msr_inv = self.gapps.get_response(self.topic, message, timeout=180)   
        # print(obj_msr_inv)

             
        # Get measurement MRIDS for kW consumptions at each node
        message = {
            "modelId": self.model_mrid,
            "requestType": "QUERY_OBJECT_MEASUREMENTS",
            "resultFormat": "JSON",
            "objectType": "EnergyConsumer"}     
        obj_msr_demand = self.gapps.get_response(self.topic, message, timeout=180)
        
        
        ## Get measurement MRIDS for regulators in the feeder
        
        message = {
            "modelId": self.model_mrid,
            "requestType": "QUERY_OBJECT_MEASUREMENTS",
            "resultFormat": "JSON",
            "objectType": "PowerTransformer"}     
        obj_msr_reg = self.gapps.get_response(self.topic, message, timeout=180)
        # print(obj_msr_reg)

        message = {
            "modelId": self.model_mrid,
            "requestType": "QUERY_OBJECT_MEASUREMENTS",
            "resultFormat": "JSON",
            "objectType": "LinearShuntCompensator"}     
        obj_msr_cap = self.gapps.get_response(self.topic, message, timeout=180)
        # print(obj_msr_cap)
        # print('Gathering Measurement MRIDS.... \n')
        # return obj_msr_loadsw, obj_msr_demand, obj_msr_reg, obj_msr_cap ,obj_msr_inv

        message = {
            "modelId": self.model_mrid,
            "requestType": "QUERY_OBJECT_MEASUREMENTS",
            "resultFormat": "JSON",
            "objectType": "ACLineSegment"}     
        obj_msr_node = self.gapps.get_response(self.topic, message, timeout=180)
        # print(obj_msr_node)
        print('Gathering Measurement MRIDS.... \n')
        return  obj_msr_demand, obj_msr_reg, obj_msr_cap ,obj_msr_inv,obj_msr_node
        # return  obj_msr_demand, obj_msr_reg, obj_msr_cap 

    def distLoad(self):
        query = """
    PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX c:  <http://iec.ch/TC57/CIM100#>
    SELECT ?name ?bus ?basev ?p ?q ?conn ?cnt ?pz ?qz ?pi ?qi ?pp ?qp ?pe ?qe ?fdrid WHERE {
    ?s r:type c:EnergyConsumer.
    # feeder selection options - if all commented out, query matches all feeders
    VALUES ?fdrid {"%s"}  # R2 12.47 3
    ?s c:Equipment.EquipmentContainer ?fdr.
    ?fdr c:IdentifiedObject.mRID ?fdrid.
    ?s c:IdentifiedObject.name ?name.
    ?s c:ConductingEquipment.BaseVoltage ?bv.
    ?bv c:BaseVoltage.nominalVoltage ?basev.
    ?s c:EnergyConsumer.customerCount ?cnt.
    ?s c:EnergyConsumer.p ?p.
    ?s c:EnergyConsumer.q ?q.
    ?s c:EnergyConsumer.phaseConnection ?connraw.
    bind(strafter(str(?connraw),"PhaseShuntConnectionKind.") as ?conn)
    ?s c:EnergyConsumer.LoadResponse ?lr.
    ?lr c:LoadResponseCharacteristic.pConstantImpedance ?pz.
    ?lr c:LoadResponseCharacteristic.qConstantImpedance ?qz.
    ?lr c:LoadResponseCharacteristic.pConstantCurrent ?pi.
    ?lr c:LoadResponseCharacteristic.qConstantCurrent ?qi.
    ?lr c:LoadResponseCharacteristic.pConstantPower ?pp.
    ?lr c:LoadResponseCharacteristic.qConstantPower ?qp.
    ?lr c:LoadResponseCharacteristic.pVoltageExponent ?pe.
    ?lr c:LoadResponseCharacteristic.qVoltageExponent ?qe.
    OPTIONAL {?ecp c:EnergyConsumerPhase.EnergyConsumer ?s.
    ?ecp c:EnergyConsumerPhase.phase ?phsraw.
    bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs) }
    ?t c:Terminal.ConductingEquipment ?s.
    ?t c:Terminal.ConnectivityNode ?cn. 
    ?cn c:IdentifiedObject.name ?bus
    }
    GROUP BY ?name ?bus ?basev ?p ?q ?cnt ?conn ?pz ?qz ?pi ?qi ?pp ?qp ?pe ?qe ?fdrid
    ORDER by ?name
        """ % self.model_mrid
        results = self.gapps.query_data(query, timeout=60)
        results_obj = results['data']
        LoadData = []
        demand = results_obj['results']['bindings']
        for ld in demand:
            name = ld['bus']['value']
            message = dict(bus = ld['bus']['value'],
                        Phase  = name[-1].upper(),
                        kW = 0.001 *  float (ld['p']['value']),
                        kVaR = 0.001 * float(ld['q']['value']),
                        kVaR_C = 0)
            LoadData.append(message)   
        print('Load..')
        # sP = 0.
        # sQ = 0.
        # for l in LoadData:
        #     sP += 0.001 * float(l['kW'])
        #     sQ += 0.001 * float(l['kVAR'])

        # print(sP, sQ)

        return LoadData


    def Inverters(self):
        query = """
    PREFIX r: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX c: <http://iec.ch/TC57/CIM100#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?inverter_mrid ?inverter_name ?inverter_mode ?inverter_max_q ?inverter_min_q ?inverter_p ?inverter_q ?inverter_rated_s ?inverter_rated_u ?phase_mrid ?phase_name ?phase_p ?phase_q 
    WHERE {
    # Update for your feeder, or remove for all feeders.
    VALUES ?feeder_mrid {"%s"}
    ?s r:type c:PowerElectronicsConnection.
    ?s c:Equipment.EquipmentContainer ?fdr.
    ?fdr c:IdentifiedObject.mRID ?feeder_mrid.
    ?s c:IdentifiedObject.mRID ?inverter_mrid.
    ?s c:IdentifiedObject.name ?inverter_name.
    ?s c:PowerElectronicsConnection.p ?inverter_p.
    ?s c:PowerElectronicsConnection.q ?inverter_q.
    ?s c:PowerElectronicsConnection.ratedS ?inverter_rated_s.
    ?s c:PowerElectronicsConnection.ratedU ?inverter_rated_u.
    OPTIONAL {
    ?s c:PowerElectronicsConnection.inverterMode ?inverter_mode.
    ?s c:PowerElectronicsConnection.maxQ ?inverter_max_q.
    ?s c:PowerElectronicsConnection.minQ ?inverter_min_q.
    }
    OPTIONAL {
    ?pecp c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?s.
    ?pecp c:IdentifiedObject.mRID ?phase_mrid.
    ?pecp c:IdentifiedObject.name ?phase_name.
    ?pecp c:PowerElectronicsConnectionPhase.p ?phase_p.
    ?pecp c:PowerElectronicsConnectionPhase.q ?phase_q.
    ?pecp c:PowerElectronicsConnectionPhase.phase
    ?phsraw bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs)
    }
    }
    GROUP BY ?inverter_mrid ?inverter_name ?inverter_rated_s ?inverter_rated_u ?inverter_p ?inverter_q ?phase_mrid ?phase_name ?phase_p ?phase_q ?inverter_mode ?inverter_max_q ?inverter_min_q
    ORDER BY ?inverter_mrid
        """ % self.model_mrid
        results = self.gapps.query_data(query, timeout=60)
        results_obj = results['data']
        Inverter_PnS = []
        inverter = results_obj['results']['bindings']
        for i in inverter:
            name = i['inverter_name']['value']
            message = dict(name = i['inverter_name']['value'],
                        mrid  = i['inverter_mrid']['value'],
                        ratedS = 0.001 * float(i['inverter_rated_s']['value']),
                        ratedP = 0.001 * float(i['inverter_p']['value']))
            Inverter_PnS.append(message)   
        

        return Inverter_PnS
        print('Inverter..')

    def PVInverters(self):
        query = """
    PREFIX r: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX c: <http://iec.ch/TC57/CIM100#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?name ?bus ?ratedS ?ratedU ?ipu ?p ?q ?fdrid ?id ?pecid WHERE {
    VALUES ?feeder_mrid {"%s"}
    ?s r:type c:PhotovoltaicUnit.
    ?s c:IdentifiedObject.name ?name.
    ?s c:IdentifiedObject.mRID ?id.
    ?pec c:PowerElectronicsConnection.PowerElectronicsUnit ?s.
    ?pec c:IdentifiedObject.mRID ?pecid.
    ?pec c:Equipment.EquipmentContainer ?fdr.
    ?fdr c:IdentifiedObject.mRID ?feeder_mrid.
    ?pec c:PowerElectronicsConnection.ratedS ?ratedS.
    ?pec c:PowerElectronicsConnection.ratedU ?ratedU.
    ?pec c:PowerElectronicsConnection.maxIFault ?ipu.
    ?pec c:PowerElectronicsConnection.p ?p.
    ?pec c:PowerElectronicsConnection.q ?q.
    OPTIONAL {?pecp c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?pec.
    ?pecp c:PowerElectronicsConnectionPhase.phase ?phsraw.
    bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs) }
    ?t c:Terminal.ConductingEquipment ?pec.
    ?t c:Terminal.ConnectivityNode ?cn.
    ?cn c:IdentifiedObject.name ?bus
    }
    GROUP by ?name ?bus ?ratedS ?ratedU ?ipu ?p ?q ?fdrid ?id ?pecid
    ORDER by ?name
        """ % self.model_mrid
        results = self.gapps.query_data(query, timeout=60)
        results_obj = results['data']
        # print(results_obj)
        Inverter_PVs = []
        inverter = results_obj['results']['bindings']
        for i in inverter:
            name = i['name']['value']
            message = dict(name = i['name']['value'],
                        bus = i['bus']['value'],
                        mrid  = i['pecid']['value'],
                        mridid  = i['id']['value'],
                        ratedS = 0.001 * float(i['ratedS']['value']),
                        ratedP = 0.001 * float(i['p']['value']))
            Inverter_PVs.append(message)   
        

       # print(Inverter_PnS)
        return Inverter_PVs
        print('PVinvert..')

    # def distributed_generators(self):
    #     query = """
    #     # SynchronousMachine - DistSyncMachine
    # PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    # PREFIX c:  <http://iec.ch/TC57/CIM100#>
    # SELECT ?name ?bus ?ratedS ?ratedU ?p ?q ?id ?fdrid WHERE {
    # VALUES ?fdrid {"%s"}  # 123 bus
    # ?s r:type c:SynchronousMachine.
    # ?s c:IdentifiedObject.name ?name.
    # ?s c:Equipment.EquipmentContainer ?fdr.
    # ?fdr c:IdentifiedObject.mRID ?fdrid.
    # ?s c:SynchronousMachine.ratedS ?ratedS.
    # ?s c:SynchronousMachine.ratedU ?ratedU.
    # ?s c:SynchronousMachine.p ?p.
    # ?s c:SynchronousMachine.q ?q. 
    # ?s c:IdentifiedObject.mRID ?id.
    # OPTIONAL {?smp c:SynchronousMachinePhase.SynchronousMachine ?s.
    # ?smp c:SynchronousMachinePhase.phase ?phsraw.
    # bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs) }
    # ?t c:Terminal.ConductingEquipment ?s.
    # ?t c:Terminal.ConnectivityNode ?cn. 
    # ?cn c:IdentifiedObject.name ?bus
    # }
    # GROUP by ?name ?bus ?ratedS ?ratedU ?p ?q ?id ?fdrid
    # ORDER by ?name
    #     """ % self.model_mrid
    #     results = self.gapps.query_data(query, timeout=60)
    #     results_obj = results['data']
    #     DERs = []
    #     MT = results_obj['results']['bindings']
    #     for d in MT:
    #         message = dict(name = d['name']['value'],
    #                        mrid  = d['id']['value'],
    #                        bus = d['bus']['value'],
    #                        ratedS = 0.001 * float(d['ratedS']['value']))
    #         DERs.append(message)  

    
    #     query = """
    #    PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    # PREFIX c:  <http://iec.ch/TC57/CIM100#>
    # SELECT ?name ?bus ?ratedS ?ratedU ?ipu ?ratedE ?storedE ?state ?p ?q ?id ?fdrid WHERE {
    # ?s r:type c:BatteryUnit.
    # ?s c:IdentifiedObject.name ?name.
    # ?pec c:PowerElectronicsConnection.PowerElectronicsUnit ?s.
    # # feeder selection options - if all commented out, query matches all feeders
    # #VALUES ?fdrid {"_C1C3E687-6FFD-C753-582B-632A27E28507"}  # 123 bus
    # #VALUES ?fdrid {"_49AD8E07-3BF9-A4E2-CB8F-C3722F837B62"}  # 13 bus
    # #VALUES ?fdrid {"_5B816B93-7A5F-B64C-8460-47C17D6E4B0F"}  # 13 bus assets
    # #VALUES ?fdrid {"_4F76A5F9-271D-9EB8-5E31-AA362D86F2C3"}  # 8500 node
    # #VALUES ?fdrid {"_67AB291F-DCCD-31B7-B499-338206B9828F"}  # J1
    # VALUES ?fdrid {"%s"}  # R2 12.47 3
    # ?pec c:Equipment.EquipmentContainer ?fdr.
    # ?fdr c:IdentifiedObject.mRID ?fdrid.
    # ?pec c:PowerElectronicsConnection.ratedS ?ratedS.
    # ?pec c:PowerElectronicsConnection.ratedU ?ratedU.
    # ?pec c:PowerElectronicsConnection.maxIFault ?ipu.
    # ?s c:BatteryUnit.ratedE ?ratedE.
    # ?s c:BatteryUnit.storedE ?storedE.
    # ?s c:BatteryUnit.batteryState ?stateraw.
    # bind(strafter(str(?stateraw),"BatteryState.") as ?state)
    # ?pec c:PowerElectronicsConnection.p ?p.
    # ?pec c:PowerElectronicsConnection.q ?q. 
    # OPTIONAL {?pecp c:PowerElectronicsConnectionPhase.PowerElectronicsConnection ?pec.
    # ?pecp c:PowerElectronicsConnectionPhase.phase ?phsraw.
    # bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs) }
    # ?s c:IdentifiedObject.mRID ?id.
    # ?t c:Terminal.ConductingEquipment ?pec.
    # ?t c:Terminal.ConnectivityNode ?cn. 
    # ?cn c:IdentifiedObject.name ?bus
    # }
    # GROUP by ?name ?bus ?ratedS ?ratedU ?ipu ?ratedE ?storedE ?state ?p ?q ?id ?fdrid
    # ORDER by ?name
    #     """ % self.model_mrid
    #     results = self.gapps.query_data(query, timeout=60)
    #     results_obj = results['data']
    #     ESS = results_obj['results']['bindings']
    #     for d in ESS:
    #         message = dict(name = d['name']['value'],
    #                        mrid  = d['id']['value'],
    #                        bus = d['bus']['value'],
    #                        ratedS = 0.001 * float(d['ratedS']['value']))
    #         DERs.append(message)  

    #     return DERs

    def get_regulators_mrids(self):
        query = """
    PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX c:  <http://iec.ch/TC57/CIM100#>
    SELECT ?rid ?rname ?pname ?tname ?wnum ?phs ?incr ?mode ?enabled ?highStep ?lowStep ?neutralStep ?normalStep ?neutralU 
    ?step ?initDelay ?subDelay ?ltc ?vlim 
        ?vset ?vbw ?ldc ?fwdR ?fwdX ?revR ?revX ?discrete ?ctl_enabled ?ctlmode ?monphs ?ctRating ?ctRatio ?ptRatio ?id ?fdrid ?bus
    WHERE {
    VALUES ?fdrid {"%s"}  # 123
    ?pxf c:Equipment.EquipmentContainer ?fdr.
    ?fdr c:IdentifiedObject.mRID ?fdrid.
    ?rtc r:type c:RatioTapChanger.
    ?rtc c:IdentifiedObject.name ?rname.
    ?rtc c:IdentifiedObject.mRID ?rid.
    ?rtc c:RatioTapChanger.TransformerEnd ?end.
    ?end c:TransformerEnd.Terminal ?trm.
    ?trm c:IdentifiedObject.mRID ?trmid.
    ?trm c:Terminal.ConnectivityNode ?cn. 
    ?cn c:IdentifiedObject.name ?bus.
    ?end c:TransformerEnd.endNumber ?wnum.
    OPTIONAL {?end c:TransformerTankEnd.phases ?phsraw.
    bind(strafter(str(?phsraw),"PhaseCode.") as ?phs)}
    ?end c:TransformerTankEnd.TransformerTank ?tank.
    ?tank c:TransformerTank.PowerTransformer ?pxf.
    ?pxf c:IdentifiedObject.name ?pname.
    ?tank c:IdentifiedObject.name ?tname.
    ?rtc c:RatioTapChanger.stepVoltageIncrement ?incr.
    ?rtc c:RatioTapChanger.tculControlMode ?moderaw.
    bind(strafter(str(?moderaw),"TransformerControlMode.") as ?mode)
    ?rtc c:TapChanger.controlEnabled ?enabled.
    ?rtc c:TapChanger.highStep ?highStep.
    ?rtc c:TapChanger.initialDelay ?initDelay.
    ?rtc c:TapChanger.lowStep ?lowStep.
    ?rtc c:TapChanger.ltcFlag ?ltc.
    ?rtc c:TapChanger.neutralStep ?neutralStep.
    ?rtc c:TapChanger.neutralU ?neutralU.
    ?rtc c:TapChanger.normalStep ?normalStep.
    ?rtc c:TapChanger.step ?step.
    ?rtc c:TapChanger.subsequentDelay ?subDelay.
    ?rtc c:TapChanger.TapChangerControl ?ctl.
    ?ctl c:TapChangerControl.limitVoltage ?vlim.
    ?ctl c:TapChangerControl.lineDropCompensation ?ldc.
    ?ctl c:TapChangerControl.lineDropR ?fwdR.
    ?ctl c:TapChangerControl.lineDropX ?fwdX.
    ?ctl c:TapChangerControl.reverseLineDropR ?revR.
    ?ctl c:TapChangerControl.reverseLineDropX ?revX.
    ?ctl c:RegulatingControl.discrete ?discrete.
    ?ctl c:RegulatingControl.enabled ?ctl_enabled.
    ?ctl c:RegulatingControl.mode ?ctlmoderaw.
    bind(strafter(str(?ctlmoderaw),"RegulatingControlModeKind.") as ?ctlmode)
    ?ctl c:RegulatingControl.monitoredPhase ?monraw.
    bind(strafter(str(?monraw),"PhaseCode.") as ?monphs)
    ?ctl c:RegulatingControl.targetDeadband ?vbw.
    ?ctl c:RegulatingControl.targetValue ?vset.
    ?asset c:Asset.PowerSystemResources ?rtc.
    ?asset c:Asset.AssetInfo ?inf.
    ?inf c:TapChangerInfo.ctRating ?ctRating.
    ?inf c:TapChangerInfo.ctRatio ?ctRatio.
    ?inf c:TapChangerInfo.ptRatio ?ptRatio.
    }
    ORDER BY ?pname ?tname ?rname ?wnum ?bus
        """ % self.model_mrid
        results = self.gapps.query_data(query, timeout=60)
        regulators = []
        name = []
        bus_n = []
        results_obj = results['data']
        for p in results_obj['results']['bindings']:
            regulators.append(p['rid']['value'])
            name.append(p['rname']['value'])
            bus_n.append(p['bus']['value'])
            # print(p)
        # for k in range(len(regulators)):
        #     print(name[k], bus_n[k], regulators[k])
        # print("\n ...........................................")
        return regulators
        with open('regulators.json', 'w') as outfile:
            json.dump(regulators, outfile)
        print('regulators..')

    def get_capacitors_mrids(self):
        query = """
    # capacitors (does not account for 2+ unequal phases on same LinearShuntCompensator) - DistCapacitor
    PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX c:  <http://iec.ch/TC57/CIM100#>
    SELECT ?name ?basev ?nomu ?bsection ?bus ?conn ?grnd ?phs ?ctrlenabled ?discrete ?mode ?deadband ?setpoint ?delay ?monclass ?moneq ?monbus ?monphs ?id ?fdrid WHERE {
    ?s r:type c:LinearShuntCompensator.
    # feeder selection options - if all commented out, query matches all feeders
    VALUES ?fdrid {"%s"}  # 123 bus
    #VALUES ?fdrid {"_49AD8E07-3BF9-A4E2-CB8F-C3722F837B62"}  # 13 bus
    #VALUES ?fdrid {"_5B816B93-7A5F-B64C-8460-47C17D6E4B0F"}  # 13 bus assets
    #VALUES ?fdrid {"_4F76A5F9-271D-9EB8-5E31-AA362D86F2C3"}  # 8500 node
    #VALUES ?fdrid {"_67AB291F-DCCD-31B7-B499-338206B9828F"}  # J1
    #VALUES ?fdrid {"_9CE150A8-8CC5-A0F9-B67E-BBD8C79D3095"}  # R2 12.47 3
    ?s c:Equipment.EquipmentContainer ?fdr.
    ?fdr c:IdentifiedObject.mRID ?fdrid.
    ?s c:IdentifiedObject.name ?name.
    ?s c:ConductingEquipment.BaseVoltage ?bv.
    ?bv c:BaseVoltage.nominalVoltage ?basev.
    ?s c:ShuntCompensator.nomU ?nomu. 
    ?s c:LinearShuntCompensator.bPerSection ?bsection. 
    ?s c:ShuntCompensator.phaseConnection ?connraw.
    bind(strafter(str(?connraw),"PhaseShuntConnectionKind.") as ?conn)
    ?s c:ShuntCompensator.grounded ?grnd.
    OPTIONAL {?scp c:ShuntCompensatorPhase.ShuntCompensator ?s.
    ?scp c:ShuntCompensatorPhase.phase ?phsraw.
    bind(strafter(str(?phsraw),"SinglePhaseKind.") as ?phs) }
    OPTIONAL {?ctl c:RegulatingControl.RegulatingCondEq ?s.
            ?ctl c:RegulatingControl.discrete ?discrete.
            ?ctl c:RegulatingControl.enabled ?ctrlenabled.
            ?ctl c:RegulatingControl.mode ?moderaw.
            bind(strafter(str(?moderaw),"RegulatingControlModeKind.") as ?mode)
            ?ctl c:RegulatingControl.monitoredPhase ?monraw.
            bind(strafter(str(?monraw),"PhaseCode.") as ?monphs)
            ?ctl c:RegulatingControl.targetDeadband ?deadband.
            ?ctl c:RegulatingControl.targetValue ?setpoint.
            ?s c:ShuntCompensator.aVRDelay ?delay.
            ?ctl c:RegulatingControl.Terminal ?trm.
            ?trm c:Terminal.ConductingEquipment ?eq.
            ?eq a ?classraw.
            bind(strafter(str(?classraw),"CIM100#") as ?monclass)
            ?eq c:IdentifiedObject.name ?moneq.
            ?trm c:Terminal.ConnectivityNode ?moncn.
            ?moncn c:IdentifiedObject.name ?monbus.
            }
    ?s c:IdentifiedObject.mRID ?id. 
    ?t c:Terminal.ConductingEquipment ?s.
    ?t c:Terminal.ConnectivityNode ?cn. 
    ?cn c:IdentifiedObject.name ?bus
    }
    ORDER by ?name
        """ % self.model_mrid
        results = self.gapps.query_data(query, timeout=60)
        capacitors = []
        results_obj = results['data']
        name = []
        bus_n = []
        for p in results_obj['results']['bindings']:
            # print(p)
            capacitors.append(p['id']['value'])
            name.append(p['name']['value'])
            bus_n.append(p['bus']['value'])
            
        # for k in range(len(capacitors)):
        #     print(name[k], bus_n[k], capacitors[k])
        # print("\n ...........................................")
        return capacitors
        with open('capacitors.json', 'w') as outfile:
            json.dump(capacitors, outfile)

        print('capacitors..')