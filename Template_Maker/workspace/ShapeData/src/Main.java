import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.ToolFactory;
import org.eclipse.jdt.core.compiler.IScanner;
import org.eclipse.jdt.core.compiler.ITerminalSymbols;
import org.eclipse.jdt.core.compiler.InvalidInputException;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.CompilationUnit;

import py4j.GatewayServer;

public class Main {

	public static void main(String[] args) {
		Main app = new Main();
	    // app を gateway.entry_point に設定
	    GatewayServer server = new GatewayServer(app);
	    server.start();
	    System.out.println("Gateway Server Started");
	}

	public String get_token(String src){
		String ret = "";
		IScanner scanner = ToolFactory.createScanner(false, false, true, "1.9");
        scanner.setSource(src.toCharArray());
        int tokenType;
        try {
			while ((tokenType = scanner.getNextToken()) != ITerminalSymbols.TokenNameEOF) {
			    String token = new String(scanner.getCurrentTokenSource());
			    ret += token + " ";
			}
		} catch (InvalidInputException e) {
			e.printStackTrace();
		}
        return ret;
	}
	
	public String analyze(String src){
		// Create AST Parser
		ASTParser parser = ASTParser.newParser(AST.JLS8);
		parser.setSource(src.toCharArray());
		CompilationUnit unit = (CompilationUnit) parser.createAST(new NullProgressMonitor());
		TokenVisitor visitor = new TokenVisitor();
		unit.accept(visitor);
		return src;
			
	}
}
