import sys
import os
from os import path

# Add project root to Python path
project_root = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.getcwd())

print("Current Dir is: "+os.getcwd())
print("Project Root is: "+project_root)

from part_1.dxl_ax12a import AX12a

# Import control table with fallback
try:
    from part_1.ax12a_control_table import *
except ImportError:
    try:
        import sys
        sys.path.append(os.path.join(project_root, 'part_1'))
        from ax12a_control_table import *
    except ImportError as e:
        print(f"Warning: Could not import ax12a_control_table: {e}")

from part_2.my_osc_client import OSC_CLIENT
from part_2.osc_commond_patterns import *

# Alternative import method if above fails
try:
    from my_osc_client import OSC_CLIENT
    from osc_commond_patterns import *
except ImportError:
    pass

from typing import Union

import pyfirmata
from pyfirmata import util,Arduino



# integrate dxl controller with osc client with the ip address that it sends the feedbacks towards
class DXL_OSC:
    motor_controller = None
    client = None
    started = False

    def start_client_controller(self, ip, port, devicename):
        if self.motor_controller is not None:
            self.motor_controller.disable_torque_group()
            AX12a.close_port()
            
        self.client = OSC_CLIENT(ip, int(port))
        self.motor_controller = AX12a(devicename)

    def start_osc(self, ip, port, devicename, dxl_ids, moving_speed, initial_positions):
        self.start_client_controller(ip, port, devicename)
        self.motor_controller.set_initial_state(dxl_ids, moving_speed, initial_positions)
        self.started = True

    def is_started(self):
        return self.started
    
class ArduinoControl:
    arduino_board:Arduino=None
    arduino_port:str=''

    def setup(self,port:str):
        self.arduino_port=port
        self.arduino_board=Arduino(self.arduino_port)
        it=util.Iterator(self.arduino_board)
        it.start()

    def setup_digital_pin(self,pin:int,mode:Union[str,int]):
        digital=self.arduino_board.digital[pin]
        m=None
        if mode=='input' or mode ==0:
            m=pyfirmata.INPUT
        
        elif mode== 'output'or mode==1:
            m=pyfirmata.OUTPUT

        digital.mode=m
        return digital
    
    def setup_analog_pin(self,pin,mode:Union[str,int]):
        analog=self.arduino_board.analog[pin]
        m=None
        if mode=='input' or mode ==0:
            m=pyfirmata.INPUT
        
        elif mode== 'output'or mode==1:
            m=pyfirmata.OUTPUT

        analog.mode=m
        return analog
    
    def digitl_read(self,pin:int):
        pin_obj=self.arduino_board.digital[pin]
        return pin_obj.read()

    def digitl_write(self,pin:int,value:int):
        pin_obj=self.arduino_board.digital[pin]
        pin_obj.write(value)

    def analog_read(self,pin:int):
        pin_obj=self.arduino_board.analog[pin]
        val=pin_obj.read()
        iter=0
        while val is None:
            val= pin_obj.read()
            iter+=1
            if iter>100:
                break
        return val
    
    def analog_write(self,pin:int,value:int):
        pin_obj=self.arduino_board.analog[pin]
        pin_obj.write(value)
        


dxl_osc_ctrl:DXL_OSC = DXL_OSC()

arduino_control:ArduinoControl=ArduinoControl()

started = 0

# functional methods
def split_msg(msg, splitter="#"):
    msg_split = msg.split(splitter)
    return msg_split


def start_osc(pattern, start_infos):
    network_info, dxl_ids, moving_speeds, initial_positions = split_msg(start_infos, "#")

    ip, port, devicename = split_msg(network_info, "$")

    m_dxl_ids = split_msg(dxl_ids, "$")
    
    m_moving_speeds=split_msg(moving_speeds,"$")

    m_initial_positions = split_msg(initial_positions, "$")

    dxl_osc_ctrl.start_osc(ip, port, devicename, m_dxl_ids, m_moving_speeds, m_initial_positions)
    dxl_osc_ctrl.client.send_osc(SRV_STRATED,1)



def client_started():
    return dxl_osc_ctrl.is_started()


def setup_arduino(pattern,device_name):
    try:
        arduino_control.setup(device_name)
        dxl_osc_ctrl.client.send_osc(ARD_SETUP, 1)
    except:
        print('failed setting arduino')
        dxl_osc_ctrl.client.send_osc(ARD_SETUP, 0)
    
def arduino_set_ditital_pin(pattern,pin_mode):
    pin,mode=split_msg(pin_mode)
    arduino_control.setup_digital_pin(int(pin),int(mode))

def arduino_set_analog_pin(pattern,pin_mode):
    pin,mode=split_msg(pin_mode)
    arduino_control.setup_analog_pin(int(pin),int(mode))

def arduino_digital_write(pattern,pin_value):
    pin,value=split_msg(pin_value)
    arduino_control.digitl_write(int(pin),int(value))

def arduino_analog_read(pattern,pin):
    read= arduino_control.analog_read(int(pin))
    value="{}#{}".format(pin, read)
    dxl_osc_ctrl.client.send_osc(ARD_AREAD, str(value))

def arduino_analog_write(pattern,pin_value):
    pin,value=split_msg(pin_value)
    arduino_control.analog_write(int(pin),int(value))


def arduino_digital_read(pattern,pin):
    read=arduino_control.digitl_read(int(pin))
    value="{}#{}".format(pin, read)
    dxl_osc_ctrl.client.send_osc(ARD_DREAD, str(value))

# read feedbacks
def read_position(pattern, _id):
    dxl_osc_ctrl.motor_controller.set_id(int(_id))
    position = dxl_osc_ctrl.motor_controller.get_position()
    value = "{}#{}".format(_id, position)
    dxl_osc_ctrl.client.send_osc(READ_POS, str(value))


def read_speed(pattern, _id):
    dxl_osc_ctrl.motor_controller.set_id(int(_id))
    speed = dxl_osc_ctrl.motor_controller.get_present_speed()
    value = "{}#{}".format(_id, speed)
    dxl_osc_ctrl.client.send_osc(READ_SPD, value)


def read_temperature(pattern, _id):
    dxl_osc_ctrl.motor_controller.set_id(int(_id))
    temp = dxl_osc_ctrl.motor_controller.get_temperature()
    value = "{}#{}".format(_id, temp)
    dxl_osc_ctrl.client.send_osc(READ_TEMP, str(value))


def read_torque_limit(pattern, _id):
    dxl_osc_ctrl.motor_controller.set_id(int(_id))
    torque_limit = dxl_osc_ctrl.motor_controller.get_torque_limit()
    value = "{}#{}".format(_id, torque_limit)
    dxl_osc_ctrl.client.send_osc(READ_TRQ_LMT, str(value))


def read_load(pattern, _id):
    dxl_osc_ctrl.motor_controller.set_id(int(_id))
    load = dxl_osc_ctrl.motor_controller.get_load()
    value = "{}#{}".format(_id, load)
    dxl_osc_ctrl.client.send_osc(READ_LOAD, str(value))


def read_is_moving(pattern, _id):
    dxl_osc_ctrl.motor_controller.set_id(int(_id))
    isMoving = dxl_osc_ctrl.motor_controller.is_moving()
    value = "{}#{}".format(_id, isMoving)
    dxl_osc_ctrl.client.send_osc(READ_MOV, str(value))


# enable torque
def torque_enable_disable(pattern, id_value):
    _id, value = split_msg(id_value)
    dxl_osc_ctrl.motor_controller.set_id(int(_id))
    if value == TORQUE_ENABLE:
        dxl_osc_ctrl.motor_controller.enable_torque()
    elif value == TORQUE_DISABLE:
        dxl_osc_ctrl.motor_controller.disable_torque()


# set parameters
def set_speed(pattern, id_value):
    _id, value = split_msg(id_value)
    dxl_osc_ctrl.motor_controller.set_id(int(_id))
    dxl_osc_ctrl.motor_controller.set_moving_speed(int(value))


def set_position(pattern, id_value):
    _id, value = split_msg(id_value)
    dxl_osc_ctrl.motor_controller.set_id(int(_id))
    dxl_osc_ctrl.motor_controller.set_position(int(value))


def set_torque_limit(pattern, id_value):
    _id, value = split_msg(id_value)
    dxl_osc_ctrl.motor_controller.set_id(int(_id))
    dxl_osc_ctrl.motor_controller.set_torque_limit(int(value))


def set_position_group(pattern, positions_group):
    positions = split_msg(positions_group, "$")
    dxl_osc_ctrl.motor_controller.set_position_group(positions,10)


def set_speed_group(pattern, speeds_group):
    speeds = split_msg(speeds_group,"$")
    dxl_osc_ctrl.motor_controller.set_speed_group(speeds)
