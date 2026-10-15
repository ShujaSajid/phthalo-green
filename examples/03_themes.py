"""Themes: register your own palette and switch between them.

This is the extension point for a second/third colour scheme: a theme is
plain data, so no styling code changes are needed.

Run:
    uv run python examples/03_themes.py
    phthalo-green show indigo

Output:
    figures/03_themes_<theme>.pdf + .png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import phthalo_green as pg

OUT = Path(__file__).resolve().parents[1] / "figures"


def curve(ax, theme_name: str) -> None:
    x = np.linspace(0, 1, 12)
    for index, color in enumerate(pg.get_palette("categorical", 4)):
        ax.plot(x, x ** (0.4 + index * 0.25), marker="o", color=color,
                label=f"Series {index + 1}")
    ax.set_title(f"{theme_name}")
    ax.legend()
    pg.despine(ax)


def main() -> None:
    # 1. A theme can be built from a single anchor colour: the ramp, the
    #    supporting accents and the neutrals are all derived for you.
    pg.register_palette(
        "brand",
        {"primary": "#2F6F4E", "dark": "#10281C", "pale": "#DCEAE2"},
        label="Brand Green",
        description="Derived from one anchor colour by make_theme().",
    )

    # 2. ... or from an ordered dark -> light ramp.
    pg.register_palette(
        "sandstone",
        ["#241A0C", "#7A5B24", "#B9903C", "#E3D3A6"],
        label="Sandstone",
    )

    # 3. ... or by hand, giving full control over every palette.
    pg.register_theme(
        pg.make_theme(
            "monochrome",
            {"dark": "#1C1C1C", "primary": "#3F3F3F"},
            categorical=["#1C1C1C", "#3F3F3F", "#6E6E6E", "#A6A6A6", "#D6D6D6"],
            sequential=["#F5F5F5", "#C8C8C8", "#9C9C9C", "#6E6E6E", "#3F3F3F",
                        "#1C1C1C"],
            label="Monochrome",
        )
    )

    pg.apply_style(preset="single_column")

    for theme_name in pg.list_themes():
        with pg.with_theme(theme_name):
            theme = pg.active_theme()
            print(f"{theme_name:<14} primary={theme['primary']} "
                  f"categorical={len(theme.palette('categorical'))}")

            with plt.style.context("default"):
                fig, ax = plt.subplots(figsize=(4.5, 3.2))
                pg.apply_style(preset="single_column", theme=theme_name)
                curve(ax, theme.label)
                pg.export_figure(fig, OUT / f"03_themes_{theme_name}")

    # Sharing the style with collaborators who do not want the dependency:
    style_path = pg.write_mplstyle(OUT / "03_brand.mplstyle",
                                   preset="journal", theme="brand")
    print(f"Wrote {style_path}  (use with plt.style.use(...))")

    # Other libraries read from the same theme data.
    template = pg.plotly_template("brand")
    print(f"Plotly colorway[0]: {template['layout']['colorway'][0]}")

    plt.close("all")


if __name__ == "__main__":
    main()
