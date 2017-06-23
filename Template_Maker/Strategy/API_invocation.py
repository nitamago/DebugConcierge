#! /usr/bin/env python
#-*- coding:utf-8 -*-
# Author:   Masayuki Hirose
# Created:  2017-06-12

from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

import sys
import javalang
from javalang.tree import *

class API_invocation():
    def __init__(self, template_maker):
        self.stat = template_maker.stat["API_invocation"]

    def run(self, q_tree, a_tree, q_start, q_end, a_start, a_end, q_exclusions, a_exclusions):
        # replace差分
        # メソッド呼び出しだけに関して、diffをとる
        var_table = {}
        for path, node in q_tree:
            if isinstance(node, MethodInvocation):
                token_line_numm = node.token.position[0]
                if token_line_numm >= q_start and token_line_numm <= q_end and token_line_numm not in q_exclusions:
                    if node.qualifier is not None:
                        print("MethodInvocation in Clone Area! {0}".format(node.token))
                        print("member: {0}, type_arguments: {1}, arguments: {2}"
                            .format(node.member,
                            node.type_arguments,
                            node.arguments))
                        print("prefix_operator: {0}, postfix_operator: {1}, qualifier: {2}, selectors: {3}"
                            .format(node.prefix_operators,
                            node.postfix_operators,
                            node.qualifier,
                            node.selectors))
                        try:
                            print("Constraint: Var {0} exsist".format(var_table[node.qualifier]))
                            self.stat["constraint_exist"] += 1
                        except KeyError:
                            print("Constraint: No avalable")
                            self.stat["constraint_not_exist"] += 1
                        self.stat["total"] += 1
            elif isinstance(node, VariableDeclaration):
                var_type = node.type.name
                for d in node.declarators:
                    var_table[d.name] = var_type

