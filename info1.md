了解です。画像の表を前提に、**「サービスレベル値（GCP）」列の記入文例**を“現行踏襲＋GKE 依存は共通基盤準拠、POD 周りは明確化”の方針で簡潔にまとめました。表へそのまま貼れる粒度です。

---

# サービスレベル値（GCP）— 記入案

## 1. 可用性

* **時間要件方針／業務拠点の要件（HW/SW）**
  現行値を踏襲。GKE 依存部分は**共通基盤要件に準拠**（Regional GKE／マルチゾーン、ノード自動修復、計画メンテ運用）。
  ※Web は**ステートレス**前提、セッションは外部化（キャッシュ等）し POD 再作成時の業務影響を最小化。

* **サービス開始時間**
  現行値を踏襲。初回起動遅延は **startupProbe** で吸収し、**readinessProbe** 合致時に受流開始。

* **業務継続性：RPO／RTO**
  現行値を踏襲。POD は再作成で即時復旧可能（**RollingUpdate＋PDB**で無停止切替）。データ系は**共通基盤のバックアップ／レプリケーション方針**に従う。

* **業務継続時：代替業務運用の範囲**
  現行運用マニュアルを踏襲。GKE 障害時は**マルチゾーン継続前提**、広域障害時の手順は**共通基盤 DR 手順**に準拠。

## 2. 拡張性設計

* **仮想・コンテナ構成**
  現行踏襲。**Cloud Native 構成**（Deployment＋Service＋Ingress/Gateway）とし、構成管理は GitOps に統一。

* **自動拡張性**
  **HPA（CPU/応答時間など）**で POD を自動スケール。ノードは**Cluster Autoscaler**（共通基盤設定）に準拠。上限/下限は**Namespace の ResourceQuota/LimitRange**で統制。

## 3. セキュリティ（診断・運用）

* **ネットワーク診断・脆弱性対策**
  **共通基盤要件に準拠**（VPC セグメント分離、Private GKE、必要に応じ Cloud Armor/WAF）。
  POD は**非特権実行（runAsNonRoot/不可昇格/ReadOnlyRootFS）**を原則。イメージは署名・スキャン済みを使用。

* **Web/AP 監視・診断**
  **Cloud Logging/Monitoring** を用い、**4xx/5xx、レイテンシ、readiness 失敗、再起動回数**でアラート。外形監視は**共通基盤の監視ポリシー**に準拠。

## 4. 運用（更新・停止・復旧）

* **デプロイ方式**
  **RollingUpdate（maxUnavailable:0 / maxSurge:1）**を標準。`revisionHistoryLimit` は現行値（例：2）踏襲し、最小限のロールバック世代を保持。

* **停止影響の抑制**
  **PodDisruptionBudget（PDB）**と**preStop＋猶予（terminationGracePeriod）**でドレインを保証。`readiness` と **LB 健全性**を一致させ無流入で終了。

* **ログ／トレース**
  アプリログは **stdout/stderr** へ出力し Cloud Logging へ集約（PV 直接出力は廃止）。必要に応じトレース（Cloud Trace）を適用。

---

# POD 周りの記述（表の脚注や別欄に追記）

* **プローブ**：`startupProbe`（起動待ち）／`readinessProbe`（受流判定）／`livenessProbe`（自己回復）を分離し設定。
* **配置**：`topologySpreadConstraints`（zone→node 均等）＋必要に応じ `podAntiAffinity`。
* **更新**：`RollingUpdate` 基本、`Recreate` は計画停止時のみ。`revisionHistoryLimit` は現行踏襲。
* **資源**：各コンテナに `requests/limits` を必須化。Namespace に **ResourceQuota/LimitRange** を適用。
* **通信**：POD 間は **Service（ClusterIP）** 経由。外部公開は **Ingress / Gateway API**（共通基盤方針）に従う。
* **監査**：イメージはレジストリ制御下で供給、脆弱性スキャン結果をリリース判定に使用（共通基盤準拠）。

---

必要なら、表に直接貼れる**1セル用の短文化テキスト**（改行なし版）も作ります。
