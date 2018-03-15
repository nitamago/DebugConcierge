
public class TupleUtil {
	public static class Pair<A, B>{	
		public final A ca;
		public final B cb;
		public Pair(A ca_, B cb_){
			ca = ca_;
			cb = cb_;
		}
	}
	
	public static class Triple<A, B, C>{	
		public final A ca;
		public final B cb;
		public final C cc;
		public Triple(A ca_, B cb_, C cc_){
			ca = ca_;
			cb = cb_;
			cc = cc_;
		}
		
		@Override
		public String toString(){
			return ca.toString() +" "+ cb.toString() +" "+ cc.toString();
		}
	}
	
}
