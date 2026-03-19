"""
Flowchart: Relation and Data Exchange between MESA and NetworkX Models
======================================================================
Run:  python mesa_networkx_flowchart.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(14, 28))
ax.set_xlim(0, 14)
ax.set_ylim(0, 28)
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
BW     = 5.0      # narrow box width
BW_W   = 9.0      # wide box width
GAP    = 0.5      # vertical gap between boxes

# ── helpers ─────────────────────────────────────────────────────────
def rbox(cx, y, w, h, text, color, fs=8.5, bold=False, bc=C_BORDER):
    x = cx - w / 2
    ax.add_patch(FancyBboxPatch((x + 0.04, y - 0.04), w, h,
                 boxstyle="round,pad=0.18", fc="#00000006", ec="none"))
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.18", fc=color, ec=bc, lw=1.0))
    wt = "bold" if bold else "normal"
    ax.text(cx, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontfamily=FONT, fontweight=wt, color="#1a1a1a", linespacing=1.45)
    return cx, y, y + h

def varrow(cx, y_from, y_to, label="", side="right"):
    ax.annotate("", xy=(cx, y_to), xytext=(cx, y_from),
                arrowprops=dict(arrowstyle="-|>", color="#2C3E50", lw=1.2,
                                mutation_scale=11))
    if label:
        off = 0.15 if side == "right" else -0.15
        ha = "left" if side == "right" else "right"
        ax.text(cx + off, (y_from + y_to) / 2, label, fontsize=6.5,
                color="#666", fontfamily=FONT, fontstyle="italic",
                va="center", ha=ha)

def harrow(x_from, x_to, y, label=""):
    ax.annotate("", xy=(x_to, y), xytext=(x_from, y),
                arrowprops=dict(arrowstyle="-|>", color="#2C3E50", lw=1.2,
                                mutation_scale=11))
    if label:
        ax.text((x_from + x_to) / 2, y + 0.18, label, fontsize=6.5,
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
    x = 0.5
    ax.add_patch(plt.Circle((x, y), 0.22, fc=color, ec="white",
                 lw=1.5, zorder=5))
    ax.text(x, y, str(num), ha="center", va="center", fontsize=8,
            fontfamily=FONT, fontweight="bold", color="white", zorder=6)
    ax.text(x + 0.38, y, label, ha="left", va="center", fontsize=9,
            fontfamily=FONT, fontweight="bold", color=color)

def zone(x, y, w, h, color, label="", lc="#999"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25",
                 fc=color, ec="#ccc", lw=0.6, ls="--", alpha=0.45))
    if label:
        ax.text(x + 0.25, y + h - 0.25, label, fontsize=6.5,
                fontfamily=FONT, fontweight="bold", color=lc,
                fontstyle="italic", alpha=0.8)

# ====================================================================
#  TITLE
# ====================================================================
ax.text(CX, 27.4, "MESA - NetworkX Data Exchange", ha="center",
        va="center", fontsize=17, fontfamily=FONT, fontweight="bold",
        color="#1B2631")
ax.text(CX, 27.0, "Bangladesh Road Transport Simulation (EPA133a - Group 14)",
        ha="center", va="center", fontsize=9.5, fontfamily=FONT,
        color="#777", fontstyle="italic")
ax.plot([2.5, 11.5], [26.7, 26.7], color="#CCD1D1", lw=0.7)

# ====================================================================
#  1  DATA INPUT
# ====================================================================
phase_dot(26.2, 1, "Data Input", "#2471A3")

_, b_csv, t_csv = rbox(COL_L, 24.7, BW, 0.9,
    "network_data.csv\nroad | id | type | lat | lon | length | condition | lrp",
    C_INPUT, fs=7.5, bold=True, bc="#85C1E9")

_, b_par, t_par = rbox(COL_R, 24.7, BW, 0.9,
    "Scenario Parameters\nBreakdown probs per condition (A/B/C/D)",
    C_INPUT, fs=7.5, bold=True, bc="#85C1E9")

# ====================================================================
#  2  MODEL INIT
# ====================================================================
phase_dot(23.8, 2, "Model Init", "#7D3C98")

_, b_init, t_init = rbox(CX, 22.7, BW_W, 0.9,
    "BangladeshModel.__init__()\n"
    "Creates:  BaseScheduler  +  ContinuousSpace  +  nx.Graph G",
    C_EXCHANGE, fs=8.5, bold=True, bc="#AF7AC5")

diag_arrow(COL_L, b_csv, CX - 1.5, t_init, "CSV", lo=(-0.5, 0))
diag_arrow(COL_R, b_par, CX + 1.5, t_init, "config", lo=(0.5, 0))

# ====================================================================
#  3  GENERATE MODEL
# ====================================================================
phase_dot(22.4, 3, "Generate Model", "#7D3C98")

_, b_gen, t_gen = rbox(CX, 21.4, 7.0, 0.8,
    "generate_model()  --  Parse CSV, create agents & build graph",
    C_EXCHANGE, fs=8, bold=True, bc="#AF7AC5")

varrow(CX, b_init, t_gen)

# ── domain zones ────────────────────────────────────────────────────
zone(0.6, 17.4, 6.0, 3.6, "#FFF5E6", "MESA Domain", "#E67E22")
zone(7.4, 17.4, 6.0, 3.6, "#EAF7ED", "NetworkX Domain", "#27AE60")

_, b_ag, t_ag = rbox(COL_L, 17.8, 5.2, 2.4,
    "Create Infrastructure Agents\n\n"
    "Source / Sink / SourceSink\n"
    "Bridge (+ breakdown prob)\n"
    "Link / Intersection\n\n"
    "Register with Scheduler & Space",
    C_MESA, fs=7.5, bc="#F0B27A")

_, b_gr, t_gr = rbox(COL_R, 17.8, 5.2, 2.4,
    "Build Weighted Graph G\n\n"
    "Nodes = component IDs\n"
    "Edges = consecutive components\n"
    "on same road (weight = length)\n\n"
    "Cross-road edges via shared LRP",
    C_NX, fs=7.5, bc="#82E0AA")

diag_arrow(CX - 1.5, b_gen, COL_L, t_ag, "agents", lo=(-0.6, 0))
diag_arrow(CX + 1.5, b_gen, COL_R, t_gr, "topology", lo=(0.5, 0))

# ====================================================================
#  4  SIMULATION LOOP
# ====================================================================
phase_dot(16.7, 4, "Simulation Loop (7,200 steps)", "#2C3E50")

zone(0.6, 4.0, 12.8, 12.3, "#F8F9F9", "", "#AAB7B8")

_, b_st, t_st = rbox(CX, 15.2, BW_W, 0.8,
    "model.step()  --  scheduler.step()  +  datacollector.collect()",
    C_EXCHANGE, fs=8.5, bold=True, bc="#AF7AC5")

diag_arrow(COL_L, b_ag, CX - 1.5, t_st, "agents", lo=(-0.6, 0))
diag_arrow(COL_R, b_gr, CX + 1.5, t_st, "graph", lo=(0.5, 0))

# ── Source ──────────────────────────────────────────────────────────
_, b_src, t_src = rbox(COL_L, 13.4, BW, 1.0,
    "Source.step()  -->  generate_truck()\n\n"
    "Create Vehicle agent\n"
    "Register with Scheduler",
    C_MESA, fs=7.5, bc="#F0B27A")

varrow(CX - 2.5, b_st, t_src)

# ── Routing (KEY EXCHANGE) ──────────────────────────────────────────
_, b_rt, t_rt = rbox(CX, 11.0, BW_W, 1.4,
    "get_route( source_id )\n\n"
    "Pick random sink\n"
    "nx.shortest_path(G, source, sink, weight='length')\n"
    "Return path as pandas Series\n"
    "Cache in path_ids_dict",
    C_EXCHANGE, fs=8, bold=True, bc="#7D3C98")

varrow(COL_L, b_src, t_rt, "request route")

# badge - placed below the box, not overlapping
ax.add_patch(FancyBboxPatch((10.0, 11.15), 2.4, 0.55,
             boxstyle="round,pad=0.12", fc="#7D3C98", ec="white", lw=1.3))
ax.text(11.2, 11.42, "KEY EXCHANGE\nMESA <-> NetworkX", ha="center",
        va="center", fontsize=6, fontfamily=FONT, fontweight="bold",
        color="white")

# ── Vehicle drive ───────────────────────────────────────────────────
_, b_dr, t_dr = rbox(COL_L, 8.4, BW, 1.4,
    "Vehicle.step()  -->  drive()\n\n"
    "Advance 800 m/tick along path_ids\n"
    "Increment location_index\n"
    "Update position in ContinuousSpace",
    C_MESA, fs=7.5, bc="#F0B27A")

varrow(COL_L, b_rt, t_dr, "path_ids")

# ── Bridge ──────────────────────────────────────────────────────────
_, b_br, t_br = rbox(COL_R, 8.4, BW, 1.4,
    "Bridge Interaction\n\n"
    "get_delay_time(condition)\n"
    "state = WAIT | DRIVE\n"
    "accumulate waiting_time",
    C_MESA, fs=7.5, bc="#F0B27A")

harrow(COL_L + BW / 2, COL_R - BW / 2, 9.1, "bridge?")

# ── Sink ────────────────────────────────────────────────────────────
_, b_sk, t_sk = rbox(CX, 5.0, BW_W, 1.6,
    "Reach Sink  -->  model.record_trip(vehicle)\n\n"
    "Collect:\n"
    "vehicle_id | origin | destination\n"
    "travel_time | waiting_time\n"
    "bridges_passed | path_length\n\n"
    "Remove vehicle from Scheduler",
    C_MESA, fs=7.5, bc="#F0B27A")

varrow(COL_L, b_dr, t_sk, "reach sink?")

# ── loop-back arrow on far right ────────────────────────────────────
lx = 13.8
# vertical line segments using annotate with no arrowhead, then final with arrow
ax.plot([COL_R + BW / 2, lx], [t_br, t_br], color="#AAB7B8", lw=1.2)
ax.plot([lx, lx], [t_br, t_st], color="#AAB7B8", lw=1.2)
ax.annotate("", xy=(CX + BW_W / 2, t_st), xytext=(lx, t_st),
            arrowprops=dict(arrowstyle="-|>", color="#AAB7B8", lw=1.2,
                            mutation_scale=10))
ax.text(lx - 0.15, (t_br + t_st) / 2, "next tick", fontsize=6.5,
        color="#AAB7B8", fontfamily=FONT, fontstyle="italic",
        ha="right", va="center", rotation=90)

# ====================================================================
#  5  DATA OUTPUT
# ====================================================================
phase_dot(3.5, 5, "Data Output", "#C0392B")

_, b_ex, t_ex = rbox(COL_L, 2.2, BW, 0.8,
    "model.export_data()\n"
    "trip_data --> pandas DataFrame --> CSV",
    C_OUTPUT, fs=8, bold=True, bc="#EC7063")

varrow(CX, b_sk, t_ex)

_, b_co, t_co = rbox(COL_L, 0.9, BW, 0.8,
    "experiment/scenario_N.csv\n"
    "5 scenarios x 10 replications",
    C_OUTPUT, fs=8, bold=True, bc="#EC7063")

varrow(COL_L, b_ex, t_co)

_, b_an, t_an = rbox(COL_R, 0.9, BW, 0.8,
    "experiment_analysis.ipynb\n"
    "Compare scenarios & visualise",
    C_OUTPUT, fs=8, bc="#EC7063")

harrow(COL_L + BW / 2, COL_R - BW / 2, 1.3, "read CSVs")

# ====================================================================
#  LEGEND
# ====================================================================
ly = 0.05
ax.add_patch(FancyBboxPatch((0.5, ly - 0.05), 13.0, 0.5,
             boxstyle="round,pad=0.1", fc="white", ec="#ddd", lw=0.5))

items = [
    (C_INPUT, "#85C1E9", "Data Input"),
    (C_MESA,  "#F0B27A", "MESA"),
    (C_NX,    "#82E0AA", "NetworkX"),
    (C_EXCHANGE, "#AF7AC5", "Exchange"),
    (C_OUTPUT, "#EC7063", "Output"),
]
for i, (fc, ec, lb) in enumerate(items):
    xp = 1.0 + i * 2.5
    ax.add_patch(FancyBboxPatch((xp, ly + 0.05), 0.35, 0.3,
                 boxstyle="round,pad=0.04", fc=fc, ec=ec, lw=0.9))
    ax.text(xp + 0.5, ly + 0.2, lb, fontsize=7, fontfamily=FONT,
            va="center", color="#444")

# ====================================================================
plt.savefig("mesa_networkx_flowchart.png", dpi=250, bbox_inches="tight",
            facecolor="white", pad_inches=0.25)
plt.savefig("mesa_networkx_flowchart.pdf", bbox_inches="tight",
            facecolor="white", pad_inches=0.25)
print("Saved: mesa_networkx_flowchart.png & mesa_networkx_flowchart.pdf")
