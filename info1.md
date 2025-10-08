[https://cloud.google.com/kubernetes-engine/docs/how-to/alias-ips?hl=ja#create_a_cluster_and_select_the_control_plane_ip_address_range
](https://cloud.google.com/sdk/gcloud/reference/container/clusters/create#--master-ipv4-cidr)
# Pod監視 設計方針（GKE移行対応）

## 1. 目的・範囲

* 対象：アプリPod（Web／Vue等）・関連Sidecar・Namespace単位での運用監視
* 目的：異常の**早期検知**、**影響最小化**、**原因特定**の迅速化（メトリクス／ログ／イベント／トレースの統合可視化）

---

## 2. 監視コンポーネント（採用方針）

* **メトリクス**：Cloud Monitoring（Google Cloud Managed Service for Prometheus＝MGMP）

  * Autopilot：**DaemonSet不要**のマネージド収集を採用
* **ログ**：Cloud Logging（コンテナ stdout/stderr 集約、ログベース指標を作成）
* **イベント**：Kubernetes Events（CrashLoopBackOff/OOMKilled/Preempt 等）をMonitoringへ連携
* **トレース**（任意）：OpenTelemetry → Cloud Trace
* **可用性**：Uptime Check（外形監視）＋LBヘルスチェック（BackendConfig/HealthCheckPolicy）と整合

---

## 3. SLI/SLO 設計

* **推奨SLI**

  * 可用性：`readiness` OK率（PodがServiceに参加している時間割合）
  * 安定性：`5xx率`、`p95/p99 レイテンシ`、`再起動回数`、`CrashLoopBackOff発生率`
  * リソース：`CPU利用率/スロットリング率`、`メモリ利用率/OOMKill`、`FS使用率`
* **SLO例**（Web系）

  * 可用性 99.9% / 月、エラーレート（5xx）≦0.5% / 5分移動、p99レイテンシ ≦ 800ms
* **アラート方針**

  * 連続N分（例：5分×3回）でSLO逸脱傾向 → 通知（高/中/低の3段階）

---

## 4. アプリ健全性（Probe とLBの整合）

* Pod：`startupProbe`（起動猶予）、`readinessProbe`（受流判定）、`livenessProbe`（自己回復）を**分離定義**
* LB：Ingress/ Gatewayのヘルスチェックは **readinessと一致**（BackendConfig/HealthCheckPolicyで明示）
* 終了時：`preStop`＋`terminationGracePeriodSeconds` で**ドレイン**を保証

---

## 5. 収集と可視化（実装）

### 5.1 メトリクス収集（Managed Prometheus）

* **Pod側**：`/metrics` をHTTP公開（例：`:8080/metrics`）
* **Scrape定義（PodMonitoring CRD）**：

```yaml
apiVersion: monitoring.googleapis.com/v1
kind: PodMonitoring
metadata:
  name: web-app
  namespace: app-prod
spec:
  selector:
    matchLabels:
      app: web
  endpoints:
  - port: http        # Service or containerPort 名
    path: /metrics
    interval: 30s
```

* **Recording/Alert ルール**（Rule CRD）でSLO/閾値を整備（例：5xx率、p99レイテンシ）

### 5.2 ログ収集（Cloud Logging）

* アプリログは**stdout/stderr**へ。PV直書きは廃止
* **ログベース指標**例（5xx率）：

  * フィルタ：`resource.type="k8s_container" severity>=ERROR httpRequest.status>=500`
  * 指標化 → アラート（5分平均で閾値超）

### 5.3 ダッシュボード（必須ウィジェット）

* SLI要約：可用性、5xx率、p99
* Pod安定：`container/restart_count`、CrashLoopBackOff件数、Pod未Ready数
* リソース：CPU/メモリ使用率、`container/cpu/throttled_time`、OOMKill回数
* 依存：DB/外部APIのレイテンシとエラー（可能ならエクスポート）

---

## 6. 代表アラート（しきい値例）

* **可用性**：`NotReady Pod > 0` が 5分継続（高）
* **再起動**：`RestartCount 増加速度 > 3/10分`（高）
* **CrashLoop**：`CrashLoopBackOff 発生 > 0` が 5分継続（高）
* **5xx率**：`>1%` が 10分継続（中）
* **レイテンシ**：`p99 > 800ms` が 10分継続（中）
* **CPUスロットリング**：`throttling_ratio > 10%` が 15分継続（中）
* **メモリ**：`利用率 > 90%` が 10分継続、`OOMKill 発生`（高）

---

## 7. 事件対応（Runbook 連携）

* 各アラートに**Runbook URL**（対処手順）を紐付け

  * 例：CrashLoop → `kubectl describe pod` / `logs -p` / config差分確認 / rollout undo 手順
  * 例：5xx上昇 → LB健全性／readiness／依存先疎通／直近リリース有無を確認

---

## 8. Autopilot特記事項

* **DaemonSet禁止**：独自エージェントは基本不可 → **Managed Prometheus/Cloud Logging** を使用
* **ノード面の監視**はGKE管理下。ワークロード側はPod/Namespace指標に集中
* **HPA**：CPU/カスタムメトリクスでの自動スケールと**アラート**を組み合わせ（スケール失敗も監視）

---

## 9. 最低限の設定テンプレート（抜粋）

### 9.1 Probe（コンテナ）

```yaml
startupProbe:
  httpGet: { path: /healthz, port: 8080 }
  periodSeconds: 5
  failureThreshold: 60   # 5分猶予
readinessProbe:
  httpGet: { path: /healthz, port: 8080 }
  periodSeconds: 5
  timeoutSeconds: 2
  failureThreshold: 3
livenessProbe:
  httpGet: { path: /livez, port: 8080 }
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3
```

### 9.2 BackendConfig（Ingress利用時のLBヘルスチェック）

```yaml
apiVersion: cloud.google.com/v1
kind: BackendConfig
metadata: { name: web-hc, namespace: app-prod }
spec:
  healthCheck:
    type: HTTP
    requestPath: /healthz
    port: 8080
    checkIntervalSec: 5
    timeoutSec: 4
    healthyThreshold: 2
    unhealthyThreshold: 2
```

---

## 10. 運用ルール

* **変更時**は Probe／LBヘルスチェック／HPA閾値の**三者整合**をレビュー必須
* **計測設計**は開発フェーズから（/metrics 実装・ログ構造化）
* **ダッシュボード**と**アラート**はPRD前に完成・演習（GameDay）を実施

---

必要なら、あなたの現行マニフェストを基に

* `PodMonitoring/Rule`（Managed Prometheus）
* ログベース指標とアラートポリシー
* ダッシュボードJSON（Cloud Monitoring）
  を**実体ファイル**で作成します。
