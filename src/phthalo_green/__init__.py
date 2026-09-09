"""Phthalo Green academic visualization style.

Installable library — use from any project:

    from phthalo_green import PALETTE, subplots, export_figure

    import matplotlib.pyplot as plt

    fig, ax = subplots(preset="thesis")
    ax.plot(x, y, color=PALETTE["primary"])
    export_figure(fig, "figures/my_fig")  # -> .pdf + .png
"""

from __future__ import annotations

from .style import (
    CATEGORICAL,
    CATEGORICAL_GREEN,
    DEEP_PHTHALO_GREEN,
    DIVERGING,
    DIVERGING_CMAP,
    EMERALD_GREEN,
    FONT_FAMILY,
    FONT_SANS_FALLBACKS,
    FONT_SERIF_FALLBACKS,
    LIGHT_GREEN,
    MEDIUM_PHTHALO_GREEN,
    PALE_GREEN,
    PALETTE,
    PHTHALO_GREEN,
    PUBLICATION_FORMATS,
    SEQUENTIAL,
    SEQUENTIAL_CMAP,
    STYLE_PRESETS,
    WORDCLOUD_FONT_PATH,
    apply_seaborn_style,
    apply_style,
    configure_latex,
    export_figure,
    figure,
    get_color,
    get_palette,
    print_style_info,
    register_colormaps,
    save_publication_figure,
    style_axis,
    style_legend,
    styled,
    subplots,
)

__version__ = "0.1.0"

__all__ = [
    "CATEGORICAL",
    "CATEGORICAL_GREEN",
    "DEEP_PHTHALO_GREEN",
    "DIVERGING",
    "DIVERGING_CMAP",
    "EMERALD_GREEN",
    "FONT_FAMILY",
    "FONT_SANS_FALLBACKS",
    "FONT_SERIF_FALLBACKS",
    "LIGHT_GREEN",
    "MEDIUM_PHTHALO_GREEN",
    "PALETTE",
    "PALE_GREEN",
    "PHTHALO_GREEN",
    "PUBLICATION_FORMATS",
    "SEQUENTIAL",
    "SEQUENTIAL_CMAP",
    "STYLE_PRESETS",
    "WORDCLOUD_FONT_PATH",
    "__version__",
    "apply_seaborn_style",
    "apply_style",
    "configure_latex",
    "export_figure",
    "figure",
    "get_color",
    "get_palette",
    "print_style_info",
    "register_colormaps",
    "save_publication_figure",
    "style_axis",
    "style_legend",
    "styled",
    "subplots",
]
