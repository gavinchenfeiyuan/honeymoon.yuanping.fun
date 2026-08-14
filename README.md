# honeymoon.yuanping.fun

移动优先、无边框矩形块拼接的纯静态站点。零依赖、零构建，部署到腾讯云 EdgeOne Makers。

## 目录结构

```
.
├── index.html        # 页面：一块块矩形块拼接（首块满屏）
├── css/style.css     # 配色与矩形块样式
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
3. 框架选「静态 / 无构建」，输出目录填 `.`（根目录）。
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

- **配色**：改 `css/style.css` 底部 `.block-a ~ .block-d` 的 `background` / `color`。
- **加一块**：复制 `index.html` 里一行 `<section class="block block-x">文字</section>`，
  再在 `css/style.css` 补 `.block-x { background:#颜色; color:#文字色; }`。
- **首块满屏**：`.block-a` 已设 `min-height:100vh`；改回 `38vh` 即变半屏。
