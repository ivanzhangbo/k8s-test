以下は、GKE 上のアプリケーション向けに設計された「ALB（HTTP(S) Load Balancer） + NEG を利用したセッション保持構成」の設計方針章です。Markdown形式で整理しています。

---

# ALB（HTTP(S) Load Balancer）設計方針

## 1. 構成概要

本システムでは、GKE 上にデプロイされたアプリケーションに対し、HTTP(S) Load Balancer（以下 ALB）を導入し、トラフィックの負荷分散およびセッション保持を実現する。ALB では GKE の NEG（Network Endpoint Group）を用いて、Pod 直接をバックエンドとする構成とし、アプリケーション層とのセッション整合を考慮した設計とする。

```
[Client] ⇄ [Akamai] ⇄ [ALB (HTTP(S))] ⇄ [NEG (Pod)] ⇄ [App]
```

---

## 2. セッション保持設計（HTTP_COOKIE）

### 2.1 ALB 側の設定

GKE の `BackendConfig` リソースを活用し、ALB に以下のセッションアフィニティ設定を実装する：

```yaml
spec:
  sessionAffinity:
    affinityType: HTTP_COOKIE
    affinityCookieTtlSec: 3600
    affinityCookieName: SESSION_ID
```

* `affinityType`: `HTTP_COOKIE` を指定することで、ALB が Cookie ベースのセッションスティッキーを行う。
* `affinityCookieName`: アプリ側で扱う Cookie 名と一致させる。
* `affinityCookieTtlSec`: Cookie の有効期限（秒）を設定。

### 2.2 動作概要

* クライアント初回アクセス時、ALB が `SESSION_ID` Cookie を自動発行（Set-Cookie）。
* 同一Cookieを含むリクエストは、TTL 有効期間中は常に同一 Pod にルーティング。
* TTL超過、Cookie消失、Podの再スケジューリング等により、再割り当てが発生する。

---

## 3. アプリケーション側の対応方針

アプリケーション（例：Flask, Spring Boot 等）は、ALB が付与する Cookie（例：`SESSION_ID`）と一致する Cookie 名を内部セッション管理に使用すること。

* Flask 等では `session_id = request.cookies.get('SESSION_ID')` を使用し、内部セッションと ALB のセッションを整合。
* セキュリティ上、`HttpOnly`、`Secure` オプションの付与を推奨。

---

## 4. 設計上の利点と制約

### ✅ 利点

| 観点      | 説明                                  |
| ------- | ----------------------------------- |
| UX向上    | セッション切断を防ぎ、ログイン維持やショッピングカート等の一貫性を担保 |
| アプリ側簡素化 | サーバ間セッション同期が不要                      |
| GKEと統合  | GKE + ALB 構成により設定と可視性を統一管理可能        |

### ⚠️ 注意点

* `affinityCookieName` の指定が必須。アプリと一致しないとセッションが分断される。
* Pod 再起動やスケーリングによるセッションリセットに備え、アプリ側のセッション永続化（例：Redis 等）も検討余地あり。
* Cookie は `SameSite=None` + `Secure` 設定が必要（クロスドメイン考慮）。

---

## 5. 導入計画と確認事項

| 項目           | 対応方針                                      |
| ------------ | ----------------------------------------- |
| Cookie 設定の整合 | `SESSION_ID` を共通名としてアプリ・ALBで共通利用          |
| Cookie TTL   | ビジネス要件に応じて 30〜3600秒で調整可能                  |
| ログ記録         | Cloud Logging にて Cookie ベースのリクエストルーティング検証 |
| トラブルシュート     | Cookie 消失時のルーティング再割り当てに備えたアプリ層処理明確化       |

---

必要であれば、図解や構成テンプレート（draw.io形式、YAML）も作成可能です。ご希望があればお知らせください。
