#pylint: disable=too-many-instance-attributes
#pylint: disable=too-many-arguments
#pylint: disable=too-many-branches
#pylint: disable=too-many-positional-arguments
"""
STEP_PWM/DIR Motion Control module
"""

import time
from ._tmc_mc import TmcMotionControl, MovementAbsRel, Direction, StopMode
from .._tmc_logger import TmcLogger, Loglevel
from .._tmc_gpio_board import tmc_gpio, Gpio, GpioMode


class TmcMotionControlStepPwmDir(TmcMotionControl):
    """STEP_PWM/DIR Motion Control class"""

    _pin_step:int = None
    _pin_dir:int = None


    @property
    def pin_step(self):
        """_pin_step property"""
        return self._pin_step

    @property
    def pin_dir(self):
        """_pin_dir property"""
        return self._pin_dir

    @property
    def speed(self):
        """_speed property"""
        return self._speed

    @speed.setter
    def speed(self, speed:int):
        """_speed setter"""
        self._speed = speed
        tmc_gpio.gpio_pwm_set_frequency(self._pin_step, self._speed)
        self._tmc_logger.log(f"Speed: {self._speed} µsteps/s", Loglevel.DEBUG)

    @property
    def speed_fullstep(self):
        """_speed property"""
        return self._speed * self.mres

    @speed_fullstep.setter
    def speed_fullstep(self, speed:int):
        """_speed setter"""
        self.speed = speed * self.mres


    def __init__(self, pin_step:int, pin_dir:int):
        """constructor"""
        self._pin_step = pin_step
        self._pin_dir = pin_dir


    def init(self, tmc_logger:TmcLogger):
        """init: called by the Tmc class"""
        super().init(tmc_logger)
        self._tmc_logger.log(f"STEP Pin: {self._pin_step}", Loglevel.DEBUG)
        tmc_gpio.gpio_pwm_setup(self._pin_step, 1, 0)

        self._tmc_logger.log(f"DIR Pin: {self._pin_dir}", Loglevel.DEBUG)
        tmc_gpio.gpio_setup(self._pin_dir, GpioMode.OUT, initial=self._direction.value)


    def __del__(self):
        """destructor"""
        if self._pin_step is not None:
            tmc_gpio.gpio_cleanup(self._pin_step)
        if self._pin_dir is not None:
            tmc_gpio.gpio_cleanup(self._pin_dir)


    def make_a_step(self):
        """method that makes on step

        for the TMC2209 there needs to be a signal duration of minimum 100 ns
        """
        tmc_gpio.gpio_output(self._pin_step, Gpio.HIGH)
        time.sleep(1/1000/1000)
        tmc_gpio.gpio_output(self._pin_step, Gpio.LOW)
        time.sleep(1/1000/1000)

        # self._tmc_logger.log("one step", Loglevel.MOVEMENT)
        self._tmc_logger.log(f"one step | cur: {self.current_pos} | tar: {self._target_pos}", Loglevel.MOVEMENT)


    def set_direction(self, direction:Direction):
        """sets the motor shaft direction to the given value: 0 = CCW; 1 = CW

        Args:
            direction (bool): motor shaft direction: False = CCW; True = CW
        """
        super().set_direction(direction)
        tmc_gpio.gpio_output(self._pin_dir, direction.value)


    def run_to_position_steps(self, steps, movement_abs_rel:MovementAbsRel = None) -> StopMode:
        """runs the moptor
        blocks the code until finished or stopped from a different thread!
        returns true when the movement if finished normally and false,
        when the movement was stopped

        Args:
            steps (int): amount of steps; can be negative
            movement_abs_rel (enum): whether the movement should be absolut or relative
                (Default value = None)

        Returns:
            stop (enum): how the movement was finished
        """
        tmc_gpio.gpio_pwm_set_duty_cycle(self._pin_step, 50)
        time.sleep(5)
        tmc_gpio.gpio_pwm_set_duty_cycle(self._pin_step, 0)
        return self._stop


    def run_speed(self, speed:int):
        """runs the motor
        does not block the code
        """
        if speed == 0:
            # stop movement
            tmc_gpio.gpio_pwm_set_duty_cycle(self._pin_step, 0)
        else:
            if speed < 0:
                self.set_direction(Direction.CCW)
                speed = -speed
            else:
                self.set_direction(Direction.CW)

            # change pwm frequency
            self.speed = speed
            tmc_gpio.gpio_pwm_set_duty_cycle(self._pin_step, 50)


    def run_speed_fullstep(self, speed:int):
        """runs the motor
        does not block the code
        """
        self.run_speed(speed * self.mres)
