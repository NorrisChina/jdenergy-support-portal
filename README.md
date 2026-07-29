# JD Energy 海外工程部综合交付与服务门户

## 法兰克福服务器上线三步走

### 1. 本地打包

在本地项目根目录执行前端生产构建：

```bash
cd frontend
npm run build
```

打包时请保留这两个目录：

```text
backend/
frontend/dist/
```

建议在本地先压缩成一个部署包，例如：

```bash
cd /Users/norris/Desktop/energy/web
tar -czf jdenergy-support-deploy.tar.gz backend frontend/dist
```

### 2. 上传到宝塔并解压

使用宝塔面板的文件管理器，把 `jdenergy-support-deploy.tar.gz` 上传到服务器后解压到：

```text
/www/wwwroot/jdenergy-support.tech
```

解压后目录建议保持如下结构：

```text
/www/wwwroot/jdenergy-support.tech/
├── backend/
└── dist/
```

### 3. 配置网站与反向代理

在宝塔面板的「网站」设置中：

1. 网站根目录指向 ` /www/wwwroot/jdenergy-support.tech/dist `。
2. Nginx 反向代理把 `/api` 请求转发到后端 `8000` 端口。
3. 前端保持静态站点托管，后端只暴露 API。

可参考的 Nginx 配置片段如下：

```nginx
location / {
    root /www/wwwroot/jdenergy-support.tech/dist;
    try_files $uri $uri/ /index.html;
}

location /api/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 后端生产启动

进入 `backend/` 后执行：

```bash
chmod +x run_prod.sh
./run_prod.sh
```

如果希望关闭 SSH 后进程继续运行，可使用 `nohup` 或 `screen`：

```bash
nohup ./run_prod.sh > backend.log 2>&1 &
```

```bash
screen -S jdenergy-backend
./run_prod.sh
# 按 Ctrl+A，再按 D 退出并保持后台运行
```

## 仅初始化“故障排查与解决”页面数据库

如果你要发布全部代码，但只初始化“故障排查与解决”（after-sales）页面数据，请按下面步骤：

1. 启动后端时关闭全量 seed（避免自动初始化其他页面示例数据）

```bash
cd /www/wwwroot/jdenergy-support.tech/backend
SEED_MODE=none nohup ./run_prod.sh > backend.log 2>&1 &
```

2. 单独导入故障码数据

```bash
cd /www/wwwroot/jdenergy-support.tech
/www/wwwroot/jdenergy-support.tech/.venv/bin/python scripts/import_fault_codes.py
```

导入脚本会对 after-sales 故障码做按 `(module, fault_code)` 的新增或更新，不会覆盖其他业务页面的数据。
