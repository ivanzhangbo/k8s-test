| 観点                       | 1つのNamespace                                       | 2つのNamespace                                        |
| ------------------------ | -------------------------------------------------- | --------------------------------------------------- |
| リリース方式                   | Rolling/Canaryを同NS内で完結しやすい（Deployment/Service切替のみ） | Blue-Green／段階的切替が明快（Service/Ingressの宛先NSを差し替え）      |
| 隔離（RBAC/ネットワーク）          | 事故の波及が大きい（同NSで権限/通信が広がりやすい）                        | 最小権限を徹底しやすい（RBAC・NetworkPolicy・PodSecurityをNS単位で分離） |
| Workload Identity / 秘密情報 | KSA→GSAやSecretの使い分けが煩雑                             | “用途ごと”に分離でき安全（例：prodとcanaryで別GSA/Secret）            |
| リソース管理（Quota/LimitRange） | 争奪が起きやすい（HPAやJobが同資源を取り合う）                         | NSごとにQuotaを割当てられるためキャパ管理が楽                          |
| 運用・監査（ラベル/メトリクス）         | 名前衝突やラベル設計に依存（厳密な命名規則が必要）                          | NSで論理境界ができ、監査・課金・SLO集計が明快                           |
| 名前解決/到達性                 | 単純（`svcA`等の同NS名で完結）                                | 相互通信は `svcB.nsB.svc` を前提。NetworkPolicyのNSセレクタ設計が必要  |
| 設定/アーティファクトの重複           | 少ない（Config/Secretを共有）                              | 重複しがち（環境ごとにConfig/Secretを分ける運用が必要）                  |
| CI/CDの複雑性                | シンプル（単一kustomize/Helm値で回せる）                        | 多少増える（ns別パイプライン or overlay 管理が必要）                   |
| 既存監視/アラート                | 単一NSでまとめやすい                                        | NS単位で閾値や通知先を分離しやすい                                  |
| 事故時ロールバック                | 影響範囲が広く緊張感高い                                       | もう一方のNSへ即時切替しやすい（Ingress/Service切替）                 |
