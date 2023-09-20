import re

INDENT = ' '  # indentation, can be empty
SEP = ' '  # separate things in one segment, can not be empty
SEG = '\n'  # separate segments, can not be empty
SEQ_SEP = ','  # separate a sequence of something, can not be empty
CMT_IND = '#'  # comment indicator, can not be empty
ID_IND = 'ID='  # ID Indicator
ID_PLACEHOLDER = '99999'  # Placeholder for new ID
AGENT_NAME = 'Self.DerkAgent::'
STR_OPERATOR_MAP = {
    'Less': ' < ',
    'Greater': ' > ',
    'Equal': ' == ',
    'NotEqual': ' != ',
    'LessEqual': ' <= ',
    'GreaterEqual': ' >= ',
    'Or': ' || ',
    'And': ' && '
}


OPERATOR_STR_MAP = {}
for k, v in STR_OPERATOR_MAP.items():
    OPERATOR_STR_MAP[v] = k


OPERATOR_GROUP = r'(?: <= | >= | == | != | < | > )'
LOGIC_GROUP = r'(?: \|\| | && )'
NODE_GROUP = r'(?:OR|AND|SUCCESS|FAILURE|CONDITION' \
             r'|ACTION|SEL|IFELSE|SEQ|NOT)'
ATTACH_GROUP = r'(?:PRECONDITION|POSTACTION)'
DUMMY_GROUP = r'(?:CHECK|IF|ELSE)'

REGEX_CONST = r'\d+(?:\.\d+)?|BT_SUCCESS|BT_FAILURE'
REGEX_CONST_INT = r'(?=)\d+'
REGEX_ATTR = rf'^(?!BT_SUCCESS$|BT_FAILURE$)(?=.*[^\d\W])(?:{INDENT})*\w+(?!\([\w, ]*\))$'
REGEX_METHOD = r'\w+\([\w, ]*\)'

REGEX_NODE = rf'(?:{INDENT})*\[({NODE_GROUP})(?:{SEP})*' \
             rf'(?:{ID_IND})?(\d+(?:,\d+)*)?\]' \
             rf'(?:{SEP})*(\w+\(.*?\))?(?:{SEP})*(?:{CMT_IND})?\s*(.+)?'
REGEX_ATTACH = rf'(?:{INDENT})*\[({ATTACH_GROUP})(?:{SEP})*' \
               rf'(?:{ID_IND})?(\d+(?:,\d+)*)?\]'
REGEX_DUMMY = rf'(?:{INDENT})*\[({DUMMY_GROUP})\]'
REGEX_TAIL = rf'(?:{INDENT})*\[END_({NODE_GROUP}|{ATTACH_GROUP}|{DUMMY_GROUP})\]'
REGEX_EVAL = rf'(?:{INDENT})*.+({OPERATOR_GROUP}).+'
REGEX_SIMPLE_EVAL = rf'^(?!.*{LOGIC_GROUP}.*)(.+)({OPERATOR_GROUP})(.+)$'
REGEX_ACTION = rf'(?:{INDENT})*({REGEX_METHOD})'

assert SEP != ''
assert SEG != ''

