from dxl_ax12a import AX12a

device_name='com3'

motor = AX12a(devicename=device_name)

connected_motors=[0,1,2]

moving_speeds=[200,200,200]

initial_positions=[512,512,512]

steps=[0,0,0]

step_sizes=[5,-5,5]

max_steps=300

motor.set_initial_state(connected_motors, moving_speeds, initial_positions)

max_iteration=100

current_iteration=0

#for i in range(max_iteration):


while current_iteration<max_iteration:
    for m in connected_motors:
        index=connected_motors.index(m)
        init_pos=initial_positions[index]
        stp=steps[index]
        goal_pos=init_pos+stp
        motor.set_position_ID(dxl_goal_position=goal_pos,index=m)

        if stp>=max_steps or stp <=-max_steps:
            step_sizes[index]=-step_sizes[index]

        steps[index]+=step_sizes[index]

    current_iteration+=1










