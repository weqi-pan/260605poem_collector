# 古诗爬虫 + FastAPI 后端

项目支持从古诗文网唐诗三百首页面抓取指定体裁和作者的诗词，并以 SQLite 作为主存储。

数据源：https://www.gushiwen.cn/gushi/tangshi.aspx

## 安装依赖

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 项目结构

```text
app/
  auth.py          # Bearer token 校验
  cache.py         # Redis 缓存封装
  config.py        # 配置和常量
  crawler.py       # 异步爬虫服务
  database.py      # SQLite 初始化、导入和查询
  main.py          # FastAPI 应用工厂
  models.py        # 爬虫内部 dataclass 模型
  parsers.py       # 古诗文网 HTML 解析器
  schemas.py       # FastAPI 请求/响应模型
  text_utils.py    # 文本清洗工具
  routers/
    crawl.py       # /crawl 路由
    poems.py       # 查询路由
crawl_tangshi.py   # CLI 入口
main.py            # uvicorn main:app 兼容入口
```

## 爬虫 CLI

```powershell
.\.venv\Scripts\python.exe .\crawl_tangshi.py --category 五言绝句 --author 王维
```

支持体裁：

- 五言绝句
- 七言绝句
- 五言律诗
- 七言律诗
- 五言古诗
- 七言古诗
- 乐府

首次运行会创建 `data/poems.db`，并自动把已有的 `data/tangshi_selected.json` 导入 SQLite；重复数据按 `url` 跳过。

## 启动 API

```powershell
.\.venv\Scripts\uvicorn.exe main:app --reload
```

默认 Redis 地址为 `redis://localhost:6379/0`，可通过环境变量覆盖：

```powershell
$env:REDIS_URL="redis://localhost:6379/0"
```

所有接口都需要令牌：

```text
Authorization: Bearer 123456
```

## 公网穿透

如果本机 `8000` 端口被 C-Lodop 等服务占用，建议把 FastAPI 启动到 `8010`：

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8010
```

再另开一个 PowerShell 窗口启动 localtunnel，并指定相对固定的子域名：

```powershell
npx -y localtunnel --port 8010 --local-host 127.0.0.1 --subdomain poem-collector-demo
```

成功后会输出：

```text
your url is: https://poem-collector-demo.loca.lt
```

当前已验证可访问的公网地址：

```text
https://poem-collector-demo.loca.lt/docs
https://poem-collector-demo.loca.lt/ui/
```

`--subdomain` 可以让地址尽量保持一致，但 localtunnel 免费服务不保证永久独占；如果子域名被占用或服务端重置，仍可能需要换名。接口仍然需要请求头：

```text
Authorization: Bearer 123456
```

如果需要查看本次穿透日志：

```powershell
Get-Content .\data\localtunnel-8010.out.log
Get-Content .\data\localtunnel-8010.err.log
```

## API

### 按标题查询

```http
GET /poems/by-title?title=登鹳雀楼
```

返回同名诗列表，每项包含 `title`、`author`、`dynasty`、`content`。

### 查询作者全部标题

```http
GET /poets/王维/titles
```

返回该作者所有诗，每项包含 `title`、`category`。

### 启动异步爬虫

```http
POST /crawl
```

Body：

```json
{
  "category": "五言绝句",
  "author": "王维"
}
```

响应包含 `matched`、`inserted`、`skipped`、`failed`。
