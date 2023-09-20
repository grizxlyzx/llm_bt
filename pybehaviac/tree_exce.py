from lxml import etree
from types import MethodType
from pybehaviac.nodes_exec import *
from pybehaviac.utils import *




def build_tree(path, agent, verbose_tree=False):
    et_root = read_behaviac_xml(path)

    if verbose_tree:
        def verbose_node(node):
            tick = node.tick

            def verbose_tick(self):
                if self.parent is None:
                    print(f'\n{self.id}->', end='')
                elif self.children:
                    print(f'{self.id}->', end='')
                else:
                    print(f'{self.id}-|', end='')
                return tick()

            node.tick = MethodType(verbose_tick, node)
            return node

    def _dfs_constructor(current_node, parent_node, verbose=verbose_tree):
        assert current_node.tag == 'Node', 'et_node must be a BT Node'
        node_id, node_type, node_kwargs = parse_node(current_node)
        preconditions = []
        post_actions = []
        node_obj = NODE_MAP[node_type](parent_node, agent, node_id, **node_kwargs)

        for child in current_node:
            if child.tag == 'Comment':
                pass

            elif child.tag == 'Attachment':
                attach_type, attach = parse_attachment(child)
                if attach_type == 'Precondition':
                    preconditions.append(attach)
                elif attach_type == 'PostAction':
                    post_actions.append(attach)
                else:
                    raise NotImplementedError

            elif child.tag == 'Connector':
                for c in child:
                    node_obj.add_child(_dfs_constructor(c, node_obj))

            elif child.tag == 'Node':
                raise ValueError('Node directly under node! check what happens in xml')

            else:
                print('unknown tag:', child.tag)
        if preconditions:
            attach_preconditions(node_obj, preconditions)
        if post_actions:
            attach_post_action(node_obj, post_actions)

        if verbose:
            node_obj = verbose_node(node_obj)
        return node_obj

    bt_root = _dfs_constructor(et_root, None)
    return bt_root



