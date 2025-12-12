Dockerコンテナから **Google Cloud Memorystore for Valkey** に対して
✔ **IAM認証**
✔ **転送中暗号化 (In-Transit Encryption, TLS)**
を有効にした状態で接続性を確認したい場合の **コンテナ準備手順** をまとめました。
以下は **GCP Memorystore for Valkey (Valkey 互換)** 向けで、GCP 標準の IAM トークンを使う接続確認が可能な構成です。([Google Cloud Documentation][1])

---

## 🔐 事前にやるべき準備

### 1) Memorystore for Valkey インスタンスの作成

1. **インスタンス作成時に IAM 認証と In-Transit Encryption (TLS)** を有効にする。

   * これはインスタンス作成時にしか設定できません。
   * `transit-encryption-mode=server-authentication` で TLS を有効にします。
   * 同じネットワーク（VPC）内からしか接続できないようにします。([Google Cloud Documentation][2])

```bash
gcloud memorystore instances create my-valkey \
    --location=asia-northeast1 \
    --transit-encryption-mode=server-authentication \
    --endpoints='[{"connections":[{"pscAutoConnection":{"network":"projects/PROJECT_ID/global/networks/NETWORK_NAME","projectId":"PROJECT_ID"}}]}]' \
    --node-type=standard-small \
    --shard-count=3
```

2. **サービスアカウントに必要な IAM ロールを付与**

   * `roles/memorystore.dbConnectionUser` をコンテナで使用するサービスアカウントに付与。
   * これにより GCP IAM 認証トークンを使って Valkey に接続できます。([Google Cloud Documentation][1])

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:MY_SA@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/memorystore.dbConnectionUser"
```

---

## 🐳 Docker コンテナの準備手順

### 1) ベースイメージとツールのインストール

テスト用コンテナとして、Valkey CLI または Redis クライアント（Valkey 互換クライアント）を動かせるコンテナを用意します。
ここでは例として Valkey CLI を使います。

**Dockerfile の例**

```dockerfile
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    git \
    build-essential \
    openssl

# Valkey CLI をビルドしてインストール (TLS対応版)
RUN git clone https://github.com/valkey-io/valkey.git && \
    cd valkey && \
    make distclean && \
    make valkey-cli BUILD_TLS=yes && \
    cp src/valkey-cli /usr/local/bin/

ENTRYPOINT ["bash"]
```

このコンテナをビルドしておきます：

```bash
docker build -t valkey-test .
```

---

### 2) GCP IAM 認証トークンを取得する方法

コンテナ内から GCP API にアクセスして IAM トークンを取得する必要があります。

#### A) **サービスアカウントキーを使う場合**

1. サービスアカウント JSON キーを GCP から取得
2. コンテナ内部にマウント（例：`/secrets/sa.json`）

```bash
docker run -it -v ~/keys/sa.json:/secrets/sa.json valkey-test bash
```

3. 内部でトークン取得

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/sa.json
ACCESS_TOKEN=$(gcloud auth application-default print-access-token)
```

※ `gcloud` がコンテナ内になければ、`curl` を使って metadata API または OAuth2 token エンドポイントから取得してください。

---

### 3) TLS 用 CA 証明書の取得

Memorystore インスタンス作成後、CA証明書を取得します：

```bash
gcloud memorystore instances get-certificate-authority my-valkey --region=asia-northeast1 \
    > server_ca.pem
```

これをコンテナにコピーまたはマウントします。

---

## 📡 接続確認

### 1) 環境変数を設定

```bash
export VALKEY_HOST=<Memorystore Discovery IP>
export VALKEY_PORT=6378  # TLS 用ポート
export ACCESS_TOKEN=<取得した IAM トークン>
```

### 2) Valkey CLI で接続確認（TLS + IAM Token）

```bash
valkey-cli -h $VALKEY_HOST -p $VALKEY_PORT \
    --tls --cacert /path/to/server_ca.pem \
    -a "$ACCESS_TOKEN" -u default

# 認証後の操作例
PING
SET foo bar
GET foo
```

🔎 ポイント

* `-u default` は Valkey のデフォルトユーザー名。IAM 認証ではこれを使います。([Google Cloud Documentation][1])
* TLS (–tls, –cacert) を指定することで In-Transit Encryption を有効にした接続になります。([Google Cloud Documentation][2])

---

## 🔄 トークンの更新

IAM トークンは短時間（約1時間）で期限切れになります。
自動更新処理をコンテナ内で仕込む必要がある場合は、以下のように **定期的に新しいトークンを取得 → 更新** を行ってください。([Google Cloud Documentation][3])

```bash
while true; do
  ACCESS_TOKEN=$(gcloud auth application-default print-access-token)
  sleep 3000  # 50分ごとに更新
done &
```

---

## 🧠 確認ポイント

| 項目                    | チェック内容                                   |
| --------------------- | ---------------------------------------- |
| IAM 認証                | `-a $ACCESS_TOKEN` が正しく Valkey に渡せているか   |
| In-Transit Encryption | TLS でコネクションでき、CA 認証が通るか                  |
| ネットワーク                | VPC / PSC の Private connectivity が整っているか |

---

必要であれば、**Kubernetes / Cloud Run で実行する方法**や、**アプリケーションコード内で IAM サポート付き接続サンプル (Lettuce / Node.js / Python)** もお見せできます。気軽に聞いてください。

[1]: https://docs.cloud.google.com/memorystore/docs/valkey/manage-iam-auth?utm_source=chatgpt.com "Manage IAM authentication | Memorystore for Valkey"
[2]: https://docs.cloud.google.com/memorystore/docs/valkey/manage-in-transit-encryption?utm_source=chatgpt.com "Manage in-transit encryption | Memorystore for Valkey"
[3]: https://docs.cloud.google.com/memorystore/docs/valkey/about-iam-auth?utm_source=chatgpt.com "About IAM authentication | Memorystore for Valkey"
