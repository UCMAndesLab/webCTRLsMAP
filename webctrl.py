import os, subprocess

from smap import actuate, driver
from smap.authentication import authenticated

class _Actuator(actuate.SmapActuator):
	def setup(self, opts):
		self.devicePath = os.path.expanduser(opts['devicePath'])
		self.serverAddr = '10.20.0.60'
		self.scriptPath = '/home/lsequeira2/svn/misc/trunk/lsequeira2/bash_webctrl.sh'

	def get_state(self, request):
		value = subprocess.check_output([self.scriptPath, "getValue", self.serverAddr, self.devicePath, "0"])
		value = float(value)
		return value

	def set_state(self, request, state):
		value = subprocess.check_output([self.scriptPath, "setValue", self.serverAddr, self.devicePath, str(state)])
		return float(state)

class Facilities_BldgA_Actuator(_Actuator, actuate.IntegerActuator):
    	def setup(self, opts):
		actuate.IntegerActuator.setup(self, opts)
		_Actuator.setup(self, opts)

class Facilities_BldgB_Actuator(_Actuator, actuate.IntegerActuator):
	def setup(self, opts):
		actuate.IntegerActuator.setup(self, opts)
		_Actuator.setup(self, opts)

class ScienceEngineering2_Actuator(_Actuator, actuate.IntegerActuator):
	def setup(self, opts):
		actuate.IntegerActuator.setup(self, opts)
		_Actuator.setup(self, opts)

class WebCtrlDriver(driver.SmapDriver):
	def setup(self, opts):
		temperature = 'temperature'
		occupancy = 'occupancy'
		unoccupied_heating_setpoint = 'unoccupied_heating_setpoint'
		unoccupied_cooling_setpoint = 'unoccupied_cooling_setpoint'
		occupied_heating_setpoint = 'occupied_heating_setpoint'
		occupied_cooling_setpoint = 'occupied_cooling_setpoint'
		mixed_air_temperature = 'mixed_air_temperature'

		data_type = 'double'

		# List of WebCtrl points/types [Facilities/Bldg1/VAV1_1/] [Damper Position] [double]
		if not 'building' in opts or opts['building'] == 'Facilities_BldgA':
			klass = Facilities_BldgA_Actuator

			for i in range(1, 9):
	                        # Temperature
                        	setup={'devicePath': 'vav-1%d_0204/lstat/output1.value'%i}
                        	self.add_actuator('/vav-1%d/%s'%(i,temperature), 'Value', klass, setup=setup, data_type=data_type)

                        	# Occupancy
                        	setup={'devicePath': 'vav-1%d_0204/schedule/schedule/present_value.value'%i}
                        	self.add_actuator('/vav-1%d/%s'%(i,occupancy), 'Value', klass, setup=setup, data_type=data_type)

                        	# Unoccupied Heating Setpoint
                        	setup={'devicePath': 'vav-1%d_0204/setpt/setpoints/unoccupied_heating.value'%i}
                        	self.add_actuator('/vav-1%d/%s'%(i,unoccupied_heating_setpoint), 'Value', klass, setup=setup, data_type=data_type)

                        	# Unoccupied Cooling Setpoint
                        	setup={'devicePath': 'vav-1%d_0204/setpt/setpoints/unoccupied_cooling.value'%i}
                        	self.add_actuator('/vav-1%d/%s'%(i,unoccupied_cooling_setpoint), 'Value', klass, setup=setup, data_type=data_type)

                        	# Occupied Heating Setpoint
                        	setup={'devicePath': 'vav-1%d_0204/setpt/setpoints/occupied_heating.value'%i}
                        	self.add_actuator('/vav-1%d/%s'%(i,occupied_heating_setpoint), 'Value', klass, setup=setup, data_type=data_type)

                        	# Occupied Cooling Setpoint
                        	setup={'devicePath': 'vav-1%d_0204/setpt/setpoints/occupied_cooling.value'%i}
                        	self.add_actuator('/vav-1%d/%s'%(i,occupied_cooling_setpoint), 'Value', klass, setup=setup, data_type=data_type)

                        	# Mixed Air Temperature
                        	setup={'devicePath': 'vav-1%d_0204/ma_temp/present_value.value'%i}
                        	self.add_actuator('/vav-1%d/%s'%(i,mixed_air_temperature), 'Value', klass, setup=setup, data_type=data_type)

		elif opts['building'] == 'Facilities_BldgB':
			klass = Facilities_BldgB_Actuator
		elif opts['building'] == 'SE2':
			klass = ScienceEngineering2_Actuator

			# Occupied Heating Setpoint
			setup={'devicePath': '\#vav-3-27/setpt/setpoints/occupied_heating.value'}
                	self.add_actuator('/vav-3-27/%s'%occupied_heating_setpoint, 'Value', klass, setup=setup, data_type=data_type)
		else:
			raise ValueError("Invalid building: " + opts['building'])

