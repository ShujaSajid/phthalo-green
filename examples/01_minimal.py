"""Minimal starter: copy this pattern into any project using phthalo-green.

Run (from repo root):
    uv sync
    uv run python examples/01_minimal.py
"""

from __future__ import annotations

from pathlib import Path

from phthalo_green import PALETTE, export_figure, subplots

# Per-project output dir — keep this 2-line pattern in your own repos.
FIGURES_DIR = Path(__file__).resolve().parents[1] / "figures"

x = [2019, 2020, 2021, 2022, 2023, 2024]
y = [12, 18, 25, 31, 40, 52]

fig, ax = subplots(preset="thesis")  # or "journal" / "single_column" / "double_column" / "presentation"
ax.plot(x, y, marker="o", color=PALETTE["primary"], label="Papers")
ax.set_title("Publication Trend")
ax.set_xlabel("Year")
ax.set_ylabel("Count")
ax.legend()

export_figure(fig, FIGURES_DIR / "01_minimal_trend")
print("Wrote figures/01_minimal_trend.pdf + .png")
