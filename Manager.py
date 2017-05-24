## マネージャクラス

from Templates.Template_Maker import Template_Maker
from DB import DB
from Bug_Detect.Bug_Detect import Bug_Detect
from Fix_Modify.Fix_Modify  import Fix_Modify
from Fix_Evaluation.Fix_Evaluation  import Fix_Evaluation

class Manager:
    def __init__(self):
        self.load()

    def load(self):
        print("Manager loads DB")
        self.data_base = DB()
        #テンプレートの生成
        Template_Maker(self.data_base).run()

    def run(self):
        bug_detect = Bug_Detect(self.data_base)
        bug_detect.run()

        fix_modify = Fix_Modify(self.data_base)
        fix_modify.run()

        fix_evaluation = Fix_Evaluation()
        fix_evaluation.run()


if __name__ == "__main__":
    manager = Manager()
    manager.run()
