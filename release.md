# Release Notes — honeymoon.yuanping.fun

移动优先、无边框矩形块拼接的静态蜜月旅行站。版本号自 v1.4 起在页面右上角标注，v0.20 起切换为 0.x 格式。

---

## 初始开发（v1.0 ~ v1.3，未标版本号）

- **v1.0** 静态框架：无边框矩形块拼接（AAAA/BBBB/CCCC/DDDD），移动优先，64 种大兴安岭秋景配色、每块随机
- **v1.1** 首块接入高德地图：`place.json` 点位标记 + 路线连线，地图画框
- **v1.2** 地图加厚边框（36px，颜色从 64 色库随机）
- **v1.3** 修复 `LngLat(NaN, NaN)`：容器 0 尺寸导致坐标换算 NaN。`#map` 改绝对定位填满内容区、显式 `center`、点位在 `complete` 后加载、`setFitView` 替代手动 `setBounds`、`map.resize()` 兜底

## v1.4 — 版本号体系建立

- 清理无用文件（旧 `path.json`、视频转写素材，git 提交）
- 页面右上角新增临时版本号标签 `#ver`，用于辨认变更

## v1.5

- 标记点击弹出信息窗（名称 + location），点地图空白处关闭

## v1.6

- 底图色调跟随边框随机色（尝试 `setMapStyle({styleJson})` —— 发现 **AMap 2.0 不支持运行时 styleJson**，静默失效）

## v1.7

- 底图色调改用纯 CSS 覆盖层 `#map-tint`（absolute 覆盖 + 边框同色 + 低透明度），底图固定「远山黛」浅色保证可读

## v1.8

- 删除全部调试代码（`#debug` 条、`setDebug`、全局错误监听、白名单 6s 提示）
- 地图画框改回竖版 4:3（`aspect-ratio: 3/4`，宽度贴满）

## v1.9

- 去掉首块 `min-height:100dvh`：地图框高度自适应、贴顶、无上下留白（4:3 与满屏不可兼得，最终选 4:3 + 自适应高度）

## v2.0

- 点位加载重构：按 `path.json` 的 `plan` 顺序 + `place.json` 取坐标（name 匹配建索引）；跳过 `overnight` 占位项；缺失点位 console 报错 + 地图底部红字条 `#map-err`
- 数据验证：34 个点位全部匹配（9 个 overnight 跳过）

## v0.20

- 版本号体系切换为 0.x 格式
- 地图染色层透明度 0.25 → 0.20

## v0.21

- 路线由直线改为平滑贝塞尔曲线（Catmull-Rom 转三次贝塞尔，曲线穿过每个点位）

## v0.22

- 标记样式：默认图钉 → 「圆点 + 点位名称标签」（自定义 `content`，`anchor: bottom-center`）

## v0.23

- 路线按 `date` 分段着色：同 date 同色、不同 date 不同色（34 点 → 10 段，对应 9/12~9/21）

## v0.24

- 线改 10 级灰阶、点改灰色、点直径 = 线宽（3px）

## v0.25

- 线配色：随机取 64 色秋景库 + 叠 50% 灰蒙版（`grayMix` 与中灰混合）

## v0.26

- 64 色秋景库替换为 **16 种中国古典色**：藤黄/黛蓝/杏黄/胭脂/月白/黄栌/竹青/柿红/秋香/松花绿/琥珀/缃色/赭石/鹅黄/黛绿/天青；`.c1`~`.c16` 一组、64 类循环 4 轮

## v0.27

- 移除地图染色蒙版（`#map-tint` 的 HTML / CSS / JS 全部删除），底图恢复纯「远山黛」浅色

## v0.28

- 16 种古典色整体替换为**莫兰迪灰调**版本（低饱和、更柔和）：藤黄 `#AF8D4E` / 黛蓝 `#4A5259` / 杏黄 `#B98C5E` / 胭脂 `#7F4147` / 月白 `#D9D4C8` / 黄栌 `#A77E51` / 竹青 `#7B7A5F` / 柿红 `#A2614A` / 秋香 `#9D8B50` / 松花绿 `#4C5A47` / 琥珀 `#97602F` / 缃色 `#C0A86B` / 赭石 `#6E5540` / 鹅黄 `#CFC298` / 黛绿 `#46504B` / 天青 `#6E7F80`；文字色按亮度自动判断

## v0.29

- 修正 `place.json` 中 **14 个点位坐标**（消除重复/错误坐标导致的断线）：神龙湾、白桦林、女脚湾、满归、伊克萨玛、老鹰嘴、临江、神仙坡、蒙兀景区、室韦、7卡、扎龙湿地、小白山、漠河——坐标来自腾讯地图/百科/GPS 实测
- 修复后仅剩 6 处 <1.5km 短线段，均为**真实相邻**（漠河/海拉尔/满洲里市区内、临江-神仙坡相邻）

## v0.30

- 地图数据源迁移：不再读取已删除的 `place.json`，改为直接解析 `path.json` 内嵌的 `coordinate`（"经度,纬度"字符串）
- 点位标记/按 date 分段贝塞尔路线逻辑不变；无效 coordinate 的点计入底部红字提示 `#map-err`
- 信息窗内容升级：名称 + 市级/县级行政区（`city`/`county`）+ 日期（YYMMDD → 年/月/日）+ 备注 `note`
- 顺带修正：缺失点位文案从"place.json 未找到"改为"coordinate 无效"

## v0.31

- 移除 `overnight` 占位项跳过逻辑（不再使用 overnight 数据）
- 路线简化：取消按 date 分段同色、取消 Catmull-Rom 贝塞尔曲线（疑似未生效）、取消 64 色秋景库 + 灰蒙版配色
- 路线改为一条普通折线（Polyline），统一使用高德默认颜色，线宽 3、不透明度 0.85

## v0.33

- **取消地图厚边框**（原 36px 随机色边框）：iOS Safari 移动端边框遮挡高德版权文字（© 2026 AutoNavi - GS(2025)5996），且高德 2.0 版权/Logo 为 Canvas 绘制、CSS 无法移动，直接取消边框让版权贴底完整显示
- 移除边框随机上色 JS 与版权上移 hack（`amap-copyright/amap-logo` 非 DOM 元素，hack 无效）
- 地图块恢复为无边框整块，`#map-frame` 保留竖版 4:3

## v0.34

- 代码清理：移除临时版本号标签 `#ver`（其唯一用途"确认后删掉"）、移除无效的 `onerror="window.__mapErr"`（从未被读取）、清理过时注释
- 高德 key 注释精简（key 已内置）

## v0.35

- CSS 精简：`.c1`~`.c64`（16 色循环 4 轮的 320 行重复）压缩为 `.c1`~`.c16` 单组（同分布，JS 随机范围 64→16）；移除 `max-width:none`、`border-radius:0` 等冗余；更新过时注释
- HTML：`#map-hint` 提示文案更新（key 已内置，改为网络/配置提示）
- `style.css` 448 行 → 约 210 行，行为不变

## v0.36

- 地图左下角新增**网站大标题**竖排水印「北境秋海」（`#site-title`，衬线字体，白字深阴影，避开高德 logo/版权区，不拦截触摸）

## v0.37

- 标题加大加粗（`clamp(44px,14vw,64px)`，weight 900），文字颜色由 JS 从 16 色配色表随机取（背景透明）
- 标题右下角新增版本号 `#ver-tag`（v0.37，黑色小字）

## v0.39

- 标题更名「**漠岭松桦**」，移至地图**宽 1/4 处**，移除阴影
- 版本号改为**竖排**，置于标题右侧、与标题**底部对齐**（v0.39，黑色）

## v0.40

- 标题改用**配色表整组配色**：JS 直接挂随机 `.cN` 类（背景 + 文字色同取自 16 色表），删除无用的 `pickColor` 函数
- 标题加**偏移硬阴影**模拟描边（`text-shadow: 4px 4px 0`，无模糊），加少量 padding 让色块更整

## v0.41

- 标题改**印章式三排**布局（左下角）：「漠岭」「松桦」两列竖排 + 版本号**横排**落款（版本号不再旋转）
- 主体文字用配色 **background** 色，偏移阴影用配色 **color** 色（3px 偏移，JS 从 16 色表随机取一组）

## v0.42

- 点位名称背景框**按日期同色**：同 `date` 复用同色，不同日期从 16 色莫兰迪表随机取底
- 颜色叠 **50% 白色蒙版淡化**（`fadeWithWhite`，与白混合），浅底配深字保持可读

## v0.43

- **按 county 叠加行政区区域**：遍历 plan 去重 county（15 个），用高德 `AMap.DistrictSearch` 查询边界，`AMap.Polygon` 半透明填充（填充 15%、边框 60%），每个 county 从 16 色随机取色（不撞色，淡化 55%）
- 边界点数抽稀到 ≤2000 点（实测额尔古纳市原始 6187 点，防移动端卡顿）
- 层级：区域 zIndex 1 < 路线 5 < 标记 10

## v0.44

- **county 边界改为预加载**：不再运行时查询高德 DistrictSearch（连续查询会回调丢失/限流，导致部分区域缺失）
- `path.json` 新增 `county_areas`（15 个 county 的边界环数组，抽稀到 ≤1500 点/环，约 284KB），由 Python 从阿里 DataV GeoAtlas 按 adcode 预取（`geo.datav.aliyun.com/areas_v3/bound/{adcode}.json`）
- `index.html` 直接读取 `county_areas` 画 Polygon，无异步查询、100% 覆盖

## v0.45

- **county 边界独立成文件 `county.json`**（216KB，紧凑格式），`path.json` 恢复为纯行程数据（7KB）
- 新增脚本 **`fetch_county.py`**（项目根目录）：自动读取 `path.json` 去重出 county → 从 DataV GeoAtlas 拉边界 → 覆盖写 `county.json`。用法 `python fetch_county.py`
- `index.html` 并行加载 `path.json` + `county.json`；`county.json` 缺失时降级为不画区域（不阻塞地图）

## v0.46

- **路线按行程状态分段着色**：折线改为逐段绘制，`plan` 点位 `arrived: true` 时，从该点出发的下一段为松霜绿 `#4A6656`（秋·松叶，线宽 4、zIndex 6），其余段石绿 `#1A7A50`（夏·松叶，线宽 3、zIndex 5）——走过的路从夏入秋
- **点位圆点随状态换色**：未到点苍筤 `#72B28E`（夏·枫叶，3px），已到点枫叶红 `#B02F23`（秋·枫叶，6px）
- `path.json` 全部点位补充 `arrived` 字段（当前通辽机场、通辽站为 `true`，行程推进时逐点标记即可点亮路线）

## v0.47

- **行程配色定稿「夏→秋」主题**：
  - 未走路线：石绿 `#1A7A50`（夏·松叶）
  - 未到圆点：苍筤 `#72B28E`（夏·枫叶，3px）
  - 已走路线：松霜绿 `#4A6656`（秋·松叶）
  - 已到圆点：枫叶红 `#B02F23`（秋·枫叶，6px）
- 走过的路从夏入秋，到达的点位枫叶变红

## v0.48

- 已走路线配色调整：松霜绿 `#4A6656` → **秋香绿 `#637049`**（秋·松叶）

## v0.49

- **行程配色体系定稿（四季·草木）**：

  | 状态 | 元素 | 色名 | 色值 | 意象 |
  |---|---|---|---|---|
  | 夏·未走 | 松叶·路线 | 翠微 | `#35856E` | 青翠欲滴 |
  | 秋·已走 | 松叶·路线 | 苍绿 | `#365B4F` | 岁寒后凋 |
  | 夏·未到 | 枫叶·点位 | 秋香 | `#C6A15B` | 含碧未红 |
  | 秋·已到 | 枫叶·点位 | 霜叶红 | `#A53A2D` | 霜叶红于二月花 |

- 走过之处，松叶由翠微转苍绿，枫叶由秋香染霜红

## v0.50

- **行程配色换为「落叶松·五花山」主题**：

  | 状态 | 元素 | 色名 | 色值 |
  |---|---|---|---|
  | 夏·未走 | 落叶松·路线 | 林海翠 | `#3A9268` |
  | 秋·已走 | 落叶松·路线 | 松金 | `#E0A62E` |
  | 夏·未到 | 杜鹃·点位 | 鹃紫 | `#A84D9C` |
  | 秋·已到 | 五花山·点位 | 五花红 | `#C2502A` |

- 林海由翠转金，杜鹃开尽五花山

## v0.51

- 已到点位（五花红）视觉增强：直径加大 + 同色半透明光环 + 深色投影，地图上更醒目

## v0.53

- **交通方式标注**：`plan` 点位 `transportation` 非空时，内容显示在该点位**前面进入它的那条线路**的正中间（白底圆角小标签 `.map-transport`，居中锚点、层级高于路线）
- 已到点位尺寸回调：直径 6px、光环 2px（v0.51 的 9px/4px 偏大）

## v0.54

- 交通方式标签 `.map-transport` 去除白底圆角背景框，改为**纯文字**（仅加白色描边阴影保证地图上的可读性）

## v0.55

- 交通方式标签定位修正：锚点由 `center` 改 `top-left` + 标签自身 `translate(-50%,-50%)`，确保精确落在路段**正中间**（AMap 2.0 的 `center` 关键字不可靠，会偏到线下方）

## v0.56

- 交通方式标签居中再修：AMap 2.0 会用自身 `transform` 覆盖元素上的 `translate(-50%,-50%)`，导致仍偏下方。改在渲染后读取标签实际尺寸，用 `setOffset(-w/2, -h/2)` 负半偏移精确居中（兼容 `getDom/getElement/getContent`）

## v0.57

- 交通方式标签居中兜底：`setTimeout(0)` 可能早于 AMap 建好标记 DOM（测得尺寸为 0、offset 未生效）。改为 `requestAnimationFrame` 轮询（最多 40 次）直到测到真实尺寸再 `setOffset` 居中

## v0.58

- 交通方式标签居中终版：不再依赖 DOM 测量，直接按文本**估算尺寸**（CJK/emoji 按 11px 宽、半角按 6px、空格 4px、行高 13px），用 `setOffset(-w/2, -h/2)` 使几何中心贴合路段中点——规避 AMap 2.0 对元素 transform 的覆盖与 DOM 时序问题

## v0.59

- **交通方式标签居中根治**：从 `AMap.Marker`（anchor/offset + 估算尺寸）改为 **`AMap.DOMOverlay` 子类 `TransportLabel`**
  - 定位：`lngLatToContainer` 拿精确像素点（AMap 官方经纬度→像素换算），坐标中点 `(a+b)/2` 不变
  - 居中：CSS `transform: translate(-50%, -50%)`，由浏览器布局引擎保证几何中心精确落点，**与字体/emoji/测量时机/anchor-offset 换算全部无关**
  - 根因：v0.55~v0.58 反复跳坑在于 AMap 2.0 对 HTML content 的 anchor→offset 换算不透明、元素宽高取的是引擎测量值，与真实布局不一致
- `.map-transport` 样式：`display:inline-block` → `position:absolute`，补 `pointer-events:none`（纯文字不拦触摸）

## v0.60

- **点位标签分级显示（小比例尺 county 名 / 放大 name）**：
  - 每个 county 第一个出现的点为「代表点」，小比例尺（zoom 3~7）显示 **county 名**（`.map-dot-county`，加粗描边更醒目），其余同 county 点隐藏
  - 放大到 zoom ≥ 8 显示具体 **name**（`.map-dot-name`），与 county 标签通过 Marker `zooms` 属性互斥切换
  - 代表点两个 marker（county 标签 `zooms:[3,7]` / name 标签 `zooms:[8,20]`），同位置、不同 zoom 段各自显示
- 解决同城密集点（漠河市区 3 点、额尔古纳市区 2 点、通辽/齐齐哈尔/哈尔滨市区各 2 点）小比例尺下标签糊成一团的问题
- 代表点 county 标签点击同样弹信息窗（内容同 name 标签）

## v0.61

- **紧急修复：点位和路线不显示的致命 bug**
  - 根因：v0.59 引入的 `AMap.DOMOverlay` 是**插件**，默认不随核心 API 加载，`onAMapLoaded` 里 `AMap.DOMOverlay.call(this)` 时其为 `undefined` → 抛 `TypeError` → `addPoints` 整体中断，点位/路线/区域全部未绘制（仅地图底图正常）
  - 修复①：JS API URL 加 `&plugin=AMap.DOMOverlay` 显式加载插件
  - 修复②：`TransportLabel` 定义改为 `typeof AMap.DOMOverlay === "function"` 判断后才创建，交通标签创建处 try/catch 兜底——即使插件加载失败，也不影响点位/路线渲染

## v0.62

- **点位标签分级策略改为 `explicit` 字段显式控制**（替代 v0.60 的 county 代表点方案）：
  - `path.json` 每个点位新增 `explicit` 布尔字段：`true` 的点默认（全 zoom 段 3~20）显示 name，`false` 的点放大到 zoom ≥ 8 才显示 name
  - 标记 `zooms` 属性按 `explicit` 二选一：`explicit===true` → `[3,20]`，否则 `[8,20]`
  - 不再显示 county 名（删除 `.map-dot-county` 样式与代表点逻辑）
  - 行程骨架（机场/火车站/主要城市/过夜点/关键景点）标 `explicit:true`，同城密集的次要点标 `false`
- 小比例尺只露行程骨架，放大后展开全部点位，避免市区密集点糊成一团

## v0.63

- **交通方式标签从 `AMap.DOMOverlay` 改回 `AMap.Text`（修复 transportation 不显示的 bug）**
  - 根因：`AMap.DOMOverlay` 是 JSAPI **v1.4.x 旧版**概念，2.0（WebGL）核心类表里根本没有它，`&plugin=AMap.DOMOverlay` 也加载不到，`typeof AMap.DOMOverlay === "function"` 恒为 false → `TransportLabel` 一直是 null → 交通标签一个都没创建
  - 修复：改用 2.0 原生 `AMap.Text`（继承自 `AMap.Marker`），`anchor: "center"` 让文字几何中心精确落在路段中点，`zIndex: 20` 高于路线/标记确保不被遮挡，`clickable: false` + `pointer-events: none` 不拦触摸
  - 移除 API URL 的 `&plugin=AMap.DOMOverlay`，删除 `TransportLabel` 类定义与 `createDOM/draw` 逻辑

## v0.64

- **路线从折线改为平滑曲线**（Catmull-Rom 样条 → 三次贝塞尔，`AMap.BezierCurve`）：
  - `smoothBezierPath` 把点位序列转成多段贝塞尔 path（控制点 = 相邻点张力 1/6），曲线穿过每个点位且段间平滑
  - 按 `arrived` 连续段拆成两条曲线：已走段实线（松金 `#E0A62E`，线宽 4、zIndex 6），未走段虚线（林海翠 `#3A9268`，线宽 3、zIndex 5）
  - 状态切换处断开：为保证曲线连续，新一组起点带入上一组末点
  - 交通方式标签仍显示在原始两点坐标中点（不受曲线影响）
  - 两点退化为直线段（单段无控制点，仍用 BezierCurve 容器）

## v0.65

- **撤回曲线，路线改为匹配高德驾车导航**（前端 JSONP，全段驾车路线）：
  - 移除 v0.64 的 `smoothBezierPath` + `AMap.BezierCurve`，改回 `AMap.Polyline`
  - 新增 `drawSegment(from, to, arrived)`：用 JSONP 调高德驾车 Web 服务 API（`/v3/direction/driving`），取 `route.paths[0].steps[].polyline` 拼接成真实道路坐标点画 `AMap.Polyline`
  - 颜色/线宽/zIndex 规则与旧版一致（已走段松金实线 zIndex 6、未走段林海翠 zIndex 5），按 `from.arrived` 决定每段
  - 逐段 JSONP 回调各自独立 `cbName`（随机后缀），成功渲染真实路网，失败或未填 key 回退两点直线
  - **依赖「Web 服务」类型 key**：页面 JS API key 调 Web 服务 API 返回 `USERKEY_PLAT_NOMATCH`（10009），需在高德控制台单独创建「Web 服务」key，填入 `index.html` 的 `WEB_SERVICE_KEY` 变量；留空则全程回退直线

## v0.66

- **撤回 v0.65 JSONP 导航，改方案 B（圆角折线）**：
  - 移除高德驾车 Web 服务调用与 `WEB_SERVICE_KEY` 依赖，不再需要额外 key
  - 相邻点位连直线，`AMap.Polyline` 加 `lineJoin:'round'` + `lineCap:'round'` 让拐角圆滑（线自身不穿点，拐角处有轻微圆角偏移）
  - 按 `arrived` 连续段分组着色（已走松金实线 zIndex 6、未走林海翠 zIndex 5），状态切换处断开重开一组，保证每段独立平滑

## v0.67

- **撤回 v0.66 圆角折线，改方案 D（平滑曲线，严格穿点）**：
  - 恢复 Catmull-Rom → 三次贝塞尔：`smoothBezierPath(pts)` 控制点 = 相邻点张力 1/6，曲线精确穿过每个点位
  - 用 `AMap.BezierCurve`，path 每段 = [控制点1, 控制点2, 终点]（3 组坐标），算法已用 node 验证穿点正确
  - 按 `arrived` 连续段分组，状态切换处断开并带入上一组末点保证段间连续
  - 已走段松金实线 zIndex 6、未走段林海翠 zIndex 5

## v0.68

- **撤回曲线，路线定格为简单直线折线**：
  - 移除方案 D（Catmull-Rom 贝塞尔 + `AMap.BezierCurve`），代码已完全清理无残留
  - 相邻点位连直线，`AMap.Polyline` 单条折线，按 `arrived` 连续段分组着色（已走松金实线 zIndex 6、未走林海翠 zIndex 5）
  - 路线绘制至此定稿为直线，不再做曲线/圆角/导航
