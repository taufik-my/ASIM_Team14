"""
Flowchart: Relation and Data Exchange between MESA and NetworkX Models
======================================================================
Run:  python mesa_networkx_flowchart.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(14, 22))
ax.set_xlim(0, 14)
ax.set_ylim(0, 22)
ax.axis("off")
fig.patch.set_facecolor("white")

# ── palette ─────────────────────────────────────────────────────────
C_INPUT    = "#D6EAF8"
C_MESA     = "#FDEBD0"
C_NX       = "#D5F5E3"
C_EXCHANGE = "#E8DAEF"
C_OUTPUT   = "#FADBD8"
C_BORDER   = "#566573"
FONT       = "DejaVu Sans"

# ── layout constants ────────────────────────────────────────────────
CX     = 7.0
COL_L  = 3.5
COL_R  = 10.5
BW     = 5.0
BW_W   = 9.0

# ── helpers ─────────────────────────────────────────────────────────
def rbox(cx, y, w, h, text, color, fs=8.5, bold=False, bc=C_BORDER):
    x = cx - w / 2
    ax.add_patch(FancyBboxPatch((x + 0.04, y - 0.04), w, h,
                 boxstyle="round,pad=0.15", fc="#00000006", ec="none"))
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.15", fc=color, ec=bc, lw=1.0))
    wt = "bold" if bold else "normal"
    ax.text(cx, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontfamily=FONT, fontweight=wt, color="#1a1a1a", linespacing=1.4)
    return cx, y, y + h

def varrow(cx, y_from, y_to, label="", side="right"):
    ax.annotate("", xy=(cx, y_to), xytext=(cx, y_from),
                arrowprops=dict(arrowstyle="-|>", color="#2C3E50", lw=1.2,
                                mutation_scale=11))
    if label:
        off = 0.12 if side == "right" else -0.12
        ha = "left" if side == "right" else "right"
        ax.text(cx + off, (y_from + y_to) / 2, label, fontsize=6.5,
                color="#666", fontfamily=FONT, fontstyle="italic",
                va="center", ha=ha)

def harrow(x_from, x_to, y, label=""):
    ax.annotate("", xy=(x_to, y), xytext=(x_from, y),
                arrowprops=dict(arrowstyle="-|>", color="#2C3E50", lw=1.2,
                                mutation_scale=11))
    if label:
        ax.text((x_from + x_to) / 2, y + 0.13, label, fontsize=6.5,
                color="#666", fontfamily=FONT, fontstyle="italic",
                ha="center", va="bottom")

def diag_arrow(x1, y1, x2, y2, label="", lo=(0.2, 0)):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#2C3E50", lw=1.2,
                                mutation_scale=11))
    if label:
        ax.text((x1 + x2) / 2 + lo[0], (y1 + y2) / 2 + lo[1], label,
                fontsize=6.5, color="#666", fontfamily=FONT,
                fontstyle="italic", va="center")

def phase_dot(y, num, label, color="#34495E"):
    x = 0.45
    ax.add_patch(plt.Circle((x, y), 0.2, fc=color, ec="white",
                 lw=1.5, zorder=5))
    ax.text(x, y, str(num), ha="center", va="center", fontsize=7.5,
            fontfamily=FONT, fontweight="bold", color="white", zorder=6)
    ax.text(x + 0.35, y, label, ha="left", va="center", fontsize=8.5,
            fontfamily=FONT, fontweight="bold", color=color)

def zone(x, y, w, h, color, label="", lc="#999"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2",
                 fc=color, ec="#ccc", lw=0.6, ls="--", alpha=0.45))
    if label:
        ax.text(x + 0.2, y + h - 0.2, label, fontsize=6,
                fontfamily=FONT, fontweight="bold", color=lc,
                fontstyle="italic", alpha=0.8)

# ====================================================================
#  TITLE
# ====================================================================
ax.text(CX, 21.55, "MESA - NetworkX Data Exchange", ha="center",
        va="center", fontsize=16, fontfamily=FONT, fontweight="bold",
        color="#1B2631")
ax.text(CX, 21.2, "Bangladesh Road Transport Simulation (EPA133a - Group 14)",
        ha="center", va="center", fontsize=9, fontfamily=FONT,
        color="#777", fontstyle="italic")
ax.plot([2.5, 11.5], [21.0, 21.0], color="#CCD1D1", lw=0.7)

# ====================================================================
#  1  DATA INPUT
# ====================================================================
phase_dot(20.85, 1, "Data Input", "#2471A3")

_, b_csv, t_csv = rbox(COL_L, 19.7, BW, 0.8,
    "network_data.csv\nroad | id | type | lat | lon | length | condition | lrp",
    C_INPUT, fs=7.5, bold=True, bc="#85C1E9")

_, b_par, t_par = rbox(COL_R, 19.7, BW, 0.8,
    "Scenario Parameters\nBreakdown probs per condition (A/B/C/D)",
    C_INPUT, fs=7.5, bold=True, bc="#85C1E9")

# ====================================================================
#  2  MODEL INIT
# ====================================================================
phase_dot(19.1, 2, "Model Init", "#7D3C98")

_, b_init, t_init = rbox(CX, 18.2, BW_W, 0.75,
    "BangladeshModel.__init__()\n"
    "Creates:  BaseScheduler  +  ContinuousSpace  +  nx.Graph G",
    C_EXCHANGE, fs=8, bold=True, bc="#AF7AC5")

diag_arrow(COL_L, b_csv, CX - 1.5, t_init, "CSV", lo=(-0.5, 0))
diag_arrow(COL_R, b_par, CX + 1.5, t_init, "config", lo=(0.5, 0))

# ====================================================================
#  3  GENERATE MODEL
# ====================================================================
phase_dot(17.65, 3, "Generate Model", "#7D3C98")

_, b_gen, t_gen = rbox(CX, 16.8, 7.0, 0.6,
    "generate_model()  --  Parse CSV, create agents & build graph",
    C_EXCHANGE, fs=7.5, bold=True, bc="#AF7AC5")

varrow(CX, b_init, t_gen)

# ── domain zones ────────────────────────────────────────────────────
zone(0.6, 14.0, 6.0, 2.2, "#FFF5E6", "MESA Domain", "#E67E22")
zone(7.4, 14.0, 6.0, 2.2, "#EAF7ED", "NetworkX Domain", "#27AE60")

_, b_ag, t_ag = rbox(COL_L, 14.15, 5.2, 1.8,
    "Create Infrastructure Agents\n\n"
    "Source / Sink / SourceSink\n"
    "Bridge (+ breakdown prob)\n"
    "Link / Intersection\n\n"
    "Register with Scheduler & Space",
    C_MESA, fs=7, bc="#F0B27A")

_, b_gr, t_gr = rbox(COL_R, 14.15, 5.2, 1.8,
    "Build Weighted Graph G\n\n"
    "Nodes = component IDs\n"
    "Edges = consecutive components\n"
    "on same road (weight = length)\n\n"
    "Cross-road edges via shared IDs",
    C_NX, fs=7, bc="#82E0AA")

diag_arrow(CX - 1.5, b_gen, COL_L, t_ag, "agents", lo=(-0.5, 0))
diag_arrow(CX + 1.5, b_gen, COL_R, t_gr, "topology", lo=(0.5, 0))

# ====================================================================
#  4  SIMULATION LOOP
# ====================================================================
phase_dot(13.55, 4, "Simulation Loop (7,200 steps)", "#2C3E50")

zone(0.6, 3.9, 12.8, 9.2, "#F8F9F9", "", "#AAB7B8")

_, b_st, t_st = rbox(CX, 12.1, BW_W, 0.7,
    "model.step()  →  scheduler.step()",
    C_EXCHANGE, fs=8, bold=True, bc="#AF7AC5")

diag_arrow(COL_L, b_ag, CX - 1.5, t_st, "agents", lo=(-0.5, 0))
diag_arrow(COL_R, b_gr, CX + 1.5, t_st, "graph", lo=(0.5, 0))

# ── Source ──────────────────────────────────────────────────────────
_, b_src, t_src = rbox(COL_L, 10.5, BW, 0.8,
    "Source.step()  →  generate_truck()\n"
    "Create Vehicle, register with Scheduler",
    C_MESA, fs=7.5, bc="#F0B27A")

varrow(CX - 2.5, b_st, t_src)

# ── Routing (KEY EXCHANGE) ──────────────────────────────────────────
_, b_rt, t_rt = rbox(CX, 8.7, BW_W, 1.1,
    "get_route( source_id )\n\n"
    "Pick random sink  →  nx.shortest_path(G, source, sink, weight='weight')\n"
    "Return path as pandas Series  |  Cache in path_ids_dict",
    C_EXCHANGE, fs=7.5, bold=True, bc="#7D3C98")

varrow(COL_L, b_src, t_rt, "request route")

# badge
ax.add_patch(FancyBboxPatch((10.0, 8.95), 2.3, 0.5,
             boxstyle="round,pad=0.1", fc="#7D3C98", ec="white", lw=1.3))
ax.text(11.15, 9.2, "KEY EXCHANGE\nMESA ↔ NetworkX", ha="center",
        va="center", fontsize=5.5, fontfamily=FONT, fontweight="bold",
        color="white")

# ── Vehicle drive ───────────────────────────────────────────────────
_, b_dr, t_dr = rbox(COL_L, 6.8, BW, 1.1,
    "Vehicle.step()  →  drive()\n\n"
    "Advance 800 m/tick along path_ids\n"
    "Update location_index & position",
    C_MESA, fs=7.5, bc="#F0B27A")

varrow(COL_L, b_rt, t_dr, "path_ids")

# ── Bridge ──────────────────────────────────────────────────────────
_, b_br, t_br = rbox(COL_R, 6.8, BW, 1.1,
    "Bridge Interaction\n\n"
    "broken_down? → get_delay_time(length)\n"
    "state = WAIT | DRIVE\n"
    "track total_delay_caused per bridge",
    C_MESA, fs=7.5, bc="#F0B27A")

harrow(COL_L + BW / 2, COL_R - BW / 2, 7.35, "bridge?")

# ── Sink ────────────────────────────────────────────────────────────
_, b_sk, t_sk = rbox(CX, 4.3, BW_W, 1.3,
    "Reach Sink  →  model.record_trip(vehicle)\n\n"
    "Collect: vehicle_id | origin | destination | travel_time\n"
    "waiting_time | bridges_passed | path_length\n"
    "Remove vehicle from Scheduler",
    C_MESA, fs=7.5, bc="#F0B27A")

varrow(COL_L, b_dr, t_sk, "reach sink?")

# ── loop-back arrow ─────────────────────────────────────────────────
lx = 13.8
ax.plot([COL_R + BW / 2, lx], [t_br, t_br], color="#AAB7B8", lw=1.2)
ax.plot([lx, lx], [t_br, t_st], color="#AAB7B8", lw=1.2)
ax.annotate("", xy=(CX + BW_W / 2, t_st), xytext=(lx, t_st),
            arrowprops=dict(arrowstyle="-|>", color="#AAB7B8", lw=1.2,
                            mutation_scale=10))
ax.text(lx - 0.12, (t_br + t_st) / 2, "next tick", fontsize=6,
        color="#AAB7B8", fontfamily=FONT, fontstyle="italic",
        ha="right", va="center", rotation=90)

# ====================================================================
#  5  DATA OUTPUT
# ====================================================================
phase_dot(3.5, 5, "Data Output", "#C0392B")

_, b_ex, t_ex = rbox(COL_L, 2.5, BW, 0.7,
    "model.export_data() + model.get_bridge_data()\n"
    "trip_data & bridge_data → CSV",
    C_OUTPUT, fs=7.5, bold=True, bc="#EC7063")

varrow(CX, b_sk, t_ex)

_, b_co, t_co = rbox(COL_L, 1.2, BW, 0.7,
    "experiment/scenario N.csv\n"
    "experiment/scenario N bridges.csv",
    C_OUTPUT, fs=7.5, bold=True, bc="#EC7063")

varrow(COL_L, b_ex, t_co)

_, b_an, t_an = rbox(COL_R, 1.2, BW, 0.7,
    "experiment_analysis.ipynb\n"
    "Compare scenarios & visualise",
    C_OUTPUT, fs=7.5, bc="#EC7063")

harrow(COL_L + BW / 2, COL_R - BW / 2, 1.55, "read CSVs")

# ====================================================================
#  LEGEND
# ====================================================================
ly = 0.3
ax.add_patch(FancyBboxPatch((0.5, ly - 0.05), 13.0, 0.45,
             boxstyle="round,pad=0.08", fc="white", ec="#ddd", lw=0.5))

items = [
    (C_INPUT, "#85C1E9", "Data Input"),
    (C_MESA,  "#F0B27A", "MESA"),
    (C_NX,    "#82E0AA", "NetworkX"),
    (C_EXCHANGE, "#AF7AC5", "Exchange"),
    (C_OUTPUT, "#EC7063", "Output"),
]
for i, (fc, ec, lb) in enumerate(items):
    xp = 1.0 + i * 2.5
    ax.add_patch(FancyBboxPatch((xp, ly + 0.05), 0.3, 0.25,
                 boxstyle="round,pad=0.04", fc=fc, ec=ec, lw=0.9))
    ax.text(xp + 0.45, ly + 0.17, lb, fontsize=6.5, fontfamily=FONT,
            va="center", color="#444")
plt.savefig("../img/mesa_networkx_flowchart.png", dpi=250, bbox_inches="tight",
            facecolor="white", pad_inches=0.2)
plt.savefig("../img/mesa_networkx_flowchart.pdf", bbox_inches="tight",
            facecolor="white", pad_inches=0.2)
print("Saved: img/mesa_networkx_flowchart.png & .pdf")
