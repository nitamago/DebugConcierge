# -*- coding: utf-8 -*-

import os
import sys

from logging import getLogger, StreamHandler, NullHandler, DEBUG
import configparser
from py4j.java_gateway import JavaGateway
import subprocess
import time
import glob

sys.path.append(os.getcwd())

# デバッガーの設定
logger = getLogger(__name__)
handler = StreamHandler()
handler = NullHandler()
# handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

# configファイルの読み込み
inifile = configparser.ConfigParser()
inifile.read("config.ini")


# seq2seq用の学習データを作るクラス
class Data_Maker:
    skeleton_type = {"MethodContent": True,
                     "ClassContent": True,
                     "CheckSemicolon": True,
                     "CloseBracket": True}

    def __init__(self, db,
                 show_code=True, simple_mode=False,
                 keyword="java", debug_flag=False, art_id=-1):

        logger.debug("Data Maker initialized")
        self.show_code = show_code
        self.simple_mode = simple_mode
        self.keyword = keyword

        self.scroll_size = 1000

        # For debug
        self.debug_flag = debug_flag
        self.art_id = art_id

        # configファイルからの読み込み
        self.out_path = inifile["Data_Maker"]["out_path"]
        self.py4j_jar_path = inifile["Enviroment"]["py4j_jar_path"]    
        self.jar_path = inifile["Data_Maker"]["jar_path"]
        self.base_info_dir = inifile["Data_Maker"]["base_info_dir"]

        # 出力ファイルの初期化
        self.init_file(self.out_path)

    def run(self):
        # java gatewayサーバーを立ち上げる
        # クラスパスを指定して実行
        args = (["java",
                 "-cp", self.py4j_jar_path,
                 "-jar", self.jar_path])
        subprocess.Popen(args)

        # サーバー起動前に処理が下へ行くのを防ぐ
        time.sleep(3)
        gateway = JavaGateway(start_callback_server=True)
        app = gateway.entry_point

        print("Data Maker running")


        # 中間データの読み込み
        total = 0
        for directory in glob.glob(self.base_info_dir+"/*"):
            total += self.process_page(directory, app)
        print("total: {0}".format(total))

        # プロセスをkill
        gateway.shutdown()

    def process_page(self, directory, app):
        q_source = ""
        a_source = ""
        try:
            with open(directory+"/q_src.java") as f:
                q_source = f.read()
            with open(directory+"/a_src.java") as f:
                a_source = f.read()
        except FileNotFoundError:
            print(directory+" does not contain files")
            return 0

        q_id, a_id = directory.split("/")[-1].split("-")

        print("# ID:{0} is being extracted # Pair({1})".format(
                        q_id, directory.split("/")[-1]))

        # データの整形
        data = {"q_id": q_id, "a_id": a_id,
                "q_src": q_source, "a_src": a_source}
        try:
            shaped_data = self.shape_data(app, data, directory)
        except FileNotFoundError:
            print(directory+" does not contain files")
            return 0

        # データの書き出し
        self.write(self.out_path, shaped_data)

        return 1

    # データの整形
    def shape_data(self, app, data, directory):
        ret = []
        q_id = data["q_id"]
        a_id = data["a_id"]
        q_src = data["q_src"]
        a_src = data["a_src"]
        
        q_tokens = app.get_token(q_src)
        a_tokens = app.get_token(a_src)

        # ディレクトリの確認
        q_anchor_path = directory+"/q_anchor.txt"
        a_anchor_path = directory+"/a_anchor.txt"
        addition_path = directory+"/addition.txt"
        removal_path = directory+"/removal.txt"
        if not os.path.exists(q_anchor_path):
            print(directory+" does not exists")
            raise FileNotFoundError
        if not os.path.exists(a_anchor_path):
            print(directory+" does not exists")
            raise FileNotFoundError
        if not os.path.exists(addition_path):
            print(directory+" does not exists")
            raise FileNotFoundError
        if not os.path.exists(removal_path):
            print(directory+" does not exists")
            raise FileNotFoundError

        # recommendの整形
        q_anchor = []
        with open(q_anchor_path) as f:
            for line in f:
                content = line.split(" ", 2)
                index = int(content[1])
                code = content[2].replace("\n", "")
                q_anchor.append((index, code))
            
        a_anchor = []
        with open(a_anchor_path) as f:
            for line in f:
                content = line.split(" ", 2)
                index = int(content[1])
                code = content[2].replace("\n", "")
                a_anchor.append((index, code))

        # 挿入操作をまとめる
        recommends = []
        with open(addition_path) as f:
            for line in f:
                content = line.split(" ", 2)
                index = int(content[1])
                code = content[2].replace("\n", "")
                line_in_clone = -1
                for i in range(0, len(a_anchor)):
                    if a_anchor[i][0] > index:
                        line_in_clone = i
                    elif line_in_clone == -1:
                        if len(q_anchor) > 0:
                            recommends.append("<add> "+
                                    app.get_token(code)+" <before> "+app.get_token(q_anchor[0][1]))
                        else:
                            recommends.append("<add> "+app.get_token(code))
                            break
                    else:
                        recommends.append("<add> "+
                                app.get_token(code)+" <after> "+app.get_token(q_anchor[line_in_clone][1]))
                        break
                if len(recommends) == 0:
                    recommend_str = "<end>"
                else:
                    recommend_str = " <end> ".join(recommends) + " <end>"
                
                ret.append([q_id, a_id, q_tokens, recommend_str])

        # 削除操作をまとめる
        recommends = []
        with open(removal_path) as f:
            for line in f:
                content = line.split(" ", 2)
                index = int(content[1])
                code = content[2].replace("\n", "")
                line_in_clone = -1
                for i in range(0, len(q_anchor)):
                    if q_anchor[i][0] > index:
                        line_in_clone = i
                    elif line_in_clone == -1:
                        if len(a_anchor) > 0:
                            recommends.append("<rm> "+
                                    app.get_token(code)+" <before> "+app.get_token(q_anchor[0][1]))
                        else:
                            recommends.append("<rm> "+app.get_token(code))
                            break
                    else:
                        recommends.append("<rm> "+
                                app.get_token(code)+" <after> "+app.get_token(q_anchor[line_in_clone][1]))
                        break
                if len(recommends) == 0:
                    recommend_str = "<end>"
                else:
                    recommend_str = " <end> ".join(recommends) + " <end>"
                
                ret.append([q_id, a_id, q_tokens, recommend_str])
 
            return ret

    # 出力先の初期化
    def init_file(self, out_path):
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        with open(out_path+"/input.txt", "w") as f_i:
            f_i.write("")
        with open(out_path+"/output.txt", "w") as f_o:
            f_o.write("")

    # データの書き出し
    def write(self, out_path, data_list):
        with open(out_path+"/input.txt", "a") as f_i:
            with open(out_path+"/output.txt", "a") as f_o:
                for i, (q_id, a_id, q_token, a_token) in enumerate(data_list):
                    f_i.write("{0}-{1} {2} {3}\n".format(
                        q_id, a_id, i, q_token.replace('\n', '<br>')))
                    f_o.write("{0}-{1} {2} {3}\n".format(q_id, a_id, i, a_token))


class ConvertError(Exception):
    def __str__(self):
        return "This is Convert Exception"
