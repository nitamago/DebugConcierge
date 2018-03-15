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
from py4j.java_gateway import JavaGateway
import time
import configparser

# configファイルの読み込み
inifile = configparser.ConfigParser()
inifile.read("config.ini")

class Get_Base_Info():
    _instance = None
    class_path = inifile["Enviroment"]["py4j_jar_path"]
    jar_path = inifile["Get_Base_Info"]["jar_path"]
    result_dir = inifile["Get_Base_Info"]["result_dir"]

    def __init__(self, template_maker):
        self.stat = template_maker.stat["Get_Base_Info"]

        # クラスパスを指定して実行
        args = (["java","-cp", self.class_path, 
                 '-jar', self.jar_path])
        self.process = subprocess.Popen(args)

        # サーバー起動前に処理が下へ行くのを防ぐ
        time.sleep(3)
        self.gateway = JavaGateway()
        self.entry_point = self.gateway.entry_point

    @classmethod
    def get_instance(cls, template_maker):
        if cls._instance is None:
            cls._instance = Get_Base_Info(template_maker)
        return cls._instance

    def shutdown(self):
        self._instance = None
        self.gateway.shutdown()

    def run(self, template_id, 
            q_path, a_path, q_start, q_end, 
            a_start, a_end, q_exclusions, a_exclusions):
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
        if not os.path.exists(self.result_dir+"/"+template_id):
            os.makedirs(self.result_dir+"/"+template_id)
        exclusions1 = "-1" if len(q_exclusions) == 0 else ",".join(map(str, q_exclusions)) 
        exclusions2 = "-1" if len(a_exclusions) == 0 else ",".join(map(str, a_exclusions))
        print((q_path, a_path))
        self.entry_point.run(q_path, a_path, self.result_dir+"/"+template_id, 
                             q_start, q_end, 
                             a_start, a_end,
                             exclusions1, exclusions2)
