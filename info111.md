承知しました。以下に **Akamaiを含めたネットワーク制御設計章の修正版** を提示します。AkamaiはCDNおよびWAFとしての役割を担うため、Cloud Armorとの関係性やL7制御の境界も明記しています。

---

# ネットワーク制御設計（Akamai含む）

本章では、GKE上に構築されるテナントシステムにおけるネットワーク制御設計を記載する。特に、**Akamai CDN/WAF**、**Cloud Load Balancer（ALB）**、および **GKE内部のセキュリティ制御** の分離と連携に焦点を当てる。

---

## 1. ネットワーク階層ごとの制御構成

| 階層                         | 制御技術                          | 概要                           |
| -------------------------- | ----------------------------- | ---------------------------- |
| エンドユーザー → Akamai           | Akamai WAF / CDN              | グローバルCDN、DDoS対策、Bot制御、L7 WAF |
| Akamai → GCP ALB           | Cloud Armor（補完的WAF）           | IPレート制限、L7ルール、Blacklist等     |
| GCP ALB → GKEノード（NodePort） | VPC Firewall Rules            | L3レイヤでの送信元IP制御（ALBなど限定）      |
| GKEノード → Pod               | CrowdStrike Falcon（DaemonSet） | ノード内プロセス単位のEPP/EDR監視         |
| Pod間通信                     | Kubernetes NetworkPolicy      | Namespace・Labelベースの通信制御      |

---

## 2. Akamai による最前段制御

Akamaiは本システムにおける**第一レイヤの防御境界**であり、以下の目的で導入する。

### 利用機能：

* **WAF（Web Application Firewall）**：SQLi、XSS、OWASP Top10対策
* **DDoS軽減**：Edge側でのトラフィック吸収
* **Botマネジメント**：不正Botアクセスの遮断
* **コンテンツキャッシュ**：静的コンテンツの応答高速化

### 設定留意点：

* GCP側のALBと通信するための**オリジンサーバ指定**と**SSL証明書適用**
* メンテナンス時のルール切替やパス指定によるバイパス制御

---

## 3. GCP側ALB + Cloud Armor による補完制御

### 目的：

* Akamai通過後のバックエンド保護
* GCP側からのL7制御・レート制御の追加補強

### ポリシー例：

* 特定のIPやGeoIP制限（Akamaiバイパス時の保険）
* URIパスベースのトラフィック制御
* 外部ALB経由でのNodePortアクセスのみ許可（NEG構成）

---

## 4. VPC Firewall によるノードレベルのL3制御

* **ALBの送信元IP範囲（Akamai Edge含む）**を指定して許可
* **SSHやBastion用のアクセスは最小限**
* その他はデフォルト `deny`

---

## 5. GKE内部のセキュリティ制御

### 5.1 NetworkPolicy

* Namespaceごとに `default deny` 適用
* 通信許可は `app`, `role`, `tier` ラベルによって制御
* テナント間通信は完全遮断

### 5.2 CrowdStrike Falcon

* 全ノードにDaemonSet展開
* 次のような脅威検知を補完：

  * 不審なプロセス起動
  * 外部への異常通信
  * コンテナ内の特権操作の検出

---

## 6. 設計ポリシーまとめ

| 項目       | 方針                                                             |
| -------- | -------------------------------------------------------------- |
| 多層防御構成   | Akamai（CDN/WAF）→ Cloud Armor → NetworkPolicy/CrowdStrike の多層構成 |
| テナント分離   | Podレベルの通信制御とラベル設計でマルチテナント構成を隔離                                 |
| アクセス経路制限 | GCP外部と内部の経路制御を明示、Podへの直通信を禁止                                   |
| ゼロトラスト準拠 | すべての通信は明示許可された経路のみ通過可能とする構成                                    |

---

さらに、Akamaiからの**ヘルスチェックやALBのorigin指定**についても、詳細が固まり次第追記可能です。必要であれば図解付きドキュメントにも展開できますので、お申し付けください。
