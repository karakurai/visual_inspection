本ディレクトリ内の[setup_tool_ja.zip](https://github.com/karakurai/visual_inspection/blob/main/setup_on_windows_ja/setup_tool_ja.zip)には、WindowsのPCでの本アプリケーションをインストール＆セットアップする際の便利ツールである下記ファイル入っています。
 - 初期セットアップ（画像検査アプリケーション）.bat　：初期セットアップする際に、一度だけ実行してください。
 - Pythonバージョン確認.bat　：実行することでアプリケーションを起動できます。

[こちら](https://github.com/karakurai/visual_inspection/blob/main/setup_on_windows_ja/setup_tool_ja.zip)のページの右上のダウンロードボタンを押し、[setup_tool_ja.zip](https://github.com/karakurai/visual_inspection/blob/main/setup_on_windows_ja/setup_tool_ja.zip)ファイルをダウンロードしてください。ダウンロードしたZIPファイルを展開し、ご利用ください。

これらの便利ツールは、Python3.9をインストール済みのWindowsPCで動作します。  
WindowsPCへのPython3.9のインストール方法は[「Pythonのインストール」](https://learn.microsoft.com/ja-jp/windows/python/beginners#install-python)を参照してください。


## 手順
### 初期セットアップ
 - 下記URLのリンクから、GitHubの画像検査アプリケーションのページを表示します。
   - https://github.com/karakurai/visual_inspection

 - 「Code」ボタン⇒「Download ZIP」ボタンを押して、ソースコードのZIPファイル（visual_inspection-main.zip）をダウンロードします。

 - ダウンロードが完了したら、 ZIPファイルをお好きな場所（画像検査アプリケーションのプログラムを配置したいディレクトリ）に移動させてください。この時点ではZIPファイルは展開しないでください。
 - 上記のZIPファイルを配置したディレクトリ内に、ダウンロードした下記ファイルを配置します。
   - 初期セットアップ（画像検査アプリケーション）.bat
   - Pythonバージョン確認.bat
 - 「初期セットアップ（画像検査アプリケーション）.bat」をダブルクリックして実行します。
 - コマンドプロンプトが自動起動し、セットアップ処理が実行されるので、しばらく待ちます。
 - 「画像検査アプリケーションの初期セットアップが正常完了しました。」と表示されれば、初期セットアップが完了です。

### アプリケーション起動
 - 「画像検査アプリケーション起動.bat」をダブルクリックして実行します。
 - 画像検査アプリケーションが自動起動され、画面が表示されます。
 - もし、アプリケーションのレイアウトが崩れていた場合、下記URLのリンク先のページを参考にして、OSのディスプレイ設定の拡大率を100%に設定してください。
   - https://support.microsoft.com/ja-jp/windows/windows-%E3%81%AE%E3%83%86%E3%82%AD%E3%82%B9%E3%83%88-%E3%82%B5%E3%82%A4%E3%82%BA%E3%82%92%E5%A4%89%E6%9B%B4%E3%81%99%E3%82%8B-1d5830c3-eee3-8eaa-836b-abcc37d99b9a

## 操作マニュアル
下記から操作マニュアルをダウンロードできます。  
[操作マニュアル](https://adfi.jp/wp-content/uploads/操作マニュアル.pdf)

## 製造業向け情報
下記ファイルを修正することで、カメラのFPSや解像度など、アプリケーションの初期値を変更できます。  
ただし、設定変更できないカメラの場合、値は反映されません。
```
conf.ini
```

AIモデル作成のための学習画像は下記ディレクトリに保存されます。
```
dataset
```

検査した画像は下記ディレクトリに保存されます。
```
inspection_image
```

結果画像と結果CSVは下記ディレクトリに保存されます。
```
result
```
