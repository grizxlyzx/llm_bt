import numpy as np


class PIDController:
    def __init__(
            self,
            kp,
            ki,
            kd,
            target,
            max_output=1,
            min_output=-1,
            proportional_on_measurement=False,
            differential_on_measurement=False
    ):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self._target = target
        self._max_output = max_output
        self._min_output = min_output
        self.proportional_on_measurement = proportional_on_measurement
        self.differential_on_measurement = differential_on_measurement

        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        self._last_input = None
        self._last_error = None
        self.reset()

    def __call__(self, input_, dt=0.02):
        error = self._target - input_
        d_input = (input_ - self._last_input) if self._last_input is not None else 0
        d_error = (error - self._last_error) if self._last_error is not None else 0
        # Proportional
        if not self.proportional_on_measurement:
            self._proportional = self.kp * error
        else:
            self._proportional -= self.kp * d_input
        # Integral
        self._integral += self.ki * error * dt
        self._integral = np.clip(self._integral, self._min_output, self._max_output)
        # Derivative
        if not self.differential_on_measurement:
            self._derivative = self.kd * d_error / dt
        else:
            self._derivative = -self.kd * d_input / dt
        # sum components
        output = self._proportional + self._integral + self._derivative
        output = np.clip(output, self._min_output, self._max_output)
        # update states
        self._last_input = input_
        self._last_error = error

        return output

    def reset(self):
        self._proportional = 0
        self._integral = 0
        self._derivative = 0
        self._last_input = None
        self._last_error = None

    def set_target(self, target):
        self._target = target