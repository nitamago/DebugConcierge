import javalang
import glob

class Bug_Detect:
    def __init__(self, DB):
        self.DB = DB

    def run(self):
        print("bug_detect is running")
        #各テンプレートに対してマッチングを試す
        """
        for template in template_list:
            print("trying "+template.id+"\n")
            bug_list = self.detect(template)
        """
        #対象ソースのリスト化
        src_list = glob.glob("test_src/*.java")
    
        #各ソースに関連するテンプレートの検索
        src_to_template = {}
        for src in src_list:
            src_to_template = self.search_template(src)

        #コードクローン検出でバグを探す
        

        try:
            f = open("test_src/target_src.java")
            src = f.read()
            tree = javalang.parse.parse(src)
            for path, node in tree:
                print("{0}, {1}".format(path, node.types[0].name))
        except javalang.parser.JavaSyntaxError:
            print("Java Syntax error")

    def detect(self, template):
        bug_list = []
        for src in self.src_list:
            bug_list.append(self.matching(src, template))
        return bug_list

    def search_template(self, src):
        src_str = open(src).read()


