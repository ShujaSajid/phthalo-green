"""
Phthalo Green Academic Visualization Style
===========================================

A reusable, publication-oriented visualization style for:
    - PhD theses
    - Journal papers
    - Conference papers
    - Research reports
    - Technical documentation
    - Academic presentations

Design principles
-----------------
1. Phthalo Green is the primary visual identity.
2. Times New Roman is the preferred academic font.
3. A robust serif fallback chain is provided for Linux/macOS/CI systems.
4. Figures use restrained styling suitable for academic publication.
5. Vector formats (PDF/SVG) are preferred when supported.
6. Sequential, categorical, and diverging palettes are provided.
7. Matplotlib and optional Seaborn support are included.
8. The module is intentionally self-contained.

Basic usage
-----------
    import matplotlib.pyplot as plt
    from phthalo_green import apply_style, PALETTE

    apply_style()

    plt.plot(x, y, color=PALETTE["primary"])
    plt.show()

Multiple series
---------------
    from phthalo_green import CATEGORICAL

    for i, series in enumerate(series_list):
        plt.plot(x, series, color=CATEGORICAL[i])

Heatmap
-------
    from phthalo_green import SEQUENTIAL_CMAP

    plt.imshow(matrix, cmap=SEQUENTIAL_CMAP)

Publication export
------------------
    from phthalo_green import save_publication_figure

    save_publication_figure(fig, "results.pdf")
    save_publication_figure(fig, "results.png", dpi=600)

Author
------
Research Visualization Style — Phthalo Green Academic Standard
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path

import matplotlib as mpl
import matplotlib.colors as mcolors
from cycler import cycler
from matplotlib import font_manager

# =============================================================================
# 1. CORE PHthalo GREEN PALETTE
# =============================================================================
#
# Phthalo Green is the visual anchor. The supporting colors are deliberately
# restrained so that the overall identity remains green rather than becoming
# a generic multicolor plotting scheme.
#

PALETTE: dict[str, str] = {
    # -------------------------------------------------------------------------
    # Phthalo Green family
    # -------------------------------------------------------------------------
    "dark": "#0B2418",
    "primary": "#123524",
    "medium": "#176B45",
    "accent": "#2E8B57",
    "light": "#72A98F",
    "pale": "#C7DED3",
    # -------------------------------------------------------------------------
    # Academic neutrals
    # -------------------------------------------------------------------------
    "charcoal": "#263238",
    "slate": "#607D76",
    "gray": "#9AA7A2",
    "gray_light": "#E7EBE9",
    "background": "#FAFBFA",
    "white": "#FFFFFF",
    # -------------------------------------------------------------------------
    # Restrained supporting colors
    # Used only when green-only categorical separation is insufficient.
    # -------------------------------------------------------------------------
    "blue_green": "#2F6F6D",
    "blue": "#3E6B7C",
    "ochre": "#A58A45",
    "rust": "#9A5B4A",
    "plum": "#6F596F",
}


# Convenient named aliases
PHTHALO_GREEN = PALETTE["primary"]
DEEP_PHTHALO_GREEN = PALETTE["dark"]
MEDIUM_PHTHALO_GREEN = PALETTE["medium"]
EMERALD_GREEN = PALETTE["accent"]
LIGHT_GREEN = PALETTE["light"]
PALE_GREEN = PALETTE["pale"]


# =============================================================================
# 2. TYPOGRAPHY
# =============================================================================

# Times New Roman is the preferred font for the user's academic workflow.
#
# The fallback chain is important because Times New Roman is commonly
# available on Windows but may not exist on Linux containers, servers,
# institutional clusters, or CI environments.
#
# Matplotlib uses the first installed font it can resolve.

FONT_FAMILY = "serif"

FONT_SERIF_FALLBACKS: list[str] = [
    "Times New Roman",
    "Times",
    "TeX Gyre Termes",
    "Liberation Serif",
    "Nimbus Roman",
    "DejaVu Serif",
]

WORDCLOUD_FONT_PATH = font_manager.findfont(
    font_manager.FontProperties(family=FONT_SERIF_FALLBACKS),
    fallback_to_default=True,
)

# Optional sans-serif fallback for rare situations where a sans-serif font
# is explicitly required by a journal or venue.
FONT_SANS_FALLBACKS: list[str] = [
    "Arial",
    "Helvetica",
    "Liberation Sans",
    "DejaVu Sans",
]


# =============================================================================
# 3. READY-TO-USE COLOR PALETTES
# =============================================================================

# Categorical palette:
# Use for independent categories, algorithms, datasets, models, groups, etc.
CATEGORICAL: list[str] = [
    PALETTE["dark"],
    PALETTE["primary"],
    "#1A4A32",
    PALETTE["medium"],
    "#247A4F",
    PALETTE["accent"],
    "#4C9A70",
    PALETTE["light"],
    "#9BC5B1",
    PALETTE["pale"],
]

# Green-only categorical palette:
# Preferred when maintaining a strict monochromatic visual identity matters.
CATEGORICAL_GREEN: list[str] = [
    PALETTE["dark"],
    PALETTE["primary"],
    PALETTE["medium"],
    PALETTE["accent"],
    PALETTE["light"],
    PALETTE["pale"],
]

# Sequential:
# Low -> high, weak -> strong, low risk -> high risk, etc.
SEQUENTIAL: list[str] = [
    PALETTE["pale"],
    "#A8C9B9",
    PALETTE["light"],
    "#4E9271",
    PALETTE["accent"],
    PALETTE["medium"],
    PALETTE["primary"],
    PALETTE["dark"],
]

# Diverging:
# Appropriate when a meaningful midpoint separates two directions.
DIVERGING: list[str] = [
    "#8B4F43",
    PALETTE["rust"],
    "#C39A8C",
    PALETTE["gray_light"],
    "#B5CFC4",
    PALETTE["light"],
    PALETTE["medium"],
    PALETTE["primary"],
]


# =============================================================================
# 4. COLORMAPS
# =============================================================================


def _build_colormaps() -> tuple[
    mcolors.LinearSegmentedColormap,
    mcolors.LinearSegmentedColormap,
]:
    """Create the standard Phthalo Green sequential and diverging colormaps."""

    sequential = mcolors.LinearSegmentedColormap.from_list(
        "phthalo_green",
        SEQUENTIAL,
        N=256,
    )

    diverging = mcolors.LinearSegmentedColormap.from_list(
        "phthalo_green_diverging",
        DIVERGING,
        N=256,
    )

    return sequential, diverging


SEQUENTIAL_CMAP, DIVERGING_CMAP = _build_colormaps()


def register_colormaps() -> None:
    """
    Register the custom colormaps with Matplotlib.

    Safe to call repeatedly.
    """
    existing = set(mpl.colormaps)

    if "phthalo_green" not in existing:
        mpl.colormaps.register(SEQUENTIAL_CMAP)

    if "phthalo_green_diverging" not in existing:
        mpl.colormaps.register(DIVERGING_CMAP)


# =============================================================================
# 5. STYLE PRESETS
# =============================================================================

STYLE_PRESETS: dict[str, dict[str, float]] = {
    # General thesis/paper figure
    "thesis": {
        "font_size": 10,
        "figure_width": 6.5,
        "figure_height": 4.2,
        "line_width": 2.0,
        "marker_size": 5.0,
    },
    # Conservative journal figure
    "journal": {
        "font_size": 9,
        "figure_width": 6.3,
        "figure_height": 4.0,
        "line_width": 1.8,
        "marker_size": 4.5,
    },
    # Larger figure for conference slides or talks
    "presentation": {
        "font_size": 13,
        "figure_width": 10.0,
        "figure_height": 6.0,
        "line_width": 2.5,
        "marker_size": 7.0,
    },
    # Compact single-column figure
    "single_column": {
        "font_size": 8.5,
        "figure_width": 3.4,
        "figure_height": 2.6,
        "line_width": 1.6,
        "marker_size": 4.0,
    },
    # Wider two-column figure
    "double_column": {
        "font_size": 9,
        "figure_width": 7.0,
        "figure_height": 4.2,
        "line_width": 1.8,
        "marker_size": 4.5,
    },
}


# =============================================================================
# 6. APPLY MATPLOTLIB STYLE
# =============================================================================


def apply_style(
    *,
    preset: str = "thesis",
    font_family: str = FONT_FAMILY,
    font_size: float | None = None,
    figure_width: float | None = None,
    figure_height: float | None = None,
    line_width: float | None = None,
    marker_size: float | None = None,
) -> None:
    """
    Apply the Phthalo Green academic style globally to Matplotlib.

    Parameters
    ----------
    preset:
        One of:
            "thesis"
            "journal"
            "presentation"
            "single_column"
            "double_column"

    font_family:
        Default is "serif", using the Times New Roman fallback chain.

    font_size:
        Optional override of the preset font size.

    figure_width:
        Optional override in inches.

    figure_height:
        Optional override in inches.

    line_width:
        Optional override for plotted lines.

    marker_size:
        Optional override for plotted markers.

    Examples
    --------
    apply_style()

    apply_style(preset="journal")

    apply_style(
        preset="thesis",
        font_size=11,
        figure_width=7,
    )
    """

    if preset not in STYLE_PRESETS:
        available = ", ".join(STYLE_PRESETS)
        raise ValueError(f"Unknown preset '{preset}'. Available presets: {available}")

    settings = STYLE_PRESETS[preset]

    font_size = settings["font_size"] if font_size is None else font_size
    figure_width = settings["figure_width"] if figure_width is None else figure_width
    figure_height = (
        settings["figure_height"] if figure_height is None else figure_height
    )
    line_width = settings["line_width"] if line_width is None else line_width
    marker_size = settings["marker_size"] if marker_size is None else marker_size

    mpl.rcParams.update(
        {
            # -----------------------------------------------------------------
            # Figure
            # -----------------------------------------------------------------
            "figure.figsize": (figure_width, figure_height),
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "figure.facecolor": PALETTE["background"],
            "savefig.facecolor": PALETTE["background"],
            # -----------------------------------------------------------------
            # Typography
            # -----------------------------------------------------------------
            "font.family": font_family,
            "font.serif": FONT_SERIF_FALLBACKS,
            "font.sans-serif": FONT_SANS_FALLBACKS,
            "font.size": font_size,
            "axes.titlesize": font_size + 1.5,
            "axes.labelsize": font_size,
            "xtick.labelsize": max(font_size - 1, 7),
            "ytick.labelsize": max(font_size - 1, 7),
            "legend.fontsize": max(font_size - 1, 7),
            # -----------------------------------------------------------------
            # Math typography
            # -----------------------------------------------------------------
            # STIX provides high-quality mathematical glyphs while keeping
            # the surrounding figure in a serif academic style.
            "mathtext.fontset": "stix",
            # -----------------------------------------------------------------
            # Axes
            # -----------------------------------------------------------------
            "axes.facecolor": PALETTE["background"],
            "axes.edgecolor": PALETTE["charcoal"],
            "axes.labelcolor": PALETTE["charcoal"],
            "axes.titlecolor": PALETTE["charcoal"],
            "axes.linewidth": 0.8,
            # -----------------------------------------------------------------
            # Grid
            # -----------------------------------------------------------------
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": PALETTE["gray_light"],
            "grid.linewidth": 0.6,
            # EPS/PostScript does not preserve transparency reliably.
            "grid.alpha": 1.0,
            # -----------------------------------------------------------------
            # Ticks
            # -----------------------------------------------------------------
            "xtick.color": PALETTE["slate"],
            "ytick.color": PALETTE["slate"],
            "xtick.major.width": 0.7,
            "ytick.major.width": 0.7,
            "xtick.minor.width": 0.5,
            "ytick.minor.width": 0.5,
            # -----------------------------------------------------------------
            # Lines / markers
            # -----------------------------------------------------------------
            "lines.linewidth": line_width,
            "lines.markersize": marker_size,
            # -----------------------------------------------------------------
            # Legend
            # -----------------------------------------------------------------
            "legend.frameon": False,
            "legend.borderaxespad": 0.5,
            "legend.handlelength": 2.2,
            # -----------------------------------------------------------------
            # Error bars
            # -----------------------------------------------------------------
            "errorbar.capsize": 3,
            # -----------------------------------------------------------------
            # Publication/vector output
            # -----------------------------------------------------------------
            "pdf.fonttype": 42,
            # Type 3 embeds the Times New Roman glyphs as vector outlines,
            # which is more reliably rendered by EPS previewers and editors.
            "ps.fonttype": 3,
            "svg.fonttype": "none",
            # -----------------------------------------------------------------
            # Default color cycle
            # -----------------------------------------------------------------
            "axes.prop_cycle": cycler(color=CATEGORICAL),
        }
    )

    register_colormaps()


# =============================================================================
# 7. OPTIONAL SEABORN SUPPORT
# =============================================================================


def apply_seaborn_style(
    *,
    preset: str = "thesis",
) -> None:
    """
    Apply the Phthalo Green style to Seaborn.

    Seaborn is imported only when this function is called, so Seaborn is
    optional for users who work exclusively with Matplotlib.
    """

    try:
        import seaborn as sns
    except ImportError as exc:
        raise ImportError(
            "Seaborn is not installed. Install it with "
            "`pip install seaborn`, or use apply_style() for Matplotlib."
        ) from exc

    apply_style(preset=preset)

    sns.set_palette(CATEGORICAL)

    sns.set_theme(
        style="whitegrid",
        rc={
            "axes.facecolor": PALETTE["background"],
            "figure.facecolor": PALETTE["background"],
            "grid.color": PALETTE["gray_light"],
            "grid.linewidth": 0.6,
            "axes.edgecolor": PALETTE["charcoal"],
            "text.color": PALETTE["charcoal"],
            "axes.labelcolor": PALETTE["charcoal"],
            "xtick.color": PALETTE["slate"],
            "ytick.color": PALETTE["slate"],
            "font.family": FONT_FAMILY,
            "font.serif": FONT_SERIF_FALLBACKS,
        },
    )

    sns.set_palette(CATEGORICAL)


# =============================================================================
# 8. PALETTE HELPERS
# =============================================================================


def get_color(name: str = "primary") -> str:
    """
    Return a named color.

    Example
    -------
    color = get_color("primary")
    """

    try:
        return PALETTE[name]
    except KeyError as exc:
        available = ", ".join(PALETTE.keys())
        raise KeyError(
            f"Unknown color '{name}'. Available colors: {available}"
        ) from exc


def get_palette(
    palette: str = "categorical",
    n: int | None = None,
) -> list[str]:
    """
    Return a predefined palette.

    Parameters
    ----------
    palette:
        "categorical"
        "categorical_green"
        "sequential"
        "diverging"

    n:
        Optional number of colors to generate.

    Examples
    --------
    get_palette("categorical", 4)
    get_palette("sequential", 6)
    """

    palettes: Mapping[str, list[str]] = {
        "categorical": CATEGORICAL,
        "categorical_green": CATEGORICAL_GREEN,
        "sequential": SEQUENTIAL,
        "diverging": DIVERGING,
    }

    key = palette.lower()

    if key not in palettes:
        available = ", ".join(palettes)
        raise KeyError(f"Unknown palette '{palette}'. Available palettes: {available}")

    selected = palettes[key]

    if n is None:
        return selected.copy()

    if n < 1:
        raise ValueError("n must be at least 1.")

    if n == 1:
        return [selected[len(selected) // 2]]

    cmap = mcolors.LinearSegmentedColormap.from_list(
        f"temporary_{key}",
        selected,
        N=256,
    )

    return [mcolors.to_hex(cmap(i / (n - 1))) for i in range(n)]


# =============================================================================
# 9. FIGURE-SPECIFIC HELPERS
# =============================================================================


def style_axis(
    ax,
    *,
    grid: bool = True,
    remove_top_right_spines: bool = False,
) -> None:
    """
    Apply final axis-level formatting.

    This is useful when you need more control than apply_style() provides.
    """

    ax.set_facecolor(PALETTE["background"])

    ax.tick_params(
        colors=PALETTE["slate"],
        width=0.7,
    )

    for spine in ax.spines.values():
        spine.set_color(PALETTE["charcoal"])
        spine.set_linewidth(0.8)

    if remove_top_right_spines:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    ax.grid(
        grid,
        color=PALETTE["gray_light"],
        linewidth=0.6,
        alpha=1.0,
    )


def style_legend(legend) -> None:
    """Apply restrained academic formatting to a Matplotlib legend."""

    if legend is None:
        return

    legend.set_frame_on(False)

    for text in legend.get_texts():
        text.set_color(PALETTE["charcoal"])


# =============================================================================
# 10. PUBLICATION EXPORT
# =============================================================================

PUBLICATION_FORMATS: dict[str, dict[str, object]] = {
    "pdf": {
        "format": "pdf",
        "dpi": 300,
        "description": (
            "Preferred for LaTeX and journal workflows because it preserves "
            "vector graphics."
        ),
    },
    "svg": {
        "format": "svg",
        "dpi": 300,
        "description": (
            "Vector format useful for editing figures in compatible tools."
        ),
    },
    "png": {
        "format": "png",
        "dpi": 600,
        "description": (
            "Preferred raster format when a journal requires bitmap figures."
        ),
    },
    "eps": {
        "format": "eps",
        "dpi": 300,
        "description": (
            "Legacy vector format for publication workflows that require EPS."
        ),
    },
}


def save_publication_figure(
    fig,
    filename: str,
    *,
    transparent: bool = False,
    dpi: int = 300,
    bbox_inches: str = "tight",
) -> None:
    """
    Save a Matplotlib figure using publication-friendly defaults.

    Parent directories are created automatically, so ``figures/ch1/fig.pdf``
    works even when ``figures/ch1/`` does not exist yet.

    Examples
    --------
    save_publication_figure(fig, "results.pdf")
    save_publication_figure(fig, "results.svg")
    save_publication_figure(fig, "results.png", dpi=600)
    """

    parent = Path(filename).parent
    if str(parent) not in ("", "."):
        parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        filename,
        dpi=dpi,
        bbox_inches=bbox_inches,
        transparent=transparent,
    )


def export_figure(
    fig,
    basename: str | Path,
    *,
    formats: tuple[str, ...] = ("pdf", "png"),
    png_dpi: int = 600,
    transparent: bool = False,
    bbox_inches: str = "tight",
    close: bool = True,
) -> list[Path]:
    """
    Save one figure in several publication formats at once.

    Parameters
    ----------
    fig:
        Matplotlib figure to save.

    basename:
        Path without extension, e.g. ``figures/01_trend``.
        Extensions are appended automatically.

    formats:
        Any combination of ``"pdf"``, ``"svg"``, ``"png"``, ``"eps"``.

    png_dpi:
        DPI used for raster ``png`` output. Vector formats use 300.

    close:
        Close the figure after saving (default True, ideal for batch runs).

    Returns
    -------
    List of written file paths.

    Example
    -------
    fig, ax = subplots()
    ax.plot(x, y)
    export_figure(fig, "figures/01_trend", formats=("pdf", "png", "svg"))
    """

    base = Path(basename)
    if str(base.parent) not in ("", "."):
        base.parent.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for fmt in formats:
        fmt = fmt.lower().lstrip(".")
        if fmt not in PUBLICATION_FORMATS:
            available = ", ".join(PUBLICATION_FORMATS)
            raise ValueError(f"Unknown format '{fmt}'. Available: {available}")
        path = base.with_suffix(f".{fmt}")
        dpi = png_dpi if fmt == "png" else 300
        save_publication_figure(
            fig,
            str(path),
            dpi=dpi,
            transparent=transparent,
            bbox_inches=bbox_inches,
        )
        written.append(path)

    if close:
        import matplotlib.pyplot as plt

        plt.close(fig)

    return written


# =============================================================================
# 11. LATEX COMPATIBILITY
# =============================================================================


def configure_latex(
    *,
    use_tex: bool = False,
) -> None:
    """
    Configure optional LaTeX rendering.

    By default this does NOT enable LaTeX because a working LaTeX
    installation is required on the machine.

    Set use_tex=True only when your system has a functional LaTeX
    installation and you want Matplotlib text rendered through LaTeX.
    """

    mpl.rcParams["text.usetex"] = use_tex

    if use_tex:
        mpl.rcParams.update(
            {
                "font.family": "serif",
                "font.serif": ["Times New Roman", "Times"],
            }
        )


# =============================================================================
# 12. INFORMATION / DIAGNOSTICS
# =============================================================================


def print_style_info() -> None:
    """Print a concise summary of the active Phthalo Green style."""

    print("Phthalo Green Academic Visualization Style")
    print("=" * 48)
    print(f"Primary color : {PHTHALO_GREEN}")
    print(f"Font family   : {FONT_FAMILY}")
    print("Font priority :")
    for font in FONT_SERIF_FALLBACKS:
        print(f"  - {font}")
    print()
    print("Available presets:")
    for preset in STYLE_PRESETS:
        print(f"  - {preset}")
    print()
    print("Available palettes:")
    print("  - categorical")
    print("  - categorical_green")
    print("  - sequential")
    print("  - diverging")


# =============================================================================
# 13. TEMPLATE HELPERS (new-project friendly)
# =============================================================================
#
# These are thin conveniences on top of apply_style() so that every future
# project starts from the same two lines:
#
#     from phthalo_green import subplots, export_figure
#     fig, ax = subplots()
#     ...
#     export_figure(fig, "figures/my_fig")
#


@contextmanager
def styled(preset: str = "thesis", **overrides) -> Iterator[None]:
    """
    Temporarily apply the Phthalo Green style.

    Restores the previous rcParams on exit. Useful in notebooks or when
    mixing styles in one process.

    Example
    -------
    with styled("journal"):
        fig, ax = plt.subplots()
        ...
    """
    previous = mpl.rcParams.copy()
    try:
        apply_style(preset=preset, **overrides)
        yield
    finally:
        mpl.rcParams.update(previous)


def figure(preset: str = "thesis", *args, **kwargs):
    """
    Create a new figure with the style applied.

    Equivalent to ``apply_style(preset)`` + ``plt.figure()``.
    Style overrides (font_size, figure_width, ...) are consumed;
    remaining kwargs go to ``plt.figure()``.
    """
    import matplotlib.pyplot as plt

    style_keys = {
        "font_family",
        "font_size",
        "figure_width",
        "figure_height",
        "line_width",
        "marker_size",
    }
    style_kwargs = {k: kwargs.pop(k) for k in list(kwargs) if k in style_keys}
    apply_style(preset=preset, **style_kwargs)
    return plt.figure(*args, **kwargs)


def subplots(preset: str = "thesis", *args, **kwargs):
    """
    Create ``fig, ax`` (or arrays) with the style applied.

    All extra args are forwarded to ``plt.subplots`` except style
    overrides (font_size, figure_width, figure_height, line_width,
    marker_size, font_family).

    Example
    -------
    fig, ax = subplots(preset="journal")
    fig, axes = subplots(preset="thesis", nrows=2, ncols=2)
    fig, ax = subplots("journal", figsize=(8, 4))
    """
    import matplotlib.pyplot as plt

    style_keys = {
        "font_family",
        "font_size",
        "figure_width",
        "figure_height",
        "line_width",
        "marker_size",
    }
    style_kwargs = {k: kwargs.pop(k) for k in list(kwargs) if k in style_keys}
    apply_style(preset=preset, **style_kwargs)
    return plt.subplots(*args, **kwargs)


# =============================================================================
# 14. MODULE EXPORTS
# =============================================================================

__all__ = [  # noqa: RUF022 — grouped by theme, not alphabetically
    # Core colors
    "PALETTE",
    "PHTHALO_GREEN",
    "DEEP_PHTHALO_GREEN",
    "MEDIUM_PHTHALO_GREEN",
    "EMERALD_GREEN",
    "LIGHT_GREEN",
    "PALE_GREEN",
    # Typography
    "FONT_FAMILY",
    "FONT_SERIF_FALLBACKS",
    "WORDCLOUD_FONT_PATH",
    "FONT_SANS_FALLBACKS",
    # Palettes
    "CATEGORICAL",
    "CATEGORICAL_GREEN",
    "SEQUENTIAL",
    "DIVERGING",
    # Colormaps
    "SEQUENTIAL_CMAP",
    "DIVERGING_CMAP",
    # Presets
    "STYLE_PRESETS",
    # Publication
    "PUBLICATION_FORMATS",
    # Functions
    "apply_style",
    "apply_seaborn_style",
    "register_colormaps",
    "get_color",
    "get_palette",
    "style_axis",
    "style_legend",
    "save_publication_figure",
    "export_figure",
    "styled",
    "figure",
    "subplots",
    "configure_latex",
    "print_style_info",
]


# =============================================================================
# 15. SELF TEST
# =============================================================================

if __name__ == "__main__":
    print_style_info()
    print()
    print("Module loaded successfully.")
