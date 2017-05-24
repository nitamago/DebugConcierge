# テンプレートを作るクラス
import os, sys
sys.path.append(os.getcwd())

import configparser
inifile = configparser.ConfigParser()
inifile.read("config.ini")

from DB.DB import DB
from Templates.Template import Template
from Templates.Clone_Detecter import Clone_Detecter
from Templates.Clone_Analyzer import Clone_Analyzer
import re
import javalang
from javalang.tree import *
from logging import getLogger, StreamHandler, NullHandler, DEBUG

logger = getLogger(__name__)
#handler = StreamHandler()
handler = NullHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

class Template_Maker:
    preference = {"MethodContent": True, "ClassContent": True, "CheckSemicolon": True, "CloseBracket": True }
    def __init__(self, db, show_code=True, simple_mode=False):
        logger.debug("Template Maker initialized")
        self.db = db
        self.stat = {}
        self.stat["total"] = 500
        self.stat["correct"] = 0
        self.stat["no_code"] = 0
        self.stat["not_compilable"] = 0
        self.stat["no_best_answer"] = 0
        self.unregistered = []

        self.clone_detecter = Clone_Detecter()
        self.clone_analyzer = Clone_Analyzer()

        self.show_code = show_code

    def run(self):
        logger.debug("Template Maker running")
        #javaタグを持つ質問を読み出す
        json = self.db.get_records_by_tag("java", self.db.q_doc_type)

        for i in range(0, self.stat["total"]):
        #for i in range(0, json["hits"]["total"]):
            q_source = json["hits"]["hits"][i]["_source"]
            q_id = q_source["Id"]
            q_body_str = q_source["Body"]
            q_plain_str = self.plain(q_body_str)

            #ベストアンサーを持たなければスキップ
            if not "AcceptedAnswerId" in json["hits"]["hits"][i]["_source"]:
                logger.debug("No.{0} don't contain best answer".format(i))
                self.stat["no_best_answer"] += 1
                continue
            best_answer_id = json["hits"]["hits"][i]["_source"]["AcceptedAnswerId"]

            #answer側の投稿を取り寄せる
            a_json = self.db.get_best_answer_record(best_answer_id)
            a_source = a_json["hits"]["hits"][0]["_source"]
            a_body_str = a_source["Body"]
            a_plain_str = self.plain(a_body_str)

            #<code>が含まれているか
            if q_plain_str.find("<code>") < 0:
                logger.debug("No.{0} question don't contain code block".format(i))
                self.stat["no_code"] += 1
                continue
            elif a_plain_str.find("<code>") < 0:
                logger.debug("No.{0} Answer don't contain code block".format(i))
                self.stat["no_code"] += 1
                continue

            #テンプレート化する
            try:
                t = self.convert_template(i, q_id, q_plain_str, a_plain_str)
                self.db.put_template(t)
                self.clone_detecter.run(t)
                self.clone_analyzer.run(t)
            except ConvertError:
                self.stat["not_compilable"] += 1

        self.db.write_template()

    def plain(self, s):
        #余分なタグを外す
        s = s.replace("<pre>", "").replace("</pre>", "\n")
        s = s.replace("<p>", "").replace("</p>", "\n")
        return s.replace("&gt;", ">").replace("&lt;", "<")

    def convert_template(self, i, q_id, q_plain_str, a_plain_str):
        try:
            q_codes = self.convert_compilable(i, "Q", q_id, q_plain_str)
            a_codes = self.convert_compilable(i, "A", q_id, a_plain_str)
        except ConvertError:
            raise ConvertError
        
        return Template(tmplt_id=q_id, target_code=q_codes, modify_code=a_codes, api_tag="", apply_constraint="")

    #コンパイル可能なコードのリストを返す
    def convert_compilable(self, i, q_or_a, q_id, plain_str):
        #p = re.compile("<code>[^(</code>)]*</code>", re.DOTALL)
        p = re.compile("<code>.*?</code>", re.DOTALL)
        logger.debug("No.{0}-{1}#{2}#################".format(i, q_or_a, q_id))

        codes = []
        for line in p.findall(plain_str):
            code = line.replace("<code>", "").replace("</code>", "")
            codes.append(code)

        #コードスニペットの解析
        ret = []
        for seq in range(0, len(codes)):
            code = codes[seq]
            if self.show_code:
                logger.debug("Code No.{0}".format(seq))
                logger.debug("==============================")
                logger.debug("raw code block")
                logger.debug("==============================")
                logger.debug(code)
                logger.debug("==============================")
            if self.try_compile(i, code):
                ret.append(code)
                continue
            #コード片をスケルトンへ移植
            is_continue = False
            for planted_code in self.plant_to_skeleton(code):
                logger.debug("Skeleton-----------------------")
                if self.try_compile(i, planted_code):
                    ret.append(planted_code)
                    is_continue = True
                    break
            if is_continue:
                break
            #コード片の最後にセミコロンを付け足して、スケルトンへ移植
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
            #コード片を中カッコで閉じる
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
            #省略(...)を消す
            eliminate_ellipsis_code = code.replace("...", "")
            logger.debug("Eliminate Ellipsis----------------------")
            if self.show_code:
                logger.debug(eliminate_ellipsis_code)
            if self.try_compile(i, eliminate_ellipsis_code):
                ret.append(eliminate_ellipsis_code)
                break
            is_continue = False
            for planted_code in self.plant_to_skeleton(eliminate_ellipsis_code):
                logger.debug("Skeleton & Eliminate Ellipsis----------------")
                if self.try_compile(i, planted_code):
                    ret.append(planted_code)
                    is_continue = True
                    break
            if is_continue:
                break
               
            #コンパイル可能化の例外リスト
            command_line = [6, 84]
            error_log = [10]
            excessive_ellipsis = [15, 30]
            bracket_problem = [53]
            xml = [42]
            unknown = [8, 36, 55, 61, 92] #解決の余地ありそう
            otherwise = [9, 25, 28, 37, 43, 44, 95, 98]
            except_list = command_line + error_log + excessive_ellipsis + bracket_problem + xml + unknown + otherwise 
            contain_error_log = [21, 63]
            contain_unknown = [18, 56]
            contain_otherwise = [5, 11, 19, 38, 58, 60, 64, 69, 76, 81, 87, 96]
            except_contain = contain_error_log + contain_unknown + contain_otherwise
            if i not in except_list + except_contain:
                logger.debug("コンパイル可能化の例外リストに登録されていません")
                logger.debug("raw code ~~~~~~~~~~~~")
                logger.debug(code)
                logger.debug("~~~~~~~~~~~~~~~~~~~~~~")
                #sys.exit()
                self.unregistered.append(i)
                logger.debug(self.unregistered) 
            raise ConvertError

        return ret


               

    #コンパイルできたらTrue
    def try_compile(self, i, code):
                try:
                    tree = javalang.parse.parse(code)
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


    def plant_to_skeleton(self, code):
        #code = self.check_semicolon(code)
        ret = []
        for i in range(1, 4):
            if i == 1 and not self.preference["MethodContent"]:
                continue
            if i == 2 and not self.preference["ClassContent"]:
                continue
            f = open("Templates/Skeletons/Skeleton"+str(i)+".java")
            skeleton = f.read()
            planted_code = skeleton.replace("/*insert here*/", code)
            ret.append(planted_code)
            f.close()
        return ret

    def check_semicolon(self, code):
        return code.replace("\n", ";\n")

    def close_bracket(self, code):
        return code+"}"

class ConvertError(Exception):
    def __str__(self):
        return "This is Convert Exception"

if __name__ == "__main__":
    db = DB(cache_write_flag=inifile.getboolean("DB_cache", "cache_write_flag"), cache_read_flag=inifile.getboolean("DB_cache", "cache_read_flag"))
    tm = Template_Maker(db, show_code=inifile.getboolean("Template_Maker", "show_code"), simple_mode=inifile.getboolean("Template_Maker", "simple_mode"))
    print(inifile["DB_cache"]["cache_read_flag"])
    tm.run()
    tm.stat["correct"] = tm.stat["total"] - tm.stat["no_code"] - tm.stat["no_best_answer"] - tm.stat["not_compilable"]
    logger.debug(tm.stat)
