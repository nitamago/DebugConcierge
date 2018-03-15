import java.util.ArrayList;
import java.util.HashMap;

import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.ArrayType;
import org.eclipse.jdt.core.dom.Assignment;
import org.eclipse.jdt.core.dom.Expression;
import org.eclipse.jdt.core.dom.FieldAccess;
import org.eclipse.jdt.core.dom.InfixExpression;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.MethodInvocation;
import org.eclipse.jdt.core.dom.Name;
import org.eclipse.jdt.core.dom.NumberLiteral;
import org.eclipse.jdt.core.dom.PrimitiveType;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.dom.SimpleType;
import org.eclipse.jdt.core.dom.SingleVariableDeclaration;
import org.eclipse.jdt.core.dom.StringLiteral;
import org.eclipse.jdt.core.dom.Type;
import org.eclipse.jdt.core.dom.VariableDeclarationFragment;
import org.eclipse.jdt.core.dom.VariableDeclarationStatement;

public class RewriteVisitor extends ASTVisitor {
	HashMap<String, String> Variable_Binding;
	private HashMap<String, Integer> Variable_Map;
	private ArrayList<String> Variable_Seq;
	
	public RewriteVisitor(){
		super();
		this.Variable_Binding = new HashMap<>();
		this.Variable_Map = new HashMap<>();
		this.Variable_Seq = new ArrayList<>();
	}
	
	public void init_map_and_seq(){
		this.Variable_Map = new HashMap<>();
		this.Variable_Seq = new ArrayList<>();
	}
	
	public HashMap<String, Integer> get_map(){
		return this.Variable_Map;
	}
	
	public ArrayList<String> get_seq(){
		return this.Variable_Seq;
	}
	
	public boolean visit(MethodDeclaration node){
		for (Object _node : node.parameters()) {
			if (_node instanceof SingleVariableDeclaration) {
				Type _type = ((SingleVariableDeclaration) _node).getType();
				if (_type instanceof SimpleType) {
					String type_str = _type.toString();
					SimpleName _sn = ((SingleVariableDeclaration) _node).getName();
					this.Variable_Binding.put(_sn.toString(), type_str);
					if (!this.Variable_Map.containsKey(_sn.toString())){
						this.Variable_Map.put(_sn.toString(), Variable_Map.size()+1);
					}
					this.Variable_Seq.add(_sn.toString());
					_sn.setIdentifier(_sn.toString()+"_"+type_str+"_Var");
				}
				else if (_type instanceof ArrayType) {
					String type_str = ((ArrayType) _type).getElementType().toString()+"_ARRAY";
					SimpleName _sn = ((SingleVariableDeclaration) _node).getName();
					this.Variable_Binding.put(_sn.toString(), type_str);
					if (!this.Variable_Map.containsKey(_sn.toString())){
						this.Variable_Map.put(_sn.toString(), Variable_Map.size()+1);
					}
					this.Variable_Seq.add(_sn.toString());
					_sn.setIdentifier(_sn.toString()+"_"+type_str+"_Var");
				}
			}
		}
		return super.visit(node);
	}
	
	public boolean visit(VariableDeclarationStatement node) {
		Type _type = node.getType();
		
		// For primitive variable
		if (_type instanceof PrimitiveType) {
			String type_str = _type.toString();
			for (Object _node : node.fragments()) {
				if (_node instanceof VariableDeclarationFragment) {
					SimpleName _sn = ((VariableDeclarationFragment) _node).getName();
					this.Variable_Binding.put(_sn.toString(), type_str);
					if (!this.Variable_Map.containsKey(_sn.toString())){
						this.Variable_Map.put(_sn.toString(), Variable_Map.size()+1);
					}
					this.Variable_Seq.add(_sn.toString());
				}
			}
		}
		else if (_type instanceof SimpleType) {
			SimpleType _st = (SimpleType)_type;
			Name _name = _st.getName();
			String type_str = _name.toString();
			for (Object _node : node.fragments()) {
				if (_node instanceof VariableDeclarationFragment) {
					SimpleName _sn = ((VariableDeclarationFragment) _node).getName();
					this.Variable_Binding.put(_sn.toString(), type_str);
					if (!this.Variable_Map.containsKey(_sn.toString())){
						this.Variable_Map.put(_sn.toString(), Variable_Map.size()+1);
					}
					this.Variable_Seq.add(_sn.toString());
				}
			}
		}
		return super.visit(node);
	}
	
	public boolean visit(VariableDeclarationFragment node){
		SimpleName sn = node.getName();
		String type_str;
		if (this.Variable_Binding.containsKey(sn.toString())) {
			type_str = this.Variable_Binding.get(sn.toString());
		}
		else {
			ASTNode _node = node.getParent();
			type_str = getVarType(_node);
			this.Variable_Binding.put(sn.toString(), type_str);
			if (!this.Variable_Map.containsKey(sn.toString())){
				this.Variable_Map.put(sn.toString(), Variable_Map.size()+1);
			}
			this.Variable_Seq.add(sn.toString());
		}
		
		sn.setIdentifier(sn.toString()+"_"+type_str+"_Var");
		return super.visit(node);
	}

	public boolean visit(MethodInvocation node) {
		Expression ex = node.getExpression();
		if (ex instanceof SimpleName) {
			SimpleName _sn = (SimpleName)ex;
			String type_str = this.Variable_Binding.get(_sn.toString());
			_sn.setIdentifier(_sn.toString()+"_"+type_str+"_Var");
		}
		
		for (Object arg_node : node.arguments()) {
			if (arg_node instanceof SimpleName) {
				SimpleName _sn = (SimpleName)arg_node;
				String type_str = this.Variable_Binding.get(_sn.toString());
				_sn.setIdentifier(_sn.toString()+"_"+type_str+"_Var");
			}
		}
		return super.visit(node);
	}
	
	public boolean visit(Assignment node) {
		Expression _L_ex = node.getLeftHandSide();
		if (_L_ex instanceof SimpleName) {
			SimpleName _sn = (SimpleName)_L_ex;
			String type_str = this.Variable_Binding.get(_sn.toString());
			_sn.setIdentifier(_sn.toString()+"_"+type_str+"_Var");
		}
		Expression _R_ex = node.getRightHandSide();
		if (_R_ex instanceof SimpleName) {
			SimpleName _sn = (SimpleName)_R_ex;
			String type_str = this.Variable_Binding.get(_sn.toString());
			_sn.setIdentifier(_sn.toString()+"_"+type_str+"_Var");
		}
		
		return super.visit(node);
	}
	
	public boolean visit(FieldAccess node){
		SimpleName _sn = node.getName();
		String type_str = this.Variable_Binding.get(_sn.toString());
		_sn.setIdentifier(_sn.toString()+"_"+type_str+"_Var");
		return super.visit(node);
	}
	
	public boolean visit(InfixExpression node){
		Expression _L_ex = node.getLeftOperand();
		if (_L_ex instanceof SimpleName) {
			String type_str = this.Variable_Binding.get(_L_ex.toString());
			((SimpleName) _L_ex).setIdentifier(_L_ex.toString()+"_"+type_str+"_Var");
		}
		Expression _R_ex = node.getRightOperand();
		if (_R_ex instanceof SimpleName) {
			String type_str = this.Variable_Binding.get(_R_ex.toString());
			((SimpleName) _R_ex).setIdentifier(_R_ex.toString()+"_"+type_str+"_Var");
		}
		for (Object _node : node.extendedOperands()) {
			if (_node instanceof SimpleName) {
				String type_str = this.Variable_Binding.get(_node.toString());
				((SimpleName) _node).setIdentifier(_node.toString()+"_"+type_str+"_Var");
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