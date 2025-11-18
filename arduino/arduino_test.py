import pyfirmata
from pyfirmata import util
import time

button_pin=10
led_pin=4
knob_pin=0

blink_min=0.01
blink_max=5.0


def blinkRemap(t:float):
    return blink_min+t*(blink_max-blink_min)


if __name__ == '__main__':
    board = pyfirmata.Arduino('com5')
    print("Communication Successfully started")

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
        blink = 0.5
        if t is not None:
            blink=blinkRemap(t)
            print(f"knob value {t}")

        if button.read():
            led.write(1)
            time.sleep(blink)
            led.write(0)
            time.sleep(blink)

        time.sleep(0.1)




