# Debug_Concierge
自動バグ修正を目指した残滓がここに眠る

## 準備
### Template_Maker/workspace内のEclipseプロジェクトを実行可能jarにする

1. Base_Info_AnalysisプロジェクトをBaseInfo.jarにビルドし、Template_Maker/BaseInfo.jarに配置する

1. ShapeDataプロジェクトをShapeData.jarにビルドし、Data_Maker/ShapeData.jarに配置する

1. SrcTokenizerプロジェクトをSrcTokenizer.jarにビルドし、Template_Maker/SrcTokenizer.jarに配置する

1. scorpio.jarをTemplate_Maker/Code_Cloneに置く

### 環境に合わせたConfig.iniを書くこと
* [ ] scorpio_dirは正しいディレクトリを指しているか

* [ ] q_codes_dirは正しいディレクトリを指しているか

* [ ] a_codes_dirは正しいディレクトリを指しているか

* [ ] clone_result_dirは正しいディレクトリを指しているか

* [ ] store_dirは正しいディレクトリを指しているか

## DeepFix用データの作成
生入力データの生成（すごく時間がかかるのでscreenなどを使うことをオススメする）
```
python Manager.py --keyword android --template_make
```

**アドレスが既に使用中ですと表示される場合**

`ps aux | grep java`の結果に、java -cp /home/.pyenv/ ... ってプロセスがあると思うので、それをkillする

Template_Maker/BaseInfo/resultの中にたくさんディレクトリができるはず

生入力データをDeepFix用に整形する
```
python Manager.py --keyword android --data_make
```
これでinput.txtとoutput.txtができるはず
