OKです。
**要件は「jq -c（1アクセス=1行）＋ wc -l で正しく統計したい」**ですね。
結論から言うと、**以下の形が“正解パターン”**です。

---

# 正解コマンド（そのまま使ってOK）

## 前提

* ログ：`gd-access.2025-12-23T19.log`
* 時間範囲：`19:32:35` ～ `19:34:15`
* path：**図のホワイトリストのみ**

---

## ① 合計アクセス件数（jq -c + wc -l）

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 19:32:35")
    and
    (.timestamp <  "2025-12-23 19:34:15")
    and
    (
      .path == "/user/"
      or .path == "/user/re-post"
      or .path == "/user/report"
      or .path == "/user/distribution"
      or .path == "/user/recruit"
      or .path == "/search"
      or .path == "/api"
    )
  )
' gd-access.2025-12-23T19.log | wc -l
```

👉 **この wc -l の数値 = 正しいアクセス件数**

---

## ② path ごとの件数も出したい場合（統計用）

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 19:32:35")
    and
    (.timestamp <  "2025-12-23 19:34:15")
    and
    (
      .path == "/user/"
      or .path == "/user/re-post"
      or .path == "/user/report"
      or .path == "/user/distribution"
      or .path == "/user/recruit"
      or .path == "/search"
      or .path == "/api"
    )
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## ③ 書きやすい版（ホワイトリスト配列）

**現場ではこちらが推奨**です。

```bash
jq -c '
  def targets: [
    "/user/",
    "/user/re-post",
    "/user/report",
    "/user/distribution",
    "/user/recruit",
    "/search",
    "/api"
  ];

  select(
    (.timestamp >= "2025-12-23 19:32:35")
    and
    (.timestamp <  "2025-12-23 19:34:15")
    and
    (.path as $p | targets | index($p))
  )
' gd-access.2025-12-23T19.log | wc -l
```

---

## ④ 前方一致にしたい場合（/api/xxx も含める）

```bash
jq -c '
  def targets: [
    "/user/",
    "/user/re-post",
    "/user/report",
    "/user/distribution",
    "/user/recruit",
    "/search",
    "/api"
  ];

  select(
    (.timestamp >= "2025-12-23 19:32:35")
    and
    (.timestamp <  "2025-12-23 19:34:15")
    and
    (targets | any(. as $t | .path | startswith($t)))
  )
' gd-access.2025-12-23T19.log | wc -l
```

---

## ⑤ 正しい理由（重要ポイント）

| ポイント         | 理由           |
| ------------ | ------------ |
| `jq -c`      | **1アクセス=1行** |
| `wc -l`      | 行数=件数        |
| path ホワイトリスト | 静的リソース除外     |
| timestamp 比較 | ミリ秒含めて正確     |

---

## ⑥ トラブル時のセルフチェック

```bash
jq -c 'select(条件)' gd-access.log | head
```

* **1行=1JSON** になっていれば OK
* 複数行なら `-c` が効いていない

---

## まとめ（これだけ覚えればOK）

```bash
jq -c 'select(時間 && path条件)' access.log | wc -l
```

これが **Tomcat JSON access log × jq × wc の正解形**です。

---

次にできること：

* 秒別アクセス数グラフ用集計
* JMeter 50PV の証跡テンプレ化
* bash スクリプト化（引数で時間/path指定）

必要なら続けます。
