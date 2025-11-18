import pyfirmata
from pyfirmata import util
import time
from part_1.dxl_ax12a import AX12a


arduino_port='com4'
dxl_port='com3'


motor_count = 3
movingSpeed = 100
connected_motors = [i for i in range(motor_count)]

movingSpeed = 32

button_pin=10
led_pin=7
knob_pin=0

pos_min=100
pos_max=800

startPos = []

mt_idx=0


def initialize_motors():
    for i in connected_motors:
        startPos.append(motor.get_position_ID(i))
        motor.set_moving_speed_ID(movingSpeed, i)


def pos_remap(t:float):
    return int(pos_min + t * (pos_max - pos_min))


if __name__ == '__main__':
    board = pyfirmata.Arduino(arduino_port)
    print("Communication Successfully started")

    motor = AX12a(dxl_port)
    print("Motor Connected")

    button = board.digital[button_pin]
    knob=board.analog[knob_pin]
    led=board.digital[led_pin]
    button.mode=pyfirmata.INPUT
    knob.mode=pyfirmata.INPUT
    led.mode=pyfirmata.OUTPUT
    it=util.Iterator(board)
    it.start()

    while True:

        t=knob.read()

        if t is not None:
            pos=pos_remap(t)
            motor.set_position_ID(pos, connected_motors[mt_idx])

        if not button.read():
            mt_idx+=1
            mt_idx%=motor_count

        time.sleep(0.1)




