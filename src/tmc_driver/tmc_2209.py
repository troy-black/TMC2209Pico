#pylint: disable=too-many-arguments
#pylint: disable=too-many-instance-attributes
#pylint: disable=too-many-positional-arguments
#pylint: disable=no-member
#pylint: disable=wildcard-import
#pylint: disable=unused-wildcard-import
"""Tmc2209 stepper driver module
"""

import statistics
from .tmc_220x import *
from ._tmc_stallguard import StallGuard
from .reg._tmc2209_reg import *


class Tmc2209(Tmc220x, StallGuard):
    """Tmc2209"""



# Constructor/Destructor
# ----------------------------
    def __init__(self,
                    tmc_ec:TmcEnableControl,
                    tmc_mc:TmcMotionControl,
                    tmc_com:TmcCom = None,
                    driver_address:int = 0,
                    gpio_mode = None,
                    loglevel:Loglevel = Loglevel.INFO,
                    logprefix:str = None,
                    log_handlers:list = None,
                    log_formatter:logging.Formatter = None
                    ):
        """constructor

        Args:
            tmc_ec (TmcEnableControl): enable control object
            tmc_mc (TmcMotionControl): motion control object
            tmc_com (TmcCom, optional): communication object. Defaults to None.
            driver_address (int, optional): driver address [0-3]. Defaults to 0.
            gpio_mode (enum, optional): gpio mode. Defaults to None.
            loglevel (enum, optional): loglevel. Defaults to None.
            logprefix (str, optional): log prefix (name of the logger).
                Defaults to None (standard TMC prefix).
            log_handlers (list, optional): list of logging handlers.
                Defaults to None (log to console).
            log_formatter (logging.Formatter, optional): formatter for the log messages.
                Defaults to None (messages are logged in the format
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s').
        """
        super().__init__(tmc_ec, tmc_mc, tmc_com, driver_address, gpio_mode, loglevel, logprefix, log_handlers, log_formatter)

        if tmc_com is not None:

            registers_classes = {
                TCoolThrs,
                SGThrs,
                SGResult,
            }

            for register_class in registers_classes:
                register = register_class(self.tmc_com)
                name = register.name.lower()
                self.tmc_registers[name] = register

                def create_getter(name):
                    def getter(self):
                        return self.tmc_registers[name]
                    return getter

                setattr(self.__class__, name, property(create_getter(name)))

        self.tmc_logger.log("TMC2209 Init finished", Loglevel.INFO)



    def __del__(self):
        """destructor"""
        if self._deinit_finished is False:
            if self._pin_stallguard is not None:
                tmc_gpio.gpio_remove_event_detect(self._pin_stallguard)
                tmc_gpio.gpio_cleanup(self._pin_stallguard)

        super().__del__()



# Tmc2209 methods
# ----------------------------
    def do_homing(self, diag_pin, revolutions = 10, threshold = 100, speed_rpm = None) -> bool:
        """homes the motor in the given direction using stallguard.
        this method is using vactual to move the motor and an interrupt on the DIAG pin

        Args:
            diag_pin (int): DIAG pin number
            revolutions (int): max number of revolutions. Can be negative for inverse direction
                (Default value = 10)
            threshold (int): StallGuard detection threshold (Default value = None)
            speed_rpm (float):speed in revolutions per minute (Default value = None)

        Returns:
            not homing_failed (bool): true when homing was successful
        """
        if self.tmc_com is None:
            self.tmc_logger.log("do_homing only works with VActual register control via COM", Loglevel.ERROR)
            return False

        self.tmc_logger.log(f"Stallguard threshold: {threshold}", Loglevel.DEBUG)

        if speed_rpm is None:
            speed_rpm = tmc_math.steps_to_rps(self.tmc_mc.max_speed_homing, self.tmc_mc.steps_per_rev)*60

        self.tmc_logger.log("---", Loglevel.INFO)
        self.tmc_logger.log("homing", Loglevel.INFO)

        # StallGuard only works with StealthChop
        self.set_spreadcycle(0)

        mc_homing = TmcMotionControlVActual()
        mc_homing.init(self.tmc_logger)
        mc_homing.tmc_com = self.tmc_com

        self.set_stallguard_callback(diag_pin, threshold, mc_homing.stop,
                                    0.5*tmc_math.rps_to_steps(speed_rpm/60, self.tmc_mc.steps_per_rev))

        homing_failed = mc_homing.set_vactual_rpm(speed_rpm, revolutions=revolutions)

        if homing_failed:
            self.tmc_logger.log("homing failed", Loglevel.INFO)
        else:
            self.tmc_logger.log("homing successful",Loglevel.INFO)

        self.tmc_mc.current_pos = 0

        self.tmc_logger.log("---", Loglevel.INFO)
        return not homing_failed



    def do_homing2(self, revolutions = 10, threshold = 100):
        """homes the motor in the given direction using stallguard
        old function, uses STEP/DIR to move the motor and pulls the StallGuard result
        from the interface

        Args:
            revolutions (int): max number of revolutions. Can be negative for inverse direction
            threshold (int, optional): StallGuard detection threshold (Default value = None)
        """
        if not isinstance(self.tmc_mc, TmcMotionControlStepDir):
            self.tmc_logger.log("do_homing2 only works with STEP/DIR Control", Loglevel.ERROR)
            return
        sgresults = []

        self.tmc_logger.log("---", Loglevel.INFO)
        self.tmc_logger.log("homing", Loglevel.INFO)

        self.tmc_logger.log(f"Stallguard threshold: {threshold}", Loglevel.DEBUG)

        self.tmc_mc.set_direction_pin(revolutions > 0)

        # StallGuard only works with StealthChop
        self.set_spreadcycle(0)

        self.tmc_mc.target_pos = self.tmc_mc.steps_per_rev * revolutions
        # self._step_interval = 0
        # self._speed = 0.0
        # self._n = 0
        self.tmc_mc.acceleration = 10000
        self.tmc_mc.max_speed = self.tmc_mc.max_speed_homing

        coolstep_thres = tmc_math.steps_to_tstep(self.tmc_mc.max_speed_homing*0.5,
                                                 self.tmc_mc.mres)
        self._set_coolstep_threshold(coolstep_thres)
        self.tmc_mc.compute_new_speed()


        step_counter=0
        #self.tmc_logger.log("Steps per Revolution: {self._steps_per_rev}"")
        while step_counter<self.tmc_mc.target_pos:
            if self.tmc_mc.run_speed(): #returns true, when a step is made
                step_counter += 1
                self.tmc_mc.compute_new_speed()
                sgresult = self.get_stallguard_result()
                sgresults.append(sgresult)
                if len(sgresults)>20:
                    sgresult_average = statistics.mean(sgresults[-6:])
                    if sgresult_average < threshold:
                        break

        if step_counter<self.tmc_mc.steps_per_rev:
            self.tmc_logger.log("homing successful",Loglevel.INFO)
            self.tmc_logger.log(f"Stepcounter: {step_counter}",Loglevel.DEBUG)
            self.tmc_logger.log(str(sgresults),Loglevel.DEBUG)
            self.tmc_mc.current_pos = 0
        else:
            self.tmc_logger.log("homing failed", Loglevel.INFO)
            self.tmc_logger.log(f"Stepcounter: {step_counter}", Loglevel.DEBUG)
            self.tmc_logger.log(str(sgresults),Loglevel.DEBUG)

        self.tmc_logger.log("---", Loglevel.INFO)



# Test methods
# ----------------------------
    def test_stallguard_threshold(self, steps):
        """test method for tuning stallguard threshold

        run this function with your motor settings and your motor load
        the function will determine the minimum stallguard results for each movement phase

        Args:
            steps (int):
        """
        self.tmc_logger.log("---", Loglevel.INFO)
        self.tmc_logger.log("test_stallguard_threshold", Loglevel.INFO)

        self.set_spreadcycle(0)

        min_stallguard_result_accel = 512
        min_stallguard_result_maxspeed = 512
        min_stallguard_result_decel = 512

        self.tmc_mc.run_to_position_steps_threaded(steps, MovementAbsRel.RELATIVE)


        while self.tmc_mc.movement_phase != MovementPhase.STANDSTILL:
            stallguard_result = self.get_stallguard_result()
            self.drvstatus.read()
            cs_actual = self.drvstatus.cs_actual

            self.tmc_logger.log(f"{self.tmc_mc.movement_phase} | {stallguard_result} | {cs_actual}",
                        Loglevel.INFO)

            if (self.tmc_mc.movement_phase == MovementPhase.ACCELERATING and
                stallguard_result < min_stallguard_result_accel):
                min_stallguard_result_accel = stallguard_result
            if (self.tmc_mc.movement_phase == MovementPhase.MAXSPEED and
                stallguard_result < min_stallguard_result_maxspeed):
                min_stallguard_result_maxspeed = stallguard_result
            if (self.tmc_mc.movement_phase == MovementPhase.DECELERATING and
                stallguard_result < min_stallguard_result_decel):
                min_stallguard_result_decel = stallguard_result

        self.tmc_mc.wait_for_movement_finished_threaded()

        self.tmc_logger.log("---", Loglevel.INFO)
        self.tmc_logger.log(f"min StallGuard result during accel: {min_stallguard_result_accel}",
                            Loglevel.INFO)
        self.tmc_logger.log(f"min StallGuard result during maxspeed: {min_stallguard_result_maxspeed}",
        Loglevel.INFO)
        self.tmc_logger.log(f"min StallGuard result during decel: {min_stallguard_result_decel}",
                            Loglevel.INFO)
        self.tmc_logger.log("---", Loglevel.INFO)
