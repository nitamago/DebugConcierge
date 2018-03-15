import java.util.ArrayList;
import java.util.List;

import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.Block;
import org.eclipse.jdt.core.dom.ExpressionStatement;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.MethodInvocation;
import org.eclipse.jdt.core.dom.ReturnStatement;
import org.eclipse.jdt.core.dom.Statement;
import org.eclipse.jdt.core.dom.VariableDeclarationFragment;
import org.eclipse.jdt.core.dom.VariableDeclarationStatement;

public class TokenVisitor extends ASTVisitor {

	ArrayList<String> tokens;
	
	public TokenVisitor(){
		tokens = new ArrayList<>();
	}
	
	public boolean visit(MethodDeclaration node){
		Block body = node.getBody();
		for (Statement statement : (List<Statement>) body.statements()) {
            if (statement instanceof ExpressionStatement) {
				System.out.println(statement);
				ExpressionStatement ES = (ExpressionStatement)statement;
			}
            else if (statement instanceof ReturnStatement) {
				System.out.println(statement);
			}
            else if (statement instanceof VariableDeclarationStatement) {
				System.out.println(statement);
				VariableDeclarationStatement VDS = (VariableDeclarationStatement)statement;
				String type = VDS.getType().toString();
			}
		}
		return super.visit(node);
	}

}
