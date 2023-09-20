from pybehaviac.tree_nl import *
from llm.gpt import *
from llm.prompts import *


USER_REQ_0 = """\
Modify the tree to meet the requirement: \
If an ally's health is less than or equal 0.1, don't heal it.
The tree is:
"""  # success

USER_REQ_1 = """\
Modify the tree to meet the requirement: \
The range of attack is limited to the range from 0.2 to 0.5.
The tree is:
"""  # 1 success / 2 try

USER_REQ_2 = """\
Modify the tree to meet the requirement: \
When to offense, the agent should always tries to attack the enemy statues \
first if agent's health is above 0.5, otherwise, the agent should follows current \
logics on choosing target.
The tree is:
"""

USER_REQ_3 = """\
Modify the tree to meet the requirement: \
When to heal allies, agent should always heal the ally with the lowest health.
The Tree is:
"""  # success

USER_REQ_4 = """\
Modify the tree to meet the requirement: \
There is no need to runaway from the enemy if the distance between \
the agent and any allies is less than 0.1.
The Tree is:
"""



if __name__ == '__main__':
    ori_path = '/home/zx/projs/llm_bt/derk_bt/behaviac_xml/fighter.xml'
    edi_path = '/home/zx/projs/llm_bt/derk_bt/behaviac_xml/demo_999.xml'

    bt_str = et2nl(ori_path, -1)
    gpt4 = GPT4BTChat(
        model_name='gpt-4-0613',
        temperature=0.5
    )
    usr_1 = f'{USER_REQ_0}{bt_str}'

    result = gpt4(usr_1)
    modi_tree = result.split('[AFTER MODIFIED]:')[-1].strip()
    print(result)

    modi_et = nl2et(modi_tree)
    save_etree(modi_et, edi_path)

