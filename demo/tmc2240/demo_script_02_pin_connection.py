"""
test file for testing the STEP, DIR, EN connection
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
    tmc = Tmc2240(TmcEnableControlPin(26), TmcMotionControlStepDir(13, 19), TmcComSpi(0, 0))
elif BOARD == Board.RASPBERRY_PI5:
    tmc = Tmc2240(TmcEnableControlPin(26), TmcMotionControlStepDir(13, 19), TmcComSpi(0, 0))
elif BOARD == Board.NVIDIA_JETSON:
    tmc = Tmc2240(TmcEnableControlPin(26), TmcMotionControlStepDir(13, 19), TmcComSpi(0, 0))
else:
    # just in case
    tmc = Tmc2240(TmcEnableControlPin(26), TmcMotionControlStepDir(13, 19), TmcComSpi(0, 0))








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


print("---\n---")





#-----------------------------------------------------------------------
# this function test whether the connection of the DIR, STEP and EN pin
# between Raspberry Pi and TMC driver is working
#-----------------------------------------------------------------------
tmc.test_dir_step_en()

print("---\n---")





#-----------------------------------------------------------------------
# deactivate the motor current output
#-----------------------------------------------------------------------
tmc.set_motor_enabled(False)

print("---\n---")





#-----------------------------------------------------------------------
# deinitiate the Tmc2209 class
#-----------------------------------------------------------------------
del tmc

print("---")
print("SCRIPT FINISHED")
print("---")
