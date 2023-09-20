import numpy as np
from pid_controller import PIDController


class AttitudeController(PIDController):
    def __init__(self, target):
        super().__init__(
            kp=0.9,
            ki=0.5,
            kd=0.5,
            target=target,
            max_output=1,
            min_output=-1,
            proportional_on_measurement=False,
            differential_on_measurement=False
        )

    def __call__(self, state, dt=0.02):
        angle_norm = state[4] / np.pi
        orientation_engine = super().__call__(angle_norm, dt)
        orientation_engine /= 2
        orientation_engine += (0.5 * np.sign(orientation_engine))
        return np.array([0, -orientation_engine])


class AltitudeController(PIDController):
    def __init__(self, target):
        super().__init__(
            kp=0.8,
            ki=0.8,
            kd=0.7,
            target=target,
            max_output=1,
            min_output=0,
            proportional_on_measurement=False,
            differential_on_measurement=False
        )

    def __call__(self, state, dt=0.02):
        alt_norm = state[1] / 1.5
        main_engin = super().__call__(alt_norm, dt)

        return np.array([main_engin, 0])


class HorizontalPositionController(PIDController):
    def __init__(self, target):
        super().__init__(
            kp=0.5,
            ki=0.0,
            kd=0.8,
            target=target,
            max_output=np.pi / 4,
            min_output=- np.pi / 4,
            proportional_on_measurement=False,
            differential_on_measurement=False
        )

    def __call__(self, state, dt=0.02):
        x_norm = state[0]
        expected_ang = super().__call__(x_norm, dt)
        return -expected_ang


class HoverInPlaceController(PIDController):
    def __init__(self):
        super().__init__(
            kp=0.8,
            ki=0.8,
            kd=0.7,
            target=0.,
            max_output=1,
            min_output=0,
            proportional_on_measurement=False,
            differential_on_measurement=False
        )