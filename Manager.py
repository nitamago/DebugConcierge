#-*- coding:utf-8 -*-
## マネージャクラス

import sys
sys.path.append("./lib")

import click
import configparser
inifile = configparser.ConfigParser()
inifile.read("config.ini")

from logging import getLogger, StreamHandler, NullHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler = NullHandler()
#handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

from Template_Maker.Template_Maker import Template_Maker
from DB.DB import DB
from Bug_Detect.Bug_Detect import Bug_Detect
from Fix_Modify.Fix_Modify  import Fix_Modify
from Fix_Evaluation.Fix_Evaluation  import Fix_Evaluation
from Data_Maker.Data_Maker import Data_Maker

class Manager:
    def __init__(self, db):
        self.data_base = db
        self.load()

    def load(self):
        print("Manager loads DB")
        #テンプレートのロード
        print("Template load is not implemented")
        sys.exit()

    def run(self):
        bug_detect = Bug_Detect(self.data_base)
        bug_detect.run()

        fix_modify = Fix_Modify(self.data_base)
        fix_modify.run()

        fix_evaluation = Fix_Evaluation()
        fix_evaluation.run()


@click.command()
@click.option('--template_make', is_flag=True, help="Template making mode")
@click.option('--data_make', is_flag=True, help="Data making mode")
@click.option('--auto_fix', is_flag=True, help="Auto fixing mode")
@click.option('--keyword', help="Keyword for thorwing Query")
@click.option('--template_make_status', '-s', is_flag=True, help="Flag whether making status or not")
@click.option('--debug_flag', '-D', is_flag=True, help="Flag debug mode")
@click.option('--article_id', default='', help='target article id (available in debug mode)')
def cmd(template_make, data_make, auto_fix, 
        keyword, template_make_status, debug_flag, article_id):
    # DBオブジェクト
    cache_write_flag=inifile.getboolean("DB_cache", "cache_write_flag")
    cache_read_flag=inifile.getboolean("DB_cache", "cache_read_flag")
    db = DB(cache_write_flag=cache_write_flag, cache_read_flag=cache_read_flag)

    # テンプレート作成モード
    if template_make:
        # Template_makerオブジェクト
        show_code = inifile.getboolean("Template_Maker", "show_code")
        simple_mode = inifile.getboolean("Template_Maker", "simple_mode")
        tm = Template_Maker(db, show_code=show_code, simple_mode=simple_mode, keyword=keyword, debug_flag=debug_flag, art_id=article_id)
        tm.run()

        # Template_makerのstat表示
        if template_make_status:
            tm.stat["correct"] = tm.stat["total"] - tm.stat["no_code"] - tm.stat["no_best_answer"] - tm.stat["not_compilable"]
            print(tm.stat)
    # データ作成モード
    elif data_make:
        out_path = inifile["Data_Maker"]["out_path"]
        data_maker = Data_Maker(db, out_path, keyword=keyword)
        data_maker.run()
    # 自動バグ修正モード(未実装)
    elif auto_fix:
        manager = Manager(db)
        manager.run()
    else:
        print("Need mode keyword")
        sys.exit()

def main():
    cmd()

if __name__ == "__main__":
    main()

