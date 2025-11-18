import easygui.boxes
import easygui.boxes.button_box
from dxl_ax12a import AX12a
import easygui
from tkinter import filedialog,simpledialog,messagebox
import tkinter as tk
from tkinter import ttk
import argparse

import threading
import time

import json


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


class MotionStatusGUI:
    def __init__(self, connected_motors):
        self.connected_motors = connected_motors
        self.window = None
        self.labels = {}
        self.step_label = None
        self.progress_bar = None
        self.is_running = False
        
    def create_window(self, max_steps):
        """创建GUI窗口"""
        self.window = tk.Tk()
        self.window.title("Motor Learning Status")
        self.window.geometry("400x300")
        
        # 主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="Motor Position Learning", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 步数显示
        self.step_label = ttk.Label(main_frame, text="Step: 0 / 0", font=('Arial', 12))
        self.step_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # 进度条
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        self.progress_bar['maximum'] = max_steps
        
        # 电机位置显示
        positions_frame = ttk.LabelFrame(main_frame, text="Motor Positions", padding="10")
        positions_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        for i, motor_id in enumerate(self.connected_motors):
            motor_label = ttk.Label(positions_frame, text=f"Motor {motor_id}:")
            motor_label.grid(row=i, column=0, sticky=tk.W, pady=2)
            
            pos_label = ttk.Label(positions_frame, text="0", font=('Courier', 10))
            pos_label.grid(row=i, column=1, sticky=tk.W, padx=(20, 0), pady=2)
            
            self.labels[motor_id] = pos_label
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Learning", command=self.stop_learning)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.close_button = ttk.Button(button_frame, text="Close", command=self.close_window)
        self.close_button.pack(side=tk.LEFT)
        
        # 配置列权重以支持调整大小
        main_frame.columnconfigure(1, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        self.is_running = True
        
        # 设置窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
    def update_status(self, step, positions):
        """更新状态显示"""
        if not self.window or not self.is_running:
            return
            
        try:
            # 更新步数
            max_steps = self.progress_bar['maximum']
            self.step_label.config(text=f"Step: {step} / {int(max_steps)}")
            
            # 更新进度条
            self.progress_bar['value'] = step
            
            # 更新位置
            for motor_id, position in positions.items():
                if motor_id in self.labels:
                    self.labels[motor_id].config(text=f"{position}")
            
            # 更新窗口
            self.window.update_idletasks()
            self.window.update()
            
        except tk.TclError:
            # 窗口已关闭
            self.is_running = False
    
    def stop_learning(self):
        """停止学习"""
        self.is_running = False
        
    def close_window(self):
        """关闭窗口"""
        self.is_running = False
        if self.window:
            self.window.destroy()
            self.window = None
    
    def is_window_open(self):
        """检查窗口是否打开"""
        return self.window is not None and self.is_running



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
    
    # 创建GUI窗口（如果选择使用）

    gui = MotionStatusGUI(connected_motors)
    gui.create_window(max_steps)

    try:
        while steps < max_steps:
            # 检查GUI是否要求停止
            if gui and not gui.is_window_open():
                break
                
            current_positions = {}
            status = "Status: "
            
            for i in connected_motors:
                pos = motor_controller.get_position_ID(i)
                position_buffers[i].append(pos)
                current_positions[i] = pos
                status += f"\nMotor-{i} Position: {pos}"
            
            steps += 1
            
            # 更新GUI（如果存在）
            if gui and gui.is_window_open():
                gui.update_status(steps, current_positions)
                time.sleep(0.1)  # 给GUI一些时间更新
            else:
                # 如果没有GUI，打印状态（可选）
                print(f"Step {steps}/{max_steps}: {current_positions}")
                time.sleep(0.05)  # 稍微慢一点以便观察

    except KeyboardInterrupt:
        print("\nLearning interrupted by user")
    except Exception as e:
        print(f"Error during learning: {e}")
    finally:
        # 清理GUI
        if gui:
            gui.close_window()
        
        # 恢复电机设置
        for i in connected_motors:
            motor_controller.enable_torque_ID(i)
            motor_controller.set_position_ID(startPos[connected_motors.index(i)], i)

        easygui.msgbox(f"Learning Completed! Recorded {steps} steps.", "", ok_button="Continue?")


def save_motion():
    path = easygui.filesavebox(
        filetypes=["*.json"], title="save motion", msg="saving motion to file"
    )

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
    "Start Learning": lambda: start_learning(max_learning_steps),
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
