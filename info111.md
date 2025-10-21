承知しました。それでは、**オンプレミスとの接続におけるFirewall制御**を追記し、全体の構成に反映した修正版の「ネットワーク制御設計章（Akamai + オンプレFW込み）」を以下に提示します。

---

# ネットワーク制御設計（Akamai + オンプレミス接続含む）

本章では、GKEテナントシステムにおけるネットワークセキュリティ制御設計を記載する。Akamai、GCP側の各種制御（Cloud Armor, NetworkPolicy等）に加え、**オンプレミス接続経路におけるFirewall制御**も含めて記載する。

---

## 1. ネットワーク階層ごとの制御構成（統合）

| 階層               | 制御技術                          | 内容概要                             |
| ---------------- | ----------------------------- | -------------------------------- |
| エンドユーザー → Akamai | Akamai WAF / CDN              | グローバルCDN、DDoS対策、Bot制御、L7 WAF     |
| Akamai → GCP ALB | Cloud Armor                   | L7 WAF補完、IP制限、レート制御など            |
| GCP ALB → GKEノード | VPC Firewall Rules            | L3レイヤでのIP許可制御（Akamaiのみ許可）        |
| GKEノード → Pod     | CrowdStrike Falcon（DaemonSet） | ノード内プロセスのEPP/EDR監視               |
| Pod間通信           | Kubernetes NetworkPolicy      | Namespace・Labelベースの通信制御          |
| GKE ↔ オンプレミス     | VPCルート + オンプレFirewall         | Interconnect経由の通信を双方向でFirewall制御 |

---

## 2. オンプレミス接続とFirewall制御

### 接続方式：

* **Cloud Interconnect（専用線）**を経由し、GCP（共有VPC）とオンプレミス間をL3接続。
* Private IPアドレスベースでのトラフィック制御を実施。

### 制御構成：

| 区間         | 制御技術                  | 制御内容                    |
| ---------- | --------------------- | ----------------------- |
| GCP → オンプレ | VPC Firewall + オンプレFW | 宛先IP/ポートに基づく許可制御        |
| オンプレ → GCP | オンプレFW + VPC Firewall | GKEノードまたはNEGバックエンド向けに限定 |

### 留意点：

* オンプレミスFW側では、GKEクラスタ内Pod IPはNAT変換（IPマスカレード）され、GKEノードIPとして認識される。
* 通信要件（DBアクセス、ログ連携など）を明確にし、**許可ポート・宛先範囲を定義**。

---

## 3. Kubernetes NetworkPolicy 設計方針

* Namespaceごとに `deny all` ベースのポリシー適用
* 各Pod通信を `app`, `tier`, `tenant` ラベルで許可制御
* **オンプレミスからのPodアクセスはService経由**とし、直接アクセスは不可とする。

---

## 4. Akamai によるフロントエンド防御

* L7 WAF、Bot対策、DDoS軽減に利用
* OriginはALBのFQDNで指定、証明書もGCPまたはAkamai側でSSL終端
* ヘルスチェック時のAkamaiルールは個別定義（バイパスも可）

---

## 5. その他制御技術の適用概要

| 技術                 | 主な用途                       |
| ------------------ | -------------------------- |
| Cloud Armor        | Akamai通過後の補完WAF、Geo/IP制御   |
| VPC Firewall       | NodePort, Interconnect経路制御 |
| CrowdStrike Falcon | ノード上プロセス監視・脅威防御            |
| NetworkPolicy      | Pod間通信のL3/L4制御（多層テナント分離）   |

---

## 6. 設計まとめ

* **Akamai ～ GCP ～ GKE ～ オンプレミス間**をまたぐ多層制御構成とし、各階層に適したセキュリティ対策を適用。
* オンプレミス接続は **Interconnect + 双方向Firewall制御**により限定し、許可リスト方式で明示管理。
* テナントシステムは NetworkPolicy で通信分離を実施。ALB配下への外部アクセスはすべて Akamai経由に統一。

---

必要に応じて、通信フロー図（外部 → Akamai → GCP → GKE → オンプレ）を含めた構成資料もご支援可能です。ご希望があればお知らせください。
