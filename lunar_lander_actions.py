from lunar_lander_controllers import *


class LunarLanderActions:
    def __init__(self):
        self.alt_ctl = AltitudeController(1.)
        self.att_ctl = AttitudeController(0.)
        self.hor_ctl = HorizontalPositionController(0.0)

        self.last_ob = None
        self.current_action = None

    def hover(self, state):
        pass

    def change_altitude(self, state):
        pass