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
import subprocess

class Get_Base_Info():
    def __init__(self, template_maker):
        self.stat = template_maker.stat["Get_Base_Info"]
    def run(self, q_tree, a_tree, q_start, q_end, a_start, a_end, q_exclusions, a_exclusions):
        lines = " ".join(map(str, [q_start, q_end, a_start, a_end]))
        exclusions = ",".join(map(str, q_exclusions)) + " " + ",".join(map(str, a_exclusions))
        self.command = "java -jar BaseInfo.java {0} {1}".format(lines, exclusions)

        print(self.command)
        """
        code = []
        for path, node in q_tree:
            if isinstance(node, MethodDeclaration):
                print(node.body)
            elif isinstance(node, PackageDeclaration):
                code.append(node.name)
            elif isinstance(node, Type):
                code.append(node.name)
            elif isinstance(node, TypeParameter):
                code.append(node.name)
            elif isinstance(node, Annotation):
                code.append(node.name)
            elif isinstance(node, ElementValuePair):
                code.append(node.name)
            elif isinstance(node, MethodDeclaration):
                code.append(node.name)
            elif isinstance(node, ConstructorDeclaration):
                code.append(node.name)
            elif isinstance(node, VariableDeclarator):
                code.append(node.token.value)
            elif isinstance(node, FormalParameter):
                code.append(node.name)
            elif isinstance(node, InferredFormalParameter):
                code.append(node.name)
            elif isinstance(node, TryResource):
                code.append(node.name)
            elif isinstance(node, CatchClauseParameter):
                code.append(node.name)
        """
        print(" ".join(code))
