
import java.util.ArrayList;
import java.util.HashMap;

import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.ToolFactory;
import org.eclipse.jdt.core.compiler.IScanner;
import org.eclipse.jdt.core.compiler.ITerminalSymbols;
import org.eclipse.jdt.core.compiler.InvalidInputException;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.CompilationUnit;

import py4j.GatewayServer;
import py4j.Py4JException;

public class Main {
	static RewriteVisitor rw_visitor;
	public static void main(String[] args) {
		String mode = "";
		if (args.length > 0) {
			mode = args[0];
		}
		
		if (mode.equals("test")) {
			main();
		}else {
			Main app = new Main();
		    // app を gateway.entry_point に設定
		    GatewayServer server = new GatewayServer(app);
		    server.start();
		    System.out.println("Gateway Server Started");
		}
	}
	
	public static void main(){
		System.out.println("Hello");
		String src = "public class Main { \n"
				+ "Scanner in=new Scanner(System.in); }";
		ArrayList<String> list = get_masked_token(src);
		for (String string : list) {
			System.out.println(string);
		}
		String s = "";
		for (String string : list) {
			s += " " + string;
		}
	}
	
	public static ArrayList<String> get_token(String src){
		IScanner scanner = ToolFactory.createScanner(false, false, true, "1.9");
        scanner.setSource(src.toCharArray());
        ArrayList<String> list = new ArrayList<>();
        int tokenType;
        try {
			while ((tokenType = scanner.getNextToken()) != ITerminalSymbols.TokenNameEOF) {
			    String token = new String(scanner.getCurrentTokenSource());
			    list.add(token);
			}
		} catch (InvalidInputException e) {
			e.printStackTrace();
		}
		return list;
	}
	
	public String get_token_str(String src){
		ArrayList<String> list = get_token(src);
		String ret_str = "";
		for (String string : list) {
			ret_str += string +" ";
		}
		return ret_str;
	}
	
	public static ArrayList<String> get_masked_token(String src) throws Py4JException{
		// Create AST Parser
		ASTParser parser = ASTParser.newParser(AST.JLS8);
		parser.setSource(src.toCharArray());
		CompilationUnit unit = (CompilationUnit) parser.createAST(new NullProgressMonitor());
			
		try {
			rw_visitor = new RewriteVisitor();
			unit.accept(rw_visitor);
		} catch (Exception e) {
			//e.printStackTrace();
			throw new Py4JException();
		}
		
		int i = 0;
		String srcString = "";
        for (String string : unit.toString().split("\n")) {
        	String part = "/*"+i+"*/"+string+"\n";
        	srcString = srcString + part;
        	i++;
		}
		
		IScanner scanner = ToolFactory.createScanner(true, false, true, "1.9");
		//scanner.setSource(unit.toString().toCharArray());
		scanner.setSource(srcString.toCharArray());
        
        ArrayList<String> list = new ArrayList<>();
        int tokenType;
        try {
			while ((tokenType = scanner.getNextToken()) != ITerminalSymbols.TokenNameEOF) {
			    String token = new String(scanner.getCurrentTokenSource());
			    list.add(token);
			}
		} catch (InvalidInputException e) {
			e.printStackTrace();
		}
		return list;
	}
	
	public static String get_masked_token_str(String src) throws Py4JException{
		ArrayList<String> list = get_masked_token(src);
		String ret_str = "";
		for (String string : list) {
			ret_str += string +" ";
		}
		return ret_str;
	}
	
	public HashMap<String, Integer> get_var_map(){
		return rw_visitor.get_map();
	}
	
	public ArrayList<String> get_var_seq(){
		return rw_visitor.get_seq();
	}

}
