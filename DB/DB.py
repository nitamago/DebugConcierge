# テンプレートのデーータベース
import configparser

inifile = configparser.ConfigParser()
inifile.read("config.ini")

from Templates.Template import Template
from elasticsearch import Elasticsearch
import copy
import json
import pickle
from logging import getLogger, StreamHandler, NullHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
#handler = NullHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

class DB:
    def __init__(self, cache_write_flag=False, cache_read_flag=False):
        self.templates = {}
        self.db_address = inifile["settings"]["host"]
        self.db_port = inifile["settings"]["port"]
        self.es = Elasticsearch(['http://'+self.db_address+':'+self.db_port])
        self.index = "code_concierge"
        self.q_doc_type = "question_posts"
        self.a_doc_type = "answer_posts"
        self.size = 1000

        self.load_templates()

        self.cache_write_flag = cache_write_flag
        self.cache_read_flag = cache_read_flag

    def load_templates(self):
        print("DB loads templates")
        self.template = Template()

    def get_records(self, kywd, doc_type):
        query = {
            "query": {
                "simple_query_string": {
                    "query" : kywd,
                    "fields": ["Body"],
                    "default_operator" : "and",
                }
            }
         }
        
        res = self.es.search(index = self.index, doc_type = doc_type, body = query)
        return res

    def get_records_by_tag(self, kywd, doc_type):
        print("flag is {0}".format(self.cache_read_flag))

        if self.cache_read_flag:
            logger.debug("DB cache mode is on")
            f = open("./DB/DB.cache", "br")
            res = pickle.load(f)
            f.close()
        else:
            query = {
                "query": {
                    "term" : {
                        "Tags" : kywd,
                    }
                },
                "size" : self.size,
            }
            res = self.es.search(index = self.index, doc_type = doc_type, body = query)
            if self.cache_write_flag:
                f = open("DB/DB.cache", "bw")
                pickle.dump(res, f)
                f.close()
        return res

    def get_best_answer_record(self, kywd):
        query = {
            "query": {
                "simple_query_string": {
                    "query" : kywd,
                    "fields": ["Id"],
                    "default_operator" : "and",
                }
            }
         }
        if self.cache_read_flag:
            f = open("DB/DB_best_answer.cache", "rb")
            res = pickle.load(f)
            f.close()
        else:
            res = self.es.search(index = self.index, doc_type = self.a_doc_type, body = query)
            if self.cache_write_flag:
                f = open("DB/DB_best_answer.cache", "wb")
                pickle.dump(res, f)
                f.close()
        return res


    def get_records_by_parent_id(self, kywd):
        query = {
            "query": {
                "simple_query_string": {
                    "query" : kywd,
                    "fields": ["ParentId"],
                    "default_operator" : "and",
                }
            }
         }
        res = self.es.search(index = self.index, doc_type = self.a_doc_type, body = query)
        return res

    def get_all_records(self, doc_type):
        query = {
            "query": {
                "match_all" : {},
            }
         }
        res = self.es.search(index = self.index, doc_type = doc_type, body = query)
        return res

    def put_template(self, template):
        print("Put template "+template.tmplt_id)
        self.templates[template.tmplt_id] = template

    def get_template(self, template_id):
        return self.templates[template_id]

    def write_template(self):
        f = open("DB/Templates/Template.txt")
        template_txt = f.read()
        f.close()
        for id, template in self.templates.items():
            tmp = template_txt
            tmp = tmp.replace("<template_id>", template.tmplt_id)

            code_str = "["
            for i in range(0, len(template.target_code)):
                code = template.target_code[i].replace("\\","\\\\")
                if i != 0:
                    code_str += ",\""+ code.replace("\"","\\\"").replace("\n", "\\n") +"\""
                else:
                    code_str += "\""+ code.replace("\"","\\\"").replace("\n", "\\n") +"\""
            code_str += "]"
            tmp = tmp.replace("<target_code>", code_str)

            code_str = "["
            for i in range(0, len(template.modify_code)):
                code = template.modify_code[i].replace("\\","\\\\")
                if i != 0:
                    code_str += ",\""+ code.replace("\"","\\\"").replace("\n", "\\n") +"\""
                else:
                    code_str += "\""+ code.replace("\"","\\\"").replace("\n", "\\n") +"\""
            code_str += "]"
            tmp = tmp.replace("<modify_code>", code_str)

            tmp = tmp.replace("<api_tag>", "\""+ template.api_tag +"\"")
            tmp = tmp.replace("<apply_constraint>", "\""+ template.apply_constraint +"\"")
            f = open("DB/Templates/"+template.tmplt_id+".tmplt", "w")
            f.write(tmp)
            f.close()
        


if __name__ == "__main__":
    db = DB()
    #json = db.get_records_by_parent_id(13685871, db.q_doc_type)
    json = db.get_records_by_tag("java", db.q_doc_type)
    print(json["hits"]["hits"][0]["_source"].keys())
