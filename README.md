# honeymoon.yuanping.fun

移动优先、无边框矩形块拼接的纯静态站点。零依赖、零构建，部署到腾讯云 EdgeOne Makers。

## 目录结构

```
.
├── index.html        # 页面：首块满屏高德地图，其余矩形块拼接
├── css/style.css     # 64 种秋景配色 + 矩形块/地图样式
├── place.json        # 行程点位（name/lng/lat/location），地图标记数据源
└── README.md
```

## 本地预览

```bash
# 在项目根目录执行
python -m http.server 8000
# 浏览器打开 http://localhost:8000
```

## 部署到 EdgeOne Makers

纯静态、无构建步骤，两种方式任选：

### 方式一：Git 部署（推荐，推代码自动续部署）

1. 把本目录推到 GitHub / Gitee / Coding 仓库。
2. EdgeOne 控制台「Makers」→ 导入该仓库。
3. 框架选「其他 / Other」，构建命令留空，输出目录填 `.`（根目录）。
4. 部署完成获得 `*.edgeone.app` 地址；之后推 `main` 自动重新部署。

### 方式二：CLI 部署（本地一条命令）

```bash
npm install -g edgeone
edgeone login -t $MAKERS_API_TOKEN     # Token 在控制台生成
edgeone makers link -n honeymoon        # 关联控制台已建好的项目
edgeone makers deploy                   # 部署当前目录
```

## 自定义域名

- 控制台绑定 `honeymoon.yuanping.fun`，加 CNAME / 改 NS 到 EdgeOne。
- ⚠️ 若要大陆访问，域名需已完成 ICP 备案。

## 自定义

- **高德地图**：首块是满屏地图，标记来自 `place.json`（name/lng/lat/location），并连成路线。
  在 `index.html` 底部填入你自己的 **Web 端 JS API key**（替换 `你的高德KEY`）和
  **安全密钥**（替换 `你的安全密钥`）；key 还需在高德后台登记允许域名（`localhost` 和 `honeymoon.yuanping.fun`）。
- **配色**：改 `css/style.css` 里 `.c1~.c64` 的 `background` / `color`，每个块随机取一个。
- **加一块**：复制 `index.html` 里一行 `<section class="block">文字</section>`，JS 会自动随机上色。
- **改点位**：直接编辑 `place.json`，地图标记自动更新（无需改代码）。
