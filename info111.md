現在 VUE および Front の POD に設定されている liveness/readiness Probe の動作について確認したく存じます。

現行設定は以下の通りです。

VUE
Path: /hc
Port: 3000

Front
Path: /health/html
Port: 8080

今回 GCP への移行に伴い、もし現状の Probe の確認ロジックがコード側でバックエンドのデータベースサーバの生死判定を行い、データベースに問題がない場合のみ 200 を返す仕様である場合、データベースが異常でも VUE/Front が 200 を返すようコードや通信方式の調整が必要になります。

つきましては確認させてください。
VUE/Front の liveness/readiness Probe のロジックにおいて、バックエンドデータベースサーバへの健康チェックは実装されていますでしょうか。
