#コードクローンを解析して、差分を検出するクラス

import os
import sys
import javalang
from javalang.tree import *
from logging import getLogger, StreamHandler, NullHandler, DEBUG

logger = getLogger(__name__)
#handler = StreamHandler()
handler = NullHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

class Clone_Analyzer:
    def __init__(self, show_code=True):
        self.show_code = show_code

        self.result_dir = "Templates/Code_Clone/result"

    def run(self, template):
        logger.debug("Clone Analyzer running")

        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
        f = open(self.result_dir +"/"+ template.tmplt_id + ".xml")
        for line in f:
            contents = line.split("\t")
            self.extract(contents, template)
           
        f.close()
        #sys.exit()
    
    def extract(self, contents, template):
            q_start = int(contents[1])
            q_end = int(contents[2])
            a_start = int(contents[4])
            a_end = int(contents[5])

            q_diffs = []
            a_diffs = []

            if contents[6] != "-":
                q_diffs = [int(x) - q_start for x in contents[6].split(",")]
            if contents[7].replace("\n", "") != "-":
                a_diffs = [int(x) - a_start for x in contents[7].split(",")]

            q_code_index = contents[0].split("/")[-1].split("_")[1].replace(".java", "")
            target_code = template.target_code[int(q_code_index)]
            target_code_separated = target_code.split("\n")
 
            a_code_index = contents[3].split("/")[-1].split("_")[1].replace(".java", "")
            modify_code = template.modify_code[int(a_code_index)]
            modify_code_separated = modify_code.split("\n")

            for i in q_diffs:
                   target_code_separated[i] = "~~~~~~"
            for i in a_diffs:
                   modify_code_separated[i] = "~~~~~~"

            if "\n".join(target_code_separated[q_start: q_end+1]) != "\n".join(modify_code_separated[a_start: a_end+1]):
                if self.show_code:
                    print("================================================")
                    print("\n".join(target_code_separated[q_start: q_end+1]))
                    print("=================================================")
                    print("\n".join(modify_code_separated[a_start: a_end+1]))
                    print("================================================")         

            q_tree = self.divide_syntax_element(target_code)
            a_tree = self.divide_syntax_element(modify_code)

            self.get_tree_diff(q_tree, a_tree, q_start, q_end, a_start, a_end)

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

    def get_tree_diff(self, q_tree, a_tree, q_start, q_end, a_start, a_end):
        for path, node in q_tree:
            """
            if isinstance(node, CompilationUnit):
                #attrs = ("package", "imports", "types")
                print("CompilationU {0} {1} {2}".format(node.package, node.imports, node.types))
            if isinstance(node, Import):
                #attrs = ("path", "static", "wildcard")
                print("Import")
            if isinstance(node, Documented):
                #attrs = ("documentation",)
                print("Documented")
            if isinstance(node, Declaration):
                #attrs = ("modifiers", "annotations")
                print("Declaration {0} {1}".format(node.modifiers, node.annotations))
            if isinstance(node, TypeDeclaration):
                #attrs = ("name", "body")
                print("TypeDeclaration {0} {1}".format(node.name, node.body))
            if isinstance(node, PackageDeclaration):
                #attrs = ("name",)
                print("PackageDeclaration")
            if isinstance(node, ClassDeclaration):
                #attrs = ("type_parameters", "extends", "implements")
                print("ClassDeclaration")
            if isinstance(node, EnumDeclaration):
                #attrs = ("implements",)
                print("EnumDeclaration")
            if isinstance(node, InterfaceDeclaration):
                #attrs = ("type_parameters", "extends",)
                print("InterfaceDeclaration")
            if isinstance(node, AnnotationDeclaration):
                #attrs = ()
                print("AnnotationDeclaration")
            # ------------------------------------------------------------------------------
            if isinstance(node, Type):
                #attrs = ("name", "dimensions",)
                print("Type {0} {1}".format(node.name, node.dimensions))
            if isinstance(node, BasicType):
                #attrs = ()
                print("BasicType {0} {1}".format(node.name, node.dimensions))
            if isinstance(node, ReferenceType):
                #attrs = ("arguments", "sub_type")
                print("ReferenceType")
                print(node.arguments)
            if isinstance(node, TypeArgument):
                #attrs = ("type", "pattern_type")
                print("TypeArgument {0}".format(node.type, node.pattern_type))
            # ------------------------------------------------------------------------------
            if isinstance(node, TypeParameter):
                #attrs = ("name", "extends")
                print("TypeParameter {0} {1}".format(node.name, node.extends))
            # ------------------------------------------------------------------------------
            if isinstance(node, Annotation):
                #attrs = ("name", "element")
                print("Annotation")
            if isinstance(node, ElementValuePair):
                #attrs = ("name", "value")
                print("ElementValuePair")
            if isinstance(node, ElementArrayValue):
                #attrs = ("values",)
                print("ElementArrayValue")
            # ------------------------------------------------------------------------------
            if isinstance(node, Member):
            #class Member(Documented):
                #attrs = ()
                print("Member {0}".format(node.documentation))
            if isinstance(node, MethodDeclaration):
                #attrs = ("type_parameters", "return_type", "name", "parameters", "throws", "body")
                print("MethodDeclaration {0} {1} {2} {3} {4} {5}".format(node.type_parameters, node.return_type, node.name, node.parameters, node.throws, node.body))
            if isinstance(node, FieldDeclaration):
                #attrs = ("type", "declarators")
                print("FieldDeclaration")
            if isinstance(node, ConstructorDeclaration):
                #attrs = ("type_parameters", "name", "parameters", "throws", "body")
                print("ConstructorDeclaration {0}".format(node.name))
            # ------------------------------------------------------------------------------
            if isinstance(node, ConstantDeclaration):
                #attrs = () 
                print("ConstantDeclaration")
            if isinstance(node, ArrayInitializer):
                #attrs = ("initializers",)
                print("ArrayInitializer")
            if isinstance(node, VariableDeclaration):
                #attrs = ("type", "declarators")
                print("Variable {0} {1}".format(node.type, node.declarators))
            if isinstance(node, LocalVariableDeclaration):
                #attrs = ()
                print("LocalVariableDeclaration")
            if isinstance(node, VariableDeclarator):
                #attrs = ("name", "dimensions", "initializer")
                print("VariableDeclarator {0} {1} {2}".format(node.name, node.dimensions, node.initializer))
            if isinstance(node, FormalParameter):
                #attrs = ("type", "name", "varargs")
                print("FormalParameter {0} {1} {2}".format(node.type, node.name, node.varargs))
            if isinstance(node, InferredFormalParameter):
                #attrs = ('name',)
                print("InferredFormalParameter")
            # ------------------------------------------------------------------------------
            if isinstance(node, Statement):
                #attrs = ("label",)
                print("Statement {0}".format(node.label))
            if isinstance(node, IfStatement):
                #attrs = ("condition", "then_statement", "else_statement")
                print("If {0} {1}".format(node.condition, node.then_statement))
            if isinstance(node, WhileStatement):
                #attrs = ("condition", "body")
                print("WhileStatement")
            if isinstance(node, DoStatement):
                #attrs = ("condition", "body")
                print("DoStatement")
            if isinstance(node, ForStatement):
                #attrs = ("control", "body")
                print("ForStatement")
            if isinstance(node, AssertStatement):
                #attrs = ("condition", "value")
                print("AssertStatement")
            if isinstance(node, BreakStatement):
                #attrs = ("goto",)
                print("BreakStatement")
            if isinstance(node, ContinueStatement):
                #attrs = ("goto",)
                print("ContinueStatement")
            if isinstance(node, ReturnStatement):
                #attrs = ("expression",)
                print("Return {0}".format(node.expression))
            if isinstance(node, ThrowStatement):
                #attrs = ("expression",)
                print("ThrowStatement")
            if isinstance(node, SynchronizedStatement):
                #attrs = ("lock", "block")
                print("SynchrinizedStatement")
            if isinstance(node, TryStatement):
                #attrs = ("resources", "block", "catches", "finally_block")
                print("TryStatement")
            if isinstance(node, SwitchStatement):
                #attrs = ("expression", "cases")
                print("SwitchStatement")
            if isinstance(node, BlockStatement):
                #attrs = ("statements",)
                print("BlockStatement {0}".format(node.statements))
            if isinstance(node, StatementExpression):
                #attrs = ("expression",)
                print("StatementExpression {0}".format(node.expression))
            # ------------------------------------------------------------------------------
            if isinstance(node, TryResource):
                #attrs = ("type", "name", "value")
                print("TryRes {0} {1} {2}".format(node.type, node.name, node.value))
            if isinstance(node, CatchClause):
                #attrs = ("parameter", "block")
                print("CatchClause")
            if isinstance(node, CatchClauseParameter):
                #attrs = ("types", "name")
                print("CatchCaluseParameter")
            # ------------------------------------------------------------------------------
            if isinstance(node, SwitchStatementCase):
                #attrs = ("case", "statements")
                print("SwitchStatement")
            if isinstance(node, ForControl):
                #attrs = ("init", "condition", "update")
                print("ForControl {0} {1} {2}".format(node.init, node.condition, node.update))
            if isinstance(node, EnhancedForControl):
                #attrs = ("var", "iterable")
                print("EnhancedForControl")
            # ------------------------------------------------------------------------------
            if isinstance(node, Expression):
                #attrs = ()
                print("Expression")
            if isinstance(node, Assignment):
                #attrs = ("expressionl", "value", "type")
                print("Assign {0} {1} {2}".format(node.expressionl, node.value, node.type))
            if isinstance(node, TernaryExpression):
                #attrs = ("condition", "if_true", "if_false")
                print("TernaryExpression")
            if isinstance(node, BinaryOperation):
                #attrs = ("operator", "operandl", "operandr")
                print("binaryOperation {0} {1} {2}".format(node.operator, node.operandl, node.operandr))
            if isinstance(node, Cast):
                #attrs = ("type", "expression")
                print("Cast")
            if isinstance(node, MethodReference):
                #attrs = ("expression", "method", "type_arguments")
                print("MethodRefernece")
            if isinstance(node, LambdaExpression):
                #attrs = ('parameters', 'body')
                print("LambdaExpression")
            # ------------------------------------------------------------------------------
            if isinstance(node, Primary):
                #attrs = ("prefix_operators", "postfix_operators", "qualifier", "selectors")
                print("Primary {0} {1} {2} {3}".format(node.prefix_operators, node.postfix_operators, node.qualifier, node.selectors))
            if isinstance(node, Literal):
                #attrs = ("value",)
                print("Literal {0}".format(node.value))
            if isinstance(node, This):
                #attrs = ()
                print("This")
            if isinstance(node, MemberReference):
                #attrs = ("member",)
                print("MemberRef {0}".format(node.member))
            if isinstance(node, Invocation):
                #attrs = ("type_arguments", "arguments")
                print("Invocation {0} {1}".format(node.type_arguments, node.arguments))
            if isinstance(node, ExplicitConstructorInvocation):
                #attrs = ()
                print("ExplicitConstructorInvocatio")
            if isinstance(node, SuperConstructorInvocation):
                #attrs = ()
                print("SuperConstructorInvocatio")
            if isinstance(node, MethodInvocation):
                #attrs = ("member",)
                print(node.member)
            if isinstance(node, SuperMethodInvocation):
                #attrs = ("member",)
                print(node.member)
            if isinstance(node, SuperMemberReference):
                #attrs = ("member",)
                print(node.name)
            if isinstance(node, ArraySelector):
                #attrs = ("index",)
                print(node.name)
            if isinstance(node, ClassReference):
                #attrs = ("type",)
                print(node.name)
            if isinstance(node, VoidClassReference):
                #attrs = ()
                print(node.name)
            # ------------------------------------------------------------------------------
            if isinstance(node, Creator):
                #attrs = ("type",)
                print("Ceator")
            if isinstance(node, ArrayCreator):
                #attrs = ("dimensions", "initializer")
                print(node.name)
            if isinstance(node, ClassCreator):
                #attrs = ("constructor_type_arguments", "arguments", "body")
                print("ClassCreator {0} {1} {2}".format(node.constructor_type_arguments, node.arguments, node.body))
            if isinstance(node, InnerClassCreator):
                #attrs = ("constructor_type_arguments", "arguments", "body")
                print(node.name)
            # -----------------------------------------------------------------------------
            if isinstance(node, EnumBody):
                #attrs = ("constants", "declarations")
                print(node.name)
            if isinstance(node, EnumConstantDeclaration):
                #attrs = ("name", "arguments", "body")
                print("EnumConstantDeclaration")
            if isinstance(node, AnnotationMethod):
                #attrs = ("name", "return_type", "dimensions", "default")
                print("AnnotationMethod")
            else:
                print("$$$$$$")
                #print("$$$$ {0}".format(node.types[0].name))
            """
            if isinstance(node, TypeDeclaration):
                #attrs = ("name", "body")
                print("TypeDeclaration {0}".format(node.name))
            if isinstance(node, Type):
                #attrs = ("name", "dimensions",)
                print("Type {0}".format(node.name))
            if isinstance(node, TypeParameter):
                #attrs = ("name", "extends")
                print("TypeParameter {0}".format(node.name))
            if isinstance(node, MethodDeclaration):
                #attrs = ("type_parameters", "return_type", "name", "parameters", "throws", "body")
                print("MethodDeclaration {0}".format(node.name))
            if isinstance(node, ConstructorDeclaration):
                #attrs = ("type_parameters", "name", "parameters", "throws", "body")
                print("ConstructorDeclaration {0}".format(node.name))
            if isinstance(node, VariableDeclarator):
                #attrs = ("name", "dimensions", "initializer")
                print("VariableDeclarator {0}".format(node.name))
            if isinstance(node, FormalParameter):
                #attrs = ("type", "name", "varargs")
                print("FormalParameter {0}".format(node.name))
            if isinstance(node, Literal):
                #attrs = ("value",)
                print("Literal {0}".format(node.value))
            if isinstance(node, MethodInvocation):
                #attrs = ("type_arguments", "arguments")
                print("MethodInvocation {0}".format(node.member))
            if isinstance(node, MethodReference):
                #attrs = ("expression", "method", "type_arguments")
                print("MethodRefernece {0}".format(node.method))
            
        #sys.exit()

class ConvertError(Exception):
    def __str__(self):
        return "This is Convert Exception"

if __name__ == "__main__":
    tm = Template_Maker(DB(), show_code=False)
    tm.run()
    tm.stat["correct"] = tm.stat["total"] - tm.stat["no_code"] - tm.stat["no_best_answer"] - tm.stat["not_compilable"]
    print(tm.stat)
