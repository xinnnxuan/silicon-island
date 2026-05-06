from __future__ import annotations

import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from plotly_style import BLUE, FABRIC_YELLOW, PAGE_BG, RED, TEXT

# ── Journey nodes ─────────────────────────────────────────────────────────────
_NODES = [
    # Stage 0 – Quartz origins
    {"id": "n_qz1", "name": "Quartz Mine",     "sub": "Appalachians, USA",       "lat":  35.5, "lon": -82.5, "color": "#06ffd4", "r": 4,  "iso3": None},
    {"id": "n_qz2", "name": "Quartz Mine",     "sub": "Minas Gerais, Brazil",    "lat": -18.5, "lon": -44.5, "color": "#06ffd4", "r": 4,  "iso3": None},
    # Stage 1 – Polysilicon refineries
    {"id": "n_ref", "name": "Polysilicon Ref.", "sub": "Germany / USA",           "lat":  49.0, "lon":  11.0, "color": "#4ade80", "r": 6,  "iso3": None},
    # Stage 2 – Silicon wafers + chemicals
    {"id": "n_si",  "name": "Silicon Wafers",  "sub": "Shin-Etsu / Sumco, Japan","lat":  35.3, "lon": 138.5, "color": "#38bdf8", "r": 6,  "iso3": None},
    {"id": "n_che", "name": "Photoresists",    "sub": "JSR / Fujifilm, Japan",   "lat":  35.7, "lon": 136.0, "color": "#38bdf8", "r": 5,  "iso3": None},
    # Stage 3 – Equipment
    {"id": "n4",    "name": "ASML",            "sub": "Netherlands",             "lat":  51.4, "lon":   5.5, "color": "#a855f7", "r": 8,  "iso3": None},
    {"id": "n5",    "name": "Appl. Materials", "sub": "Santa Clara, USA",        "lat":  37.4, "lon":-122.0, "color": "#a855f7", "r": 5,  "iso3": None},
    {"id": "n6",    "name": "Tokyo Electron",  "sub": "Japan",                   "lat":  35.7, "lon": 139.5, "color": "#a855f7", "r": 5,  "iso3": None},
    # Stage 4 – Chip design
    {"id": "n7",    "name": "Apple / NVIDIA",  "sub": "Silicon Valley, USA",     "lat":  37.3, "lon":-121.9, "color": "#f472b6", "r": 5,  "iso3": None},
    {"id": "n8",    "name": "ARM Holdings",    "sub": "Cambridge, UK",           "lat":  52.2, "lon":   0.1, "color": "#f472b6", "r": 5,  "iso3": None},
    # Stage 5 – Fabrication
    {"id": "n9",    "name": "TSMC",            "sub": "Taiwan",                  "lat":  24.0, "lon": 121.5, "color": "#f97316", "r": 11, "iso3": "TWN"},
    {"id": "n10",   "name": "Samsung",         "sub": "South Korea",             "lat":  37.2, "lon": 127.1, "color": "#f97316", "r": 6,  "iso3": "KOR"},
    # Stage 6 – Assembly & markets
    {"id": "n11",   "name": "Assembly",        "sub": "SE Asia",                 "lat":   4.0, "lon": 110.0, "color": "#fde047", "r": 6,  "iso3": "_SEA"},
    {"id": "n12",   "name": "Assembly",        "sub": "China",                   "lat":  31.2, "lon": 121.5, "color": "#fde047", "r": 5,  "iso3": "CHN"},
    {"id": "n13",   "name": "USA",             "sub": "",                        "lat":  39.5, "lon": -98.4, "color": "#34d399", "r": 6,  "iso3": "USA"},
    {"id": "n14",   "name": "China",           "sub": "",                        "lat":  33.9, "lon": 108.9, "color": "#34d399", "r": 6,  "iso3": "CHN"},
    {"id": "n15",   "name": "Europe",          "sub": "",                        "lat":  50.1, "lon":  14.4, "color": "#34d399", "r": 6,  "iso3": "_EUR"},
    {"id": "n16",   "name": "Japan / Korea",   "sub": "",                        "lat":  36.5, "lon": 132.0, "color": "#34d399", "r": 5,  "iso3": "_JPNKOR"},
]

# ── Routes ────────────────────────────────────────────────────────────────────
_ROUTES = [
    # Stage 0 – Quartz → Refinery
    {"from": "n_qz1", "to": "n_ref", "color": "#06ffd4", "label": "Quartz → Refinery",       "speed": 5000},
    {"from": "n_qz2", "to": "n_ref", "color": "#06ffd4", "label": "Quartz → Refinery",       "speed": 5400},
    # Stage 1 – Refinery → Silicon
    {"from": "n_ref", "to": "n_si",  "color": "#4ade80", "label": "Polysilicon → Wafers",    "speed": 4600},
    # Stage 2 – Silicon + chemicals → TSMC
    {"from": "n_si",  "to": "n9",    "color": "#38bdf8", "label": "Silicon wafers → Taiwan", "speed": 4200},
    {"from": "n_che", "to": "n9",    "color": "#38bdf8", "label": "Photoresists → Taiwan",   "speed": 3900},
    # Stage 3 – Equipment → fabs
    {"from": "n4",    "to": "n9",    "color": "#a855f7", "label": "ASML → TSMC",             "speed": 5500},
    {"from": "n4",    "to": "n10",   "color": "#a855f7", "label": "ASML → Samsung",          "speed": 5200},
    {"from": "n5",    "to": "n9",    "color": "#a855f7", "label": "Equipment → TSMC",        "speed": 4500},
    {"from": "n6",    "to": "n9",    "color": "#a855f7", "label": "TEL → TSMC",              "speed": 3600},
    # Stage 4 – Design → TSMC
    {"from": "n8",    "to": "n7",    "color": "#f472b6", "label": "ARM IP → Designers",      "speed": 3000},
    {"from": "n7",    "to": "n9",    "color": "#f472b6", "label": "Designs → TSMC",          "speed": 3200},
    # Stage 5 – Fabricated wafers → assembly
    {"from": "n9",    "to": "n11",   "color": "#f97316", "label": "Wafers → SE Asia",        "speed": 3400},
    {"from": "n9",    "to": "n12",   "color": "#f97316", "label": "Wafers → China OSAT",     "speed": 2800},
    {"from": "n10",   "to": "n11",   "color": "#f97316", "label": "Samsung → OSAT",          "speed": 3600},
    # Stage 6 – Chips → markets
    {"from": "n11",   "to": "n13",   "color": "#fde047", "label": "Chips → USA",             "speed": 4800},
    {"from": "n11",   "to": "n14",   "color": "#fde047", "label": "Chips → China",           "speed": 2600},
    {"from": "n11",   "to": "n15",   "color": "#fde047", "label": "Chips → Europe",          "speed": 5200},
    {"from": "n11",   "to": "n16",   "color": "#fde047", "label": "Chips → Japan/Korea",     "speed": 3000},
    {"from": "n12",   "to": "n13",   "color": "#fde047", "label": "Chips → USA",             "speed": 4600},
    {"from": "n12",   "to": "n14",   "color": "#fde047", "label": "Chips → China market",    "speed": 2400},
]

_LEGEND = [
    {"color": "#06ffd4", "label": "Quartz"},
    {"color": "#4ade80", "label": "Refinery"},
    {"color": "#38bdf8", "label": "Silicon"},
    {"color": "#a855f7", "label": "Equipment"},
    {"color": "#f472b6", "label": "Design"},
    {"color": "#f97316", "label": "Fabrication"},
    {"color": "#fde047", "label": "Distribution"},
]

_SEA_ISOS    = ["SGP", "MYS", "THA", "VNM", "IDN", "PHL"]
_EUR_ISOS    = ["DEU", "NLD", "GBR", "FRA", "ITA", "ESP", "BEL", "CHE", "SWE", "POL", "CZE", "AUT", "PRT", "GRC", "DNK", "NOR", "FIN", "IRL"]
_JPNKOR_ISOS = ["JPN", "KOR"]


def _build_exports_json(destinations: pd.DataFrame) -> str:
    if destinations.empty:
        return "{}"
    latest_year = int(destinations["Year"].max())
    df = destinations[destinations["Year"] == latest_year]
    result: dict = {}
    for _, row in df.iterrows():
        cid = str(row.get("Country ID", "")).strip().upper()
        if not cid:
            continue
        result[cid] = {
            "country": str(row.get("Country", cid)),
            "exports": float(row.get("Exports (USD)", 0) or 0),
            "share":   float(row.get("Share (%)", 0) or 0),
            "year":    latest_year,
        }

    def _agg(isos: list[str], label: str, key: str) -> None:
        exp   = sum(result.get(i, {}).get("exports", 0) for i in isos)
        share = sum(result.get(i, {}).get("share",   0) for i in isos)
        if exp > 0:
            result[key] = {"country": label, "exports": exp, "share": share, "year": latest_year}

    _agg(_SEA_ISOS,    "SE Asia (aggregate)",       "_SEA")
    _agg(_EUR_ISOS,    "Europe (aggregate)",         "_EUR")
    _agg(_JPNKOR_ISOS, "Japan & Korea (aggregate)", "_JPNKOR")
    return json.dumps(result)


def _flight_map_html(exports_js: str) -> str:
    nodes_js  = json.dumps(_NODES)
    routes_js = json.dumps(_ROUTES)
    legend_js = json.dumps(_LEGEND)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:100%; height:100%; background:#ffffff; overflow:hidden;
    display:flex; flex-direction:column; }}
  #map-area {{ position:relative; flex:1 1 0; min-height:0; overflow:hidden; }}
  svg {{ display:block; width:100%; height:100%; cursor:grab; }}
  svg:active {{ cursor:grabbing; }}
  #desc-bar {{
    flex:0 0 auto;
    background:#f8fafc; border-top:1px solid #e2e8f0;
    padding:10px 24px 12px; overflow-y:auto;
  }}
  .desc-row {{
    display:flex; align-items:baseline; gap:8px;
    padding:5px 0; border-bottom:1px solid #e9ecf0;
    font-family:-apple-system,BlinkMacSystemFont,sans-serif;
  }}
  .desc-row:last-child {{ border-bottom:none; }}
  .desc-row-dot {{
    width:9px; height:9px; border-radius:50%; flex-shrink:0;
    margin-top:3px; align-self:flex-start;
  }}
  .desc-row-name {{
    font-size:11px; font-weight:700; color:#1e293b;
    white-space:nowrap; flex-shrink:0;
  }}
  .desc-row-text {{
    font:italic 11px/1.5 -apple-system,BlinkMacSystemFont,sans-serif;
    color:#475569;
  }}
  #zoom-controls {{
    position:absolute; top:10px; right:10px;
    display:flex; flex-direction:column; gap:3px;
  }}
  #zoom-controls button {{
    width:26px; height:26px; border-radius:5px;
    background:white; border:1px solid rgba(0,0,0,0.12);
    color:#334155; font-size:14px; cursor:pointer;
    display:flex; align-items:center; justify-content:center;
    box-shadow:0 1px 3px rgba(0,0,0,0.08);
  }}
  #zoom-controls button:hover {{ background:#f1f5f9; }}
  #stagebar {{
    position:absolute; bottom:10px; left:50%; transform:translateX(-50%);
    display:flex; align-items:center; gap:14px;
    background:white; padding:8px 18px; border-radius:24px;
    border:1px solid rgba(0,0,0,0.09); white-space:nowrap; z-index:10;
    box-shadow:0 2px 8px rgba(0,0,0,0.08);
    font-family:-apple-system,BlinkMacSystemFont,sans-serif;
  }}
  .sc-item {{
    display:flex; align-items:center; gap:5px; cursor:pointer;
    transition:opacity 0.2s;
  }}
  .sc-dot {{
    width:8px; height:8px; border-radius:50%; flex-shrink:0;
  }}
  .sc-cb {{
    width:13px; height:13px; cursor:pointer; flex-shrink:0;
    border-radius:3px;
  }}
  .sc-label {{
    font-size:11px; font-weight:600; color:#334155;
    user-select:none; cursor:pointer;
  }}
  #tooltip {{
    position:absolute; background:white; border:1px solid rgba(0,0,0,0.10);
    color:#1e293b; padding:7px 11px; border-radius:8px; font-size:11px;
    font-family:-apple-system,BlinkMacSystemFont,sans-serif;
    pointer-events:none; display:none; z-index:20; line-height:1.7;
    box-shadow:0 2px 8px rgba(0,0,0,0.10); max-width:230px;
  }}
</style>
</head>
<body>
<div id="map-area">
  <svg id="map"></svg>
  <div id="zoom-controls">
    <button id="btn-in"    title="Zoom in">+</button>
    <button id="btn-out"   title="Zoom out">−</button>
    <button id="btn-reset" title="Reset view" style="font-size:10px;">⊙</button>
  </div>
  <div id="stagebar"></div>
  <div id="tooltip"></div>
</div>
<div id="desc-bar"></div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson@3/dist/topojson.min.js"></script>
<script>
const NODES   = {nodes_js};
const ROUTES  = {routes_js};
const LEGEND  = {legend_js};
const EXPORTS = {exports_js};

const mapArea = document.getElementById("map-area");
const W = mapArea.clientWidth || window.innerWidth;
const H = mapArea.clientHeight || (window.innerHeight - 72);
const svg = d3.select("#map").attr("viewBox", `0 0 ${{W}} ${{H}}`);
svg.append("rect").attr("width",W).attr("height",H).attr("fill","#ffffff");

// ── Flat Natural Earth projection — drag shifts the central meridian (wraps) ──
let baseScale = Math.min(W / 4.0, (H - 110) / 2.2);
const projection = d3.geoNaturalEarth1()
    .scale(baseScale)
    .translate([W / 2, H / 2])
    .rotate([-20, 0, 0]);  // centre on Atlantic so quartz mines are visible first
const geoPath = d3.geoPath().projection(projection);
const nodeById = {{}};
NODES.forEach(n => {{ nodeById[n.id] = n; }});

// ── Journey stages ────────────────────────────────────────────────────────────
const STAGES = [
    {{
        name:  "Quartz",
        color: "#06ffd4",
        desc:  "It starts as quartz. Mines in the Appalachians and Brazil ship raw material to refineries — before a chip exists, it is already crossing borders.",
    }},
    {{
        name:  "Refinery",
        color: "#4ade80",
        desc:  "Moves through refineries. Wacker in Germany and Hemlock in the USA purify quartz into polysilicon at 1,400°C — one impurity per billion atoms is still too many.",
    }},
    {{
        name:  "Silicon",
        color: "#38bdf8",
        desc:  "Becomes silicon. Shin-Etsu and Sumco in Japan slice crystals into wafers thinner than a human hair. Photoresists add the chemistry that makes lithography possible.",
    }},
    {{
        name:  "Equipment",
        color: "#a855f7",
        desc:  "Crosses borders again. ASML ships EUV machines that cost $150M each from the Netherlands — without them, advanced chips cannot be made anywhere on Earth.",
    }},
    {{
        name:  "Design",
        color: "#f472b6",
        desc:  "Blueprints from Apple, NVIDIA, and ARM travel to Taiwan. The chip does not exist yet — it is still just mathematics.",
    }},
    {{
        name:  "Fabrication",
        color: "#f97316",
        desc:  "TSMC transforms silicon into intelligence. Hundreds of deposition, lithography, and etch steps. Months of precision. One mistake destroys the wafer.",
    }},
    {{
        name:  "Distribution",
        color: "#fde047",
        desc:  "Packaged chips leave for the USA, Europe, China, and Japan. Every iPhone. Every data center. Every AI model.",
    }},
];

const routeStage = ROUTES.map(r => {{
    if (r.color === "#06ffd4") return 0;
    if (r.color === "#4ade80") return 1;
    if (r.color === "#38bdf8") return 2;
    if (r.color === "#a855f7") return 3;
    if (r.color === "#f472b6") return 4;
    if (r.color === "#f97316") return 5;
    if (r.color === "#fde047") return 6;
    return -1;
}});

const activeStages = new Set(STAGES.map((_, i) => i));
let activeNodeIds = null;
let cursorStep = 0;
let arcSel = null;
let nodeEls = [];

// DOM refs (set once layers are built)
let countryPaths = null;

function recomputeActiveNodes() {{
    if (activeStages.size === 0) {{ activeNodeIds = null; return; }}
    activeNodeIds = new Set();
    ROUTES.forEach((r, i) => {{
        if (activeStages.has(routeStage[i])) {{
            activeNodeIds.add(r.from);
            activeNodeIds.add(r.to);
        }}
    }});
}}

function updateArcs() {{
    if (!arcSel) return;
    const all = activeStages.size === 0;
    arcSel
        .attr("stroke-opacity", d => all ? 0.60 : activeStages.has(d.stage) ? 1.0 : 0.06)
        .attr("stroke-width",   d => (!all && activeStages.has(d.stage)) ? 3.0 : 1.4);
}}

// ── Populate static stage descriptions ───────────────────────────────────────
(function() {{
    const bar = document.getElementById("desc-bar");
    STAGES.forEach(s => {{
        const row = document.createElement("div");
        row.className = "desc-row";
        const dot = document.createElement("span");
        dot.className = "desc-row-dot";
        dot.style.background = s.color;
        const name = document.createElement("span");
        name.className = "desc-row-name";
        name.textContent = s.name + ":";
        const text = document.createElement("span");
        text.className = "desc-row-text";
        text.textContent = s.desc;
        row.appendChild(dot); row.appendChild(name); row.appendChild(text);
        bar.appendChild(row);
    }});
}})();

function updateUI() {{
    const any = activeStages.size > 0;
    document.querySelectorAll(".sc-cb").forEach((cb, i) => {{
        cb.checked = activeStages.has(i);
    }});
    document.querySelectorAll(".sc-item").forEach((el, i) => {{
        el.style.opacity = (!any || activeStages.has(i)) ? "1" : "0.38";
    }});
}}

// ── Redraw: flat map, all countries always visible ────────────────────────────
function redraw() {{
    if (countryPaths) countryPaths.attr("d", geoPath);
    if (arcSel)       arcSel.attr("d", d => geoPath(d.feat) || "");

    nodeEls.forEach(({{ circle, label, nodeId }}) => {{
        const node = nodeById[nodeId];
        const pos  = projection([node.lon, node.lat]);
        if (!pos) return;
        const fade = (!activeNodeIds || activeNodeIds.has(nodeId)) ? 1 : 0.07;
        circle.attr("cx", pos[0]).attr("cy", pos[1]).attr("opacity", 0.9 * fade);
        label .attr("x",  pos[0]).attr("y", pos[1] - node.r - 4).attr("opacity", fade);
    }});
}}

function apply() {{
    recomputeActiveNodes(); updateArcs(); redraw(); updateUI();
}}

// ── Stage checkboxes ─────────────────────────────────────────────────────────
const stagebarEl = document.getElementById("stagebar");
STAGES.forEach((s, i) => {{
    const item = document.createElement("label");
    item.className = "sc-item";
    item.title = s.desc;

    const dot = document.createElement("span");
    dot.className = "sc-dot";
    dot.style.background = s.color;

    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.className = "sc-cb";
    cb.style.accentColor = s.color;
    cb.checked = activeStages.has(i);
    cb.addEventListener("change", () => {{
        if (cb.checked) {{ activeStages.add(i); }} else {{ activeStages.delete(i); }}
        apply();
    }});

    const lbl = document.createElement("span");
    lbl.className = "sc-label";
    lbl.textContent = s.name;

    item.appendChild(dot);
    item.appendChild(cb);
    item.appendChild(lbl);
    stagebarEl.appendChild(item);
}});
updateUI();

// ── Vertical clamp: keep map edges inside viewport when zoomed in ─────────────
function clampCy(newCy) {{
    // pixel distance from projection centre to the north pole at current scale
    const halfMapH = Math.abs(projection([0, 90])[1] - projection.translate()[1]);
    if (halfMapH <= H / 2) return H / 2;          // map fits — lock to centre
    return Math.max(H - halfMapH, Math.min(halfMapH, newCy));
}}

// ── Drag: horizontal wrapping + vertical pan with clamped bounds ──────────────
let dragOrigin = null;
svg.call(d3.drag()
    .on("start", event => {{
        dragOrigin = {{
            x: event.x, y: event.y,
            lon: projection.rotate()[0],
            cy:  projection.translate()[1],
        }};
        svg.style("cursor", "grabbing");
    }})
    .on("drag", event => {{
        if (!dragOrigin) return;
        const sens = 360 / (projection.scale() * 2 * Math.PI);
        const lon  = dragOrigin.lon + (event.x - dragOrigin.x) * sens;
        projection.rotate([lon, 0, 0]);
        const cy = clampCy(dragOrigin.cy + (event.y - dragOrigin.y));
        projection.translate([W / 2, cy]);
        redraw();
    }})
    .on("end", () => svg.style("cursor", "grab"))
);

// ── Zoom ──────────────────────────────────────────────────────────────────────
const minScale = Math.min(W / 4.0, (H - 110) / 2.2);
function doZoom(f) {{
    const prevCy = projection.translate()[1];
    baseScale = Math.max(minScale, Math.min(baseScale * f, H * 1.8));
    projection.scale(baseScale);
    projection.translate([W / 2, clampCy(prevCy)]);
    redraw();
}}
svg.on("wheel.zoom", e => {{ e.preventDefault(); doZoom(e.deltaY < 0 ? 1.15 : 0.87); }});
document.getElementById("btn-in")   .addEventListener("click", () => doZoom(1.5));
document.getElementById("btn-out")  .addEventListener("click", () => doZoom(0.67));
document.getElementById("btn-reset").addEventListener("click", () => {{
    baseScale = Math.min(W / 4.0, (H - 110) / 2.2);
    projection.scale(baseScale).translate([W / 2, H / 2]).rotate([-20, 0, 0]);
    activeStages.clear(); STAGES.forEach((_, i) => activeStages.add(i)); cursorStep = 0; apply();
}});

// ── Load world ────────────────────────────────────────────────────────────────
d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json").then(world => {{
    const countries = topojson.feature(world, world.objects.countries);

    // Ocean background
    svg.insert("path", ":first-child").datum({{type:"Sphere"}})
        .attr("d", geoPath).attr("fill","#ffffff");

    countryPaths = svg.append("g")
        .selectAll("path").data(countries.features).join("path")
        .attr("fill","#1e293b")
        .attr("stroke","#0f172a")
        .attr("stroke-width", 0.5);


    // Arcs
    const arcData = ROUTES.map((r, i) => {{
        const fn = nodeById[r.from], tn = nodeById[r.to];
        return {{
            feat:  {{ type:"Feature", geometry:{{ type:"LineString",
                       coordinates:[[fn.lon,fn.lat],[tn.lon,tn.lat]] }} }},
            color: r.color,
            stage: routeStage[i],
        }};
    }});
    arcSel = svg.append("g").selectAll("path").data(arcData).join("path")
        .attr("fill","none")
        .attr("stroke", d => d.color)
        .attr("stroke-width", 1.4)
        .attr("stroke-opacity", 0.60)
        .attr("stroke-linecap","round");

    // Nodes
    const tooltip   = d3.select("#tooltip");
    const nodeLayer = svg.append("g");
    NODES.forEach(node => {{
        const pos0 = projection([node.lon, node.lat]);
        const x0   = pos0 ? pos0[0] : -9999, y0 = pos0 ? pos0[1] : -9999;
        const isKey = node.id === "n9" || node.id === "n4";

        const circle = nodeLayer.append("circle")
            .attr("cx", x0).attr("cy", y0).attr("r", node.r)
            .attr("fill", node.color)
            .attr("opacity", pos0 ? 0.9 : 0)
            .attr("stroke","white").attr("stroke-width",1.5)
            .style("cursor","pointer")
            .on("mouseover", () => {{
                const exp = node.iso3 && EXPORTS[node.iso3] ? EXPORTS[node.iso3] : null;
                let html  = `<strong>${{node.name}}</strong>`;
                if (node.sub) html += `<br/><span style="color:#64748b">${{node.sub}}</span>`;
                if (exp) {{
                    const bn = (exp.exports / 1e9).toFixed(1);
                    html += `<br/><span style="color:#0f172a;font-weight:600">Taiwan exports: $${{bn}}B</span>`;
                    html += `<br/><span style="color:#64748b">Share: ${{exp.share.toFixed(1)}}% · ${{exp.year}}</span>`;
                }} else if (node.id === "n9") {{
                    html += `<br/><span style="color:#94a3b8;font-size:10px">~90% of leading-edge capacity</span>`;
                }} else {{
                    html += `<br/><span style="color:#94a3b8;font-size:10px">Supply chain stage</span>`;
                }}
                tooltip.style("display","block").html(html);
            }})
            .on("mousemove", event => {{
                tooltip.style("left",(event.pageX+12)+"px").style("top",(event.pageY-28)+"px");
            }})
            .on("mouseout", () => tooltip.style("display","none"));

        const label = nodeLayer.append("text")
            .attr("x", x0).attr("y", y0 - node.r - 4)
            .attr("text-anchor","middle")
            .attr("fill", isKey ? "#0f172a" : "#64748b")
            .attr("font-size", isKey ? "10px" : "8px")
            .attr("font-weight", isKey ? "700" : "400")
            .attr("font-family","-apple-system,BlinkMacSystemFont,sans-serif")
            .attr("pointer-events","none")
            .attr("opacity", pos0 ? 1 : 0)
            .text(node.name);

        nodeEls.push({{ circle, label, nodeId: node.id }});
    }});

    // Animated packets (only on front hemisphere)
    const packetLayer = svg.append("g");
    ROUTES.forEach((route, ri) => {{
        const fn     = nodeById[route.from], tn = nodeById[route.to];
        const interp = d3.geoInterpolate([fn.lon,fn.lat],[tn.lon,tn.lat]);
        const nPkt   = (route.color === "#f97316" || route.color === "#fde047") ? 3 : 2;
        for (let p = 0; p < nPkt; p++) {{
            const phase = (p / nPkt) * route.speed + ri * 180;
            const dot   = packetLayer.append("circle")
                .attr("r",3).attr("fill",route.color).attr("opacity",0)
                .attr("stroke","white").attr("stroke-width",0.8)
                .attr("pointer-events","none");
            d3.timer(elapsed => {{
                const on = activeStages.size === 0 || activeStages.has(routeStage[ri]);
                if (!on) {{ dot.attr("opacity",0); return; }}
                const t   = ((elapsed + phase) % route.speed) / route.speed;
                const pos = projection(interp(t));
                if (!pos) {{ dot.attr("opacity",0); return; }}
                const alpha = t < 0.06 ? t / 0.06 : t > 0.91 ? (1-t) / 0.09 : 1;
                dot.attr("cx",pos[0]).attr("cy",pos[1]).attr("opacity", alpha * 0.9);
            }});
        }}
    }});

    // First full draw with stage 0 active
    apply();

}}).catch(() => {{
    svg.append("text").attr("x",W/2).attr("y",H/2)
        .attr("text-anchor","middle").attr("fill","#4ade80")
        .attr("font-family","-apple-system,sans-serif")
        .text("Map failed to load — check internet connection.");
}});


</script>
</body>
</html>"""


def render(destinations: pd.DataFrame) -> None:
    st.caption(
        "Every chip crosses a dozen borders before it exists. "
        "Drag to pan · scroll to zoom · check a stage to highlight its routes · hover a node for export data · ⊙ resets the view."
    )
    components.html(_flight_map_html(_build_exports_json(destinations)), height=860, scrolling=False)
    st.caption(
        "Sources: ASML IR, TSMC IR, Applied Materials IR, ITC Trade Map, SIA. "
        "Node positions are approximate — arc paths are illustrative great-circle routes."
    )


def _loop_iframe() -> None:
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <style>
    html, body {{ margin:0; padding:0; background:{PAGE_BG};
      font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue",Helvetica,Arial,sans-serif; }}
    .wrap {{ padding:0.35rem 1rem 0.85rem 1rem; max-width:1100px; margin:0 auto; box-sizing:border-box; }}
    .title {{ font-size:0.68rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
      color:#6b7280; margin:0 0 0.45rem 0; }}
    .row {{ display:flex; flex-wrap:wrap; align-items:center; justify-content:center; gap:0.3rem 0.45rem; }}
    .node {{
      padding:0.32rem 0.6rem; border-radius:999px; font-size:0.76rem; font-weight:600;
      border:2px solid #d1d5db; background:#ffffff; color:#6b7280; opacity:0.45;
    }}
    .arr {{ font-size:0.8rem; color:#9ca3af; font-weight:600; }}
    .repeat {{ font-size:0.7rem; font-weight:700; letter-spacing:0.06em;
      text-transform:uppercase; color:{FABRIC_YELLOW}; opacity:0.5; }}
    .n1 {{ animation: n1 6s ease-in-out infinite; }}
    .n2 {{ animation: n2 6s ease-in-out infinite; }}
    .n3 {{ animation: n3 6s ease-in-out infinite; }}
    .n4 {{ animation: n4 6s ease-in-out infinite; }}
    @keyframes n1 {{ 0%, 19% {{ opacity:1; border-color:{FABRIC_YELLOW}; color:{TEXT};
      box-shadow:0 0 0 2px rgba(180,83,9,0.15); }} 20%, 100% {{ opacity:0.45;
      border-color:#d1d5db; color:#6b7280; box-shadow:none; }} }}
    @keyframes n2 {{ 0%, 19% {{ opacity:0.45; }} 20%, 39% {{ opacity:1; border-color:{FABRIC_YELLOW};
      color:{TEXT}; box-shadow:0 0 0 2px rgba(180,83,9,0.15); }}
      40%, 100% {{ opacity:0.45; border-color:#d1d5db; color:#6b7280; box-shadow:none; }} }}
    @keyframes n3 {{ 0%, 39% {{ opacity:0.45; }} 40%, 59% {{ opacity:1; border-color:{FABRIC_YELLOW};
      color:{TEXT}; box-shadow:0 0 0 2px rgba(180,83,9,0.15); }}
      60%, 100% {{ opacity:0.45; border-color:#d1d5db; color:#6b7280; box-shadow:none; }} }}
    @keyframes n4 {{ 0%, 59% {{ opacity:0.45; }} 60%, 79% {{ opacity:1; border-color:{FABRIC_YELLOW};
      color:{TEXT}; box-shadow:0 0 0 2px rgba(180,83,9,0.15); }}
      80%, 100% {{ opacity:0.45; border-color:#d1d5db; color:#6b7280; box-shadow:none; }} }}
    .repeat-pulse {{ animation: rp 6s ease-in-out infinite; }}
    @keyframes rp {{ 0%, 79% {{ opacity:0.35; }} 80%, 95% {{ opacity:1; }} 100% {{ opacity:0.35; }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <p class="title">The fabrication loop (conceptual)</p>
    <div class="row">
      <span class="node n1">Deposit</span><span class="arr">→</span>
      <span class="node n2">Pattern</span><span class="arr">→</span>
      <span class="node n3">Etch</span><span class="arr">→</span>
      <span class="node n4">Modify</span><span class="arr">→</span>
      <span class="repeat repeat-pulse">Repeat ×100s</span>
    </div>
  </div>
</body>
</html>"""
    components.html(page, width=1400, height=130, scrolling=False)
