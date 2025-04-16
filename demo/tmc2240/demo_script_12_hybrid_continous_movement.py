"""
test file for testing basic movement
"""

import time
try:
    from src.tmc_driver.tmc_2240 import *
except ModuleNotFoundError:
    from tmc_driver.tmc_2240 import *


print("---")
print("SCRIPT START")
print("---")





#-----------------------------------------------------------------------
# initiate the Tmc2209 class
# use your pins for pin_en, pin_step, pin_dir here
#-----------------------------------------------------------------------
if BOARD == Board.RASPBERRY_PI:
    tmc = Tmc2240(TmcEnableControlPin(26), TmcMotionControlStepPwmDir(13, 19), TmcComSpi(0, 0))
elif BOARD == Board.RASPBERRY_PI5:
    tmc = Tmc2240(TmcEnableControlPin(26), TmcMotionControlStepPwmDir(13, 19), TmcComSpi(0, 0))
elif BOARD == Board.NVIDIA_JETSON:
    tmc = Tmc2240(TmcEnableControlPin(26), TmcMotionControlStepPwmDir(13, 19), TmcComSpi(0, 0))
else:
    # just in case
    tmc = Tmc2240(TmcEnableControlPin(26), TmcMotionControlStepPwmDir(13, 19), TmcComSpi(0, 0))






#-----------------------------------------------------------------------
# set the loglevel of the libary (currently only printed)
# set whether the movement should be relative or absolute
# both optional
#-----------------------------------------------------------------------
tmc.tmc_logger.loglevel = Loglevel.DEBUG
tmc.movement_abs_rel = MovementAbsRel.ABSOLUTE





#-----------------------------------------------------------------------
# these functions change settings in the TMC register
#-----------------------------------------------------------------------
tmc.set_direction_reg(False)
tmc.set_current(300)
tmc.set_interpolation(True)
tmc.set_spreadcycle(False)
tmc.set_microstepping_resolution(2)
tmc.set_toff(5)


print("---\n---")





#-----------------------------------------------------------------------
# these functions read and print the current settings in the TMC register
#-----------------------------------------------------------------------
tmc.read_ioin()
tmc.read_chopconf()
tmc.read_drv_status()
tmc.read_gconf()

print("---\n---")





#-----------------------------------------------------------------------
# set the Acceleration and maximal Speed in fullsteps
#-----------------------------------------------------------------------
tmc.acceleration_fullstep = 1000
tmc.max_speed_fullstep = 250







#-----------------------------------------------------------------------
# activate the motor current output
#-----------------------------------------------------------------------
tmc.set_motor_enabled(True)
print("BEFORE MOVEMENT")
print(f"Temperature:\t{tmc.get_temperature()} °C")
print(f"VSupply:\t{tmc.get_vsupply()} V")



#-----------------------------------------------------------------------
# move the motor
#-----------------------------------------------------------------------

# conventional movement
tmc.run_to_position_fullsteps(200)                              #move to position 200 (fullsteps)
tmc.run_to_position_fullsteps(0)                                #move to position 0

# continous movement using pwm
tmc.tmc_mc.run_speed_pwm_fullstep(250)
time.sleep(5)
tmc.tmc_mc.run_speed_pwm_fullstep(0)
time.sleep(1)
tmc.tmc_mc.run_speed_pwm_fullstep(-250)
time.sleep(5)
tmc.tmc_mc.run_speed_pwm_fullstep(0)

# conventional movement
tmc.run_to_position_fullsteps(200)                              #move to position 200 (fullsteps)
tmc.run_to_position_fullsteps(0)                                #move to position 0


#-----------------------------------------------------------------------
# deactivate the motor current output
#-----------------------------------------------------------------------
print("AFTER MOVEMENT")
print(f"Temperature:\t{tmc.get_temperature()} °C")
print(f"VSupply:\t{tmc.get_vsupply()} V")
tmc.set_motor_enabled(False)

print("---\n---")





#-----------------------------------------------------------------------
# deinitiate the Tmc2209 class
#-----------------------------------------------------------------------
del tmc

print("---")
print("SCRIPT FINISHED")
print("---")
