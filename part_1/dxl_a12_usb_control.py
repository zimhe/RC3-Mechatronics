from dxl_ax12a import AX12a
import tkinter
from tkinter import simpledialog as sd

DEVICENAME = 'com4'  # Default COM Port

motor_controller = AX12a(DEVICENAME)

modes_pattern = ("none", "write_pos", "write_pos_group","wheel_mode", "write_speed", "read_position", "read_load", "quit")

#所连接的马达id
connected_motors = [0,1,2]

#对应每个马达的转动速度
moving_speeds=[100,120,150]


#每个马达的初始位置
initial_positions=[300,300,300]

motor_controller.set_initial_state(connected_motors, moving_speeds, initial_positions)

def set_position_group(position):
    positions=[position]*len(connected_motors)
    motor_controller.set_position_group(positions)
    


def user_input():
    """ Check to see if user wants to continue """
    ans = input('Continue? : y/n ')
    if ans == 'n':
        return False
    else:
        return True


def execute(mode, _id=None):
    if _id is not None:
        motor_controller.set_id(_id)

    if mode == modes_pattern[0]:
        return
    elif mode == modes_pattern[1]:
        motor_controller.enable_torque()
        value = int(input("Input a target position (0-1023) : "))
        motor_controller.set_position(value)
    elif mode == modes_pattern[2]:
        motor_controller.enable_torque()
        value = int(input("Input a target position (0-1023) : "))
        set_position_group(value)
    elif mode == modes_pattern[3]:
        motor_controller.enable_torque()
        value = int(input("Input [0] False, [1] True : "))
        motor_controller.set_wheel_mode(value)
    elif mode == modes_pattern[4]:
        motor_controller.enable_torque()
        value = int(input("Input a target speed (CCW > 0-1024,CW > 1024-2047) : "))
        motor_controller.set_moving_speed(value)

    elif mode == modes_pattern[5]:
        motor_controller.get_position()

    elif mode == modes_pattern[6]:
        motor_controller.get_load()



def listening():
    
    is_listening = True
    while is_listening:
        prompt = "[0] %s,[1] %s, [2] %s, [3] %s, [4] %s, [5] %s, [6] %s , [7] %s:" % modes_pattern
        ptn_id = int(input(prompt))
        #ptn_id=sd.askinteger(prompt=prompt,title="select an action")
        m_cmd = modes_pattern[ptn_id]

        if m_cmd != modes_pattern[7]:
            m_id=None
            if m_cmd != modes_pattern[2]:
                input_string = ""
                for _id in connected_motors:
                    input_string += "[{}] servo_ID_{} ".format(_id, _id)

                input_string += ":"
                
                m_id = int(input(input_string))

            execute(m_cmd, m_id)
            is_listening = user_input()
        else:
            is_listening=False
            break



# detect obstacles with current load parameters
# to be fixed
def listenLoadChange(motor_object):
    motor_object.set_wheel_mode(1)
    motor_object.set_moving_speed(50)

    is_listening = True
    while is_listening:
        load = motor_object.get_load()
        print("current load is %s" % load)
        if 200 > load > 100:
            motor_object.set_moving_speed(load)
        elif 1500 > load > 1300:
            motor_object.set_moving_speed(load)


# reset to default mode
# to be fixed
def reset(motor_object):
    motor_object.wheel_mode(0)


if __name__ == "__main__":
    root=tkinter.Tk(screenName="dxl control usb")
    listening()
    root.mainloop()
    motor_controller.disable_torque_group()
    AX12a.close_port()