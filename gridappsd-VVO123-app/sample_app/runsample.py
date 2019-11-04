# -------------------------------------------------------------------------------
# Copyright (c) 2017, Battelle Memorial Institute All rights reserved.
# Battelle Memorial Institute (hereinafter Battelle) hereby grants permission to any person or entity
# lawfully obtaining a copy of this software and associated documentation files (hereinafter the
# Software) to redistribute and use the Software in source and binary forms, with or without modification.
# Such person or entity may use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and may permit others to do so, subject to the following conditions:
# Redistributions of source code must retain the above copyright notice, this list of conditions and the
# following disclaimers.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and
# the following disclaimer in the documentation and/or other materials provided with the distribution.
# Other than as used herein, neither the name Battelle Memorial Institute or Battelle may be used in any
# form whatsoever without the express written consent of Battelle.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# BATTELLE OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# General disclaimer for use with OSS licenses
#
# This material was prepared as an account of work sponsored by an agency of the United States Government.
# Neither the United States Government nor the United States Department of Energy, nor Battelle, nor any
# of their employees, nor any jurisdiction or organization that has cooperated in the development of these
# materials, makes any warranty, express or implied, or assumes any legal liability or responsibility for
# the accuracy, completeness, or usefulness or any information, apparatus, product, software, or process
# disclosed, or represents that its use would not infringe privately owned rights.
#
# Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer,
# or otherwise does not necessarily constitute or imply its endorsement, recommendation, or favoring by the United
# States Government or any agency thereof, or Battelle Memorial Institute. The views and opinions of authors expressed
# herein do not necessarily state or reflect those of the United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY operated by BATTELLE for the
# UNITED STATES DEPARTMENT OF ENERGY under Contract DE-AC05-76RL01830
# -------------------------------------------------------------------------------
"""
Created on Jan 19, 2018

@author: Craig Allwardt
"""

__version__ = "0.0.8"

import argparse
import json
import logging
import sys
import time
from IEE1234VR4C import WSUVVO
from legacy_dev_status import LEGACY_DEV
# from IEEE123 import RestorationWSU
# from Fault_Isolation import Isolation
# from top_identify import Topology

from gridappsd import GridAPPSD, DifferenceBuilder, utils, GOSS
from gridappsd.topics import simulation_input_topic, simulation_output_topic, simulation_log_topic, simulation_output_topic

DEFAULT_MESSAGE_PERIOD = 5
message_period = 5

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
#                     format="%(asctime)s - %(name)s;%(levelname)s|%(message)s",
#                     datefmt="%Y-%m-%d %H:%M:%S")
# Only log errors to the stomp logger.
logging.getLogger('stomp.py').setLevel(logging.ERROR)

_log = logging.getLogger(__name__)


class SwitchingActions(object):
    """ A simple class that handles publishing forward and reverse differences

    The object should be used as a callback from a GridAPPSD object so that the
    on_message function will get called each time a message from the simulator.  During
    the execution of on_meessage the `CapacitorToggler` object will publish a
    message to the simulation_input_topic with the forward and reverse difference specified.
    """

    def __init__(self, simulation_id, gridappsd_obj, reg_list, cap_list, msr_mrids_cap, msr_mrids_reg):
        """ Create a ``CapacitorToggler`` object

        This object should be used as a subscription callback from a ``GridAPPSD``
        object.  This class will toggle the capacitors passed to the constructor
        off and on every five messages that are received on the ``fncs_output_topic``.

        Note
        ----
        This class does not subscribe only publishes.

        Parameters
        ----------
        simulation_id: str
            The simulation_id to use for publishing to a topic.
        gridappsd_obj: GridAPPSD
            An instatiated object that is connected to the gridappsd message bus
            usually this should be the same object which subscribes, but that
            isn't required.
        capacitor_list: list(str)
            A list of capacitors mrids to turn on/off
        """
        self._gapps = gridappsd_obj
        self._flag = 0
        self._Isolate = False
        self._Restoration = False
        self.reg_list = reg_list[1:]
        self._cap_list = cap_list
        self._store = []
        self._message_count = 0
        self._last_toggle_on = False
        self._open_diff = DifferenceBuilder(simulation_id)
        self._close_diff = DifferenceBuilder(simulation_id)
        self._publish_to_topic = simulation_input_topic(simulation_id)
        self.msr_mrids_cap = msr_mrids_cap
        self.msr_mrids_reg = msr_mrids_reg
        _log.info("Building cappacitor list")

        
    def on_message(self, headers, message):
        """ Handle incoming messages on the simulation_output_topic for the simulation_id

        Parameters
        ----------
        headers: dict
            A dictionary of headers that could be used to determine topic of origin and
            other attributes.
        message: object
            A data structure following the protocol defined in the message structure
            of ``GridAPPSD``.  Most message payloads will be serialized dictionaries, but that is
            not a requirement.
        """

        self._message_count += 1
        if self._message_count % message_period == 0:
            print(self.reg_list)
            # calling VVO
            capreg_st = WSUVVO()
            statusO_c, statusO_r = capreg_st.VVO()
            print('\n \n ........................')
            print('Optimization results')
            print( 'capacitor switch status', statusO_c,)
            print( 'regulator tap position', statusO_r)
            print('........................\n \n')

            ch = []
            for m in range(4):
                if statusO_c[m] == 0:
                    ch.append(self._cap_list[m])
            no_opt = LEGACY_DEV(self.msr_mrids_cap,self.msr_mrids_reg, message) 
            statusP_c = no_opt.cap_()
            statusP_r = no_opt.reg_()
            print('\n \n ........................')
            print('Platform Status')
            print('capacitor switch status', statusP_c)            
            print('regulator tap position' , statusP_r)
            print('........................\n \n')

            for cap_mrid in ch:
                self._close_diff.add_difference(cap_mrid, "ShuntCompensator.sections", 0, 1)
                msg = self._close_diff.get_message()
                self._gapps.send(self._publish_to_topic, json.dumps(msg))

            ind = 0
            for reg_mrid in self.reg_list:
                self._close_diff.add_difference(reg_mrid, "TapChanger.step", statusO_r[ind], 0)
                ind += 1
                msg = self._close_diff.get_message()
                self._gapps.send(self._publish_to_topic, json.dumps(msg))




def get_regulators_mrids(gridappsd_obj, mrid):
    query = """
PREFIX r:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX c:  <http://iec.ch/TC57/CIM100#>
SELECT ?rid ?rname ?pname ?tname ?wnum ?phs ?incr ?mode ?enabled ?highStep ?lowStep ?neutralStep ?normalStep ?neutralU
 ?step ?initDelay ?subDelay ?ltc ?vlim
?vset ?vbw ?ldc ?fwdR ?fwdX ?revR ?revX ?discrete ?ctl_enabled ?ctlmode ?monphs ?ctRating ?ctRatio ?ptRatio ?fdrid
WHERE {
VALUES ?fdrid {"%s"}  # 123
 ?pxf c:Equipment.EquipmentContainer ?fdr.
 ?fdr c:IdentifiedObject.mRID ?fdrid.
 ?rtc r:type c:RatioTapChanger.
 ?rtc c:IdentifiedObject.name ?rname.
 ?rtc c:IdentifiedObject.mRID ?rid.
 ?rtc c:RatioTapChanger.TransformerEnd ?end.
 ?end c:TransformerEnd.endNumber ?wnum.
{?end c:PowerTransformerEnd.PowerTransformer ?pxf.}
  UNION
{?end c:TransformerTankEnd.TransformerTank ?tank.
 ?tank c:IdentifiedObject.name ?tname.
 OPTIONAL {?end c:TransformerTankEnd.phases ?phsraw.
  bind(strafter(str(?phsraw),"PhaseCode.") as ?phs)}
 ?tank c:TransformerTank.PowerTransformer ?pxf.}
 ?pxf c:IdentifiedObject.name ?pname.
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
ORDER BY ?pname ?tname ?rname ?wnum
    """ % mrid
    results = gridappsd_obj.query_data(query)
    regulators = []
    results_obj = results['data']
    for p in results_obj['results']['bindings']:
        regulators.append(p['rid']['value'])
    return regulators


def get_capacitors_mrids(gridappsd_obj, mrid):
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
    """ % mrid
    results = gridappsd_obj.query_data(query)
    capacitors = []
    results_obj = results['data']
    for p in results_obj['results']['bindings']:
        capacitors.append(p['id']['value'])
    return capacitors


def _main():
    _log.debug("Starting application")
    print("Application starting-------------------------------------------------------")
    global message_period
    parser = argparse.ArgumentParser()
    parser.add_argument("simulation_id",
                        help="Simulation id to use for responses on the message bus.")
    parser.add_argument("request",
                        help="Simulation Request")
    parser.add_argument("--message_period",
                        help="How often the sample app will send open/close capacitor message.",
                        default=DEFAULT_MESSAGE_PERIOD)
    # These are now set through the docker container interface via env variables or defaulted to
    # proper values.
    #
    # parser.add_argument("-u", "--user", default="system",
    #                     help="The username to authenticate with the message bus.")
    # parser.add_argument("-p", "--password", default="manager",
    #                     help="The password to authenticate with the message bus.")
    # parser.add_argument("-a", "--address", default="127.0.0.1",
    #                     help="tcp address of the mesage bus.")
    # parser.add_argument("--port", default=61613, type=int,
    #                     help="the stomp port on the message bus.")
    #
    opts = parser.parse_args()
    listening_to_topic = simulation_output_topic(opts.simulation_id)
    print(listening_to_topic)
    message_period = int(opts.message_period)
    sim_request = json.loads(opts.request.replace("\'",""))
    model_mrid = sim_request["power_system_config"]["Line_name"]
    print("\n \n The model running is IEEE 123 node with MRID:")
    print(model_mrid)
         

    _log.debug("Model mrid is: {}".format(model_mrid))
    gapps = GridAPPSD(opts.simulation_id, address=utils.get_gridappsd_address(),
                      username=utils.get_gridappsd_user(), password=utils.get_gridappsd_pass())

    # Get measurement MRIDS for regulators in the feeder
    topic = "goss.gridappsd.process.request.data.powergridmodel"
    message = {
        "modelId": model_mrid,
        "requestType": "QUERY_OBJECT_MEASUREMENTS",
        "resultFormat": "JSON",
        "objectType": "PowerTransformer"}     
    obj_msr_reg = gapps.get_response(topic, message, timeout=90)

    message = {
        "modelId": model_mrid,
        "requestType": "QUERY_OBJECT_MEASUREMENTS",
        "resultFormat": "JSON",
        "objectType": "LinearShuntCompensator"}     
    obj_msr_cap = gapps.get_response(topic, message, timeout=90)

    message = {
        "modelId": model_mrid,
        "requestType": "QUERY_OBJECT_MEASUREMENTS",
        "resultFormat": "JSON",
        "objectType": "EnergyConsumer"}     
    obj_msr_loads = gapps.get_response(topic, message, timeout=90)
    print(obj_msr_loads)
    with open('msr_reg.json','w') as json_file:
        json.dump(obj_msr_reg, json_file)
	
    # get objects mrids
    regulators = get_regulators_mrids(gapps, model_mrid)  
    capacitors = get_capacitors_mrids(gapps, model_mrid)


    # print(regulators)
    # print('.......................................\n \n ')
    # print(obj_msr_reg)


    toggler = SwitchingActions(opts.simulation_id, gapps, regulators, capacitors, obj_msr_cap, obj_msr_reg)
    print("Now subscribing")
    gapps.subscribe(listening_to_topic, toggler)
    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    _main()
