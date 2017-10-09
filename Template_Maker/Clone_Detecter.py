#-*- coding:utf-8 -*-
#コードクローン検出用クラス

import subprocess
import os
import shutil
from distutils.dir_util import copy_tree                
import glob
import sys
from logging import getLogger, StreamHandler, NullHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
#handler = NullHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

class Clone_Detecter:
    def __init__(self, min_detect_line_num,  show_code=True, simple_mode=True):
        #self.exe_path = os.path.dirname(os.path.abspath(__file__))
        self.scorpio_dir = "Template_Maker/Code_Clone/scorpio.jar"
        self.q_codes_dir = "Template_Maker/Code_Clone/Question_codes"
        self.a_codes_dir = "Template_Maker/Code_Clone/Answer_codes"
        self.clone_result_dir = "Template_Maker/Code_Clone/result/"
        self.store_dir = "Template_Maker/Code_Clone/store/"
        self.scorpio_run_command = "java -jar {0} -d {1} -ad {2} -cross on -o {3} -s {4} -t 2 > /dev/null"
        self.min_detect_line_num = min_detect_line_num
        
    def run(self, template):
        print("Clone Detecter running \nmin detect num: {0}".format(self.min_detect_line_num))
        #コードをファイルに書き出す
        self.write_to_file(template.tmplt_id, template.target_code, template.modify_code)
        #scorpioを走らせて、クローンを検出
        try:
            self.run_scorpio(template.tmplt_id)

            #evidence用にコードをstore_dirに移動
            self.move_files_store()
        except NoScorpioException as e:
            logger.debug(e.message)
            sys.exit()

    def write_to_file(self, template_id, q_codes, a_codes):
        for f in glob.glob(self.q_codes_dir+"/*.java"):
            if os.path.isfile(f):
                os.remove(f)

        for f in glob.glob(self.a_codes_dir+"/*.java"):
            if os.path.isfile(f):
                os.remove(f)
        
        for i, code in enumerate(q_codes):
            if not os.path.exists(self.q_codes_dir):
                os.makedirs(self.q_codes_dir)
            with open("{0}/{1}_{2}.java".format(self.q_codes_dir, template_id, i), "w") as f:
                f.write(code)

        for i, code in enumerate(a_codes):
            if not os.path.exists(self.a_codes_dir):
                os.makedirs(self.a_codes_dir)
            with open("{0}/{1}_{2}.java".format(self.a_codes_dir, template_id, i), "w") as f:
                f.write(code)

    def run_scorpio(self, output_name):
        #scorpio.jarが存在するか
        if not os.path.exists(self.scorpio_dir):
            raise NoScorpioException()
        #scorpioの出力先ディレクトリが存在するか
        if not os.path.exists(self.clone_result_dir):
            os.makedirs(self.clone_result_dir)

        result_full_path = self.clone_result_dir + output_name + ".xml"
        res = subprocess.call(self.scorpio_run_command.format(self.scorpio_dir, self.q_codes_dir, self.a_codes_dir, result_full_path, self.min_detect_line_num), shell=True)
        print(res)

    def move_files_store(self):                
        # storeディレクトの存在確認
        store_q_dir = self.store_dir+"Question_codes"
        if not os.path.exists(store_q_dir):
            os.makedirs(store_q_dir)            
        store_a_dir = self.store_dir+"Answer_codes"
        if not os.path.exists(store_a_dir):
            os.makedirs(store_a_dir)
        # ディレクトリコピー
        copy_tree(self.q_codes_dir, store_q_dir)
        copy_tree(self.a_codes_dir, store_a_dir)


class NoScorpioException(Exception):
    def __init__(self):
        self.message = "Not exist scorpio.jar"

