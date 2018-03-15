# Debug_Concierge
自動バグ修正を目指した残滓がここに眠る

## 準備
Template_Maker/workspace内のEclipseプロジェクトを実行可能jarにする

1. Base_Info_AnalysisプロジェクトをBaseInfo.jarにビルドし、Template_Maker/BaseInfo.jarに配置する

1. ShapeDataプロジェクトをShapeData.jarにビルドし、Data_Maker/ShapeData.jarに配置する

1. SrcTokenizerプロジェクトをSrcTokenizer.jarにビルドし、Template_Maker/SrcTokenizer.jarに配置する

1. scorpio.jarをTemplates/Code_Cloneに置く

環境に合わせたConfig.iniを書くこと

## DeepFix用データの作成
生入力データの生成
```
python Manager.py --keyword android --template_make
```

Template_Maker/BaseInfo/resultの中にたくさんディレクトリができるはず

