## テンプレートクラス


class Template:
    def __init__(self, tmplt_id=None, target_code=None, modify_code=None, api_tag=None, apply_constraint=None):
        self.tmplt_id = tmplt_id
        self.target_code = target_code
        self.modify_code = modify_code
        self.api_tag = api_tag
        self.apply_constraint = apply_constraint

    def set_diff_info(self, diff_info_list):
        self.diff_info_list = diff_info_list

