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
import os
import javalang
from javalang.tree import *
import subprocess

class Get_Base_Info():
    def __init__(self, template_maker, jar_path):
        self.stat = template_maker.stat["Get_Base_Info"]

        self.jar_path = jar_path "/home/hirose/git/Debug_Concierge/Template_Maker/BaseInfo.jar"

    def run(self, template_id, q_path, a_path, q_start, q_end, a_start, a_end, q_exclusions, a_exclusions):
        lines = " ".join(map(str, [q_start, q_end, a_start, a_end]))
        exclusions = "-1" if len(q_exclusions) == 0 else ",".join(map(str, q_exclusions)) 
        exclusions += " " 
        exclusions += "-1" if len(a_exclusions)==0 else ",".join(map(str, a_exclusions))
        #out_path = "/Users/HiroseMasayuki/Documents/Git/Debug_Concierge"
        result_dir = "Template_Maker/BaseInfo/result/"+template_id
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        self.command = "java -jar {0} {1} {2} {3} {4} {5}".format(jar_path, q_path, a_path, result_dir, lines, exclusions)

        print(self.command)
        subprocess.call(self.command, shell=True)

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
        #print(" ".join(code))
