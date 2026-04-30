import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Polygon
from matplotlib.font_manager import FontProperties
import numpy as np
import os

FONTS = r'C:\Users\giris\.claude\plugins\cache\anthropic-agent-skills\document-skills\0f7c287eaf0d\skills\canvas-design\canvas-fonts'
OUT = r'C:\Users\giris\Documents\GitHub\ai-enablement-ws\projects\argus\docs\diagrams'

def fp(name, size):
    return FontProperties(fname=os.path.join(FONTS, name), size=size)

FP_TITLE    = fp('BigShoulders-Bold.ttf', 20)
FP_SUBTITLE = fp('InstrumentSans-Regular.ttf', 8.5)
FP_AGENT    = fp('GeistMono-Bold.ttf', 8.5)
FP_SUB      = fp('InstrumentSans-Regular.ttf', 6.8)
FP_TAG      = fp('JetBrainsMono-Regular.ttf', 7)
FP_INFRA    = fp('InstrumentSans-Bold.ttf', 8.5)
FP_SMALL    = fp('Jura-Light.ttf', 6.5)
FP_DECISION = fp('GeistMono-Bold.ttf', 7.5)

# Palette
BG             = '#0B0F1A'
ORCH_BG        = '#0E0B22'
ORCH_BORDER    = '#5B21B6'
AGENT_BG       = '#150E32'
AGENT_BORDER   = '#8B5CF6'
IO_BG          = '#091C3A'
IO_BORDER      = '#3B82F6'
INFRA_BG       = '#061A14'
INFRA_BORDER   = '#10B981'
DECISION_BG    = '#1A1000'
DECISION_BORDER= '#F59E0B'
ESCALATE_BG    = '#190808'
ESCALATE_BORDER= '#EF4444'
GEMINI_BG      = '#040E0C'
GEMINI_BORDER  = '#0D9488'
TEXT_PRI       = '#E2E8F0'
TEXT_DIM       = '#475569'
TEXT_DIM2      = '#64748B'
TEXT_AGENT     = '#C4B5FD'
TEXT_IO        = '#93C5FD'
TEXT_INFRA     = '#34D399'
ARROW_MAIN     = '#6D28D9'
ARROW_IO       = '#3B82F6'
ARROW_INFRA    = '#059669'
ARROW_AUTO     = '#D97706'
ARROW_FLAG     = '#DC2626'
ARROW_PROPOSE  = '#7C3AED'
GRID           = '#131929'

fig, ax = plt.subplots(figsize=(26, 16))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 26)
ax.set_ylim(0, 16)
ax.axis('off')

# Subtle grid
for y in np.arange(1, 16, 1):
    ax.axhline(y, color=GRID, lw=0.4, zorder=0)
for x in np.arange(0, 26, 1):
    ax.axvline(x, color=GRID, lw=0.4, zorder=0)

def rbox(cx, cy, w, h, fill, edge, lw=1.6, alpha=1.0, z=3, pad=0.1):
    b = FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                        boxstyle=f'round,pad={pad}',
                        facecolor=fill, edgecolor=edge,
                        linewidth=lw, alpha=alpha, zorder=z)
    ax.add_patch(b)

def agent(cx, cy, label, sub=None):
    rbox(cx, cy, 4.8, 0.95, AGENT_BG, AGENT_BORDER, z=4)
    if sub:
        ax.text(cx, cy+0.17, label, ha='center', va='center', fontproperties=FP_AGENT, color=TEXT_AGENT, zorder=5)
        ax.text(cx, cy-0.2,  sub,   ha='center', va='center', fontproperties=FP_SUB,   color=TEXT_DIM2,  zorder=5)
    else:
        ax.text(cx, cy,      label, ha='center', va='center', fontproperties=FP_AGENT, color=TEXT_AGENT, zorder=5)

def infra(cx, cy, label, sub=None):
    rbox(cx, cy, 4.0, 0.9, INFRA_BG, INFRA_BORDER, z=4)
    if sub:
        ax.text(cx, cy+0.16, label, ha='center', va='center', fontproperties=FP_INFRA, color=TEXT_INFRA, zorder=5)
        ax.text(cx, cy-0.18, sub,   ha='center', va='center', fontproperties=FP_SMALL, color=TEXT_DIM2,  zorder=5)
    else:
        ax.text(cx, cy,      label, ha='center', va='center', fontproperties=FP_INFRA, color=TEXT_INFRA, zorder=5)

def diamond(cx, cy, w, h, fill, edge):
    pts = [[cx, cy+h/2], [cx+w/2, cy], [cx, cy-h/2], [cx-w/2, cy]]
    ax.add_patch(Polygon(pts, facecolor=fill, edgecolor=edge, linewidth=1.8, zorder=4))

def arr(x1, y1, x2, y2, color, lw=1.5, rad=0, label=None, lx=None, ly=None):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                               connectionstyle=f'arc3,rad={rad}'), zorder=3)
    if label:
        mx = lx if lx else (x1+x2)/2
        my = ly if ly else (y1+y2)/2
        ax.text(mx, my, label, ha='center', va='center',
                fontproperties=FP_TAG, color=color, zorder=6,
                bbox=dict(facecolor=BG, edgecolor='none', alpha=0.85, pad=1.5))

def bidir(x1, y1, x2, y2, color, lw=1.4, label=None):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='<->', color=color, lw=lw,
                               connectionstyle='arc3,rad=0'), zorder=3)
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2+0.2, label, ha='center', va='center',
                fontproperties=FP_SMALL, color=color, zorder=6,
                bbox=dict(facecolor=BG, edgecolor='none', alpha=0.85, pad=1.5))

# ── TITLE ──────────────────────────────────────────────────────────────────────
ax.text(13, 15.4, 'PROJECT ARGUS', ha='center', va='center',
        fontproperties=FP_TITLE, color=TEXT_PRI, zorder=6)
ax.text(13, 14.85, 'Catalog Integrity  ·  Multi-Agent Architecture', ha='center', va='center',
        fontproperties=FP_SUBTITLE, color=TEXT_DIM2, zorder=6)

# ── ORCHESTRATOR ───────────────────────────────────────────────────────────────
orch = FancyBboxPatch((2.2, 1.1), 20.4, 13.3,
                       boxstyle='round,pad=0.15',
                       facecolor=ORCH_BG, edgecolor=ORCH_BORDER,
                       linewidth=2.0, linestyle=(0,(6,3)), alpha=0.95, zorder=1)
ax.add_patch(orch)
ax.text(2.8, 14.15, 'argus_orchestrator', ha='left', va='center',
        fontproperties=FP_TAG, color='#7C3AED', zorder=6)

# ── GEMINI LAYER (bottom strip) ────────────────────────────────────────────────
gem = FancyBboxPatch((2.3, 1.2), 20.2, 0.85,
                      boxstyle='round,pad=0.05',
                      facecolor=GEMINI_BG, edgecolor=GEMINI_BORDER,
                      linewidth=1.0, alpha=0.95, zorder=2)
ax.add_patch(gem)
ax.text(12.4, 1.625, '>>  Gemini flash-latest  ·  underlying model layer  ·  powers all agents',
        ha='center', va='center', fontproperties=FP_SMALL, color=GEMINI_BORDER, zorder=5)

# ── INPUT: Syndigo ─────────────────────────────────────────────────────────────
CX = 8.2   # pipeline centerline

rbox(1.1, 12.0, 1.6, 0.78, IO_BG, IO_BORDER, z=4)
ax.text(1.1, 12.13, 'Syndigo', ha='center', va='center', fontproperties=FP_AGENT, color=TEXT_IO, zorder=5)
ax.text(1.1, 11.87, 'supplier', ha='center', va='center', fontproperties=FP_SMALL, color=TEXT_DIM2, zorder=5)

# A2A entry arrow
arr(1.9, 12.0, 5.8, 12.0, IO_BORDER, lw=2.0, label='A2A', lx=3.85, ly=12.28)

# ── AGENT PIPELINE ─────────────────────────────────────────────────────────────

# 1 — ItemValidatorAgent
agent(CX, 12.0, 'ItemValidatorAgent', 'missing fields · bad format · price anomaly · taxonomy')
arr(CX, 11.525, CX, 10.75, ARROW_MAIN)

# 2 — CorrectionResolverAgent
agent(CX, 10.3, 'CorrectionResolverAgent', 'vector similarity · confidence score · tier assign')
arr(CX, 9.825, CX, 9.05, ARROW_MAIN)

# 3 — Decision fork (diamond)
DX, DY = CX, 8.55
diamond(DX, DY, 2.8, 0.95, DECISION_BG, DECISION_BORDER)
ax.text(DX, DY, 'Tier Decision', ha='center', va='center',
        fontproperties=FP_DECISION, color='#FCD34D', zorder=5)

# ── BRANCH: FLAG (right) ───────────────────────────────────────────────────────
FLAG_X = 13.5
arr(DX+1.4, DY, FLAG_X, 7.85, ARROW_FLAG, lw=1.6, rad=-0.15,
    label='FLAG', lx=11.8, ly=8.45)

rbox(FLAG_X, 7.5, 2.6, 0.65, ESCALATE_BG, ESCALATE_BORDER, lw=1.5, z=4)
ax.text(FLAG_X, 7.62, 'Escalate', ha='center', va='center', fontproperties=FP_AGENT, color='#FCA5A5', zorder=5)
ax.text(FLAG_X, 7.38, 'no write · stop', ha='center', va='center', fontproperties=FP_SMALL, color=TEXT_DIM2, zorder=5)

# ── BRANCH: PROPOSE (center-down) ─────────────────────────────────────────────
arr(DX, 8.075, DX, 7.35, ARROW_PROPOSE, label='PROPOSE', lx=DX+0.9, ly=7.7)

# ApprovalOrchestrator
agent(CX, 6.9, 'ApprovalOrchestrator', 'Slack Block Kit · await approve / reject')
arr(CX, 6.425, CX, 5.475, ARROW_PROPOSE, label='approved', lx=CX+0.9, ly=5.95)

# ── BRANCH: AUTO (left arc bypass) ────────────────────────────────────────────
ax.annotate('', xy=(CX-1.5, 5.45), xytext=(DX-1.4, DY),
            arrowprops=dict(arrowstyle='->', color=ARROW_AUTO, lw=1.6,
                           connectionstyle='arc3,rad=0.45'), zorder=3)
ax.text(5.4, 7.1, 'AUTO', ha='center', va='center',
        fontproperties=FP_DECISION, color=ARROW_AUTO, zorder=6,
        bbox=dict(facecolor=BG, edgecolor='none', alpha=0.9, pad=2))
ax.text(5.4, 6.78, '≥ 0.85', ha='center', va='center',
        fontproperties=FP_SMALL, color=TEXT_DIM2, zorder=6,
        bbox=dict(facecolor=BG, edgecolor='none', alpha=0.9, pad=1.5))

# ── CatalogWriterAgent ─────────────────────────────────────────────────────────
agent(CX, 5.0, 'CatalogWriterAgent', 'write audit diff · mark released / blocked')
arr(CX, 4.525, CX, 3.75, ARROW_MAIN)

# ── FeedbackAgent ──────────────────────────────────────────────────────────────
agent(CX, 3.3, 'FeedbackAgent', 're-embed correction · insert correction_history')

# ── OUTPUT ────────────────────────────────────────────────────────────────────
rbox(1.1, 3.3, 1.6, 0.78, IO_BG, IO_BORDER, z=4)
ax.text(1.1, 3.43, 'Output', ha='center', va='center', fontproperties=FP_AGENT, color=TEXT_IO, zorder=5)
ax.text(1.1, 3.17, 'released/blocked', ha='center', va='center', fontproperties=FP_SMALL, color=TEXT_DIM2, zorder=5)
arr(5.2, 5.0, 1.9, 3.5, IO_BORDER, lw=1.6, rad=0.25,
    label='write', lx=3.3, ly=4.65)

# ── INFRASTRUCTURE (right column x=20.0, inside orchestrator) ─────────────────
IX = 20.0
IX_LEFT = IX - 2.0   # left edge of infra boxes = 18.0

# Subtle vertical separator between pipeline and infra
ax.plot([14.3, 14.3], [2.2, 13.5], color='#1E2A40', lw=1.0, zorder=1, linestyle='--')

# Infra section label
ax.text(IX, 11.5, 'INFRASTRUCTURE', ha='center', va='center',
        fontproperties=FP_SMALL, color=TEXT_DIM, zorder=5)

# BigQuery Vector Search
infra(IX, 10.3, 'BigQuery', 'Vector Search')
bidir(10.6, 10.3, IX_LEFT, 10.3, INFRA_BORDER, label='similarity search')

# Slack
infra(IX, 6.9, 'Slack', 'Block Kit approvals')
bidir(10.6, 6.9, IX_LEFT, 6.9, INFRA_BORDER, label='interactive message')

# BigQuery correction_history
infra(IX, 3.3, 'BigQuery', 'correction_history')
arr(10.6, 3.3, IX_LEFT, 3.3, INFRA_BORDER, lw=1.4, label='RAG insert', lx=14.3, ly=3.55)

# dashed line: BQ VS also feeds FeedbackAgent (future RAG retrieval)
ax.annotate('', xy=(10.6, 3.5), xytext=(IX_LEFT, 10.0),
            arrowprops=dict(arrowstyle='->', color=ARROW_INFRA, lw=0.8, alpha=0.25,
                           connectionstyle='arc3,rad=0.15'), zorder=2)

# ── LEGEND (outside orchestrator, x > 22.6) ────────────────────────────────────
legend = [
    (AGENT_BORDER,    AGENT_BG,    'Agent'),
    (IO_BORDER,       IO_BG,       'Input / Output'),
    (INFRA_BORDER,    INFRA_BG,    'Infrastructure'),
    (DECISION_BORDER, DECISION_BG, 'Decision'),
    (ESCALATE_BORDER, ESCALATE_BG, 'Escalate / Stop'),
]
LX, LY = 23.0, 13.8
ax.text(LX, LY+0.1, 'LEGEND', ha='left', va='center', fontproperties=FP_SMALL, color=TEXT_DIM, zorder=6)
for i, (edge, fill, name) in enumerate(legend):
    by = LY - 0.35 - i*0.58
    b = FancyBboxPatch((LX, by-0.17), 0.42, 0.34,
                        boxstyle='round,pad=0.03',
                        facecolor=fill, edgecolor=edge, linewidth=1.2, zorder=5)
    ax.add_patch(b)
    ax.text(LX+0.58, by, name, ha='left', va='center', fontproperties=FP_SMALL, color=TEXT_DIM2, zorder=6)

# ── FOOTNOTE ──────────────────────────────────────────────────────────────────
ax.text(13, 0.55, 'argus · catalog integrity · phase 1 · syndigo / our brands  ·  compliance_fields always capped at PROPOSE',
        ha='center', va='center', fontproperties=FP_SMALL, color='#1E293B', zorder=6)

# ── SAVE ───────────────────────────────────────────────────────────────────────
out = os.path.join(OUT, 'argus-architecture.png')
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG, edgecolor='none')
plt.close()
print(f"Saved: {out}")
