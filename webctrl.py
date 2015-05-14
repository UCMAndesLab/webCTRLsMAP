import os, subprocess
import json
from smap import actuate, driver
from smap.authentication import authenticated

class _Actuator(actuate.SmapActuator):
   def setup(self, opts):
      self.devicePath = os.path.expanduser(opts['devicePath'])
      self.serverAddr = opts['webctrlServerAddr'];
      self.scriptPath = opts['scriptPath'];
   
   def webctrlRequest(self, typeOfRequest, inputValue = "0"):
      cleanDevicePath = "\"{0}\"".format(self.devicePath)
      pythonCmd = [self.scriptPath, typeOfRequest, self.serverAddr, cleanDevicePath, inputValue]
      print pythonCmd;
      value = subprocess.check_output(pythonCmd)
      return value;


   def get_state(self, request):
      return float(self.webctrlRequest("getValue"));
   
   def set_state(self, request, state):
      status = self.webctrlRequest("setValue", str(state));
      if status:
         return float(state);
      
class WebCTRL_Actuator(_Actuator, actuate.IntegerActuator):
   def setup(self, opts):
      actuate.IntegerActuator.setup(self, opts)
      _Actuator.setup(self, opts)

class WebCtrlDriver(driver.SmapDriver):
   def setup(self, opts):
      zoneSetpoint = []
      zoneSetpoint.append('unoccupied_heating');
      zoneSetpoint.append('unoccupied_cooling');
      zoneSetpoint.append('occupied_heating');
      zoneSetpoint.append('occupied_cooling');
      
      
      # List of WebCtrl points/types [Facilities/Bldg1/VAV1_1/] [Damper Position] [double]
      klass = WebCTRL_Actuator
      setpointFile = open(opts['setpointFile'], 'r');
      jsonStr = setpointFile.read();
      setpoints = json.loads(jsonStr);
      
      for entry in setpoints:
         data_type = 'double'
         for point in zoneSetpoint: 
            devicePath = '{0}/{1}/setpoints/{2}.value'.format(entry['refName'], entry['block'], point);
            setup=opts;
            setup['devicePath'] = devicePath;

            actuatorPath = '{0}/{1}'.format(entry['path'], point);
            print actuatorPath
            self.add_actuator(actuatorPath, 'Value', klass, setup=setup, data_type=data_type)
                       
