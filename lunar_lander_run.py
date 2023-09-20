import gymnasium as gym
import numpy as np

from lunar_lander_controllers import *

def run():
    env = gym.make(
        "LunarLander-v2",
        continuous=True,
        gravity=-2.,
        enable_wind=True,
        wind_power=15.0,
        turbulence_power=1.5,
        render_mode='human'
    )
    observation, info = env.reset()
    att_ctl = AttitudeController(0.)
    alt_ctl = AltitudeController(0.2)
    hor_ctl = HorizontalPositionController(0.0)
    while True:
        action = np.array([0., 0.])
        expected_ang = hor_ctl(observation)
        att_ctl.set_target(expected_ang)
        action += att_ctl(observation)
        action += alt_ctl(observation)
        print(expected_ang)
        print(observation)
        observation, reward, terminated, truncated, info = env.step(action)
        if terminated:
            observation, info = env.reset()

    env.close()



if __name__ == '__main__':
    run()
