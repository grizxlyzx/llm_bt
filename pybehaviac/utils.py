from dataclasses import dataclass
import re
from enum import Enum
from lxml import etree


class EBTStatus(Enum):
    BT_INVALID = 0
    BT_SUCCESS = 1
    BT_FAILURE = 2
    BT_RUNNING = 3

    def __bool__(self):
        return True if self == EBTStatus.BT_SUCCESS else False


STATUS_MAP = {
    'BT_INVALID': EBTStatus.BT_INVALID,
    'BT_SUCCESS': EBTStatus.BT_SUCCESS,
    'BT_FAILURE': EBTStatus.BT_FAILURE,
    'BT_RUNNING': EBTStatus.BT_RUNNING
}


@dataclass
class Precondition:
    id_: str
    when: str  # 'Enter' or 'Update' or 'Both'
    logic_op: str  # 'or' or 'and'
    op: str
    opl: str
    opl_type: str
    opr: str
    opr_type: str


@dataclass
class PostAction:
    pass


OPERATOR_MAP = {
    'Less': lambda x, y: EBTStatus.BT_SUCCESS if (x < y) else EBTStatus.BT_FAILURE,
    'Greater': lambda x, y: EBTStatus.BT_SUCCESS if (x > y) else EBTStatus.BT_FAILURE,
    'Equal': lambda x, y: EBTStatus.BT_SUCCESS if (x == y) else EBTStatus.BT_FAILURE,
    'NotEqual': lambda x, y: EBTStatus.BT_SUCCESS if (x != y) else EBTStatus.BT_FAILURE,
    'LessEqual': lambda x, y: EBTStatus.BT_SUCCESS if (x <= y) else EBTStatus.BT_FAILURE,
    'GreaterEqual': lambda x, y: EBTStatus.BT_SUCCESS if (x >= y) else EBTStatus.BT_FAILURE,
    'Or': lambda x, y: EBTStatus.BT_SUCCESS if ((x == EBTStatus.BT_SUCCESS) or (y == EBTStatus.BT_SUCCESS)) else EBTStatus.BT_FAILURE,
    'And': lambda x, y: EBTStatus.BT_SUCCESS if ((x == EBTStatus.BT_SUCCESS) and (y == EBTStatus.BT_SUCCESS)) else EBTStatus.BT_FAILURE,
}


def parse_operand(operand_str: str):
    if re.match(parse_operand.const_pattern, operand_str):
        return 'const', operand_str.split()[-1]
    elif re.match(parse_operand.attr_pattern, operand_str):
        return 'attr', operand_str.split('::')[-1]
    elif re.match(parse_operand.method_pattern, operand_str):
        return 'method', re.sub(parse_operand.method_sub, '', operand_str.split('::')[-1])
    else:
        raise ValueError(f'parse_operand: operand_str "{operand_str}" not supported'
                         f'only "const", "attr", "method" are supported')

parse_operand.const_pattern = r'^const (.+) (.+)$'
parse_operand.attr_pattern = r'^([^()]+)$'
parse_operand.method_pattern = r'^([^()]+)\(([^\)]*)\)$'
parse_operand.method_sub = r'\((.*?)\)'


def parse_node(et_node):
    assert et_node.tag == 'Node', 'et_node must be a Node'
    node_type = et_node.attrib['Class'].split('.')[-1]
    node_id = et_node.attrib['Id']
    node_kwargs = {}
    if node_type == 'Condition':
        node_kwargs['op'] = et_node.attrib['Operator']
        node_kwargs['opl_type'], node_kwargs['opl'] = parse_operand(et_node.attrib['Opl'])
        node_kwargs['opr_type'], node_kwargs['opr'] = parse_operand(et_node.attrib['Opr'])
    elif node_type == 'Action':
        action_type, node_kwargs['action_name'] = parse_operand(et_node.attrib['Method'])
        assert action_type == 'method', f'only method action is supported: {et_node.attrib["Method"]}'

    return node_id, node_type, node_kwargs

def parse_attachment(et_node):
    assert et_node.tag == 'Attachment', 'et_node must be an Attachment'
    node_type = et_node.attrib['Class'].split('.')[-1]
    if node_type == 'Precondition':
        opl_type, opl = parse_operand(et_node.attrib['Opl'])
        opr_type, opr = parse_operand(et_node.attrib['Opr2'])  # didn't figure out what Opr1 is...
        precon = Precondition(
            id_=et_node.attrib['Id'],
            when=et_node.attrib['Phase'],
            logic_op=et_node.attrib['BinaryOperator'],
            op = et_node.attrib['Operator'],
            opl = opl,
            opl_type = opl_type,
            opr = opr,
            opr_type = opr_type,
        )
        return node_type, precon
    elif node_type == 'post_action':
        raise NotImplementedError
    else:
        raise NotImplementedError

def match_operand(agent, operand, operand_type):
    if operand_type == 'const':
        if operand in STATUS_MAP:
            operand = STATUS_MAP[operand]
        else:
            operand = float(operand)
        return lambda: operand
    elif operand_type == 'attr':
        return lambda: getattr(agent, operand)
    elif operand_type == 'method':
        return getattr(agent, operand)
    else:
        raise ValueError(f'parse_operand: operand_type "{operand_type}" not supported'
                         f'only "const", "attr", "method" are supported')


def evaluation_func_factory(agent, op, opl, opl_type, opr, opr_type):
    operator = OPERATOR_MAP[op]
    operand_l = match_operand(agent, opl, opl_type)
    operand_r = match_operand(agent, opr, opr_type)
    return lambda: operator(operand_l(), operand_r())


def read_behaviac_xml(path):
    et = etree.parse(path)
    root = et.getroot()

    def find_first_bt_node(et_node):
        for child in et_node:
            if child.tag == 'Node' and child.attrib['Id'] != '-1':
                return child
            found_in_subtree = find_first_bt_node(child)
            if found_in_subtree is not None:
                return found_in_subtree
        return None

    return find_first_bt_node(root)
