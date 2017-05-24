#-*- coding:utf-8 -*-
#コードクローン検出用クラス

import subprocess
import os
import glob
import sys
from logging import getLogger, StreamHandler, NullHandler, DEBUG

logger = getLogger(__name__)
#handler = StreamHandler()
handler = NullHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

class Clone_Detecter:
    def __init__(self):
        #self.exe_path = os.path.dirname(os.path.abspath(__file__))
        self.scorpio_dir = "Templates/Code_Clone/scorpio.jar"
        self.q_codes_dir = "Templates/Code_Clone/Question_codes"
        self.a_codes_dir = "Templates/Code_Clone/Answer_codes"
        self.clone_result_dir = "Templates/Code_Clone/result/"
        self.scorpio_run_command = "java -jar {0} -d {1} -ad {2} -cross on -o {3} -s 2 -t 2"
        
    def run(self, template):
        logger.debug("Clone Detecter running")
        #コードをファイルに書き出す
        self.write_to_file(template.tmplt_id, template.target_code, template.modify_code)
        #scorpioを走らせて、クローンを検出
        self.run_scorpio(template.tmplt_id)

    def write_to_file(self, template_id, q_codes, a_codes):
        for f in glob.glob(self.q_codes_dir+"/*.java"):
            if os.path.isfile(f):
                os.remove(f)

        for f in glob.glob(self.a_codes_dir+"/*.java"):
            if os.path.isfile(f):
                os.remove(f)
        
        for i, code in enumerate(q_codes):
            f = open("{0}/{1}_{2}.java".format(self.q_codes_dir, template_id, i), "w")
            f.write(code)
            f.close()

        for i, code in enumerate(a_codes):
            f = open("{0}/{1}_{2}.java".format(self.a_codes_dir, template_id, i), "w")
            f.write(code)
            f.close()

    def run_scorpio(self, output_name):
        result_full_path = self.clone_result_dir + output_name + ".xml"
        res = subprocess.call(self.scorpio_run_command.format(self.scorpio_dir, self.q_codes_dir, self.a_codes_dir, result_full_path), shell=True)
        logger.debug(res)
