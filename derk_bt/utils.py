import numpy as np
from types import MethodType
from gym_derk.envs import DerkEnv
from derk_bt.derk_agent import *
from pybehaviac.tree_exce import build_tree

# TEAM SETUP
HOME_TEAM = [
    {   # Player 0
        'primaryColor': '#71cdff',
        'secondaryColor': '#f28c41',
        'ears': 2,
        'eyes': 2,
        'backSpikes': 3,
        'slots': ['Pistol', 'HealingGland', 'Shell'],
    },
    {   # Player 1
        'primaryColor': '#c4e6ff',
        'secondaryColor': '#f28c41',
        'ears': 2,
        'eyes': 2,
        'backSpikes': 3,
        'slots': ['Pistol', 'HealingGland', 'Shell'],
    },
    {   # Player 2
        'primaryColor': '#c4e6ff',
        'secondaryColor': '#f28c41',
        'ears': 2,
        'eyes': 2,
        'backSpikes': 3,
        'slots': ['Pistol', 'HealingGland', 'Shell'],
    }
]
AWAY_TEAM = [
    {   # Player 3
        'primaryColor': '#ff0000',
        'secondaryColor': '#f9fb74',
        'ears': 2,
        'eyes': 2,
        'backSpikes': 3,
        'slots': ['Pistol', 'HealingGland', None]
    },
    {   # Player 4
        'primaryColor': '#ff0000',
        'secondaryColor': '#f9fb74',
        'ears': 2,
        'eyes': 2,
        'backSpikes': 3,
        'slots': ['Pistol', 'HealingGland', None]
    },
    {   # Player 5
        'primaryColor': '#ff0000',
        'secondaryColor': '#f9fb74',
        'ears': 2,
        'eyes': 2,
        'backSpikes': 3,
        'slots': ['Pistol', 'HealingGland', None]
    }
]
SESSION_ARGS = {
    'turbo_mode': False
}
BEHAVIAC_XML_PATH = '/home/zx/projs/llm_bt/derk_bt/behaviac_xml/fighter.xml'


def expand_observation(ob_n):
    """
    expand original observation for each player from 64 to
    i.e. append extra information to the end of the observation of each derk
    appended:
        friend_1_hp = 64
        friend_2_hp = 65
    :param ob_n: ndarray, shape of [6, 64]
    :return: ndarray, shape pf [6, 66]
    """
    num_team = 2
    team_size = 3
    expanded_ob = np.zeros([6, 66], dtype=float)
    expanded_ob[:, :64] = ob_n

    for team in range(num_team):
        for player in range(team_size):
            player_idx = (team * team_size) + player
            ob_idx = 64
            for friend in [x for x in range(team_size) if x != player]:
                friend_idx = (team * team_size) + friend
                expanded_ob[player_idx, ob_idx] = ob_n[friend_idx, 0]  # friend_hp
                ob_idx += 1
    return expanded_ob


def make_env():
    return DerkEnv(
        mode='normal',
        n_arenas=1,
        home_team=HOME_TEAM,
        away_team=AWAY_TEAM,
        session_args=SESSION_ARGS
    )


def make_bt_agent(xml_path=BEHAVIAC_XML_PATH, verbose_tree=False):
    agent = DerkAgent()
    bt = build_tree(xml_path, agent, verbose_tree=verbose_tree)

    # bind behaviour tree to agent's action
    def step_with_bt(self: DerkAgent, ob):
        self._ob = ob
        self.update_focus_on()
        self.reset_action()
        bt.tick()
        return self._action

    agent.step = MethodType(step_with_bt, agent)
    return agent




