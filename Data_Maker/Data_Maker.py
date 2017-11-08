# -*- coding: utf-8 -*-

import os
import sys

import re
import javalang
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
        self.py4j_jar_path = inifile["Data_Maker"]["py4j_jar_path"]
        self.jar_path = inifile["Data_Maker"]["jar_path"]
    
        self.base_info_dir = inifile["Data_Maker"]["base_info_dir"]
        self.id_pairs = self.get_id_pairs(self.base_info_dir)

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
        for directory in glob.glob(self.base_info_dir):
            self.process_page(directory, app)
            total += 1
            print("{0} is done".format(total))
        print("total: {0}".format(total))

        # プロセスをkill
        gateway.shutdown()

    def process_page(self, directory, app):
        q_source = ""
        with open(directory+"/q_src.java") as f:
            q_source = f.read()
        a_source = ""
        with open(directory+"/a_src.java") as f:
            a_source = f.read()

        q_id, a_id = directory.split("/")[-1].split("-")

        print("# ID:{0} is being extracted # Pair({1})".format(
                        q_id, directory.split("/")[-1]))

        # データの整形
        data = {"q_id": q_id, "a_id": a_id,
                "q_src": q_source, "a_src": a_source}
        shaped_data = self.shape_data(app, data, directory)

        # データの書き出し
        self.write(self.out_path, shaped_data)

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
        if not os.path.exists(q_anchor_path):
            print(directory+" does not exists")
            exit()
        if not os.path.exists(a_anchor_path):
            print(directory+" does not exists")
            exit()
        if not os.path.exists(addition_path):
            print(directory+" does not exists")
            exit()

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
                            recommends.append(
                                    app.get_token(code)+" <before> "+app.get_token(q_anchor[0][1]))
                        else:
                            recommends.append("<add> "+app.get_token(code))
                            break
                    else:
                        recommends.append(
                                app.get_token(code)+" <after> "+app.get_token(q_anchor[line_in_clone][1]))
                        break
                if len(recommends) == 0:
                    recommend_str = "<end>"
                else:
                    recommend_str = " <end> ".join(recommends) + " <end>"
                
                ret.append([q_id, a_id, q_tokens, recommend_str])
            return ret

    # データの書き出し
    def write(self, out_path, data_list):
        with open(out_path+"/input.txt", "a") as f_i:
            with open(out_path+"/output.txt", "a") as f_o:
                for i, (q_id, a_id, q_token, a_token) in enumerate(data_list):
                    f_i.write("{0}-{1} {2} {3}\n".format(
                        q_id, a_id, i, q_token.replace('\n', '<br>')))
                    f_o.write("{0}-{1} {2} {3}\n".format(q_id, a_id, i, a_token))

    # 余分なタグを外す
    def plain(self, s):
        s = s.replace("<pre>", "").replace("</pre>", "\n")
        s = s.replace("<p>", "").replace("</p>", "\n")
        return s.replace("&gt;", ">").replace("&lt;", "<")

    # コンパイル可能なコードのリストを返す
    def convert_compilable(self, q_or_a, q_id, plain_str):
        p = re.compile("<code>.*?</code>", re.DOTALL)

        codes = []
        for line in p.findall(plain_str):
            code = line.replace("<code>", "").replace("</code>", "")
            codes.append(code)

        # コードスニペットの解析
        ret = []
        for seq in range(0, len(codes)):
            code = codes[seq]
            if self.show_code:
                logger.debug("Code No.{0}".format(seq))
                logger.debug("== raw code block ============================")
                logger.debug(code)
                logger.debug("==============================")
            if self.try_compile(code):
                ret.append(code)
                continue

            # コード片をスケルトンへ移植
            is_continue = False
            for planted_code in self.plant_to_skeleton(code):
                logger.debug("Skeleton-----------------------")
                if self.try_compile(planted_code):
                    ret.append(planted_code)
                    is_continue = True
                    break
            if is_continue:
                break

            # コード片の最後にセミコロンを付け足して、スケルトンへ移植
            """
            if self.preference["CheckSemicolon"]:
                semicoloned_code = self.check_semicolon(code)
                logger.debug("Check Semicolon------------------------")
                if self.try_compile(i, semicoloned_code):
                    ret.append(semicoloned_code)
                    break
                is_continue = False
                for planted_code in self.plant_to_skeleton(semicoloned_code):
                    logger.debug("Skeleton & Check Semicolon----------------")
                    if self.try_compile(i, planted_code):
                        ret.append(planted_code)
                        is_continue = True
                if is_continue:
                    break
            """
            # コード片を中カッコで閉じる
            """
            if self.preference["CloseBracket"]:
                closed_bracket_code = self.close_bracket(code)
                logger.debug("Closed Bracket--------------------------")
                if self.try_compile(i, closed_bracket_code):
                    ret.append(closed_bracket_code)
                    break
                d_closed_bracket_code = self.close_bracket(closed_bracket_code)
                logger.debug("Double Closed Bracket--------------------------")
                if self.try_compile(i, d_closed_bracket_code):
                    ret.append(d_closed_bracket_code)
                    break
            """

            raise ConvertError

        return ret

    # コンパイルできたらTrue
    def try_compile(self, code):
                try:
                    tokens = list(javalang.tokenizer.tokenize(code))
                    fixed_tokens = self.replace_literal(tokens)
                    codes = []
                    for j in range(0, len(fixed_tokens)):
                        codes.append(fixed_tokens[j].value)
                    javalang.parse.Parser(tokens)
                    return True
                except javalang.parser.JavaSyntaxError:
                    logger.debug("- JavaSyntaxError")
                    if self.show_code:
                        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        logger.debug(code)
                        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                except javalang.tokenizer.LexerError:
                    logger.debug("- LexerError")
                    if self.show_code:
                        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        logger.debug(code)
                        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                except TypeError:
                    logger.debug("- TypeError")
                    if self.show_code:
                        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        logger.debug(code)
                        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                except AttributeError:
                    logger.debug("- AttributeError")
                    if self.show_code:
                        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        logger.debug(code)
                        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                except IndexError:
                    logger.debug("- IndexError")
                    if self.show_code:
                        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        logger.debug(code)
                        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                except StopIteration:
                    logger.debug("- StopIteration")
                    if self.show_code:
                        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        logger.debug(code)
                        logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    # リテラルを置き換える
    def replace_literal(self, tokens):
        ret = []
        for i in range(0, len(tokens)):
            if type(tokens[i]) is javalang.tokenizer.Identifier:
                tokens[i].value = tokens[i].value
            if type(tokens[i]) is javalang.tokenizer.String:
                tokens[i].value = "<Str>"
            # print(type(tokens[i]))
            ret.append(tokens[i])
        return ret

    # スケルトンコードに埋め込む
    def plant_to_skeleton(self, code):
        # code = self.check_semicolon(code)
        ret = []
        for i in range(1, 4):
            if i == 1 and not self.skeleton_type["MethodContent"]:
                continue
            if i == 2 and not self.skeleton_type["ClassContent"]:
                continue
            with open("Template_Maker/Skeletons/Skeleton"+str(i)+".java") as f:
                skeleton = f.read()
            planted_code = skeleton.replace("/*insert here*/", code)
            ret.append(planted_code)
        return ret

    def check_semicolon(self, code):
        return code.replace("\n", ";\n")

    def close_bracket(self, code):
        return code+"}"

    def get_id_pairs(self, info_dir):
        ids = os.listdir(path=info_dir)
        return set(ids)


class ConvertError(Exception):
    def __str__(self):
        return "This is Convert Exception"
