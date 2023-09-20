from abc import ABC, abstractmethod
import types
from pybehaviac.utils import *


# | Attachments
def attach_preconditions(
        node,
        preconditions: list[Precondition]
):
    tick = node.tick
    # build precondition function that combines all preconditions
    precon_func = lambda: EBTStatus.BT_SUCCESS
    for precon in preconditions:
        logic_func = OPERATOR_MAP[precon.logic_op]
        eval_func = evaluation_func_factory(node.agent,
                                            precon.op,
                                            precon.opl,
                                            precon.opl_type,
                                            precon.opr,
                                            precon.opr_type)
        precon_func = lambda p_func=precon_func, e_func=eval_func, l_func=logic_func: l_func(p_func(), e_func())

    def preconditioned_tick(self):
        # didn't implement logic to check and handle when operand returns RUNNING or INVALID
        # just expect all operands to return SUCCESS or FAILURE
        # Nor implement logic to handle different 'when', below implementation equivalents to 'enter'
        if self.running or precon_func() == EBTStatus.BT_SUCCESS:
            return tick()
        else:
            return EBTStatus.BT_FAILURE

    node.tick = types.MethodType(preconditioned_tick, node)


def attach_post_action(node, action_funcs):
    raise NotImplementedError



# Tree nodes
class BaseNode(ABC):
    def __init__(self,
                 parent,
                 agent,
                 id_):
        self.parent = parent
        self.id = id_
        self.children: list[BaseNode] = []
        self.to_tick = 0
        self.running = False
        self.agent = agent

    def add_child(self, child):
        self.children.append(child)

    @abstractmethod
    def tick(self):
        pass


# | Conditions
class Or(BaseNode):
    def __init__(self, parent, agent, id_):
        super(Or, self).__init__(parent, agent, id_)

    def tick(self):
        for child in self.children:
            if child.tick() == EBTStatus.BT_SUCCESS:
                return EBTStatus.BT_SUCCESS
        return EBTStatus.BT_FAILURE


class And(BaseNode):
    def __init__(self, parent, agent, id_):
        super(And, self).__init__(parent, agent, id_)

    def tick(self):
        for child in self.children:
            if child.tick() == EBTStatus.BT_FAILURE:
                return EBTStatus.BT_FAILURE
        return EBTStatus.BT_SUCCESS


# | - > Leaf
class TrueLeaf(BaseNode):
    def __init__(self, parent, agent, id_):
        super(TrueLeaf, self).__init__(parent, agent, id_)

    def tick(self):
        return EBTStatus.BT_SUCCESS


class FalseLeaf(BaseNode):
    def __init__(self, parent, agent, id_):
        super(FalseLeaf, self).__init__(parent, agent, id_)

    def tick(self):
        return EBTStatus.BT_FAILURE


class Condition(BaseNode):
    def __init__(
            self, parent, agent, id_,
            op: str,
            opl: str,
            opl_type: int,
            opr: str,
            opr_type: int
    ):
        super(Condition, self).__init__(parent, agent, id_)
        self.evaluate_func = evaluation_func_factory(agent, op, opl, opl_type, opr, opr_type)

    def tick(self):
        return self.evaluate_func()


# | ACTIONS
class Action(BaseNode):
    def __init__(self, parent, agent, id_, action_name):
        super(Action, self).__init__(parent, agent, id_)
        self.action = match_operand(self.agent, action_name, 'method')

    def tick(self):
        return self.action()


# | Composites
# | - > Selectors
class Selector(BaseNode):
    def __init__(self, parent, agent, id_):
        super(Selector, self).__init__(parent, agent, id_)

    def tick(self):
        for i in range(self.to_tick, len(self.children)):
            child = self.children[i]
            status = child.tick()
            if status == EBTStatus.BT_SUCCESS:
                self.to_tick = 0
                self.running = False
                return EBTStatus.BT_SUCCESS
            elif status == EBTStatus.BT_RUNNING:
                self.to_tick = i
                self.running = True
                return EBTStatus.BT_RUNNING
        self.to_tick = 0
        self.running = False
        return EBTStatus.BT_FAILURE


# | - > Sequences
class IfElse(BaseNode):
    def __init__(self, parent, agent, id_):
        super(IfElse, self).__init__(parent, agent, id_)
        self.condition = 0

    def tick_child(self):
        return self.children[self.to_tick].tick()

    def tick(self):
        status = self.tick_child()
        if status == EBTStatus.BT_RUNNING:
            self.running = True
            return EBTStatus.BT_RUNNING
        if self.to_tick == 0:  # status is condition returns
            if status == EBTStatus.BT_SUCCESS:
                self.to_tick = 1
            else:
                self.to_tick = 2
            status = self.tick_child()
            if status == EBTStatus.BT_RUNNING:  # child is running
                self.running = True
                return EBTStatus.BT_RUNNING
            else:
                self.to_tick = 0
                self.running = False
                return status
        else:
            self.to_tick = 0
            return status


class Sequence(BaseNode):
    def __init__(self, parent, agent, id_):
        super(Sequence, self).__init__(parent, agent, id_)

    def tick(self):
        for i in range(self.to_tick, len(self.children)):
            child = self.children[i]
            status = child.tick()
            if status == EBTStatus.BT_FAILURE:
                self.running = False
                self.to_tick = 0
                return EBTStatus.BT_FAILURE
            elif status == EBTStatus.BT_RUNNING:
                self.running = True
                self.to_tick = i
                return EBTStatus.BT_RUNNING
        self.running = False
        self.to_tick = 0
        return EBTStatus.BT_SUCCESS

# | - > Decorators
class DecoratorNot(BaseNode):
    def __init__(self, parent, agent, id_):
        super(DecoratorNot, self).__init__(parent, agent, id_)

    def add_child(self, child):
        self.children.append(child)
        assert len(self.children) < 2, 'DecoratorNot can only have one child'

    def tick(self):
        status = self.children[0].tick()
        if status == EBTStatus.BT_SUCCESS:
            self.running = False
            return EBTStatus.BT_FAILURE
        elif status == EBTStatus.BT_FAILURE:
            self.running = False
            return EBTStatus.BT_SUCCESS
        else:
            self.running = True
            return status

NODE_MAP = {
    'Or': Or,
    'And': And,
    'TrueLeaf': TrueLeaf,
    'FalseLeaf': FalseLeaf,
    'Condition': Condition,
    'Action': Action,
    'Selector': Selector,
    'IfElse': IfElse,
    'Sequence': Sequence,
    'DecoratorNot': DecoratorNot
}

ATTACHMENT_MAP = {
    'Precondition': attach_preconditions,
    'PostAction': attach_post_action,
}


