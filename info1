了解です。いただいた現状メモをもとに、方式設計書の「POD設計方針」章としてそのまま流用しやすい形に整理しました。GKE（Standard/Autopilot 共通）でのベストプラクティスと差分も織り込み、根拠は公式ドキュメントへ添付しています。

# POD設計方針（GKE移行対応）

## 1. 目的・適用範囲

本方針は、オンプレミス K8S 上の Web/Vue（フロント）コンテナ群を GKE へリフトするにあたり、POD の配置・可用性・監視性・運用性（ログ/リソース管理）を GKE ベストプラクティスに合わせて定義する。対象は Web 系 Deployment、Service、および周辺（Gateway/Ingress、Namespace ポリシー）に関連する設定。

---

## 2. ロギング方針

* **基本方針**：アプリケーションログは**PV への直接出力を廃止**し、**標準出力/標準エラー（stdout/stderr）へ出力**する。GKE ではノードのログエージェント（Fluent Bit 系）がコンテナログを**Cloud Logging**へ集約するため、最小労力で一元管理できる。必要に応じてログルータの調整やシンク（BigQuery/Cloud Storage）を併用する。([Google Cloud][1])
* **例外**：アプリ側要件で**ファイル出力が不可欠**な場合は、(a) サイドカーで tail → stdout にブリッジする、(b) Fluent Bit の DaemonSet を**カスタマイズ**して該当パスを収集対象に加える、のいずれかで Cloud Logging 連携を確保する。([Medium][2])
* **備考**：POD/ノードのライフサイクルに伴い**ローカル/Pod 配下のログは消失**し得るため、永続化の観点でも Cloud Logging を一次集約とする。([Google Cloud][3])

---

## 3. 配置方針（可用性・分散）

* **ノード/ゾーン分散**：Replica を均等配置するため、**Pod Topology Spread Constraints** を採用する（`topology.kubernetes.io/zone` / `kubernetes.io/hostname` を使用、`maxSkew: 1` を基本）。高可用性および効率的な資源利用の両立を図る。([Kubernetes][4])
* **アンチアフィニティ**：同一ノード集中を避けたいワークロードは `podAntiAffinity`（`topologyKey: kubernetes.io/hostname`）を**補助的に併用**する（厳格性とスケジュール失敗リスクのバランスで選択）。([Kubernetes][4])
* **クラスタ構成の前提**：ゾーン分散を有効にするため、**Regional クラスタ**または複数ゾーンに跨るノードプールを使用する。可用性要件に応じて標準は Regional を推奨。([Google Cloud][5])

---

## 4. フロント（BigIP）代替と内部通信

* **外部公開**：オンプレの BigIP 相当は、GKE では **Gateway API**（推奨）または **Ingress** を適用する。Gateway は Ingress の機能を一般化/拡張し、ルーティングとフロント設定（Gateway/HTTPRoute の分離）を標準化する。移行時は Ingress 設定を **Gateway/HTTPRoute に機械変換可能**（設計責務分離にも寄与）。([Google Cloud][6])
* **サービス間通信**：Web ↔ Vue 間は **ClusterIP Service 経由**とし、POD 直参照を禁止する（Service 名の内部 DNS 解決を前提）。L7 要件（パス/ヘッダマッチ、重み付け配信 等）がある場合は Gateway で定義する。([Google Cloud][6])

---

## 5. 可用性監視（ヘルスチェック / プローブ）

* **プローブ設計**：オンプレの `liveness/readiness` は踏襲しつつ、**起動の重いアプリ**には `startupProbe` を追加してウォームアップ中の誤再起動を回避する。GKE/クラウド LB 側のヘルスチェックは**readiness**と整合するよう設計（遅延初期化コンテナは startupProbe で吸収）。([Kubernetes][7])
* **運用目線**：プローブ失敗時のイベント/ログは Cloud Logging/Monitoring で検知・可視化する。ベンチ時に閾値/タイムアウト/周期を実測調整。([Kubernetes][7])

---

## 6. リソース管理（requests/limits・Namespace ポリシー）

* **コンテナ単位**：現行の `resources.requests/limits` は維持し、**OOM/Kill や CPU スロットリング**の有無を観測しながら適正化する（特に limit の過小設定はスロットリングを招く）。([Sysdig][8])
* **Namespace 単位**：既存の **ResourceQuota** と **LimitRange** を移行し、クラスタ全体での資源配分を統制。新規ワークロード追加時の上限枠を明確化する。([Kubernetes][9])

---

## 7. デプロイ/スケール

* **Deployment 設定**：レプリカ数・ローリング更新（`maxSurge/maxUnavailable`）は基本踏襲。分散要件を満たすため、前述の **Topology Spread** と併用する。([Kubernetes][4])
* **ノードプール**：ワークロード特性（CPU/メモリ/スポット可否/Node TAINT）に応じてノードプールを**分離**し、`nodeSelector`/`tolerations` で割当て。アップグレードやスケールの影響範囲を最小化する。([Google Cloud][10])

---

## 8. セキュリティ/その他（抜粋）

* **ServiceAccount / 最小権限**：Workload Identity の採用を検討（GCP API 利用時の鍵管理排除）。
* **ネットワーク**：ネームスペース/アプリ単位の NetworkPolicy を段階導入（ゼロトラスト化）。
* **監視**：Cloud Monitoring によるメトリクス/アラート（プローブ失敗率、再起動回数、P99 レイテンシ 等）を整備。
  （※上記はプロジェクト基準の別章に詳細化想定）

---

## 9. 設計スニペット例（抜粋）

### 9.1 ログ：stdout/stderr へ出力（アプリ設定の原則）

```text
# アプリ側：ファイル出力をやめ、標準出力/標準エラーへ
logger.info("...")  -> stdout
logger.error("...") -> stderr
# これにより GKE のログエージェントが Cloud Logging へ自動送信
```

### 9.2 分散配置（ゾーン→ノードの二段均等）

```yaml
spec:
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels: { app: web }
    - maxSkew: 1
      topologyKey: kubernetes.io/hostname
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels: { app: web }
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          podAffinityTerm:
            labelSelector:
              matchLabels: { app: web }
            topologyKey: kubernetes.io/hostname
```

（Regional 構成/複数ゾーン前提）([Kubernetes][4])

### 9.3 Gateway（外部公開）と Service（内部通信）

```yaml
# 外部公開：Gateway + HTTPRoute（例）
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata: { name: web-gw }
spec:
  gatewayClassName: gke-l7-global-external-managed
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      tls: { mode: Terminate, certificateRefs: [{name: my-cert}] }

---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: web-route }
spec:
  parentRefs: [{ name: web-gw }]
  rules:
    - matches: [{ path: { type: PathPrefix, value: / } }]
      backendRefs: [{ name: web-svc, port: 80 }]
```

（Ingress → Gateway/HTTPRoute への変換方針を採用）([Google Cloud][6])

---

## 10. 既存設定からの移行判断（要/不要の目安）

| 項目      | 現状          | GKEでの判断                                                                            |
| ------- | ----------- | ---------------------------------------------------------------------------------- |
| ログ出力    | PV へファイル    | **廃止**し stdout/stderr へ。特殊要件のみサイドカー/Fluent Bit カスタムで吸い上げ。([Google Cloud][1])       |
| 配置戦略    | Affinity なし | **Topology Spread** を基本適用、必要に応じて Anti-Affinity。Regional 前提でゾーン均等。([Kubernetes][4]) |
| 外部 LB   | BigIP       | **Gateway API（推奨）** または Ingress。ルーティング要件は HTTPRoute へ定義。([Google Cloud][6])        |
| ヘルスチェック | そのまま        | `startupProbe` 追加を検討。readiness と LB 健全性の整合を確認。([Kubernetes][7])                    |
| リソース    | 現状維持        | requests/limits を観測で適正化。Namespace の **ResourceQuota/LimitRange** を踏襲。([Sysdig][8]) |

---

## 11. 移行時の留意点（実務）

1. **クラスタ設計と整合**：Regional 化、ノードプール分離（スポット/汎用/メモリ最適化 等）、スケジュール制約の整合性。([Google Cloud][10])
2. **段階移行**：まず Ingress 等価で受け、要件に応じて Gateway/HTTPRoute へ**段階移行**（ポリシー分離・高度なトラフィック制御を将来適用）。([Google Cloud][6])
3. **可観測性の先行整備**：Cloud Logging/Monitoring の**ログベース指標**やアラートを先に設計（プローブ/再起動/4xx/5xx/遅延）。([Google Cloud][3])

---

必要であれば、いただいた YAML をベースに **Topology Spread/Anti-Affinity の具体値** や **Gateway/HTTPRoute 定義**、**ResourceQuota/LimitRange の雛形** まで落とし込んだ“貼り替え用パッチ”を作成します。

[1]: https://cloud.google.com/blog/products/gcp/7-best-practices-operating-containers?utm_source=chatgpt.com "7 Google best practices for operating containers"
[2]: https://medium.com/google-cloud/customizing-fluent-bit-for-google-kubernetes-engine-logs-a484b5d80072?utm_source=chatgpt.com "Customizing Fluent Bit for Google Kubernetes Engine logs"
[3]: https://cloud.google.com/kubernetes-engine/docs/concepts/about-logs?utm_source=chatgpt.com "About GKE logs | Google Kubernetes Engine (GKE)"
[4]: https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/?utm_source=chatgpt.com "Pod Topology Spread Constraints"
[5]: https://cloud.google.com/kubernetes-engine/docs/concepts/regional-clusters?utm_source=chatgpt.com "Regional clusters | Google Kubernetes Engine (GKE)"
[6]: https://cloud.google.com/kubernetes-engine/docs/concepts/gateway-api?utm_source=chatgpt.com "About Gateway API | GKE networking"
[7]: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/?utm_source=chatgpt.com "Configure Liveness, Readiness and Startup Probes"
[8]: https://www.sysdig.com/blog/kubernetes-limits-requests?utm_source=chatgpt.com "Understanding Kubernetes Limits and Requests"
[9]: https://kubernetes.io/docs/concepts/policy/resource-quotas/?utm_source=chatgpt.com "Resource Quotas"
[10]: https://cloud.google.com/kubernetes-engine/docs/how-to/node-pools?utm_source=chatgpt.com "Add and manage node pools | Google Kubernetes Engine ..."
