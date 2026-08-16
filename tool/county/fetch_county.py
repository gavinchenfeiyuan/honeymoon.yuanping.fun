#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
path.json <-> county.json 双向工具：先逆地理编码填充行政区划，再按 county 拉取边界。

用法：
    python fetch_county.py

阶段 1：逆地理编码填充 path.json 的 city / county
- 遍历 path.json 的 plan 每个点，凡有 coordinate 的点，调用高德 regeo 逆地理编码，
  用返回的 addressComponent 填充 city 与 county 字段（仅当缺失或可校正时更新）。
- 需要高德 Web 服务 key：从本地 amap_key.txt 读取（gitignore，勿提交）。文件缺失则跳过阶段 1。
- 若已配置并成功，将填充后的 plan 写回 path.json。

阶段 2：按 county 拉取行政边界写 county.json
- 从 path.json 的 plan 去重提取 county（保持出现顺序）。
- adcode 从内置 COUNTY_ADCODE 兜底表查（四省 380 县级已内置，离线可用）。
- 若 county.json 中该 county 已有 boundaries，则跳过下载（直接复用，零请求）。
- 仅对缺失/无边界的 county，按 adcode 从
  https://geo.datav.aliyun.com/areas_v3/bound/{adcode}.json 拉 GeoJSON。
- 抽稀到 ≤1000 点/环、坐标保留 5 位小数，写入 county.json（紧凑格式）。
- 失败保护：完全无数据时不覆盖旧文件。

adcode 来源：仅内置 COUNTY_ADCODE（四省 380 县级）。加格达奇区已覆盖为权威值 232718。
"""
import io
import json
import os
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # tool/county/ -> 项目根
PATH_JSON = os.path.join(ROOT, "path.json")
COUNTY_JSON = os.path.join(ROOT, "county.json")
BOUND = "https://geo.datav.aliyun.com/areas_v3/bound/{adcode}.json"
REGOEO = "https://restapi.amap.com/v3/geocode/regeo"
UA = {"User-Agent": "Mozilla/5.0"}
AMAP_KEY_FILE = os.path.join(ROOT, "amap_key.txt")  # 高德 key 本地文件（gitignore，勿提交）


def _load_amap_key():
    """从本地 amap_key.txt 读取高德 Web 服务 key。文件缺失返回空串。"""
    try:
        with open(AMAP_KEY_FILE, encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""

# 内置兜底表：东北三省 + 内蒙古 全部县级行政区划名 -> adcode（高德行政区划代码）。
# 数据源：github.com/tombcato/china-zipcode-data（jsDelivr CDN），加格达奇区覆盖为权威值。
COUNTY_ADCODE = {
    "新城区": 150102,
    "回民区": 150103,
    "玉泉区": 150104,
    "赛罕区": 150105,
    "土默特左旗": 150121,
    "托克托县": 150122,
    "和林格尔县": 150123,
    "清水河县": 150124,
    "武川县": 150125,
    "东河区": 150202,
    "昆都仑区": 150203,
    "青山区": 150204,
    "石拐区": 150205,
    "白云鄂博矿区": 150206,
    "九原区": 150207,
    "土默特右旗": 150221,
    "固阳县": 150222,
    "达尔罕茂明安联合旗": 150223,
    "海勃湾区": 150302,
    "海南区": 150303,
    "乌达区": 150304,
    "红山区": 150402,
    "元宝山区": 150403,
    "松山区": 150404,
    "阿鲁科尔沁旗": 150421,
    "巴林左旗": 150422,
    "巴林右旗": 150423,
    "林西县": 150424,
    "克什克腾旗": 150425,
    "翁牛特旗": 150426,
    "喀喇沁旗": 150428,
    "宁城县": 150429,
    "敖汉旗": 150430,
    "科尔沁区": 150502,
    "科尔沁左翼中旗": 150521,
    "科尔沁左翼后旗": 150522,
    "开鲁县": 150523,
    "库伦旗": 150524,
    "奈曼旗": 150525,
    "扎鲁特旗": 150526,
    "霍林郭勒市": 150581,
    "东胜区": 150602,
    "康巴什区": 150603,
    "达拉特旗": 150621,
    "准格尔旗": 150622,
    "鄂托克前旗": 150623,
    "鄂托克旗": 150624,
    "杭锦旗": 150625,
    "乌审旗": 150626,
    "伊金霍洛旗": 150627,
    "海拉尔区": 150702,
    "扎赉诺尔区": 150703,
    "阿荣旗": 150721,
    "莫力达瓦达斡尔族自治旗": 150722,
    "鄂伦春自治旗": 150723,
    "鄂温克族自治旗": 150724,
    "陈巴尔虎旗": 150725,
    "新巴尔虎左旗": 150726,
    "新巴尔虎右旗": 150727,
    "满洲里市": 150781,
    "牙克石市": 150782,
    "扎兰屯市": 150783,
    "额尔古纳市": 150784,
    "根河市": 150785,
    "临河区": 150802,
    "五原县": 150821,
    "磴口县": 150822,
    "乌拉特前旗": 150823,
    "乌拉特中旗": 150824,
    "乌拉特后旗": 150825,
    "杭锦后旗": 150826,
    "集宁区": 150902,
    "卓资县": 150921,
    "化德县": 150922,
    "商都县": 150923,
    "兴和县": 150924,
    "凉城县": 150925,
    "察哈尔右翼前旗": 150926,
    "察哈尔右翼中旗": 150927,
    "察哈尔右翼后旗": 150928,
    "四子王旗": 150929,
    "丰镇市": 150981,
    "乌兰浩特市": 152201,
    "阿尔山市": 152202,
    "科尔沁右翼前旗": 152221,
    "科尔沁右翼中旗": 152222,
    "扎赉特旗": 152223,
    "突泉县": 152224,
    "二连浩特市": 152501,
    "锡林浩特市": 152502,
    "阿巴嘎旗": 152522,
    "苏尼特左旗": 152523,
    "苏尼特右旗": 152524,
    "东乌珠穆沁旗": 152525,
    "西乌珠穆沁旗": 152526,
    "太仆寺旗": 152527,
    "镶黄旗": 152528,
    "正镶白旗": 152529,
    "正蓝旗": 152530,
    "多伦县": 152531,
    "阿拉善左旗": 152921,
    "阿拉善右旗": 152922,
    "额济纳旗": 152923,
    "和平区": 210102,
    "沈河区": 210103,
    "大东区": 210104,
    "皇姑区": 210105,
    "铁西区": 220302,
    "苏家屯区": 210111,
    "浑南区": 210112,
    "沈北新区": 210113,
    "于洪区": 210114,
    "辽中区": 210115,
    "康平县": 210123,
    "法库县": 210124,
    "新民市": 210181,
    "中山区": 210202,
    "西岗区": 210203,
    "沙河口区": 210204,
    "甘井子区": 210211,
    "旅顺口区": 210212,
    "金州区": 210213,
    "普兰店区": 210214,
    "长海县": 210224,
    "瓦房店市": 210281,
    "庄河市": 210283,
    "铁东区": 220303,
    "立山区": 210304,
    "千山区": 210311,
    "台安县": 210321,
    "岫岩满族自治县": 210323,
    "海城市": 210381,
    "新抚区": 210402,
    "东洲区": 210403,
    "望花区": 210404,
    "顺城区": 210411,
    "抚顺县": 210421,
    "新宾满族自治县": 210422,
    "清原满族自治县": 210423,
    "平山区": 210502,
    "溪湖区": 210503,
    "明山区": 210504,
    "南芬区": 210505,
    "本溪满族自治县": 210521,
    "桓仁满族自治县": 210522,
    "元宝区": 210602,
    "振兴区": 210603,
    "振安区": 210604,
    "宽甸满族自治县": 210624,
    "东港市": 210681,
    "凤城市": 210682,
    "古塔区": 210702,
    "凌河区": 210703,
    "太和区": 210711,
    "黑山县": 210726,
    "义县": 210727,
    "凌海市": 210781,
    "北镇市": 210782,
    "站前区": 210802,
    "西市区": 210803,
    "鲅鱼圈区": 210804,
    "老边区": 210811,
    "盖州市": 210881,
    "大石桥市": 210882,
    "海州区": 210902,
    "新邱区": 210903,
    "太平区": 210904,
    "清河门区": 210905,
    "细河区": 210911,
    "阜新蒙古族自治县": 210921,
    "彰武县": 210922,
    "白塔区": 211002,
    "文圣区": 211003,
    "宏伟区": 211004,
    "弓长岭区": 211005,
    "太子河区": 211011,
    "辽阳县": 211021,
    "灯塔市": 211081,
    "双台子区": 211102,
    "兴隆台区": 211103,
    "大洼区": 211104,
    "盘山县": 211122,
    "银州区": 211202,
    "清河区": 211204,
    "铁岭县": 211221,
    "西丰县": 211223,
    "昌图县": 211224,
    "调兵山市": 211281,
    "开原市": 211282,
    "双塔区": 211302,
    "龙城区": 211303,
    "朝阳县": 211321,
    "建平县": 211322,
    "喀喇沁左翼蒙古族自治县": 211324,
    "北票市": 211381,
    "凌源市": 211382,
    "连山区": 211402,
    "龙港区": 211403,
    "南票区": 211404,
    "绥中县": 211421,
    "建昌县": 211422,
    "兴城市": 211481,
    "南关区": 220102,
    "宽城区": 220103,
    "朝阳区": 220104,
    "二道区": 220105,
    "绿园区": 220106,
    "双阳区": 220112,
    "九台区": 220113,
    "农安县": 220122,
    "榆树市": 220182,
    "德惠市": 220183,
    "公主岭市": 220184,
    "昌邑区": 220202,
    "龙潭区": 220203,
    "船营区": 220204,
    "丰满区": 220211,
    "永吉县": 220221,
    "蛟河市": 220281,
    "桦甸市": 220282,
    "舒兰市": 220283,
    "磐石市": 220284,
    "梨树县": 220322,
    "伊通满族自治县": 220323,
    "双辽市": 220382,
    "龙山区": 220402,
    "西安区": 231005,
    "东丰县": 220421,
    "东辽县": 220422,
    "东昌区": 220502,
    "二道江区": 220503,
    "通化县": 220521,
    "辉南县": 220523,
    "柳河县": 220524,
    "梅河口市": 220581,
    "集安市": 220582,
    "浑江区": 220602,
    "江源区": 220605,
    "抚松县": 220621,
    "靖宇县": 220622,
    "长白朝鲜族自治县": 220623,
    "临江市": 220681,
    "宁江区": 220702,
    "前郭尔罗斯蒙古族自治县": 220721,
    "长岭县": 220722,
    "乾安县": 220723,
    "扶余市": 220781,
    "洮北区": 220802,
    "镇赉县": 220821,
    "通榆县": 220822,
    "洮南市": 220881,
    "大安市": 220882,
    "延吉市": 222401,
    "图们市": 222402,
    "敦化市": 222403,
    "珲春市": 222404,
    "龙井市": 222405,
    "和龙市": 222406,
    "汪清县": 222424,
    "安图县": 222426,
    "道里区": 230102,
    "南岗区": 230103,
    "道外区": 230104,
    "平房区": 230108,
    "松北区": 230109,
    "香坊区": 230110,
    "呼兰区": 230111,
    "阿城区": 230112,
    "双城区": 230113,
    "依兰县": 230123,
    "方正县": 230124,
    "宾县": 230125,
    "巴彦县": 230126,
    "木兰县": 230127,
    "通河县": 230128,
    "延寿县": 230129,
    "尚志市": 230183,
    "五常市": 230184,
    "龙沙区": 230202,
    "建华区": 230203,
    "铁锋区": 230204,
    "昂昂溪区": 230205,
    "富拉尔基区": 230206,
    "碾子山区": 230207,
    "梅里斯达斡尔族区": 230208,
    "龙江县": 230221,
    "依安县": 230223,
    "泰来县": 230224,
    "甘南县": 230225,
    "富裕县": 230227,
    "克山县": 230229,
    "克东县": 230230,
    "拜泉县": 230231,
    "讷河市": 230281,
    "鸡冠区": 230302,
    "恒山区": 230303,
    "滴道区": 230304,
    "梨树区": 230305,
    "城子河区": 230306,
    "麻山区": 230307,
    "鸡东县": 230321,
    "虎林市": 230381,
    "密山市": 230382,
    "向阳区": 230803,
    "工农区": 230403,
    "南山区": 230404,
    "兴安区": 230405,
    "东山区": 230406,
    "兴山区": 230407,
    "萝北县": 230421,
    "绥滨县": 230422,
    "尖山区": 230502,
    "岭东区": 230503,
    "四方台区": 230505,
    "宝山区": 230506,
    "集贤县": 230521,
    "友谊县": 230522,
    "宝清县": 230523,
    "饶河县": 230524,
    "萨尔图区": 230602,
    "龙凤区": 230603,
    "让胡路区": 230604,
    "红岗区": 230605,
    "大同区": 230606,
    "肇州县": 230621,
    "肇源县": 230622,
    "林甸县": 230623,
    "杜尔伯特蒙古族自治县": 230624,
    "伊美区": 230717,
    "乌翠区": 230718,
    "友好区": 230719,
    "嘉荫县": 230722,
    "汤旺县": 230723,
    "丰林县": 230724,
    "大箐山县": 230725,
    "南岔县": 230726,
    "金林区": 230751,
    "铁力市": 230781,
    "前进区": 230804,
    "东风区": 230805,
    "郊区": 230811,
    "桦南县": 230822,
    "桦川县": 230826,
    "汤原县": 230828,
    "同江市": 230881,
    "富锦市": 230882,
    "抚远市": 230883,
    "新兴区": 230902,
    "桃山区": 230903,
    "茄子河区": 230904,
    "勃利县": 230921,
    "东安区": 231002,
    "阳明区": 231003,
    "爱民区": 231004,
    "林口县": 231025,
    "绥芬河市": 231081,
    "海林市": 231083,
    "宁安市": 231084,
    "穆棱市": 231085,
    "东宁市": 231086,
    "爱辉区": 231102,
    "逊克县": 231123,
    "孙吴县": 231124,
    "北安市": 231181,
    "五大连池市": 231182,
    "嫩江市": 231183,
    "北林区": 231202,
    "望奎县": 231221,
    "兰西县": 231222,
    "青冈县": 231223,
    "庆安县": 231224,
    "明水县": 231225,
    "绥棱县": 231226,
    "安达市": 231281,
    "肇东市": 231282,
    "海伦市": 231283,
    "漠河市": 232701,
    "呼玛县": 232721,
    "塔河县": 232722,
    "加格达奇区": 232718,
}


def _get_json(url):
    req = urllib.request.Request(url, headers=UA)
    return json.loads(urllib.request.urlopen(req, timeout=25).read().decode("utf-8"))


def regeo(lng, lat, key):
    """高德逆地理编码：经纬度 -> {city, county}。key 为空或失败返回 {}。"""
    if not key:
        return {}
    params = urllib.parse.urlencode({
        "location": "{},{}".format(lng, lat),
        "key": key,
        "extensions": "base",
    })
    try:
        data = _get_json(REGOEO + "?" + params)
    except Exception:
        return {}
    if data.get("status") != "1":
        return {}
    ac = (data.get("regeocode") or {}).get("addressComponent") or {}
    # city 字段对直辖市/直筒子市可能为空数组/空串，此时回退到 province
    city = ac.get("city") or ac.get("province") or ""
    if isinstance(city, list):
        city = city[0] if city else ""
    return {
        "city": str(city).strip(),
        "county": str(ac.get("district") or "").strip(),
    }


def fill_city_county(plan):
    """阶段 1：用坐标逆地理编码填充每点的 city/county。返回被更新的点数。"""
    key = _load_amap_key()
    if not key:
        print("警告: 未找到 " + AMAP_KEY_FILE + "，跳过逆地理编码阶段 1（city/county 保持原值）")
        return 0
    updated = 0
    for i, it in enumerate(plan):
        if not it:
            continue
        coord = it.get("coordinate")
        if not coord:
            continue
        parts = str(coord).split(",")
        if len(parts) < 2:
            continue
        lng, lat = parts[0].strip(), parts[1].strip()
        try:
            lng, lat = float(lng), float(lat)
        except ValueError:
            continue
        res = regeo(lng, lat, key)
        if not res or not res.get("county"):
            continue  # 逆地理编码失败/无区县，保留原值
        changed = False
        if it.get("county") != res["county"]:
            print(f"  [{i}] {it.get('name')}: county {it.get('county')!r} -> {res['county']!r}")
            it["county"] = res["county"]
            changed = True
        if it.get("city") != res["city"]:
            print(f"  [{i}] {it.get('name')}: city   {it.get('city')!r} -> {res['city']!r}")
            it["city"] = res["city"]
            changed = True
        if changed:
            updated += 1
        time.sleep(0.1)  # 高德配额内低频，避免限流
    return updated


def simplify(ring, max_n=1000):
    """间隔采样抽稀，保留首尾点。"""
    if len(ring) <= max_n:
        return ring
    step = len(ring) / max_n
    out = [ring[0]]
    idx = step
    while idx < len(ring) - 1:
        out.append(ring[int(idx)])
        idx += step
    out.append(ring[-1])
    return out


def round_pts(ring, digits=5):
    """坐标降精度：保留 5 位小数（约 1 米），减体积。"""
    return [[round(p[0], digits), round(p[1], digits)] for p in ring]


def fetch_boundaries(adcode):
    """从 DataV GeoAtlas 拉取区划边界，返回多边形环列表（GCJ-02 坐标，与高德一致）。"""
    url = BOUND.format(adcode=adcode)
    data = _get_json(url)
    rings = []
    for feat in data.get("features", []):
        g = feat.get("geometry", {})
        coords = g.get("coordinates") or []
        if g.get("type") == "Polygon":
            rings.extend(coords)
        elif g.get("type") == "MultiPolygon":
            for poly in coords:
                rings.extend(poly)
    return rings


def _load_old_areas():
    """读取现有 county.json 的 county_areas，作为复用/失败回退。不存在则返回 {}。"""
    try:
        return json.load(open(COUNTY_JSON, encoding="utf-8")).get("county_areas", {})
    except Exception:
        return {}


def main():
    data = json.load(open(PATH_JSON, encoding="utf-8"))
    plan = data.get("plan", [])

    # ---- 阶段 1：逆地理编码填充 path.json 的 city/county ----
    print("=== 阶段 1: 逆地理编码填充 city/county ===")
    n_updated = fill_city_county(plan)
    if n_updated:
        # 有更新才写回 path.json
        with io.open(PATH_JSON, "w", encoding="utf-8", newline="") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"已更新 {n_updated} 个点，写回 {PATH_JSON}")
    else:
        print("无字段需要更新（或逆地理编码未启用/全部命中）")

    # ---- 阶段 2：按 county 拉取边界写 county.json ----
    counties = []
    seen = set()
    for it in plan:
        c = it.get("county", "")
        if c and c not in seen:
            seen.add(c)
            counties.append(c)

    old = _load_old_areas()  # 现有 county.json（含已下载的边界）

    county_areas = {}
    stats = []
    for c in counties:
        ad = COUNTY_ADCODE.get(c)
        if not ad:
            stats.append((c, "NO ADCODE", 0, 0))
            if c in old:
                county_areas[c] = old[c]
                stats[-1] = (c, "NO ADCODE", "FALLBACK", 0)
            continue
        # 关键：county.json 已有该县边界则跳过下载，直接复用
        if c in old and old[c].get("boundaries"):
            county_areas[c] = old[c]
            stats.append((c, ad, "CACHED", len(old[c]["boundaries"][0])))
            continue
        try:
            rings = fetch_boundaries(ad)
            if not rings:
                stats.append((c, ad, "EMPTY", 0))
                if c in old:
                    county_areas[c] = old[c]
                    stats[-1] = (c, ad, "EMPTY(FALLBACK)", 0)
                continue
            simp = [round_pts(simplify(r)) for r in rings]
            county_areas[c] = {"adcode": ad, "boundaries": simp}
            stats.append((c, ad, "OK", len(simp[0])))
        except Exception as e:
            stats.append((c, ad, "ERR " + str(e), 0))
            if c in old:
                county_areas[c] = old[c]
                stats[-1] = (c, ad, "ERR(FALLBACK)", 0)

    # 失败保护：若本次一个县都没有（既无缓存也未拉到），禁止用空数据覆盖旧文件
    if not county_areas:
        print("警告: 未能从 county.json 取到或拉到任何边界，已保留原文件，未写入。")
        return
    with io.open(COUNTY_JSON, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps({"county_areas": county_areas}, ensure_ascii=False, separators=(",", ":")))

    print("=== 阶段 2 结果: 行政边界写入 county.json ===")
    for c, ad, st, pts in stats:
        print(f"  {c:<8s} adcode={ad} {st} pts~{pts}")
    cached = sum(1 for _, _, st, _ in stats if st == "CACHED")
    ok = sum(1 for _, _, st, _ in stats if st == "OK")
    print(f"成功: {ok}/{len(counties)}（其中 {cached} 个直接复用 county.json，未联网下载）")
    size = os.path.getsize(COUNTY_JSON)
    print(f"已写入 {COUNTY_JSON}（{size:,} 字节）")


if __name__ == "__main__":
    main()
