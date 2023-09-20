from derk_bt.utils import *


def run():
    env = make_env()
    agents = []
    for _ in range(6):
        if _ == 0:
            agents.append(make_bt_agent(verbose_tree=True))
        else:
            agents.append(make_bt_agent())
    for _ in range(100):
        ob_n = env.reset()
        ob_n = expand_observation(ob_n)
        while True:
            action_n = []
            for p in range(6):
                if ob_n[p][0] == 0:
                    action_n.append([0, 0, 0, 0, 0])
                else:
                    action_n.append(agents[p].step(ob_n[p]))
            ob_n, reward_n, done_n, info_n = env.step(action_n)
            ob_n = expand_observation(ob_n)

            if all(done_n) or (not ob_n[:3, 0].any()) or (not ob_n[3:, 0].any()):
                print('Episode finished')
                for a in agents:
                    a.reset()
                break

    env.close()


if __name__ == '__main__':
    run()

