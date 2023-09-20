import numpy as np
from pybehaviac.utils import *


PISTOL_RANGE = 0.32


class DerkAgent:
    def __init__(self):
        self._ob = None
        self.focus_on = None

        self._action = [
            np.array(0.),
            np.array(0.),
            np.array(0.),
            0,
            0
        ]

    def reset_action(self):
        self._action = [
            np.array(0.),
            np.array(0.),
            np.array(0.),
            0,
            0
        ]

    def update_focus_on(self):
        self.focus_on = None if self._ob[16] == 0 else self.focus_on

    def _try_to_focus(self):
        pass

    def step(self, ob):
        raise NotImplementedError('step() should be overridden or replaced')

    def reset(self):
        self._ob = None
        self.focus_on = None

        self._action = [
            np.array(0.),
            np.array(0.),
            np.array(0.),
            0,
            0
        ]

    # do things that can be done within one frame (multiple things can be done within one frame)
    def do_nothing(self):
        self._action[0] = np.array(0.)
        self._action[1] = np.array(0.)
        self._action[2] = np.array(0.)
        self._action[3] = 0
        self._action[4] = 0
        return EBTStatus.BT_SUCCESS

    def do_use_arm_weapon(self):
        self._action[3] = 1
        return EBTStatus.BT_SUCCESS

    def do_use_tail_weapon(self):
        self._action[3] = 2
        return EBTStatus.BT_SUCCESS

    def do_chase_focus(self):
        self._action[2] = 1
        return EBTStatus.BT_SUCCESS

    def do_move_backwards(self):
        self._action[0] = -1
        return EBTStatus.BT_SUCCESS

    def do_facing_focus(self):
        focus_relative_rotation = self._ob[17]
        if abs(focus_relative_rotation) < 0.5:
            self._action[1] = -focus_relative_rotation * 0.2
        else:
            self._action[1] = -focus_relative_rotation * 0.6
        return EBTStatus.BT_SUCCESS

    def do_check_self_in_enemy_range(self):
        if min(self._ob[10], self._ob[12], self._ob[14]) > PISTOL_RANGE:
            return EBTStatus.BT_FAILURE
        else:
            return EBTStatus.BT_SUCCESS

    def do_run_away_from_enemy(self):
        enemy_dist = self._ob[[10, 12, 14]]
        enemy_ang = self._ob[[11, 13, 15]]
        enemy_ang = enemy_ang[(enemy_dist < 0.6)]  # get rid of dead and too far away enemies
        enemy_dist = enemy_dist[(enemy_dist < 0.6)]  # (dead enemies have dist of 2. and angle of 0.)
        weights = softmax(-enemy_dist)
        # convert angles to vec:
        sum_x, sum_y = 0, 0
        for i, a in enumerate(enemy_ang):
            sum_x += np.cos(np.pi * a) * weights[i]
            sum_y += np.sin(np.pi * a) * weights[i]
        esc_ang = np.arctan2(-sum_y, -sum_x) / np.pi

        self._action[1] = -esc_ang * 0.1
        self._action[0] = -np.cos(esc_ang)
        return EBTStatus.BT_SUCCESS

    # run an action that takes more than one frame to finish
    def run_focus_on_nearest_enemy(self, include_statu=True):
        focus = 0
        shortest_dist = np.inf
        shortest_ang = None
        enemy_dist_keys = (8, 10, 12, 14) if include_statu else (10, 12, 14)
        for ob_key in enemy_dist_keys:
            # 8: dist of enemy statu
            # 10, 12, 14: dist of enemy 1, 2, 3;
            if self._ob[ob_key] < shortest_dist:
                shortest_dist = self._ob[ob_key]
                shortest_ang = self._ob[ob_key + 1]
                focus = ob_key / 2
        # running one step to ensure focusing on correct target
        if self.focus_on != focus:
            self._action[1] = shortest_ang
            self._action[4] = focus
            self.focus_on = int(focus)
            return EBTStatus.BT_RUNNING
        return EBTStatus.BT_SUCCESS

    def run_focus_on_enemy_statue(self):
        enemy_statue = 4
        enemy_statue_angle = 9
        self._action[4] = enemy_statue
        if self.focus_on != enemy_statue:
            self._action[1] = self._ob[enemy_statue_angle]
            self.focus_on = enemy_statue
            return EBTStatus.BT_RUNNING
        return EBTStatus.BT_SUCCESS


    def run_focus_on_friend_1(self):
        self._action[4] = 2
        if self.focus_on != 2:
            self._action[1] = self._ob[5]
            self.focus_on = 2
            return EBTStatus.BT_RUNNING
        return EBTStatus.BT_SUCCESS

    def run_focus_on_friend_2(self):
        self._action[4] = 3
        if self.focus_on != 3:
            self._action[1] = self._ob[7]
            self.focus_on = 3
            return EBTStatus.BT_RUNNING
        return EBTStatus.BT_SUCCESS

    def run_focus_on_nearest_friend(self):
        focus = 0
        shortest_dist = np.inf
        shortest_ang = None
        friends_dist_keys = (4, 6)
        for ob_keys in friends_dist_keys:
            if self._ob[ob_keys] < shortest_dist:
                shortest_dist = self._ob[ob_keys]
                shortest_ang = self._ob[ob_keys + 1]
                focus = int(ob_keys / 2)

        # running one step to ensure focusing on correct target
        if self.focus_on != focus:
            self._action[1] = shortest_ang
            self._action[4] = focus
            self.focus_on = focus
            return EBTStatus.BT_RUNNING
        else:
            return EBTStatus.BT_SUCCESS

    # get values directly
    def get_self_hp(self):
        return self._ob[0]

    def get_friend_1_hp(self):
        # print('f1 hp:', self._ob[64], end='')
        return self._ob[64]

    def get_friend_2_hp(self):
        # print('f2 hp:', self._ob[65], end='')
        return self._ob[65]

    def get_friend_1_distance(self):
        return self._ob[4]

    def get_friend_2_distance(self):
        return self._ob[6]

    def get_nearest_enemy_distance(self):
        return min(self._ob[10], self._ob[12], self._ob[14])

    def get_nearest_friend_distance(self):
        return min(self._ob[4], self._ob[6])

    def get_focus_hp(self):
        return self._ob[20]

    def get_focus_distance(self):
        if self.focus_on is None:
            raise ValueError('focus on None')
        return self._ob[self.focus_on * 2]

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)