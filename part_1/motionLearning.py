import easygui.boxes
import easygui.boxes.button_box
from dxl_ax12a import AX12a
import easygui
from tkinter import filedialog,simpledialog,messagebox
import argparse

import threading

import json

#DEVICENAME = "com4"  # Default COM Port


# Argument parsing
parser = argparse.ArgumentParser(description="Motor Controller Script")
parser.add_argument("--devicename", type=str, default="COM3", help="COM Port for the motor controller")
parser.add_argument("--connected_motors", type=int, nargs="+", default=[0, 1, 2], help="List of connected motor IDs (e.g., 1 3 4)")
parser.add_argument("--moving_speed", type=int, default=100, help="Default moving speed for motors")
parser.add_argument("--max_learning_steps", type=int, default=300, help="Maximum learning steps")


args = parser.parse_args()


DEVICENAME = args.devicename
connected_motors = args.connected_motors
movingSpeed = args.moving_speed
max_learning_steps = args.max_learning_steps

motor_controller = AX12a(DEVICENAME)

commands = (
    "restore position",
    "start learning",
    "save motion",
    "load motion",
    "disable torque",
    "quit",
)


startPos = []
position_buffers = {}

example_position_buffers={0:[200,300,600],
                          1:[],
                          2:[]
                          }



def initialize_motors():
    for i in connected_motors:
        startPos.append(motor_controller.get_position_ID(i))
        position_buffers[i] = []
        motor_controller.set_moving_speed_ID(movingSpeed, i)


def user_input():
    """Check to see if user wants to continue"""
    ans = input("Continue? : y/n ")
    if ans == "n":
        return False
    else:
        return True


def restore_positions():
    for i in connected_motors:
        motor_controller.set_position_ID(startPos[i], i)

    easygui.msgbox("Position Restored")


def start_learning(max_steps: int = 300):
    custom_steps = easygui.enterbox(
        msg=f"Enter number of steps for learning (default {max_steps}):",
        title="Set Learning Steps",
    )
    if custom_steps:
        try:
            max_steps = int(custom_steps)
        except ValueError:
            easygui.msgbox("Invalid input. Using default value.", title="Error")

    for i in connected_motors:
        motor_controller.disable_torque_ID(i)
        position_buffers[i].clear()

    steps = 0
    position_buffers["max_steps"] = max_steps

   
    while steps < max_steps:

        status="Status: "
        for i in connected_motors:
            pos=motor_controller.get_position_ID(i)
            position_buffers[i].append(pos)
            status+=f"\nMotor-{i} Position: {pos}"
        steps += 1
       
       

    
    for i in connected_motors:
        motor_controller.enable_torque_ID(i)
        motor_controller.set_position_ID(startPos[connected_motors.index(i)], i)

    easygui.msgbox("Learning Completed","",ok_button="Contine?")


def save_motion():
    path = easygui.filesavebox(
        filetypes=["*.json"], title="save motion", msg="saving motion to file"
    )

    #path=filedialog.asksaveasfilename(filetypes=["*.json"],title="save motion")
    
    print(path)

    if path is None:
        return

    path = path + ".json"
    with open(path, "w", encoding="utf-8") as data:
        json.dump(position_buffers, data)
        position_buffers.clear()


def load_motion():
    path = easygui.fileopenbox(
        filetypes=["*.json"], title="load motion", msg="loading motion from file"
    )
    #path=filedialog.askopenfilename(filetypes=["*.json"],title="load motion")
    if path is None:
        return
    with open(path, "r", encoding="utf-8") as data:
        motions = json.load(data)

    maxsteps = motions["max_steps"]

    for i in connected_motors:
        motor_controller.enable_torque_ID(i)

    steps = 0
    while steps < maxsteps:
        status="Status: "
        for i in connected_motors:
            pos=motions[str(i)][steps]
            motor_controller.set_position_ID(pos, i)
            status+=f"\nMotor-{i} Position: {pos}"

        # easygui.msgbox(
        #     msg=f"{status}", 
        #     title="Moving Progress")
        
        #messagebox.showinfo(status)
           

        steps += 1


def disable_torque():
    for i in connected_motors:
        motor_controller.disable_torque_ID(i)

    easygui.msgbox("Torque disabled")


def execute(mode):
    if mode == commands[0]:
        restore_positions()

    elif mode == commands[1]:
        start_learning(max_learning_steps)
        print("Learning Finished")

    elif mode == commands[2]:
        save_motion()

    elif mode == commands[3]:
        load_motion()
        print("Motion Finished")

    elif mode == commands[4]:
        disable_torque()

    elif mode == commands[5]:
        disable_torque()
        AX12a.close_port()
        quit()



def quit_program():
    disable_torque()
    AX12a.close_port()
    exit()

# GUI Functionality
functions = {
    "Restore Positions": restore_positions,
    "Start Learning": lambda: start_learning(300),
    "Save Motion": save_motion,
    "Load Motion": load_motion,
    "Disable Torque": disable_torque,
    "Quit": quit_program,
}





def main():
    
    initialize_motors()
    
    while True:
        
        choice = easygui.buttonbox(
            msg="Select a command:",
            title="Motor Controller",
            choices=list(functions.keys()),
        )
        if choice:
            functions[choice]()
        else:
            break


if __name__ == "__main__":
     main()
