"""
test file for testing the UART connection
"""

import time
try:
    from src.tmc_driver.tmc_2240 import *
except ModuleNotFoundError:
    from tmc_driver.tmc_2240 import *


print("---")
print("SCRIPT START")
print("---")


tmc:Tmc2240 = None


#-----------------------------------------------------------------------
# initiate the Tmc2209 class
# use your pins for pin_en, pin_step, pin_dir here
#-----------------------------------------------------------------------
if BOARD == Board.RASPBERRY_PI:
    tmc = Tmc2240(None, None, TmcComSpi(0, 0), loglevel=Loglevel.DEBUG)
elif BOARD == Board.RASPBERRY_PI5:
    tmc = Tmc2240(None, None, TmcComSpi(0, 0), loglevel=Loglevel.DEBUG)
elif BOARD == Board.NVIDIA_JETSON:
    tmc = Tmc2240(None, None, TmcComSpi(0, 0), loglevel=Loglevel.DEBUG)
else:
    # just in case
    tmc = Tmc2240(None, None, TmcComSpi(0, 0), loglevel=Loglevel.DEBUG)


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
# these functions read and print the current settings in the TMC register
#-----------------------------------------------------------------------
tmc.read_ioin()
tmc.read_chopconf()
tmc.read_drv_status()
tmc.read_gconf()

print("---\n---")

# you can either read the register like this:
# unfortunately you need to know the names of the register for this method
# because they are generated at runtime and therefore not available in the IDE as a suggestion
tmc.adcv_supply_ain.read()
tmc.adcv_supply_ain.log(tmc.tmc_logger)

tmc.adc_temp.read()
tmc.adc_temp.log(tmc.tmc_logger)

print("---\n---")

# or use the wrapper functions in the Tmc2240 class
print(f"Temperature:\t{tmc.get_temperature()} °C")
print(f"VSupply:\t{tmc.get_vsupply()} V")

print("---\n---")


#-----------------------------------------------------------------------
# deinitiate the Tmc2209 class
#-----------------------------------------------------------------------
del tmc

print("---")
print("SCRIPT FINISHED")
print("---")
