


import dxl_control_osc, my_osc_server
from osc_commond_patterns import *


my_osc_server.dispatch_callback(START_OSC, dxl_control_osc.start_osc)

my_osc_server.dispatch_callback(READ_POS, dxl_control_osc.read_position)
my_osc_server.dispatch_callback(READ_SPD, dxl_control_osc.read_speed)
my_osc_server.dispatch_callback(READ_LOAD, dxl_control_osc.read_load)
my_osc_server.dispatch_callback(READ_TEMP, dxl_control_osc.read_temperature)
my_osc_server.dispatch_callback(READ_TRQ_LMT, dxl_control_osc.read_torque_limit)

my_osc_server.dispatch_callback(SET_POS, dxl_control_osc.set_position)
my_osc_server.dispatch_callback(SET_SPD, dxl_control_osc.set_speed)
my_osc_server.dispatch_callback(SET_TRQ_LMT, dxl_control_osc.set_torque_limit)

my_osc_server.dispatch_callback(SET_POS_GRP, dxl_control_osc.set_position_group)
my_osc_server.dispatch_callback(SET_SPD_GRP, dxl_control_osc.set_speed_group)

my_osc_server.dispatch_callback(TRQ_TOGGLE, dxl_control_osc.torque_enable_disable)

# my_osc_server.dispatch_callback(ARD_SETUP, dxl_control_osc.setup_arduino)
# my_osc_server.dispatch_callback(ARD_SET_APIN, dxl_control_osc.arduino_set_analog_pin)
# my_osc_server.dispatch_callback(ARD_SET_DPIN, dxl_control_osc.arduino_set_ditital_pin)
# my_osc_server.dispatch_callback(ARD_DREAD, dxl_control_osc.arduino_digital_read)
# my_osc_server.dispatch_callback(ARD_DWRITE, dxl_control_osc.arduino_digital_write)
# my_osc_server.dispatch_callback(ARD_AREAD, dxl_control_osc.arduino_analog_read)
# my_osc_server.dispatch_callback(ARD_AWRITE, dxl_control_osc.arduino_analog_write)

my_osc_server.server_threading(my_osc_server.address, my_osc_server.dispatcher)
