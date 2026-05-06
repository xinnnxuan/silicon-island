"""
D3.js choropleth for Taiwan export destinations.
Matches the supply chain map style: dark countries, white background,
Natural Earth projection, same zoom/drag/tooltip controls.
"""
from __future__ import annotations

import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ── ISO-3 (including Trade Map variants) → ISO 3166-1 numeric ─────────────────
_ISO3_TO_NUM: dict[str, int] = {
    # Standard ISO3
    "ABW": 533, "AFG": 4,   "AGO": 24,  "AIA": 660, "ALB": 8,
    "AND": 20,  "ARE": 784, "ARG": 32,  "ARM": 51,  "ASM": 16,
    "ATG": 28,  "AUS": 36,  "AUT": 40,  "AZE": 31,  "BDI": 108,
    "BEL": 56,  "BEN": 204, "BFA": 854, "BGD": 50,  "BGR": 100,
    "BHR": 48,  "BHS": 44,  "BHU": 64,  "BIH": 70,  "BLM": 652,
    "BLR": 112, "BLZ": 84,  "BMU": 60,  "BOL": 68,  "BRA": 76,
    "BRB": 52,  "BRN": 96,  "BTN": 64,  "BWA": 72,  "CAF": 140,
    "CAN": 124, "CCK": 166, "CHE": 756, "CHL": 152, "CHN": 156,
    "CIV": 384, "CMR": 120, "COD": 180, "COG": 178, "COK": 184,
    "COL": 170, "COM": 174, "CPV": 132, "CRI": 188, "CUB": 192,
    "CUW": 531, "CXR": 162, "CYM": 136, "CYP": 196, "CZE": 203,
    "DEU": 276, "DJI": 262, "DMA": 212, "DNK": 208, "DOM": 214,
    "DZA": 12,  "ECU": 218, "EGY": 818, "ERI": 232, "ESP": 724,
    "EST": 233, "ETH": 231, "FIN": 246, "FJI": 242, "FLK": 238,
    "FRA": 250, "FRO": 234, "FSM": 583, "GAB": 266, "GBR": 826,
    "GEO": 268, "GHA": 288, "GIB": 292, "GIN": 324, "GMB": 270,
    "GNB": 624, "GNQ": 226, "GRC": 300, "GRD": 308, "GRL": 304,
    "GTM": 320, "GUM": 316, "GUY": 328, "HKG": 344, "HND": 340,
    "HRV": 191, "HTI": 332, "HUN": 348, "IDN": 360, "IND": 356,
    "IRL": 372, "IRN": 364, "IRQ": 368, "ISL": 352, "ISR": 376,
    "ITA": 380, "JAM": 388, "JOR": 400, "JPN": 392, "KAZ": 398,
    "KEN": 404, "KGZ": 417, "KHM": 116, "KIR": 296, "KNA": 659,
    "KOR": 410, "KWT": 414, "LAO": 418, "LBN": 422, "LBR": 430,
    "LBY": 434, "LCA": 662, "LKA": 144, "LSO": 426, "LTU": 440,
    "LUX": 442, "LVA": 428, "MAC": 446, "MAR": 504, "MDA": 498,
    "MDG": 450, "MDV": 462, "MEX": 484, "MHL": 584, "MKD": 807,
    "MLI": 466, "MLT": 470, "MMR": 104, "MNE": 499, "MNG": 496,
    "MNP": 580, "MOZ": 508, "MRT": 478, "MSR": 500, "MUS": 480,
    "MWI": 454, "MYS": 458, "NAM": 516, "NCL": 540, "NER": 562,
    "NGA": 566, "NIC": 558, "NLD": 528, "NOR": 578, "NPL": 524,
    "NRU": 520, "NZL": 554, "OMN": 512, "PAK": 586, "PAN": 591,
    "PER": 604, "PHL": 608, "PLW": 585, "PNG": 598, "POL": 616,
    "PRT": 620, "PRY": 600, "PSE": 275, "PYF": 258, "QAT": 634,
    "ROU": 642, "RUS": 643, "RWA": 646, "SAU": 682, "SDN": 729,
    "SEN": 686, "SGP": 702, "SLB": 90,  "SLE": 694, "SLV": 222,
    "SMR": 674, "SOM": 706, "SRB": 688, "SSD": 728, "STP": 678,
    "SUR": 740, "SVK": 703, "SVN": 705, "SWE": 752, "SWZ": 748,
    "SYC": 690, "SYR": 760, "TCA": 796, "TCD": 148, "TGO": 768,
    "THA": 764, "TJK": 762, "TKM": 795, "TLS": 626, "TON": 776,
    "TTO": 780, "TUN": 788, "TUR": 792, "TUV": 798, "TZA": 834,
    "UGA": 800, "UKR": 804, "URY": 858, "USA": 840, "UZB": 860,
    "VCT": 670, "VEN": 862, "VGB": 92,  "VNM": 704, "VUT": 548,
    "WSM": 882, "YEM": 887, "ZAF": 710, "ZMB": 894, "ZWE": 716,
    "TWN": 158,
    # Trade Map variant codes
    "ALG": 12,  "ANG": 24,  "ANT": 28,  "ARU": 533, "BAH": 44,
    "BAN": 50,  "BAR": 52,  "BER": 60,  "BES": 535, "BON": 535,
    "BOS": 70,  "BOT": 72,  "BRI": 92,  "BRU": 96,  "BUL": 100,
    "BUR": 854, "CAB": 132, "CAM": 116, "CAY": 136, "CEN": 140,
    "CHA": 148, "CHI": 152, "CHR": 162, "COC": 166, "CON": 178,
    "COO": 184, "COS": 188, "CRO": 191, "CUR": 531, "CÔT": 384,
    "EQU": 226, "ESW": 748, "FAL": 238, "FAR": 234, "FIJ": 242,
    "FRE": 258, "GAM": 270, "GRE": 300, "GUA": 320, "GUI": 324,
    "HAI": 332, "HON": 340, "ICE": 352, "IRA": 364, "IRE": 372,
    "KUW": 414, "KYR": 417, "LAT": 428, "LEB": 422, "LES": 426,
    "LIB": 434, "LIT": 440, "MAD": 450, "MAF": 663, "MAL": 458,
    "MAU": 480, "MIC": 583, "MOL": 498, "MON": 492, "MOR": 504,
    "MYA": 104, "NAU": 520, "NEP": 524, "NET": 528, "NEW": 554,
    "NIG": 562, "NIU": 570, "OMA": 512, "PAL": 275, "PAP": 598,
    "PAR": 600, "POR": 620, "ROM": 642, "SAM": 882, "SAO": 678,
    "SER": 688, "SEY": 690, "SIE": 694, "SIN": 702, "SLO": 705,
    "SOL": 90,  "SOM": 706, "SOU": 710, "SRI": 144, "SUD": 729,
    "TAJ": 762, "TAN": 834, "TIM": 626, "TOG": 768, "TOK": 772,
    "TRI": 780, "TÜR": 792, "URU": 858, "VAN": 548, "WAL": 876,
    "WLF": 876, "ZAM": 894, "ZIM": 716,
    # Extra variants seen in data
    "GIB": 292, "ESW": 748, "EL ": 222, "MAL": 458, "NIG": 566,
    "UNI": 784,
}


def _build_dest_json(destinations: pd.DataFrame) -> str:
    """Return JSON: {year: {iso_numeric_str: {s:share, e:exports, n:name}}}."""
    out: dict = {}
    for year in sorted(destinations["Year"].unique()):
        yr_df = destinations[destinations["Year"] == year]
        yr_dict: dict = {}
        for _, row in yr_df.iterrows():
            iso3 = str(row.get("Country ID", "")).strip().upper()
            num = _ISO3_TO_NUM.get(iso3)
            if num is None:
                continue
            share = float(row.get("Share (%)", 0) or 0)
            exports = float(row.get("Exports (USD)", 0) or 0)
            if exports <= 0:
                continue
            yr_dict[str(num)] = {
                "s": round(share, 3),
                "e": int(exports),
                "n": str(row.get("Country", iso3)),
            }
        out[int(year)] = yr_dict
    return json.dumps(out)


def _choropleth_html(dest_json: str, height: int = 580) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:100%; height:{height}px; background:#ffffff; overflow:hidden;
    display:flex; flex-direction:column; }}
  #map-area {{ position:relative; flex:1 1 0; min-height:0; overflow:hidden; }}
  svg {{ display:block; width:100%; height:100%; cursor:grab; }}
  svg:active {{ cursor:grabbing; }}
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
  #yearbar {{
    position:absolute; bottom:10px; left:50%; transform:translateX(-50%);
    display:flex; align-items:center; gap:10px;
    background:white; padding:7px 18px; border-radius:24px;
    border:1px solid rgba(0,0,0,0.09); white-space:nowrap; z-index:10;
    box-shadow:0 2px 8px rgba(0,0,0,0.08);
    font-family:-apple-system,BlinkMacSystemFont,sans-serif;
  }}
  #yearbar button {{
    width:24px; height:24px; border-radius:50%;
    background:#1e293b; border:none; color:white;
    font-size:12px; cursor:pointer; display:flex;
    align-items:center; justify-content:center;
    flex-shrink:0;
  }}
  #yearbar button:hover {{ background:#334155; }}
  #year-label {{
    font-size:12px; font-weight:700; color:#1e293b;
    min-width:36px; text-align:center;
  }}
  #year-slider {{
    -webkit-appearance:none; appearance:none;
    width:140px; height:4px; border-radius:2px;
    background:#e2e8f0; outline:none; cursor:pointer;
  }}
  #year-slider::-webkit-slider-thumb {{
    -webkit-appearance:none; width:14px; height:14px;
    border-radius:50%; background:#ef4444; cursor:pointer;
    border:2px solid white; box-shadow:0 1px 3px rgba(0,0,0,0.2);
  }}
  #legend {{
    position:absolute; top:10px; left:10px;
    background:rgba(255,255,255,0.92); border:1px solid #e2e8f0;
    border-radius:8px; padding:8px 12px;
    font-family:-apple-system,BlinkMacSystemFont,sans-serif;
    font-size:10px; color:#475569;
    box-shadow:0 1px 4px rgba(0,0,0,0.08);
  }}
  #legend-title {{ font-weight:700; color:#1e293b; margin-bottom:5px; font-size:10px; }}
  #legend-bar {{ width:120px; height:8px; border-radius:3px; margin-bottom:3px;
    background:linear-gradient(to right, #2a3a5c, #7c2525, #ef4444, #fca5a5); }}
  #legend-labels {{ display:flex; justify-content:space-between; }}
  #tooltip {{
    position:absolute; background:white; border:1px solid rgba(0,0,0,0.10);
    color:#1e293b; padding:7px 11px; border-radius:8px; font-size:11px;
    font-family:-apple-system,BlinkMacSystemFont,sans-serif;
    pointer-events:none; display:none; z-index:20; line-height:1.7;
    box-shadow:0 2px 8px rgba(0,0,0,0.10); max-width:220px;
  }}
</style>
</head>
<body>
<div id="map-area">
  <svg id="map"></svg>
  <div id="zoom-controls">
    <button id="btn-in">+</button>
    <button id="btn-out">−</button>
    <button id="btn-reset" style="font-size:10px;">⊙</button>
  </div>
  <div id="legend">
    <div id="legend-title">Share of Taiwan's Exports</div>
    <div id="legend-bar"></div>
    <div id="legend-labels"><span>0%</span><span id="legend-max">5%+</span></div>
  </div>
  <div id="yearbar">
    <button id="btn-play" title="Play/Pause">▶</button>
    <span id="year-label">2006</span>
    <input type="range" id="year-slider" min="0" max="0" value="0" step="1"/>
  </div>
  <div id="tooltip"></div>
</div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson@3/dist/topojson.min.js"></script>
<script>
const ALL_DATA = {dest_json};

const mapArea = document.getElementById("map-area");
const W = mapArea.clientWidth  || window.innerWidth;
const H = mapArea.clientHeight || ({height} - 0);
const svg = d3.select("#map").attr("viewBox", `0 0 ${{W}} ${{H}}`);
svg.append("rect").attr("width",W).attr("height",H).attr("fill","#ffffff");

const projection = d3.geoNaturalEarth1().rotate([-20, 0, 0]);
projection.fitSize([W, H], {{type: "Sphere"}});
let baseScale = projection.scale();
const geoPath = d3.geoPath().projection(projection);

// ── Years ─────────────────────────────────────────────────────────────────────
const YEARS = Object.keys(ALL_DATA).map(Number).sort((a,b) => a-b);
let yearIdx = 0;
let playing = false;
let playTimer = null;

const slider   = document.getElementById("year-slider");
const yearLbl  = document.getElementById("year-label");
const btnPlay  = document.getElementById("btn-play");

slider.max   = YEARS.length - 1;
slider.value = yearIdx;

// ── Colour scale ──────────────────────────────────────────────────────────────
// Compute 98th-percentile share across all years for the colour domain
const allShares = Object.values(ALL_DATA).flatMap(yd => Object.values(yd).map(d => d.s));
allShares.sort((a,b) => a-b);
const maxShare = allShares[Math.floor(allShares.length * 0.98)] || 5;
document.getElementById("legend-max").textContent = maxShare.toFixed(1) + "%+";

const colorScale = d3.scaleSequential()
    .domain([0, maxShare])
    .interpolator(d3.interpolate("#2a3a5c", "#ef4444"))
    .clamp(true);

// ── Country paths (built after topojson loads) ────────────────────────────────
let countryPaths = null;

function getYearData() {{ return ALL_DATA[YEARS[yearIdx]] || {{}}; }}

function updateColors() {{
    if (!countryPaths) return;
    const yd = getYearData();
    countryPaths
        .attr("fill", d => {{
            const rec = yd[String(d.id)];
            return rec ? colorScale(rec.s) : "#1e293b";
        }})
        .attr("stroke", d => {{
            const rec = yd[String(d.id)];
            return rec ? "#0f172a" : "#0f172a";
        }});
}}

function setYear(idx) {{
    yearIdx = idx;
    slider.value = idx;
    yearLbl.textContent = YEARS[idx];
    updateColors();
}}

slider.addEventListener("input", () => setYear(+slider.value));

// ── Play / pause ──────────────────────────────────────────────────────────────
function startPlay() {{
    if (playing) return;
    playing = true;
    btnPlay.textContent = "⏸";
    playTimer = setInterval(() => {{
        const next = yearIdx + 1;
        if (next >= YEARS.length) {{ stopPlay(); return; }}
        setYear(next);
    }}, 800);
}}
function stopPlay() {{
    playing = false;
    btnPlay.textContent = "▶";
    clearInterval(playTimer);
    playTimer = null;
}}
btnPlay.addEventListener("click", () => playing ? stopPlay() : startPlay());

// ── Clamp vertical drag ───────────────────────────────────────────────────────
function clampCy(newCy) {{
    const halfMapH = Math.abs(projection([0, 90])[1] - projection.translate()[1]);
    if (halfMapH <= H / 2) return H / 2;
    return Math.max(H - halfMapH, Math.min(halfMapH, newCy));
}}

function redraw() {{
    if (countryPaths) countryPaths.attr("d", geoPath);
}}

// ── Drag ──────────────────────────────────────────────────────────────────────
let dragOrigin = null;
svg.call(d3.drag()
    .on("start", event => {{
        dragOrigin = {{ x: event.x, y: event.y,
            lon: projection.rotate()[0], cy: projection.translate()[1] }};
        svg.style("cursor","grabbing");
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
    .on("end", () => svg.style("cursor","grab"))
);

// ── Zoom ──────────────────────────────────────────────────────────────────────
const minScale = baseScale;  // never zoom out past the full-world fit
function doZoom(f) {{
    const prevCy = projection.translate()[1];
    baseScale = Math.max(minScale, Math.min(baseScale * f, H * 1.8));
    projection.scale(baseScale).translate([W / 2, clampCy(prevCy)]);
    redraw();
}}
svg.on("wheel.zoom", e => {{ e.preventDefault(); doZoom(e.deltaY < 0 ? 1.15 : 0.87); }});
document.getElementById("btn-in")   .addEventListener("click", () => doZoom(1.5));
document.getElementById("btn-out")  .addEventListener("click", () => doZoom(0.67));
document.getElementById("btn-reset").addEventListener("click", () => {{
    projection.fitSize([W, H], {{type:"Sphere"}}).rotate([-20, 0, 0]);
    baseScale = projection.scale();
    redraw();
}});

// ── Load world ────────────────────────────────────────────────────────────────
const tooltip = d3.select("#tooltip");

d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json").then(world => {{
    const countries = topojson.feature(world, world.objects.countries);

    svg.insert("path", ":first-child").datum({{type:"Sphere"}})
        .attr("d", geoPath).attr("fill","#ffffff");

    countryPaths = svg.append("g")
        .selectAll("path")
        .data(countries.features)
        .join("path")
        .attr("stroke","#0f172a")
        .attr("stroke-width", 0.4)
        .style("cursor","pointer")
        .on("mouseover", function(event, d) {{
            const rec = getYearData()[String(d.id)];
            if (!rec) return;
            const bn = rec.e >= 1e9
                ? "$" + (rec.e / 1e9).toFixed(1) + "B"
                : "$" + (rec.e / 1e6).toFixed(0) + "M";
            tooltip.style("display","block").html(
                `<strong>${{rec.n}}</strong><br/>
                 <span style="color:#64748b">Share: ${{rec.s.toFixed(2)}}%</span><br/>
                 <span style="color:#0f172a;font-weight:600">Exports: ${{bn}}</span><br/>
                 <span style="color:#94a3b8;font-size:10px">${{YEARS[yearIdx]}}</span>`
            );
            d3.select(this).attr("stroke-width", 1.5).attr("stroke","#f8fafc");
        }})
        .on("mousemove", event => {{
            tooltip.style("left",(event.pageX+12)+"px").style("top",(event.pageY-28)+"px");
        }})
        .on("mouseout", function() {{
            tooltip.style("display","none");
            d3.select(this).attr("stroke-width", 0.4).attr("stroke","#0f172a");
        }});

    updateColors();
    redraw();
    setTimeout(startPlay, 600);

}}).catch(() => {{
    svg.append("text").attr("x",W/2).attr("y",H/2)
        .attr("text-anchor","middle").attr("fill","#ef4444")
        .attr("font-family","-apple-system,sans-serif")
        .text("Map failed to load — check internet connection.");
}});
</script>
</body>
</html>"""


def render(destinations: pd.DataFrame, height: int = 580) -> None:
    dest_json = _build_dest_json(destinations)
    components.html(_choropleth_html(dest_json, height=height), height=height, scrolling=False)
