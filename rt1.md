了解です。
**先ほど整理した「開始〜終了時間」それぞれについて、同じ形式の jq -c コマンドを作成**します。
（※ path 集計まで含めた **そのまま実行できる形**）

---

## No2-1. 業務のお知らせ

**19:32:35 ～ 19:34:15**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 19:32:35")
    and
    (.timestamp <  "2025-12-23 19:34:15")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-2. 再掲載

**19:34:55 ～ 19:36:20**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 19:34:55")
    and
    (.timestamp <  "2025-12-23 19:36:20")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-3. 希望申告

**19:36:55 ～ 19:38:45**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 19:36:55")
    and
    (.timestamp <  "2025-12-23 19:38:45")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-4. 本日以降配分

**19:39:30 ～ 19:41:15**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 19:39:30")
    and
    (.timestamp <  "2025-12-23 19:41:15")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-5. 募集送信

**19:41:40 ～ 19:43:10**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 19:41:40")
    and
    (.timestamp <  "2025-12-23 19:43:10")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-6. 公開買付

**19:43:50 ～ 19:45:10**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 19:43:50")
    and
    (.timestamp <  "2025-12-23 19:45:10")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-7. 債権情報

**19:45:40 ～ 19:47:10**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 19:45:40")
    and
    (.timestamp <  "2025-12-23 19:47:10")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-8. 目論見書

**19:47:45 ～ 19:49:20**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 19:47:45")
    and
    (.timestamp <  "2025-12-23 19:49:20")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-9. 広告宣伝アイテム

**19:50:00 ～ 19:51:25**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 19:50:00")
    and
    (.timestamp <  "2025-12-23 19:51:25")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-10. メールオンライン

**19:52:05 ～ 19:53:45**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 19:52:05")
    and
    (.timestamp <  "2025-12-23 19:53:45")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-11. 休場一覧

**19:54:20 ～ 19:56:00**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 19:54:20")
    and
    (.timestamp <  "2025-12-23 19:56:00")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-12. プロモート情報

**19:56:55 ～ 19:58:55**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 19:56:55")
    and
    (.timestamp <  "2025-12-23 19:58:55")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-13. 総務連絡（トップ）

**20:09:15 ～ 20:10:50**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 20:09:15")
    and
    (.timestamp <  "2025-12-23 20:10:50")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-14. 総務連絡（再掲載）

**20:11:30 ～ 20:13:05**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 20:11:30")
    and
    (.timestamp <  "2025-12-23 20:13:05")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-15. 総務連絡検索結果一覧

**（開始なし）～ 20:16:15**
※開始が無いので **終了時刻のみ基準（直前〜終了）**にするか、要調整
（ここは運用判断が必要）

---

## No2-16. マイページ

**20:16:45 ～ 20:18:20**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 20:16:45")
    and
    (.timestamp <  "2025-12-23 20:18:20")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-17. 検索画面(一般)

**20:19:00 ～ 20:20:40**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 20:19:00")
    and
    (.timestamp <  "2025-12-23 20:20:40")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

## No2-18. 検索画面(管理者)

**20:21:10 ～ 20:23:05**

```bash
jq -c '
  select(
    (.timestamp >= "2025-12-23 20:21:10")
    and
    (.timestamp <  "2025-12-23 20:23:05")
  )
  | .path
' gd-access.2025-12-23T19.log \
| sort | uniq -c | sort -nr
```

---

### 次におすすめ

* これらを **bash 1スクリプト＋配列化**
* path を **ホワイトリスト（/user, /search, /api）で限定**
* 結果を **CSV 化 → Excel / Confluence 貼り付け**

必要なら **一括実行スクリプト**まで作ります。
