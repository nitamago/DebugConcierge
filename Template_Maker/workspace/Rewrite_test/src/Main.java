import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IWorkspaceRoot;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.core.runtime.Path;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jface.text.Document;
import org.eclipse.jface.text.IDocument;
import org.eclipse.text.edits.TextEdit;
import org.eclipse.ui.editors.text.FileDocumentProvider;
import org.eclipse.ui.part.FileEditorInput;

public class Main {
	public static void main(String[] args) {
		String path = "/Users/HiroseMasayuki/Documents/Git/Debug_Concierge/Template_Maker/workspace/Rewrite_test/src/Main.java";
		try {
			rewrite_variable(path);
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public static void rewrite_variable(String path) throws IOException{
		FileReader fileReader = new FileReader(new File(path));
		BufferedReader br = new BufferedReader(fileReader);
		String total_src = "";
		String src;
		while((src = br.readLine()) != null){
		    total_src += src;
		    total_src += "\n";
		}
		System.out.println(total_src);
		
		ASTParser parser = ASTParser.newParser(AST.JLS8);
		parser.setKind(ASTParser.K_COMPILATION_UNIT);
		parser.setResolveBindings(true);
		parser.setSource(total_src.toCharArray());
		CompilationUnit unit = (CompilationUnit) parser.createAST(new NullProgressMonitor());
		RewriteVisitor visitor = new RewriteVisitor();
		unit.accept(visitor);
		
		System.out.println(unit.toString());
	}
}
