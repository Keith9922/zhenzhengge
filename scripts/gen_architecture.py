#!/usr/bin/env python3
"""
Generate architecture diagram for 证证鸽
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

# Set up the figure with dark background
fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 16)
ax.set_ylim(0, 12)
ax.axis('off')
fig.patch.set_facecolor('#f8fafc')

# Colors
colors = {
    'user': '#3b82f6',      # Blue
    'web': '#8b5cf6',        # Purple
    'plugin': '#10b981',    # Green
    'api': '#f59e0b',        # Amber
    'llm': '#ef4444',        # Red
    'orch': '#ec4899',       # Pink
    'storage': '#6366f1',    # Indigo
    'capture': '#14b8a6',    # Teal
    'notify': '#84cc16',     # Lime
    'bg': '#1e293b',         # Dark
}

def draw_box(ax, x, y, w, h, label, sublabel='', color='#3b82f6', fontsize=10):
    """Draw a rounded rectangle with label"""
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.2",
                          facecolor=color, edgecolor='white', linewidth=2, alpha=0.9)
    ax.add_patch(box)

    # Main label
    ax.text(x + w/2, y + h/2 + 0.15, label,
            ha='center', va='center', fontsize=fontsize, fontweight='bold', color='white')

    # Sub label
    if sublabel:
        ax.text(x + w/2, y + h/2 - 0.25, sublabel,
                ha='center', va='center', fontsize=fontsize-2, color='white', alpha=0.9)

def draw_arrow(ax, x1, y1, x2, y2, color='#94a3b8', style='->'):
    """Draw an arrow between two points"""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=2))

# Title
ax.text(8, 11.5, '证证鸽技术架构', ha='center', va='center',
        fontsize=20, fontweight='bold', color='#1e293b')
ax.text(8, 10.9, 'ZhengZhengGe Architecture', ha='center', va='center',
        fontsize=12, color='#64748b')

# === USER LAYER ===
ax.text(8, 10.2, '用户端', ha='center', va='center', fontsize=11, fontweight='bold', color='#475569')

# Browser Extension
draw_box(ax, 1, 8.5, 3.5, 1.2, '浏览器插件', 'Plasmo', colors['plugin'])
# Web Frontend
draw_box(ax, 6, 8.5, 3.5, 1.2, 'Web 工作台', 'Next.js', colors['web'])
# Mobile (placeholder)
draw_box(ax, 11, 8.5, 3.5, 1.2, '移动端', '(预留)', '#94a3b8')

# === API LAYER ===
ax.text(8, 7.8, 'API 网关', ha='center', va='center', fontsize=11, fontweight='bold', color='#475569')
draw_box(ax, 4, 5.8, 8, 1.5, 'FastAPI', 'Python 3.11+ | CORS | 路由', colors['api'])

# === SERVICES ===
# Hermes Orchestrator
draw_box(ax, 0.5, 3.5, 4, 1.8, 'Hermes Orchestrator', '任务编排中枢', colors['orch'])

# LLM Service
draw_box(ax, 5.5, 3.5, 4, 1.8, 'LLM Service', 'MiMo | 文书生成', colors['llm'])

# Playwright
draw_box(ax, 10.5, 3.5, 4, 1.8, 'Playwright', '页面抓取 | 截图', colors['capture'])

# === DATA & NOTIFICATION ===
# Database
draw_box(ax, 1, 1, 4, 1.5, 'SQLite', '案件 | 证据包', colors['storage'])

# Notification
draw_box(ax, 5.5, 1, 4, 1.5, 'Notification', 'Email | Webhook', colors['notify'])

# Storage
draw_box(ax, 10.5, 1, 4, 1.5, 'File Storage', '截图 | HTML', colors['storage'])

# === ARROWS ===
# User to services
draw_arrow(ax, 2.75, 8.5, 2.75, 7.3)
draw_arrow(ax, 7.75, 8.5, 7.75, 7.3)
draw_arrow(ax, 12.75, 8.5, 12.75, 7.3)

# API to services
draw_arrow(ax, 6, 5.8, 2.5, 5.3)
draw_arrow(ax, 8, 5.8, 7.5, 5.3)
draw_arrow(ax, 10, 5.8, 12.5, 5.3)

# Services to data
draw_arrow(ax, 2.5, 3.5, 2.5, 2.5)
draw_arrow(ax, 7.5, 3.5, 7.5, 2.5)
draw_arrow(ax, 12.5, 3.5, 12.5, 2.5)

# === LEGEND ===
ax.text(0.5, 0.3, '图例', fontsize=9, fontweight='bold', color='#475569')
legend_items = [
    (colors['plugin'], '浏览器插件'),
    (colors['web'], 'Web 前端'),
    (colors['api'], 'API 网关'),
    (colors['orch'], '任务编排'),
    (colors['llm'], '大语言模型'),
]
for i, (color, label) in enumerate(legend_items):
    rect = FancyBboxPatch((0.5 + i*2.5, 0), 1.8, 0.4, boxstyle="round,pad=0.02",
                           facecolor=color, alpha=0.8)
    ax.add_patch(rect)
    ax.text(0.5 + i*2.5 + 0.9, 0.2, label, ha='center', va='center',
            fontsize=7, color='white', fontweight='bold')

# === LAYER LABELS ===
ax.text(-0.3, 9.1, '用户层', ha='center', va='center', fontsize=9, color='#94a3b8', rotation=90)
ax.text(-0.3, 6.5, '网关层', ha='center', va='center', fontsize=9, color='#94a3b8', rotation=90)
ax.text(-0.3, 4.3, '服务层', ha='center', va='center', fontsize=9, color='#94a3b8', rotation=90)
ax.text(-0.3, 1.7, '数据层', ha='center', va='center', fontsize=9, color='#94a3b8', rotation=90)

# Save
plt.tight_layout()
plt.savefig('docs/architecture.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print('Architecture diagram saved to docs/architecture.png')
