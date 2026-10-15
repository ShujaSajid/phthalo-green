"""Phthalo Green academic visualization style.

Installable library — use from any project:

    import phthalo_green as pg

    fig, ax = pg.subplots(preset="thesis")
    ax.plot(x, y, color=pg.PALETTE["primary"])
    pg.export_figure(fig, "figures/my_fig")  # -> .pdf + .png

Switch palettes (themes) without touching your plotting code:

    pg.set_theme("indigo")                 # or your own palette:
    pg.register_palette("mine", {"primary": "#2F6F4E"})

Attribute access is preferred over ``from phthalo_green import X`` because
color constants (`pg.PHTHALO_GREEN`), colormaps (`pg.SEQUENTIAL_CMAP`) and
helper functions are resolved at call time. The palette containers
(`pg.PALETTE`, `pg.CATEGORICAL`, ...) are live objects, so they work either
way.
"""

from __future__ import annotations

from typing import Any

from . import style as _style
from .cli import main as _cli_main

# Static, import-time bindings. Theme-reactive names (color constants,
# colormap objects) are resolved dynamically by ``__getattr__`` below.
from .style import (
    ACCENT_KEYS,
    CATEGORICAL,
    CATEGORICAL_GREEN,
    DEFAULT_THEME_NAME,
    DIVERGING,
    FONT_FAMILY,
    FONT_SANS_FALLBACKS,
    FONT_SERIF_FALLBACKS,
    MATH_FONTSET,
    NEUTRAL_KEYS,
    PALETTE,
    PALETTE_KINDS,
    PHTHALO_GREEN_THEME,
    PUBLICATION_FORMATS,
    RAMP_KEYS,
    RASTER_FORMATS,
    SEQUENTIAL,
    SETTING_KEYS,
    STYLE_OVERRIDE_KEYS,
    STYLE_PRESETS,
    THEMES,
    VECTOR_FORMATS,
    WORDCLOUD_FONT_PATH,
    Theme,
    active_theme,
    apply_plotly_theme,
    apply_seaborn_style,
    apply_style,
    configure_latex,
    contrast_ratio,
    css_rgba,
    darken,
    describe_theme,
    despine,
    export_dpi,
    export_figure,
    figure,
    get_cmap,
    get_color,
    get_palette,
    get_preset,
    get_theme,
    lighten,
    list_themes,
    make_theme,
    mix,
    plotly_template,
    preset_rc,
    print_style_info,
    register_colormaps,
    register_palette,
    register_theme,
    relative_luminance,
    resolved_serif_font,
    save_publication_figure,
    set_theme,
    shift_hue,
    style_axis,
    style_legend,
    styled,
    subplots,
    to_hex,
    use_theme,
    with_alpha,
    with_theme,
    write_mplstyle,
)
from .themes import INDIGO, register_builtin_themes

__version__ = "0.1.1"

# Register the optional themes that ship with the package.
register_builtin_themes()

# Console entry point / ``python -m phthalo_green``.
main = _cli_main

# Names that must follow the active theme, resolved on every access.
_DYNAMIC = frozenset(set(_style._COLOR_ALIASES) | set(_style._CMAP_ALIASES))


def __getattr__(name: str) -> Any:
    if name in _DYNAMIC:
        return getattr(_style, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | _DYNAMIC)


__all__ = [
    # Constants and live palette containers
    "ACCENT_KEYS",
    "CATEGORICAL",
    "CATEGORICAL_CMAP",
    "CATEGORICAL_GREEN",
    "DEEP_PHTHALO_GREEN",
    "DEFAULT_THEME_NAME",
    "DIVERGING",
    "DIVERGING_CMAP",
    "EMERALD_GREEN",
    "FONT_FAMILY",
    "FONT_SANS_FALLBACKS",
    "FONT_SERIF_FALLBACKS",
    "INDIGO",
    "LIGHT_GREEN",
    "MATH_FONTSET",
    "MEDIUM_PHTHALO_GREEN",
    "NEUTRAL_KEYS",
    "PALETTE",
    "PALETTE_KINDS",
    "PALE_GREEN",
    # Theme-reactive
    "PHTHALO_GREEN",
    "PHTHALO_GREEN_THEME",
    "PUBLICATION_FORMATS",
    "RAMP_KEYS",
    "RASTER_FORMATS",
    "SEQUENTIAL",
    "SEQUENTIAL_CMAP",
    "SETTING_KEYS",
    "STYLE_OVERRIDE_KEYS",
    "STYLE_PRESETS",
    "THEMES",
    "VECTOR_FORMATS",
    "WORDCLOUD_FONT_PATH",
    "Theme",
    "__version__",
    "active_theme",    # Themes
    "apply_plotly_theme",
    # Other libraries
    "apply_seaborn_style",
    # Style application
    "apply_style",
    "configure_latex",
    "contrast_ratio",
    "css_rgba",
    "darken",
    "describe_theme",
    "despine",
    # Export
    "export_dpi",
    "export_figure",
    "figure",
    "get_cmap",
    # Colors
    "get_color",
    "get_palette",
    "get_preset",
    "get_theme",
    "lighten",
    "list_themes",
    # CLI
    "main",
    "make_theme",
    "mix",
    "plotly_template",
    "preset_rc",
    "print_style_info",
    "register_builtin_themes",
    "register_colormaps",
    "register_palette",
    "register_theme",
    "relative_luminance",
    "resolved_serif_font",
    "save_publication_figure",
    "set_theme",
    "shift_hue",
    # Figure helpers
    "style_axis",
    "style_legend",
    "styled",
    "subplots",
    "to_hex",
    "use_theme",
    "with_alpha",
    "with_theme",
    "write_mplstyle",
]
