#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拉取 path.json 中所有 county 的行政边界（阿里 DataV GeoAtlas，免 key），覆盖写 county.json。

用法：
    python fetch_county.py

- 自动读取 path.json 的 plan 列表，去重出 county（保持出现顺序）
- 按 adcode 从 https://geo.datav.aliyun.com/areas_v3/bound/{adcode}.json 拉 GeoJSON
- 抽稀到 ≤1000 点/环、坐标保留 5 位小数，写入 county.json（紧凑格式，约 216KB）
"""
import io
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PATH_JSON = os.path.join(HERE, "path.json")
COUNTY_JSON = os.path.join(HERE, "county.json")
BASE = "https://geo.datav.aliyun.com/areas_v3/bound/{adcode}.json"

# county 名 -> adcode（高德行政区划代码，2026 实测）
COUNTY_ADCODE = {
    "科尔沁区": 150502, "洮北区": 220802, "加格达奇区": 232718, "呼玛县": 232721,
    "漠河市": 232701, "根河市": 150785, "额尔古纳市": 150784, "陈巴尔虎旗": 150725,
    "海拉尔区": 150702, "满洲里市": 150781, "新巴尔虎右旗": 150727, "建华区": 230203,
    "铁锋区": 230204, "南岗区": 230103, "松北区": 230109,
}


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
    url = BASE.format(adcode=adcode)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8"))
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


def main():
    data = json.load(open(PATH_JSON, encoding="utf-8"))
    # 保持 plan 中 county 出现顺序去重
    counties = []
    seen = set()
    for it in data.get("plan", []):
        c = it.get("county", "")
        if c and c not in seen:
            seen.add(c)
            counties.append(c)

    county_areas = {}
    stats = []
    for c in counties:
        ad = COUNTY_ADCODE.get(c)
        if not ad:
            stats.append((c, "NO ADCODE", 0, 0))
            continue
        try:
            rings = fetch_boundaries(ad)
            if not rings:
                stats.append((c, ad, "EMPTY", 0))
                continue
            simp = [round_pts(simplify(r)) for r in rings]
            county_areas[c] = {"adcode": ad, "boundaries": simp}
            stats.append((c, ad, "OK", len(simp[0])))
        except Exception as e:
            stats.append((c, ad, "ERR " + str(e), 0))

    with io.open(COUNTY_JSON, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps({"county_areas": county_areas}, ensure_ascii=False, separators=(",", ":")))

    print("=== 拉取结果 ===")
    for c, ad, st, pts in stats:
        print(f"  {c:<8s} adcode={ad} {st} pts~{pts}")
    ok = sum(1 for _, _, st, _ in stats if st == "OK")
    print(f"成功: {ok}/{len(counties)}")
    size = os.path.getsize(COUNTY_JSON)
    print(f"已写入 {COUNTY_JSON}（{size:,} 字节）")


if __name__ == "__main__":
    main()
