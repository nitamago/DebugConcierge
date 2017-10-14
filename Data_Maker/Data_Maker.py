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

sys.path.append(os.getcwd())

# デバッガーの設定
logger = getLogger(__name__)
handler = StreamHandler()
handler = NullHandler()
# handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

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
        self.db = db
        self.show_code = show_code
        self.simple_mode = simple_mode
        self.keyword = keyword

        # For debug
        self.debug_flag = debug_flag
        self.art_id = art_id

        self.stat = {}
        self.stat["total"] = 10000
        self.stat["correct"] = 0
        self.stat["no_code"] = 0
        self.stat["not_compilable"] = 0
        self.stat["no_best_answer"] = 0

        self.unregistered = []

        # configファイルからの読み込み
        self.out_path = inifile["Data_Maker"]["out_path"]
        self.py4j_jar_path = inifile["Data_Maker"]["py4j_jar_path"]
        self.jar_path = inifile["Data_Maker"]["jar_path"]

    def run(self):
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

        # javaタグを持つ質問を読み出す
        page = self.db.get_records_by_tag(
                self.keyword, self.db.q_doc_type, self.stat["total"])

        # javaタグの関連記事の総数
        print("keyword: {0}, result count {1}".format(
            self.keyword, page["hits"]["hits"][0]["_source"].keys()))

        total = 0
        sid = page["_scroll_id"]
        while page is not None:
            page = self.db.scroll(sid)
            sid = page["_scroll_id"]
            total += len(page['hits']['hits'])
            self.process_page(page, app)
        print("total: {0}".format(total))

        # プロセスをkill
        gateway.shutdown()

    def process_page(self, page, app):
        for i in range(0, self.stat["total"]):
            q_source = page["hits"]["hits"][i]["_source"]
            q_id = q_source["Id"]

            # answer側の投稿を取り寄せる
            # a_pages = self.db.get_best_answer_record(best_answer_id)
            a_page = self.db.get_records_by_parent_id(q_id)
            a_sources = a_page["hits"]["hits"]

            """
            #<code>が含まれているか
            if q_plain_str.find("<code>") < 0:
                logger.debug(
                "No.{0} question don't contain code block".format(i))
                self.stat["no_code"] += 1
                continue
            elif a_plain_str.find("<code>") < 0:
                logger.debug(
                "No.{0} Answer don't contain code block".format(i))
                self.stat["no_code"] += 1
                continue
            """

            # データを抽出する
            for j in range(0, len(a_sources)):
                try:
                    print("# ID:{0} is being extracted # Pair({1},{2})".format(
                        q_id, i, j))
                    # 生データの抽出
                    raw_data = self.get_raw_data(q_source,
                                                 a_sources[j]["_source"])

                    # データの整形
                    shaped_data = self.shape_data(app, raw_data)

                    # データの書き出し
                    self.write(self.out_path, shaped_data)

                except ConvertError:
                    self.stat["not_compilable"] += 1
                    print("Failed")

    # 生データの抽出
    def get_raw_data(self, q_source, a_source):
        q_id = q_source["Id"]
        q_body_str = q_source["Body"]
        q_plain_str = self.plain(q_body_str)
        q_score = q_source["Score"]

        a_id = a_source["Id"]
        a_body_str = a_source["Body"]
        a_plain_str = self.plain(a_body_str)
        a_score = a_source["Score"]

        try:
            q_codes = self.convert_compilable("Q", q_id, q_plain_str)
            a_codes = self.convert_compilable("A", q_id, a_plain_str)
        except ConvertError:
            raise ConvertError

        return {"q_id": q_id, "q_codes": q_codes, "q_score": q_score,
                "a_id": a_id, "a_codes": a_codes, "a_score": a_score}

    # データの整形
    def shape_data(self, app, raw_data):
        ret = []
        q_id = raw_data["q_id"]
        a_id = raw_data["a_id"]
        for q_src in raw_data["q_codes"]:
            # q_tokens = list(javalang.tokenizer.tokenize(q_src))
            q_tokens = app.get_token(q_src)

            for a_src in raw_data["a_codes"]:
                # a_tokens = list(javalang.tokenizer.tokenize(a_src))

                # FIXME javaで実装した方がいい
                # fixed_tokens = self.replace_literal(tokens)
                a_tokens = app.get_token(a_src)
                ret.append([q_id, a_id, q_tokens, a_tokens])
        return ret

    # データの書き出し
    def write(self, out_path, data_list):
        with open(out_path+"/input.txt", "a") as f_i:
            with open(out_path+"/output.txt", "a") as f_o:
                for q_id, a_id, q_token, a_token in data_list:
                    f_i.write("{0}-{1} {2}\n".format(q_id, a_id, q_token.replace('\n', '<br>')))
                    f_o.write("{0}-{1} {2}\n".format(q_id, a_id, a_token))

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


class ConvertError(Exception):
    def __str__(self):
        return "This is Convert Exception"
