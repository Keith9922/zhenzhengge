#!/usr/bin/env python3
"""
Generate architecture diagram for 证证鸽 (English labels for better rendering)
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Set up the figure
fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 16)
ax.set_ylim(0, 12)
ax.axis('off')
fig.patch.set_facecolor('#f8fafc')

# Colors
colors = {
    'user': '#3b82f6',
    'web': '#8b5cf6',
    'plugin': '#10b981',
    'api': '#f59e0b',
    'llm': '#ef4444',
    'orch': '#ec4899',
    'storage': '#6366f1',
    'capture': '#14b8a6',
    'notify': '#84cc16',
}

def draw_box(ax, x, y, w, h, label, sublabel='', color='#3b82f6', fontsize=11):
    """Draw a rounded rectangle with label"""
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.15",
                          facecolor=color, edgecolor='white', linewidth=2.5, alpha=0.95)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2 + 0.2, label,
            ha='center', va='center', fontsize=fontsize, fontweight='bold', color='white')
    if sublabel:
        ax.text(x + w/2, y + h/2 - 0.25, sublabel,
                ha='center', va='center', fontsize=fontsize-2, color='white', alpha=0.9)

def draw_arrow(ax, x1, y1, x2, y2, color='#94a3b8'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=2.5,
                              connectionstyle="arc3,rad=0"))

# Title
ax.text(8, 11.5, 'ZhengZhengGe System Architecture', ha='center', va='center',
        fontsize=22, fontweight='bold', color='#1e293b')
ax.text(8, 10.85, 'AI IP Infringement Response Platform', ha='center', va='center',
        fontsize=13, color='#64748b', style='italic')

# ========== USER LAYER ==========
ax.add_patch(FancyBboxPatch((0.3, 8.2), 15.4, 1.7, boxstyle="round,pad=0.02,rounding_size=0.1",
                             facecolor='#e2e8f0', edgecolor='#cbd5e1', linewidth=1, alpha=0.5))
ax.text(0.5, 9.7, 'USER LAYER', fontsize=9, fontweight='bold', color='#64748b')

# Browser Extension
draw_box(ax, 1, 8.4, 3.5, 1.3, 'Browser Extension', 'Plasmo', colors['plugin'])
# Web Frontend
draw_box(ax, 6.2, 8.4, 3.5, 1.3, 'Web Workspace', 'Next.js', colors['web'])
# Mobile
draw_box(ax, 11.4, 8.4, 3.5, 1.3, 'Mobile (Planned)', '-', '#94a3b8')

# ========== API GATEWAY ==========
ax.add_patch(FancyBboxPatch((0.3, 5.5), 15.4, 2.0, boxstyle="round,pad=0.02,rounding_size=0.1",
                             facecolor='#fef3c7', edgecolor='#fcd34d', linewidth=1, alpha=0.3))
ax.text(0.5, 7.35, 'API GATEWAY', fontsize=9, fontweight='bold', color='#b45309')

draw_box(ax, 4, 5.7, 8, 1.6, 'FastAPI', 'Python 3.11+ | CORS | Routing', colors['api'], fontsize=12)

# ========== SERVICES LAYER ==========
ax.add_patch(FancyBboxPatch((0.3, 2.8), 15.4, 2.5, boxstyle="round,pad=0.02,rounding_size=0.1",
                             facecolor='#fce7f3', edgecolor='#f9a8d4', linewidth=1, alpha=0.3))
ax.text(0.5, 5.15, 'SERVICES LAYER', fontsize=9, fontweight='bold', color='#be185d')

# Hermes
draw_box(ax, 0.5, 3.0, 4, 1.8, 'Hermes', 'Task Orchestration', colors['orch'])
# LLM
draw_box(ax, 5.5, 3.0, 4, 1.8, 'LLM Service', 'MiMo | Doc Generation', colors['llm'])
# Playwright
draw_box(ax, 10.5, 3.0, 4.5, 1.8, 'Playwright', 'Page Capture | Screenshot', colors['capture'])

# ========== DATA LAYER ==========
ax.add_patch(FancyBboxPatch((0.3, 0.8), 15.4, 1.8, boxstyle="round,pad=0.02,rounding_size=0.1",
                             facecolor='#e0e7ff', edgecolor='#a5b4fc', linewidth=1, alpha=0.3))
ax.text(0.5, 2.45, 'DATA LAYER', fontsize=9, fontweight='bold', color='#4338ca')

# Database
draw_box(ax, 0.5, 0.9, 4.2, 1.4, 'SQLite', 'Cases | Evidence', colors['storage'])
# Notification
draw_box(ax, 5.5, 0.9, 4.2, 1.4, 'Notification', 'Email | Webhook', colors['notify'])
# File Storage
draw_box(ax, 10.5, 0.9, 4.5, 1.4, 'File Storage', 'Screenshots | HTML', colors['storage'])

# ========== ARROWS ==========
# User to API
draw_arrow(ax, 2.75, 8.4, 2.75, 7.3)
draw_arrow(ax, 7.95, 8.4, 7.95, 7.3)
draw_arrow(ax, 13.15, 8.4, 13.15, 7.3)

# API to Services
draw_arrow(ax, 5.5, 5.7, 2.5, 4.8)
draw_arrow(ax, 8, 5.7, 7.5, 4.8)
draw_arrow(ax, 10.5, 5.7, 12.5, 4.8)

# Services to Data
draw_arrow(ax, 2.5, 3.0, 2.5, 2.3)
draw_arrow(ax, 7.5, 3.0, 7.5, 2.3)
draw_arrow(ax, 12.5, 3.0, 12.5, 2.3)

# ========== LEGEND ==========
legend_items = [
    (colors['plugin'], 'Browser Plugin'),
    (colors['web'], 'Web Frontend'),
    (colors['api'], 'API Gateway'),
    (colors['orch'], 'Orchestration'),
    (colors['llm'], 'LLM'),
    (colors['capture'], 'Capture'),
    (colors['storage'], 'Storage'),
    (colors['notify'], 'Notification'),
]
for i, (color, label) in enumerate(legend_items):
    col = i % 4
    row = i // 4
    x = 0.5 + col * 3.8
    y = -0.3 - row * 0.5
    rect = FancyBboxPatch((x, y), 3.2, 0.4, boxstyle="round,pad=0.02",
                           facecolor=color, alpha=0.9)
    ax.add_patch(rect)
    ax.text(x + 1.6, y + 0.2, label, ha='center', va='center',
            fontsize=8, color='white', fontweight='bold')

# Save
plt.tight_layout()
plt.savefig('docs/architecture.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print('Saved to docs/architecture.png')
