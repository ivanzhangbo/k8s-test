了解です。
では **index.html（Webページ用）** と **health.html（LBヘルスチェック用）** の両方を配置するための
**完全版 Dockerfile + Nginx 設定 + HTML ファイル例** を作成します。

---

# ✅ **最適構成（index.html + health.html を正しく返せる HTTPS サーバー）**

## 📁 **ファイル構成（推奨）**

```
.
├── Dockerfile
├── default.conf
├── index.html
└── health.html
```

---

# 🚀 **Dockerfile（完全版）**

```Dockerfile
FROM debian:stable-slim

# Install tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl iputils-ping dnsutils traceroute \
    netcat-openbsd nginx openssl \
    && rm -rf /var/lib/apt/lists/*

# Create SSL certificate
RUN mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -days 365 \
      -newkey rsa:2048 \
      -keyout /etc/nginx/ssl/server.key \
      -out /etc/nginx/ssl/server.crt \
      -subj "/CN=localhost"

# Copy HTML files
RUN mkdir -p /var/www/html
COPY index.html  /var/www/html/index.html
COPY health.html /var/www/html/health.html

# Copy Nginx conf
COPY default.conf /etc/nginx/conf.d/default.conf

# Log to stdout/stderr
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
```

---

# 📝 **default.conf（index + health）**

```nginx
server {
    listen 80;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name _;

    ssl_certificate     /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;

    # Health check
    location = /healthz {
        root /var/www/html;
        try_files /health.html =200;
    }

    # Main page
    location / {
        root /var/www/html;
        index index.html;
    }
}
```

### 🔍 挙動

* `/` または `/index.html` → **index.html を返す（200 OK）**
* `/healthz` → **health.html の内容を返す（200 OK）**
* HTTP → 自動で HTTPS にリダイレクト

---

# 🧾 **index.html（例）**

```html
<html>
<body>
  <h1>HTTPS Web Server Working</h1>
</body>
</html>
```

---

# 🧾 **health.html（例）**

```html
OK
```

シンプルな文字列だけで十分です（LB の HC はボディ内容は気にしない）。

---

# 🏗️ **ビルド**

```sh
docker build -t debug-https-server .
```

---

# ▶️ **起動**

```sh
docker run -p 8080:80 -p 8443:443 --name web debug-https-server
```

---

# 🔍 **動作確認**

### ページ

```sh
curl -k https://localhost:8443/
```

### ヘルスチェック

```sh
curl -k https://localhost:8443/healthz
```

---

# 🎯 **次に必要なものは？**

* **内部 ALB / 外部 ALB のヘルスチェック設定例（GCP用）**
* **Terraform に組み込む例**
* **Artifact Registry に push する手順**
* **GKE Deployment + Service YAML を作る**

必要ならすぐ作成します。
