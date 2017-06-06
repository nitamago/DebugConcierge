## マネージャクラス

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

import sys
from Template_Maker.Template_Maker import Template_Maker
from DB.DB import DB
from Bug_Detect.Bug_Detect import Bug_Detect
from Fix_Modify.Fix_Modify  import Fix_Modify
from Fix_Evaluation.Fix_Evaluation  import Fix_Evaluation

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
@click.option('--template_make', '-t', is_flag=True)
@click.option('--template_make_status', '-s', is_flag=True)
def cmd(template_make, template_make_status):
    if template_make:
        # DBオブジェクト
        cache_write_flag=inifile.getboolean("DB_cache", "cache_write_flag")
        cache_read_flag=inifile.getboolean("DB_cache", "cache_read_flag")
        db = DB(cache_write_flag=cache_write_flag, cache_read_flag=cache_read_flag)

        # Template_makerオブジェクト
        show_code=inifile.getboolean("Template_Maker", "show_code")
        simple_mode=inifile.getboolean("Template_Maker", "simple_mode")
        tm = Template_Maker(db, show_code=show_code, simple_mode=simple_mode)
        tm.run()
        
        # Template_makerのstat表示
        if template_make_status:
            tm.stat["correct"] = tm.stat["total"] - tm.stat["no_code"] - tm.stat["no_best_answer"] - tm.stat["not_compilable"]
            print(tm.stat)
    else:
        db = DB()

    manager = Manager(db)
    manager.run()

def main():
    cmd()

if __name__ == "__main__":
    main()
    
