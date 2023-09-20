from pybehaviac.utils import *
from pybehaviac.nl_format import *



def or_node(id_, depth, cmt, **kwargs):
    indent = depth * INDENT
    return f'{indent}[OR{SEP}{ID_IND}{id_}]{SEP}{cmt}{SEG}' \
           f'{"".join(kwargs["children"])}' \
           f'{indent}[END_OR]{SEG}'

def or_node_et(**kwargs):
    et_node = etree.Element('Node')
    et_node.set('Class', 'PluginBehaviac.Nodes.Or')
    et_node.set('Enable', 'true')
    et_node.set('HasOwnPrefabData', 'false')
    et_node.set('Id', kwargs['id'])
    et_node.set('PrefabName', '')
    et_node.set('PrefabNodeId', '-1')
    conn = connector_et('Conditions')
    for child in kwargs['children']:
        conn.append(child)
    et_node.append(comment_et(kwargs['cmt']))
    et_node.append(conn)
    return et_node

or_node.et = or_node_et


def and_node(id_, depth, cmt, **kwargs):
    indent = depth * INDENT
    return f'{indent}[AND{SEP}{ID_IND}{id_}]{SEP}{cmt}{SEG}' \
           f'{"".join(kwargs["children"])}' \
           f'{indent}[END_AND]{SEG}'

def and_node_et(**kwargs):
    et_node = etree.Element('Node')
    et_node.set('Class', 'PluginBehaviac.Nodes.And')
    et_node.set('Enable', 'true')
    et_node.set('HasOwnPrefabData', 'false')
    et_node.set('Id', kwargs['id'])
    et_node.set('PrefabName', '')
    et_node.set('PrefabNodeId', '-1')
    conn = connector_et('Conditions')
    for child in kwargs['children']:
        conn.append(child)
    et_node.append(comment_et(kwargs['cmt']))
    et_node.append(conn)
    return et_node

and_node.et = and_node_et


def true_leaf(id_, depth, cmt, **kwargs):
    indent = depth * INDENT
    return f'{indent}[SUCCESS{SEP}{ID_IND}{id_}]{SEP}{cmt}{SEG}'

def true_leaf_et(**kwargs):
    et_node = etree.Element('Node')
    et_node.set('Class', 'PluginBehaviac.Nodes.True')
    et_node.set('Enable', 'true')
    et_node.set('HasOwnPrefabData', 'false')
    et_node.set('Id', kwargs['id'])
    et_node.set('PrefabName', '')
    et_node.set('PrefabNodeId', '-1')
    et_node.append(comment_et(kwargs['cmt']))
    return et_node

true_leaf.et = true_leaf_et

def false_leaf(id_, depth, cmt, **kwargs):
    indent = depth * INDENT
    return f'{indent}[FAILURE{SEP}{ID_IND}{id_}]{SEP}{cmt}{SEG}'

def false_leaf_et(**kwargs):
    et_node = etree.Element('Node')
    et_node.set('Class', 'PluginBehaviac.Nodes.False')
    et_node.set('Enable', 'true')
    et_node.set('HasOwnPrefabData', 'false')
    et_node.set('Id', kwargs['id'])
    et_node.set('PrefabName', '')
    et_node.set('PrefabNodeId', '-1')
    et_node.append(comment_et(kwargs['cmt']))
    return et_node

false_leaf.et = false_leaf_et

def condition(id_, depth, cmt, **kwargs):
    indent = depth * INDENT
    opl = kwargs['opl'] + '()' if kwargs['opl_type'] == 'method' else kwargs['opl']
    opr = kwargs['opr'] + '()' if kwargs['opr_type'] == 'method' else kwargs['opr']
    eval_str = evaluation(kwargs['op'], opl, opr)
    # return f'{indent}[CONDITION, {ID_INDICATOR}{id_}] {eval_str} {cmt}{SEG}'
    return f'{indent}[CONDITION{SEP}{ID_IND}{id_}]{SEP}{cmt}{SEG}' \
           f'{indent}{eval_str}{SEG}' \
           f'{indent}[END_CONDITION]{SEG}'

def condition_et(**kwargs):
    op, opl, _, opr, _ = kwargs['evals'][0][0]
    et_node = etree.Element('Node')
    et_node.set('Class', 'PluginBehaviac.Nodes.Condition')
    et_node.set('Enable', 'true')
    et_node.set('HasOwnPrefabData', 'false')
    et_node.set('Id', kwargs['id'])
    et_node.set('Operator', op)  # won't check if there's only one evaluation in the kwargs
    et_node.set('Opl', opl)
    et_node.set('Opr', opr)
    et_node.set('PrefabName', '')
    et_node.set('PrefabNodeId', '-1')
    et_node.append(comment_et(kwargs['cmt']))
    return et_node

condition.et = condition_et

def action(id_, depth, cmt, **kwargs):
    indent = depth * INDENT
    action_str = f'{kwargs["action_name"]}()'
    # return f'{indent}[ACTION{SEP}{ID_INDICATOR}{id_}]{SEP}{parse_operand(action_str)[1]}(){SEP}{cmt}{SEG}'
    return f'{indent}[ACTION{SEP}{ID_IND}{id_}]{SEP}{cmt}{SEG}' \
           f'{indent}{parse_operand(action_str)[1]}(){SEG}' \
           f'{indent}[END_ACTION]{SEG}'

def action_et(**kwargs):
    et_node = etree.Element('Node')
    et_node.set('Class', 'PluginBehaviac.Nodes.Action')
    et_node.set('Enable', 'true')
    et_node.set('HasOwnPrefabData', 'false')
    et_node.set('Id', kwargs['id'])
    et_node.set('Method', f'{AGENT_NAME}{kwargs["actions"][0]}')  # won't check if there's only one action in the kwargs
    et_node.set('PrefabName', '')
    et_node.set('PrefabNodeId', '-1')
    et_node.set('ResultFunctor', '""')  # currently not support, result always use method return
    et_node.set('ResultOption', 'BT_INVALID')
    add_attachments(et_node, kwargs['attachments'])
    et_node.append(comment_et(kwargs['cmt']))
    return et_node

action.et = action_et

def selector(id_, depth, cmt, **kwargs):
    indent = depth * INDENT
    return f'{indent}[SEL{SEP}{ID_IND}{id_}]{SEP}{cmt}{SEG}' \
           f'{"".join(kwargs["children"])}' \
           f'{indent}[END_SEL]{SEG}'

def selector_et(**kwargs):
    et_node = etree.Element('Node')
    et_node.set('Class', 'PluginBehaviac.Nodes.Selector')
    et_node.set('Enable', 'true')
    et_node.set('HasOwnPrefabData', 'false')
    et_node.set('Id', kwargs['id'])
    et_node.set('PrefabName', '')
    et_node.set('PrefabNodeId', '-1')
    conn = connector_et('GenericChildren')
    for child in kwargs['children']:
        conn.append(child)
    et_node.append(comment_et(kwargs['cmt']))
    add_attachments(et_node, kwargs['attachments'])
    et_node.append(conn)
    return et_node

selector.et = selector_et


def if_else(id_, depth, cmt, **kwargs):
    indent = depth * INDENT
    cond_str = kwargs['children'][0]
    if_str = kwargs['children'][1]
    else_str = kwargs['children'][2]
    return f'{indent}[IFELSE{SEP}{ID_IND}{id_}]{SEP}{cmt}{SEG}' \
           f'{indent}[CHECK]{SEG}' \
           f'{cond_str}' \
           f'{indent}[END_CHECK]{SEG}' \
           f'{indent}[IF]{SEG}' \
           f'{if_str}' \
           f'{indent}[END_IF]{SEG}' \
           f'{indent}[ELSE]{SEG}' \
           f'{else_str}' \
           f'{indent}[END_ELSE]{SEG}' \
           f'{indent}[END_IFELSE]{SEG}'

def if_else_et(**kwargs):
    et_node = etree.Element('Node')
    et_node.set('Class', 'PluginBehaviac.Nodes.IfElse')
    et_node.set('Enable', 'true')
    et_node.set('HasOwnPrefabData', 'false')
    et_node.set('Id', kwargs['id'])
    et_node.set('PrefabName', '')
    et_node.set('PrefabNodeId', '-1')
    cond_conn = connector_et('_condition')
    if_conn = connector_et('_if')
    else_conn = connector_et('_else')
    cond_conn.append(kwargs['children'][0])
    if_conn.append(kwargs['children'][1])
    else_conn.append(kwargs['children'][2])  # won't check to see how many children may in the kwargs
    et_node.append(comment_et(kwargs['cmt']))
    add_attachments(et_node, kwargs['attachments'])
    et_node.append(cond_conn)
    et_node.append(if_conn)
    et_node.append(else_conn)

    return et_node

if_else.et = if_else_et


def sequence(id_, depth, cmt, **kwargs):
    indent = depth * INDENT
    return f'{indent}[SEQ{SEP}{ID_IND}{id_}]{SEP}{cmt}{SEG}' \
           f'{"".join(kwargs["children"])}' \
           f'{indent}[END_SEQ]{SEG}'

def sequence_et(**kwargs):
    et_node = etree.Element('Node')
    et_node.set('Class', 'PluginBehaviac.Nodes.Sequence')
    et_node.set('Enable', 'true')
    et_node.set('HasOwnPrefabData', 'false')
    et_node.set('Id', kwargs['id'])
    et_node.set('PrefabName', '')
    et_node.set('PrefabNodeId', '-1')
    conn = connector_et('GenericChildren')
    for child in kwargs['children']:
        conn.append(child)
    et_node.append(comment_et(kwargs['cmt']))
    add_attachments(et_node, kwargs['attachments'])
    et_node.append(conn)
    return et_node

sequence.et = sequence_et


def decorator_not(id_, depth, cmt, **kwargs):
    indent = depth * INDENT
    return f'{indent}[NOT{SEP}{ID_IND}{id_}]{SEP}{cmt}{SEG}' \
           f'{"".join(kwargs["children"])}' \
           f'{indent}[END_NOT]{SEG}'

def decorator_not_et(**kwargs):
    et_node = etree.Element('Node')
    et_node.set('Class', 'PluginBehaviac.Nodes.DecoratorNot')
    et_node.set('DecorateWhenChildEnds', 'false')  # unknown and unused attr
    et_node.set('Enable', 'true')
    et_node.set('HasOwnPrefabData', 'false')
    et_node.set('Id', kwargs['id'])
    et_node.set('PrefabName', '')
    et_node.set('PrefabNodeId', '-1')
    conn = connector_et('GenericChildren')
    conn.append(kwargs['children'][0])  # won't check num of children in kwargs
    et_node.append(comment_et(kwargs['cmt']))
    add_attachments(et_node, kwargs['attachments'])
    et_node.append(conn)
    return et_node

decorator_not.et = decorator_not_et


def comment(cmt_str):
    return f'{CMT_IND} {cmt_str}'

def comment_et(cmt, bg_clr='NoColor'):
    et_node = etree.Element('Comment')
    et_node.set('Background', bg_clr)
    et_node.set('Text', cmt)
    return et_node

def evaluation(op, opl, opr):
    return f'{opl}{STR_OPERATOR_MAP[op]}{opr}'
    # return f'{parse_operand(opl)[1]}{OPERATOR_STR_MAP[op]}{parse_operand(opr)[1]}'

def preconditions(precon: list[Precondition], depth=0):
    # combine all preconditions into oneline expression
    indent = depth * INDENT
    combined = ''
    ids = []
    for pc in precon:
        ids.append(pc.id_)
        op_str = STR_OPERATOR_MAP[pc.logic_op]
        opl = pc.opl + '()' if pc.opl_type == 'method' else pc.opl
        opr = pc.opr + '()' if pc.opr_type == 'method' else pc.opr
        eval_str = evaluation(pc.op, opl, opr)
        if combined == '':
            combined = f'({eval_str})'
        else:
            combined = f'({combined}{op_str}{eval_str})'

    return f'{indent}[PRECONDITION{SEP}{ID_IND}{SEQ_SEP.join(ids)}]{SEG}' \
           f'{indent}{combined}{SEG}' \
           f'{indent}[END_PRECONDITION]{SEG}'

def preconditions_et(**kwargs):
    precon_nodes = []
    for i in range(len(kwargs['ids'])):
        id_ = kwargs['ids'][i]
        logic = kwargs['evals'][i][1]
        logic = OPERATOR_STR_MAP[logic]
        op, opl, _, opr, _ = kwargs['evals'][i][0]
        et_node = etree.Element('Attachment')
        et_node.set('Class', 'PluginBehaviac.Events.Precondition')
        et_node.set('BinaryOperator', logic)
        et_node.set('Enable', 'true')
        et_node.set('Id', id_)
        et_node.set('Operator', op)
        et_node.set('Opl', opl)
        et_node.set('Opr1', '""')
        et_node.set('Opr2', opr)
        et_node.set('Phase', 'Enter')
        et_node.set('PrefabAttachmentId', '-1')
        precon_nodes.append(et_node)
    return precon_nodes

preconditions.et = preconditions_et


def post_action(*args, **kwargs):
    raise NotImplementedError


def connector_et(identifier: str):
    ele = etree.Element('Connector')
    ele.set('Identifier', identifier)
    return ele

def behaviac_root_et(**kwargs):
    et_node = etree.Element('Node')
    et_node.set('Class', 'Behaviac.Design.Nodes.Behavior')
    et_node.set('AgentType', kwargs['agent_type'])
    et_node.set('Domains', '')
    et_node.set('Enable', 'true')
    et_node.set('HasOwnPrefabData', 'false')
    et_node.set('Id', '-1')
    et_node.set('PrefabName', '')
    et_node.set('PrefabNodeId', '-1')
    conn = connector_et('GenericChildren')
    for child in kwargs['children']:
        conn.append(child)
    des_ref = etree.Element('DescriptorRefs')
    des_ref.set('value', '0:')  # don't know what it is...
    et_node.append(comment_et(kwargs['cmt']))
    et_node.append(des_ref)
    et_node.append(conn)
    return et_node


def add_attachments(et_node, attachments):
    for att in attachments:
        et_node.append(att)


STRING_TEMPLATE_MAP = {
    'Or': or_node,
    'And': and_node,
    'True': true_leaf,
    'False': false_leaf,
    'Condition': condition,
    'Action': action,
    'Selector': selector,
    'IfElse': if_else,
    'Sequence': sequence,
    'DecoratorNot': decorator_not
}

NODE_SYMBOL_MAP = {
    'OR': or_node_et,
    'AND': and_node_et,
    'SUCCESS': true_leaf_et,
    'FAILURE': false_leaf_et,
    'CONDITION': condition_et,
    'ACTION': action_et,
    'SEL': selector_et,
    'IFELSE': if_else_et,
    'SEQ': sequence_et,
    'NOT': decorator_not_et,
    'ROOT': behaviac_root_et,
    'PRECONDITION': preconditions_et
}

def make_string(
        node_type,
        node_id,
        cmt,
        precons,
        post_actions,
        depth,
        **node_kwargs
):
    ret = ''
    if precons:
        ret += preconditions(precons, depth)
    ret += STRING_TEMPLATE_MAP[node_type](node_id, depth, cmt, **node_kwargs)
    if post_actions:
        ret += post_actions
    return ret