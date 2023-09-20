import re

from lxml import etree
from pybehaviac.utils import *
from pybehaviac.nodes_nl import *
from pybehaviac.nl_format import *


def et2nl(path, max_expand_depth):
    et_root = read_behaviac_xml(path)

    def _dfs_node_parser(current_node, depth):
        assert current_node.tag == 'Node', 'et_node must be a BT Node'
        node_id, node_type, node_kwargs = parse_node(current_node)
        cmt = ''
        precons = []
        post_acts = []
        children = []
        for child in current_node:
            if child.tag == 'Comment':
                cmt = child.attrib["Text"]
                if cmt != '':
                    cmt = f'# {cmt}'
            elif child.tag == 'Attachment':
                attach_type, attach = parse_attachment(child)
                if attach_type == 'Precondition':
                    precons.append(attach)
                elif attach_type == 'PostAction':
                    post_acts.append(attach)
                else:
                    raise ValueError(f'unknown attachment type: {attach_type}')

            elif child.tag == 'Connector':
                for c in child:
                    children.append(_dfs_node_parser(c, depth + 1))

            elif child.tag == 'Node':
                raise ValueError('Node directly under node! check what happens in xml')

            else:
                raise ValueError(f'unknown tag:{child.tag}')

        node_kwargs['children'] = children
        ret_str = make_string(
            node_type,
            node_id,
            cmt,
            precons,
            post_acts,
            depth,
            **node_kwargs
        )
        return ret_str

    return _dfs_node_parser(et_root, 0)[:-1]  # remove last '\n'


def interpret_operand(operand_str: str):
    if (match := re.search(REGEX_METHOD, operand_str)) is not None:
        operand = match.group().replace(INDENT, '')
        return 'method', f'{AGENT_NAME}{operand}'

    elif (match := re.search(REGEX_ATTR, operand_str)) is not None:
        operand = match.group().replace(INDENT, '')
        return 'attr', f'float {AGENT_NAME}{operand}'

    elif (match := re.search(REGEX_CONST, operand_str)) is not None:
        dtype = 'behaviac::EBTStatus '
        if 'BT_' not in operand_str:
            if '.' not in operand_str:
                dtype = 'int '
            else:
                dtype = 'float '
        operand = match.group()
        return 'const', f'const {dtype}{operand}'

    else:
        raise ValueError(f'Unable to interpret operand: "{operand_str}"')


def interpret_simple_eval(eval_str: str):
    if match := re.match(REGEX_SIMPLE_EVAL, eval_str):
        opl, op, opr = match.groups()
        opl_type, opl_str = interpret_operand(opl)
        opr_type, opr_str = interpret_operand(opr)
        return OPERATOR_STR_MAP[op], opl_str, opl_type, opr_str, opr_type
    else:
        raise ValueError(f'Unable to interpret evaluation: "{eval_str}"')


def interpret_evaluation(precon_str: str):
    logic_ops = [STR_OPERATOR_MAP['And']]
    simple_evals = []
    for i, token in enumerate(re.split(rf'({LOGIC_GROUP})', precon_str)):
        if i % 2 == 0:
            simple_evals.append(interpret_simple_eval(token))
        else:
            logic_ops.append(token)
    assert len(simple_evals) == len(logic_ops)
    return list(zip(simple_evals, logic_ops))


def interpret_segment(seg_str):
    if match := re.match(REGEX_NODE, seg_str):
        sec_type, id_, expr, cmt = match.groups()
        cmt = '' if cmt is None else cmt
        # print(seg_str, '-----head', sec_type, id_, expr, cmt)
        kwargs = {
            'type': sec_type,
            'id': id_,
            'expr': expr,
            'cmt': cmt
        }
        return 'node', kwargs

    elif match := re.match(REGEX_ATTACH, seg_str):
        attach_type, ids = match.groups()
        ids = ids.split(SEQ_SEP)
        kwargs = {
            'type': attach_type,
            'ids': ids
        }
        return 'attach', kwargs

    elif match := re.match(REGEX_DUMMY, seg_str):
        dummy_type = match.groups()
        kwargs = {
            'type': dummy_type
        }
        return 'dummy', kwargs

    elif re.match(REGEX_EVAL, seg_str):
        # print(seg_str, '-----eval')
        evals = interpret_evaluation(seg_str)
        kwargs = {
            'evals': evals
        }
        return 'evals', kwargs

    elif match := re.match(REGEX_ACTION, seg_str):
        act_name = match.groups()[0].strip()
        # print(seg_str, '-----action', act_name)
        kwargs = {
            'act_name': act_name
        }
        return 'action', kwargs

    elif match := re.match(REGEX_TAIL, seg_str):
        end_of = match.groups()[0]
        # print(seg_str, '-----end of:', end_of)
        kwargs = {
            'end_of': end_of
        }
        return 'tail', kwargs

    else:
        print(seg_str, '-----UNMATCHED!!!')
        kwargs = {}
        return 'unmatched', kwargs




def nl2et(nl_str: str):
    segments = nl_str.split(SEG)
    seg_idx = -1
    max_id = -1

    def check_uid(component_kwargs):
        nonlocal max_id
        if 'id' in component_kwargs:
            ids = [component_kwargs['id']]
            single_id = True
        elif 'ids' in component_kwargs:
            ids = component_kwargs['ids']
            single_id = False
        else:
            return
        new_ids = []
        for id_ in ids:
            if id_ == ID_PLACEHOLDER:
                max_id += 1
                new_ids.append(str(max_id))
            elif (int_id := int(id_)) > max_id:
                max_id = int_id
                new_ids.append(id_)
            elif (int_id := int(id_)) == max_id:
                print(f'Warning: repeat ID: {int_id}')
            else:
                new_ids.append(id_)
        if single_id:
            component_kwargs['id'] = new_ids[0]
        else:
            component_kwargs['ids'] = new_ids
        return


    def build_element(node_kwargs):
        child_attach = []
        children = []
        evals = []
        actions = []
        nonlocal segments
        nonlocal seg_idx

        while True:
            if seg_idx == 122:
                print()
            seg_idx += 1
            if seg_idx >= len(segments):
                seg_type = 'tail'
                kwargs = {
                    'end_of': f'{node_kwargs["type"]}'
                }
            else:
                seg_str = segments[seg_idx]
                seg_type, kwargs = interpret_segment(seg_str)

            if seg_type == 'node':
                # print(kwargs['type'])
                kwargs['attachments'] = child_attach
                child_attach = []
                children.append(build_element(kwargs))

            elif seg_type == 'attach':
                child_attach += build_element(kwargs)

            elif seg_type == 'dummy':
                continue

            elif seg_type == 'evals':
                evals += kwargs['evals']

            elif seg_type == 'action':
                actions.append(kwargs['act_name'])

            elif seg_type == 'tail':
                # node_kwargs['attachments'] = child_attach
                node_kwargs['children'] = children
                node_kwargs['evals'] = evals
                node_kwargs['actions'] = actions
                # print(seg_str)
                node_type = node_kwargs['type']

                if node_type == kwargs['end_of']:
                    check_uid(node_kwargs)
                    node_func = NODE_SYMBOL_MAP[node_type]
                    return node_func(**node_kwargs)
                else:
                    print(node_type, '!=', kwargs['end_of'])
                    continue

            elif seg_type == 'unmatched':
                # raise ValueError('segment unmatched')
                continue
            else:
                raise ValueError('unknown type of segment')


    root_kwargs = {
        'type': 'ROOT',
        'agent_type': 'DerkAgent',
        'cmt': ''
    }
    et_root = build_element(root_kwargs)
    behaviour_root = etree.Element('Behavior')
    behaviour_root.set('Version', '5')
    behaviour_root.set('NoError', 'true')
    behaviour_root.append(et_root)
    return behaviour_root


def save_etree(root, path):
    tree = etree.ElementTree(root)
    with open(path, 'wb') as file:
        tree.write(file, pretty_print=True, xml_declaration=True, encoding='utf-8')
    tree.write(path, pretty_print=True, xml_declaration=True, encoding='utf-8')


if __name__ == '__main__':
    ori_path = '/home/zx/projs/llm_bt/derk_bt/behaviac_xml/fighter.xml'
    edi_path = '/home/zx/projs/llm_bt//derk_bt/behaviac_xml/interpreter_test.xml'
    nl = et2nl(ori_path, -1)
    nl = nl.replace('ID=1]', 'ID=99999]')
    et = nl2et(nl)
    save_etree(et, edi_path)
    print(nl)

    # s1 = '(((get_friend_1_hp(a, b) > 0) || focus_on == BT_SUCCESS) && get_nearest_friend_distance() <= 0.32)'
    # s2 = 'get_self_hp < 0.5'
    # oper = interpret_simple_eval('get_self_1_hp(w, a) <= 5.1')
    # ret = interpret_evaluation(s1)
    # node = etree.Element('Node')
    # node.append(etree.Element('Node'))
    # node.set('foo', 'bar')
    # a = node[0]


