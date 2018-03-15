import java.util.HashMap;
import java.util.List;

import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.Block;
import org.eclipse.jdt.core.dom.Expression;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.MethodInvocation;
import org.eclipse.jdt.core.dom.NumberLiteral;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.dom.SimpleType;
import org.eclipse.jdt.core.dom.Statement;
import org.eclipse.jdt.core.dom.StringLiteral;
import org.eclipse.jdt.core.dom.Type;
import org.eclipse.jdt.core.dom.VariableDeclaration;
import org.eclipse.jdt.core.dom.VariableDeclarationFragment;
import org.eclipse.jdt.core.dom.VariableDeclarationStatement;
import org.eclipse.jdt.internal.compiler.lookup.VariableBinding;

public class RewriteVisitor extends ASTVisitor {
	HashMap<String, String> Variable_Binding;
	
	public RewriteVisitor(){
		super();
		this.Variable_Binding = new HashMap<>();
	}
	
	public boolean visit(SimpleName node){
		String string = node.getFullyQualifiedName();
		if (node.resolveBinding() instanceof VariableBinding) {
			System.out.println(string);
		}
		return super.visit(node);
	}
	
	public boolean visit(VariableDeclarationFragment node){
		SimpleName sn = node.getName();
		int i = 0;
		String type_str;
		if (this.Variable_Binding.containsKey(sn.toString())) {
			type_str = this.Variable_Binding.get(sn.toString());
		}
		else {
			ASTNode _node = node.getParent();
			type_str = getVarType(_node);
			this.Variable_Binding.put(sn.toString(), type_str);
		}
		
		sn.setIdentifier(type_str+"_Var");
		System.out.println(sn.toString());
		return super.visit(node);
	}

	public boolean visit(MethodInvocation node) {
		Expression ex = node.getExpression();
		if (ex instanceof SimpleName) {
			SimpleName _sn = (SimpleName)ex;
			String type_str = this.Variable_Binding.get(_sn.toString());
			_sn.setIdentifier(type_str+"_Var");
			//SimpleName _sn = ex.getAST().newSimpleName("TOKEN");
			//node.setExpression(_sn);
			System.out.println(_sn.toString());
		}
		
		for (Object arg_node : node.arguments()) {
			if (arg_node instanceof SimpleName) {
				SimpleName _sn = (SimpleName)arg_node;
				String type_str = this.Variable_Binding.get(_sn.toString());
				_sn.setIdentifier(type_str+"_Var");
				System.out.println(_sn.toString());
			}
		}
		return super.visit(node);
	}
	
	private String getVarType(ASTNode node) {
		if (node instanceof VariableDeclarationStatement) {
			VariableDeclarationStatement vds = (VariableDeclarationStatement)node;
			Type type = vds.getType();
			if (type instanceof SimpleType) {
				SimpleType st = (SimpleType)type;
				String type_str = st.getName().toString();
				return type_str;
			}
		}
		return "NoType";
	}
	
	public boolean visit(StringLiteral node){
		node.setLiteralValue("StringLiteral");
		return super.visit(node);
	}
	
	public boolean visit(NumberLiteral node) {
		node.setToken("0");
		return super.visit(node);
	}
}