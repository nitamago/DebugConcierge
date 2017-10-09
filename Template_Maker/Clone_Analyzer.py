#コードクローンを解析して、差分を検出するクラス

import os
import sys
import copy
import math
import javalang
from javalang.tree import *
from logging import getLogger, StreamHandler, NullHandler, DEBUG

from Template_Maker.Strategy.API_invocation import API_invocation
from Template_Maker.Strategy.Get_Base_Info import Get_Base_Info

logger = getLogger(__name__)
handler = StreamHandler()
#handler = NullHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

class Clone_Analyzer:
    def __init__(self, template_maker, show_code=True, simple_mode=True):
        self.template_maker = template_maker
        self.show_code = show_code

        self.result_dir = "Template_Maker/Code_Clone/result"

    def run(self, template):
        print("Clone Analyzer running")

        ret = []
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
        with open(self.result_dir +"/"+ template.tmplt_id + ".xml") as f:
            for line in f:
                contents = line.split("\t")
                diff_info = self.extract(contents, template)
                ret.append(diff_info)
        return ret
    
    def extract(self, contents, template):
            ret = {}

            # クローンの範囲をピックアップ
            q_start = int(contents[1])
            q_end = int(contents[2])
            a_start = int(contents[4])
            a_end = int(contents[5])

            # クローン対象外の行番号をピックアップ
            q_exclusions= []
            a_exclusions = []

            if contents[6] != "-":
                q_exclusions = [int(x) for x in contents[6].split(",")]
            if contents[7].replace("\n", "") != "-":
                a_exclusions = [int(x) for x in contents[7].split(",")]

            # クローン部分の行番号をピックアップ
            q_clone_part = []
            a_clone_part = []

            for i in range(q_start, q_end+1):
                if i not in q_exclusions:
                    q_clone_part.append(i)
            for i in range(a_start, a_end+1):
                if i not in a_exclusions:
                    a_clone_part.append(i)

            # 該当ソースコードの読み込み(Question)
            q_code_index = contents[0].split("/")[-1].split("_")[1].replace(".java", "")
            target_code = template.target_code[int(q_code_index)]
            target_code_separated = target_code.split("\n")
 
            # 該当ソースコードの読み込み(Answer)
            a_code_index = contents[3].split("/")[-1].split("_")[1].replace(".java", "")
            modify_code = template.modify_code[int(a_code_index)]
            modify_code_separated = modify_code.split("\n")

            # 構文要素に分解 ASTの構築
            q_tree = self.divide_syntax_element(target_code)
            a_tree = self.divide_syntax_element(modify_code)

            # ASTの解析して戦略を適用
            diff_dict = self.get_tree_diff(q_tree, a_tree, q_start, q_end, a_start, a_end, a_exclusions, q_exclusions)
            #api_strategy = API_invocation(self.template_maker)
            #api_strategy.run(q_tree, a_tree, q_start, q_end, a_start, a_end, q_exclusions, a_exclusions)
            get_base_info = Get_Base_Info(self.template_maker)
            get_base_info.run(q_tree, a_tree, q_start, q_end, a_start, a_end, q_exclusions, a_exclusions)
            #FIXME
            print(q_exclusions)
            exit()

            # コード表示
            self.show_code_diff(diff_dict, q_start, q_end, a_start, a_end,
                    target_code_separated, modify_code_separated, 
                    q_exclusions, a_exclusions)
            self.show_code_add_rm(diff_dict, q_start, q_end, a_start, a_end,
                    target_code_separated, modify_code_separated,
                    q_exclusions, a_exclusions)

            # クローンをアンカーにして、差分コードの情報を作成
            remove_list = self.get_rm_diff_list(diff_dict, q_clone_part, target_code_separated)
            print("remove list")
            print(remove_list)
            ret["remove_list"] = remove_list

            add_list = self.get_add_diff_list(diff_dict, a_clone_part, modify_code_separated)
            print("add list")
            print(add_list)
            ret["add_list"] = add_list

            return ret

    #構文要素に分解
    def divide_syntax_element(self, code):
                try:
                    tree = javalang.parse.parse(code)
                    return tree
                except javalang.parser.JavaSyntaxError:
                    print("- JavaSyntaxError")
                    if self.show_code:
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        print(code)
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                except javalang.tokenizer.LexerError:
                    print("- LexerError")
                    if self.show_code:
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        print(code)
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                except TypeError:
                    print("- TypeError")
                    if self.show_code:
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        print(code)
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                except AttributeError:
                    print("- AttributeError")
                    if self.show_code:
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        print(code)
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                except IndexError:
                    print("- IndexError")
                    if self.show_code:
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        print(code)
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    # 単純に差分を取る戦略
    # 差分の辞書型を返す {"add":, "rm":, "rep":}
    def get_tree_diff(self, q_tree, a_tree, q_start, q_end, a_start, a_end, q_exclusions, a_exclusions):
        ret = {"add":[], "rm":[], "rep":[]}

        # add差分
        ret["add"].extend(q_exclusions) 

        # remove差分
        ret["rm"].extend(a_exclusions)

        return ret

    def show_code_diff(self, diff_dict, q_start, q_end, a_start, a_end,
            target_code_separated, modify_code_separated,
            q_exclusions, a_exclusions):
        # 対象外コードを"~"に置換
        marked_target_code_separated = copy.deepcopy(target_code_separated)
        for i in [x-1 for x in q_exclusions]:
            #target_code_separated[i] = "~~~~~~"
            marked_target_code_separated[i] = "~d~ " + target_code_separated[i]
                   
        marked_modify_code_separated = copy.deepcopy(modify_code_separated)
        for i in [x-1 for x in a_exclusions]:
            #modify_code_separated[i] = "~~~~~~"
            marked_modify_code_separated[i] = "~d~ " + modify_code_separated[i]

        # コードの表示
        if self.show_code:
            print("== Show Diff ====================================")
            print("\n".join(marked_target_code_separated[q_start: q_end+1]))
            print("=================================================")
            print("\n".join(marked_modify_code_separated[a_start: a_end+1]))
            print("=================================================")         

    def show_code_add_rm(self, diff_dict, q_start, q_end, a_start, a_end,
            target_code_separated, modify_code_separated,
            q_exclusions, a_exclusions):
        # 差分コードにマークする
        marked_target_code_separated = copy.deepcopy(target_code_separated)
        for i in [x-1 for x in diff_dict["rm"]]:
            #target_code_separated[i] = "~~~~~~"
            marked_target_code_separated[i] = "~r~" + target_code_separated[i]  
        
        marked_modify_code_separated = copy.deepcopy(modify_code_separated)
        for i in [x-1 for x in diff_dict["add"]]:
            #modify_code_separated[i] = "~~~~~~"
            marked_modify_code_separated[i] = "~a~" + modify_code_separated[i]

        # コードの表示
        if self.show_code:
            print("== Show Add & Remove ============================")
            print("\n".join(marked_target_code_separated[q_start: q_end+1]))
            print("=================================================")
            print("\n".join(marked_modify_code_separated[a_start: a_end+1]))
            print("=================================================")         

    def get_rm_diff_list(self, diff_dict, q_clone_part, target_code_separated):
        # クローンをアンカーにして、差分コードの情報を作成
        remove_list = []
        for i in diff_dict["rm"]:
            dist = sys.maxsize
            info = {}
            for anc_line in q_clone_part:
                if abs(i-anc_line) < dist:
                    dist = i - anc_line

            info["anchor"] = anc_line
            info["anchor_code"] = target_code_separated[anc_line-1]
            info["offset"] = i - anc_line
            info["diff_code"] = target_code_separated[i-1]
            remove_list.append(info)
        return remove_list

    def get_add_diff_list(self, diff_dict, a_clone_part, modify_code_separated):
        add_list = []
        for i in diff_dict["add"]:
            dist = sys.maxsize
            info = {}
            for anc_line in a_clone_part:
                if abs(i-anc_line) < dist:
                    dist = i - anc_line
            info["anchor"] = anc_line
            info["anchor_code"] = modify_code_separated[anc_line-1]
            info["offset"] = i - anc_line
            info["diff_code"] = modify_code_separated[i-1]
            add_list.append(info)
        return add_list


class ConvertError(Exception):
    def __str__(self):
        return "This is Convert Exception"

if __name__ == "__main__":
    tm = Template_Maker(DB(), show_code=False)
    tm.run()
    tm.stat["correct"] = tm.stat["total"] - tm.stat["no_code"] - tm.stat["no_best_answer"] - tm.stat["not_compilable"]
    print(tm.stat)
