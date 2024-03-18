#!/usr/bin/env python3

import ply.lex as lex
import ply.yacc as yacc
import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.sax.saxutils import escape
import argparse
import sys

arg_parser = argparse.ArgumentParser(description='Tokenize a file')
arg_parser.add_argument('input', type=str, help='File to tokenize')
arg_parser.add_argument('output', nargs='?', type=str, help='Output file name', default='out.xml')
arg_parser.add_argument('-d', '--debug', action='store_true', help='Print debug information')
arg_parser.add_argument('-n', '--name', type=str, help='Program name')
args = arg_parser.parse_args()

xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
doctype_declaration = '<!DOCTYPE program [\n' \
                      '  <!ELEMENT program (tac+)>\n' \
                      '  <!ELEMENT tac (dst?,src1?,src2?)>\n' \
                      '  <!ELEMENT dst (#PCDATA)>\n' \
                      '  <!ELEMENT src1 (#PCDATA)>\n' \
                      '  <!ELEMENT src2 (#PCDATA)>\n' \
                      '  <!ATTLIST program name CDATA #IMPLIED>\n' \
                      '  <!ATTLIST tac opcode CDATA #REQUIRED>\n' \
                      '  <!ATTLIST tac order CDATA #REQUIRED>\n' \
                      '  <!ATTLIST dst type (integer|string|variable|label) #REQUIRED>\n' \
                      '  <!ATTLIST src1 type (integer|string|variable) #REQUIRED>\n' \
                      '  <!ATTLIST src2 type (integer|string|variable) #REQUIRED>\n' \
                      '  <!ENTITY language "IPPeCode">\n' \
                      '  <!ENTITY eol "&#xA;">\n' \
                      '  <!ENTITY lt "&lt;">\n' \
                      '  <!ENTITY gt "&gt;">\n' \
                      ']>\n'

flag_for_error = False
actions = []

def print_debug(*_args, **kwargs):
    if args.debug:
        print(*_args, **kwargs)

def print_error(*_args, **kwargs):
    print(*_args, file=sys.stderr, **kwargs)
    sys.exit(1)

# List of token names
tokens = (
    'OPCODE', 'REGISTER', 'INTEGER', 'LABEL', 'COMMENT', 'STRING' 
)

# Regular expressions with enhanced parsing
def t_OPCODE(t):
    r'MOV|LABEL|ADD|SUB|MUL|DIV|READINT|READSTR|PRINT|PRINTLN|JUMPIFEQ|JUMPIFLT|JUMP|CALL|RETURN|PUSH|POP'
    return t

def t_REGISTER(t):
    r'[a-zA-Z]+[a-zA-Z0-9]*'
    return t

def t_INTEGER(t):
    r'[+\-]?\d+'
    t.value = int(t.value)
    return t

def t_LABEL(t):
    r'@\w+'
    return t

# Discard comments
def t_COMMENT(t):
    r'\#.*'
    pass 

def t_STRING(t):
    r'"([^"\\]|\\.)*"' 
    t.value = t.value[1:-1]
    return t

# Track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Whitespace handling
t_ignore = ' \t'

# Error handling 
def t_error(t):
    global flag_for_error
    print_error("Illegal character: %r on line %d" % (repr(t.value[0]), t.lexer.lineno))
    flag_for_error = True
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

def xml_escape(text):
    text = escape(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('\\n', '&eol;')
    return text

# Parsing rules
def p_program(p):
    'program : tac_list'
    program_name = args.name if args.name else "$language$ Program"
    root = ET.Element("program", name=program_name)
    for i, action in enumerate(actions, 1):
        tac = ET.SubElement(root, "tac", opcode=action['opcode'], order=str(i))
        if 'dst' in action:
            dst = ET.SubElement(tac, "dst", type=action['dst_type'])
            dst.text = xml_escape(action['dst'])
        if 'src1' in action:
            src1 = ET.SubElement(tac, "src1", type=action['src1_type'])
            src1.text = xml_escape(action['src1'])
        if 'src2' in action:
            src2 = ET.SubElement(tac, "src2", type=action['src2_type'])
            src2.text = xml_escape(action['src2'])
    # XML string
    global flag_for_error
    if not flag_for_error:
        xml_str = minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent="  ")
        xml_content = xml_declaration + doctype_declaration + xml_str.split('\n', 1)[1].replace('$language$', '&language;')
        print_debug(xml_content)
        if args.output != '-':
            with open(args.output, 'w') as file:
                print_debug(f"Writing to {args.output}")
                file.write(xml_content)
        else:
            print(xml_content)

def p_tac_list_1(p):
    'tac_list : tac tac_list'

def p_tac_list_2(p):
    'tac_list : tac'

def p_tac(p):
    '''
    tac : OPCODE dst src1 src2
        | OPCODE dst src1
        | OPCODE dst
        | OPCODE STRING
    '''
    action = {'opcode': p[1]}
    if len(p) == 5:
        action.update({'dst_type': 'variable', 'dst': p[2]['value'], 'src1_type': p[3]['type'], 'src1': p[3]['value'], 'src2_type': p[4]['type'], 'src2': p[4]['value']})
    elif len(p) == 4:
        # Assuming first operand is always dst for simplicity; refine as needed
        action.update({'dst_type': 'variable', 'dst': p[2]['value'], 'src1_type': p[3]['type'], 'src1': p[3]['value']})
    elif len(p) == 3:
        if isinstance(p[2], dict):  # Operand is dst
            action.update({'dst_type': p[2]['type'], 'dst': p[2]['value']})
        else:  # Operand is STRING
            action.update({'dst_type': 'string', 'dst': p[2]})
    
    actions.append(action)

def p_dst(p):
    '''
    dst : REGISTER
        | LABEL
    '''
    p[0] = {'value': p[1], 'type': 'variable' if p.slice[1].type == 'REGISTER' else 'label'}

def p_src1(p):
    '''
    src1 : REGISTER
         | INTEGER
    '''
    p[0] = {'value': str(p[1]), 'type': 'variable' if p.slice[1].type == 'REGISTER' else 'integer'}

def p_src2(p):
    '''
    src2 : REGISTER
         | INTEGER
    '''
    p[0] = {'value': str(p[1]), 'type': 'variable' if p.slice[1].type == 'REGISTER' else 'integer'}

def p_error(p):
    global flag_for_error
    flag_for_error = True
    print_error("Syntax error: '%s' on line %d" % (p.value, p.lexer.lineno))

# Build the parser
parser = yacc.yacc()

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

if __name__ == "__main__":
    print_debug('Input:', args.input)
    print_debug('Output:', args.output)
    print_debug('Debug:', args.debug)
    print_debug('Name:', args.name)
    
    data = read_file(args.input) if args.input != '-' else sys.stdin.read()

    # Give the lexer some input
    lexer.input(data)
    
    print_debug("Tokenizing...")

    # Tokenize
    while not flag_for_error:
        tok = lexer.token()
        if not tok:
            break  # No more input
        print_debug(tok)
    
    if flag_for_error:
        print_debug("Tokenization failed")
    else:
        print_debug("Tokenization complete")
    
    print_debug("Parsing...")
    
    result = parser.parse(data, lexer=lexer)
    if flag_for_error:
        print_debug("Parsing failed")
    else:
        print_debug("Parsing complete")
