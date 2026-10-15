"""
Phthalo Green Academic Visualization Style
==========================================

A reusable, publication-oriented visualization style for:
    - PhD theses
    - Journal papers
    - Conference papers
    - Research reports
    - Technical documentation
    - Academic presentations

Design principles
-----------------
1. Phthalo Green is the primary visual identity (the default theme).
2. Every theme is a plain data object, so new palettes plug in without
   touching the styling code (see ``register_theme`` / ``register_palette``).
3. Times New Roman is the preferred academic font, with a robust serif
   fallback chain for Linux/macOS/CI systems.
4. Figures use restrained styling suitable for academic publication.
5. Vector formats (PDF/SVG) are preferred when supported.
6. Sequential, categorical, and diverging palettes are provided.
7. Matplotlib is required; Seaborn and Plotly support is optional.
8. The module is intentionally self-contained (only ``matplotlib`` needed),
   which keeps the "copy one file into your project" workflow viable.

Basic usage
-----------
    import matplotlib.pyplot as plt
    import phthalo_green as pg

    fig, ax = pg.subplots()
    ax.plot(x, y, color=pg.PALETTE["primary"])
    pg.export_figure(fig, "figures/results")

Multiple series
---------------
    for i, series in enumerate(series_list):
        ax.plot(x, series, color=pg.CATEGORICAL[i])

Heatmap
-------
    ax.imshow(matrix, cmap=pg.get_cmap("sequential"))

Other themes
------------
    pg.set_theme("indigo")            # switch palette everywhere
    pg.register_palette("mine", {...})
    with_theme("phthalo_green"):
        ...

Publication export
-----------------
    save_publication_figure(fig, "results.pdf")
    save_publication_figure(fig, "results.png", dpi=600)

Author
------
Research Visualization Style — Phthalo Green Academic Standard
"""

from __future__ import annotations

import colorsys
import warnings
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

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
# Colour roles used throughout the library:
#   ramp        dark -> primary -> medium -> accent -> light -> pale
#   accents     optional supporting hues for categorical separation
#   neutrals    text, grid, background
#

PALETTE: dict[str, str] = {
    # -------------------------------------------------------------------------
    # Phthalo Green family (the ramp)
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

# Colour-role ordering (used to auto-complete user supplied palettes).
RAMP_KEYS: tuple[str, ...] = ("dark", "primary", "medium", "accent", "light", "pale")
ACCENT_KEYS: tuple[str, ...] = ("blue_green", "blue", "ochre", "rust", "plum")
NEUTRAL_KEYS: tuple[str, ...] = (
    "charcoal",
    "slate",
    "gray",
    "gray_light",
    "background",
    "white",
)

# Palette kinds understood by ``Theme.palette`` / ``get_palette`` / ``get_cmap``.
PALETTE_KINDS: tuple[str, ...] = (
    "categorical",
    "categorical_green",
    "sequential",
    "diverging",
)

# Names accepted as aliases when asking for a palette kind.
_PALETTE_ALIASES: dict[str, str] = {
    "cat": "categorical",
    "categorical": "categorical",
    "categories": "categorical",
    "categorical_green": "categorical_green",
    "green": "categorical_green",
    "mono": "categorical_green",
    "seq": "sequential",
    "sequential": "sequential",
    "div": "diverging",
    "diverging": "diverging",
}

# Kinds that have a corresponding Matplotlib colormap.
_CMAP_KINDS: tuple[str, ...] = ("categorical", "categorical_green", "sequential", "diverging")


# =============================================================================
# 2. COLOUR UTILITIES
# =============================================================================


def to_hex(color: Any) -> str:
    """
    Normalize any Matplotlib color specification to a lowercase ``#rrggbb``.

    Accepts hex strings (3 or 6 digits), CSS4 color names, and RGB(A)
    tuples/lists in the 0-1 range.
    """

    try:
        return mcolors.to_hex(color).lower()
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Could not interpret {color!r} as a color.") from exc


def mix(color_a: Any, color_b: Any, amount: float = 0.5) -> str:
    """
    Blend two colors in sRGB space.

    ``amount=0.0`` returns ``color_a`` and ``amount=1.0`` returns ``color_b``.
    """

    r1, g1, b1, _ = mcolors.to_rgba(color_a)
    r2, g2, b2, _ = mcolors.to_rgba(color_b)
    r = r1 + (r2 - r1) * amount
    g = g1 + (g2 - g1) * amount
    b = b1 + (b2 - b1) * amount
    return to_hex((r, g, b))


def lighten(color: Any, amount: float = 0.25) -> str:
    """Mix a color towards white. ``amount`` is clamped to [0, 1]."""

    return mix(color, "#FFFFFF", max(0.0, min(1.0, amount)))


def darken(color: Any, amount: float = 0.25) -> str:
    """Mix a color towards black. ``amount`` is clamped to [0, 1]."""

    return mix(color, "#000000", max(0.0, min(1.0, amount)))


def shift_hue(color: Any, degrees: float) -> str:
    """Rotate the hue of a color, keeping its lightness and saturation."""

    r, g, b, _ = mcolors.to_rgba(color)
    h, lightness, s = colorsys.rgb_to_hls(r, g, b)
    h = (h + degrees / 360.0) % 1.0
    return to_hex(colorsys.hls_to_rgb(h, lightness, s))


def with_alpha(color: Any, alpha: float = 1.0) -> tuple[float, float, float, float]:
    """
    Return an RGBA tuple suitable for Matplotlib ``alpha``-style arguments.

    Unlike ``matplotlib.colors.to_rgba`` the input may already carry an
    alpha channel, which is then multiplied by ``alpha``.
    """

    r, g, b, a = mcolors.to_rgba(color)
    return (r, g, b, a * alpha)


def css_rgba(color: Any, alpha: float = 1.0) -> str:
    """Return a CSS ``rgba(...)`` string, as used by Plotly/Vega templates."""

    r, g, b, a = with_alpha(color, alpha)
    return f"rgba({r * 255:.0f}, {g * 255:.0f}, {b * 255:.0f}, {a:.4f})"


def relative_luminance(color: Any) -> float:
    """WCAG relative luminance of a color, in the range [0, 1]."""

    r, g, b, _ = mcolors.to_rgba(color)

    def channel(value: float) -> float:
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(color_a: Any, color_b: Any) -> float:
    """
    WCAG contrast ratio between two colors (1.0 = identical, 21.0 = max).

    Useful to check that text/axis colors stay readable on the figure
    background and in grayscale printouts.
    """

    lum_a = relative_luminance(color_a)
    lum_b = relative_luminance(color_b)
    lighter, darker = max(lum_a, lum_b), min(lum_a, lum_b)
    return (lighter + 0.05) / (darker + 0.05)


# =============================================================================
# 3. TYPOGRAPHY
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

MATH_FONTSET = "stix"


def resolved_serif_font() -> str:
    """Return the name of the serif font Matplotlib will actually use."""

    found = font_manager.findfont(
        font_manager.FontProperties(family=FONT_SERIF_FALLBACKS),
        fallback_to_default=True,
    )
    return Path(found).name


# =============================================================================
# 4. THEMES
# =============================================================================
#
# A Theme is a plain data object that owns:
#   * the full colour dictionary (ramp + accents + neutrals)
#   * the four ready-to-use palettes
#   * the font stack and math fontset
#
# Everything downstream (rcParams, colormaps, Seaborn/Plotly adapters,
# export helpers) reads from the active theme, so registering a new palette
# is the only step needed to support a completely different look.


@dataclass(frozen=True)
class Theme:
    """A complete, self-contained colour + typography palette."""

    name: str
    colors: dict[str, str] = field(default_factory=dict)
    categorical: list[str] = field(default_factory=list)
    categorical_green: list[str] = field(default_factory=list)
    sequential: list[str] = field(default_factory=list)
    diverging: list[str] = field(default_factory=list)
    serif: Sequence[str] = field(default_factory=lambda: list(FONT_SERIF_FALLBACKS))
    sans: Sequence[str] = field(default_factory=lambda: list(FONT_SANS_FALLBACKS))
    math_fontset: str = MATH_FONTSET
    label: str = ""
    description: str = ""
    is_default: bool = False

    def __post_init__(self) -> None:
        # Frozen dataclass, but the colormap cache is genuinely mutable state.
        object.__setattr__(self, "_cache", {})

    # -- color access -------------------------------------------------------

    def __getitem__(self, key: str) -> str:
        return self.colors[key]

    def __contains__(self, key: object) -> bool:
        return key in self.colors

    def get(self, key: str, default: str | None = None) -> str | None:
        """Return a named color, e.g. ``theme["primary"]``."""

        return self.colors.get(key, default)

    def color(self, key: str) -> str:
        """Return a named color, raising a helpful error for typos."""

        try:
            return self.colors[key]
        except KeyError as exc:
            available = ", ".join(self.colors)
            raise KeyError(
                f"Theme '{self.name}' has no color '{key}'. Available: {available}"
            ) from exc

    def __getattr__(self, key: str) -> Any:
        # Only runs when normal lookup fails; guard against recursion during
        # unpickling/copying before ``colors`` exists.
        colors = self.__dict__.get("colors")
        if colors is None or key.startswith("_"):
            raise AttributeError(key)
        try:
            return colors[key]
        except KeyError:
            raise AttributeError(
                f"Theme '{self.name}' has no attribute or color '{key}'. "
                f"Color roles: {', '.join(colors)}"
            ) from None

    # -- palettes ----------------------------------------------------------

    def palettes(self) -> dict[str, list[str]]:
        """Return all palettes as fresh lists keyed by palette kind."""

        return {
            "categorical": list(self.categorical),
            "categorical_green": list(self.categorical_green),
            "sequential": list(self.sequential),
            "diverging": list(self.diverging),
        }

    def palette(self, kind: str = "categorical", n: int | None = None) -> list[str]:
        """
        Return one palette by name, optionally resampled to ``n`` colors.

        When ``n`` is smaller than the palette length the first ``n`` colors
        are returned unchanged (they are hand-picked to stay distinguishable);
        larger values interpolate along the corresponding colormap.
        """

        selected = self._palette_for(kind)

        if n is None:
            return list(selected)

        if n < 1:
            raise ValueError("n must be at least 1.")

        if n == 1:
            return [selected[len(selected) // 2]]

        if n <= len(selected):
            return list(selected[:n])

        cmap = self.cmap(kind)
        return [to_hex(cmap(i / (n - 1))) for i in range(n)]

    def _palette_for(self, kind: str) -> list[str]:
        key = _palette_key(kind)
        if key not in PALETTE_KINDS:
            available = ", ".join(PALETTE_KINDS)
            raise KeyError(f"Unknown palette '{kind}'. Available: {available}")
        return list(getattr(self, key))

    # -- colormaps ---------------------------------------------------------

    def cmap_name(self, kind: str = "sequential") -> str:
        """Name the theme's colormap of ``kind`` is registered under."""

        key = _palette_key(kind)
        if key not in _CMAP_KINDS:
            available = ", ".join(PALETTE_KINDS)
            raise KeyError(f"Unknown colormap kind '{kind}'. Available: {available}")
        if key == "sequential":
            return self.name
        return f"{self.name}_{key}"

    def cmap(self, kind: str = "sequential") -> mcolors.Colormap:
        """Build (once) and return the theme's colormap for ``kind``."""

        cache: dict[str, mcolors.Colormap] = self.__dict__["_cache"]
        if kind not in cache:
            name = self.cmap_name(kind)
            colors = self._palette_for(kind)
            if kind == "categorical" or kind == "categorical_green":
                cache[kind] = mcolors.ListedColormap(colors, name=name)
            else:
                cache[kind] = mcolors.LinearSegmentedColormap.from_list(
                    name, colors, N=256
                )
        return cache[kind]

    def cat_cmap(self) -> mcolors.Colormap:
        """Discrete ListedColormap for the categorical palette."""

        return self.cmap("categorical")

    def cmaps(self) -> dict[str, mcolors.Colormap]:
        """All colormaps for this theme, keyed by palette kind."""

        return {kind: self.cmap(kind) for kind in _CMAP_KINDS}

    # -- fonts -------------------------------------------------------------

    def font_stack(self) -> str:
        """CSS font stack, e.g. ``"'Times New Roman', 'DejaVu Serif', serif"``."""

        quoted = [f"'{name}'" if " " in name else name for name in self.serif]
        return ", ".join(quoted + ["serif"])

    def summary(self) -> dict[str, Any]:
        """Machine readable description, handy for docs and tests."""

        return {
            "name": self.name,
            "label": self.label or self.name,
            "description": self.description,
            "colors": dict(self.colors),
            "palettes": self.palettes(),
            "serif": list(self.serif),
            "sans": list(self.sans),
            "math_fontset": self.math_fontset,
            "colormaps": {k: v.name for k, v in self.cmaps().items()},
        }


def _palette_key(kind: str) -> str:
    """Normalize user supplied palette names to canonical keys."""

    key = str(kind).strip().lower().replace("-", "_").replace(" ", "_")
    return _PALETTE_ALIASES.get(key, key)


# --- palette auto-completion ------------------------------------------------


def _as_ramp(values: Sequence[Any]) -> dict[str, str]:
    """Turn an ordered dark->light list of colors into the 6 ramp roles."""

    colors = [to_hex(v) for v in values]
    if not colors:
        raise ValueError("A color ramp needs at least one color.")
    if len(colors) > 6:
        colors = [to_hex(colors[round(i * (len(colors) - 1) / 5)]) for i in range(6)]
    ramp = {key: to_hex(color) for key, color in zip(RAMP_KEYS, colors)}
    return _fill_ramp(ramp)


def _fill_ramp(colors: Mapping[str, str]) -> dict[str, str]:
    """Fill in any missing ramp roles by interpolating the known ones."""

    out = dict(colors)
    present = [i for i, key in enumerate(RAMP_KEYS) if key in out]

    if not present:
        raise ValueError(
            "A theme needs at least one ramp color: " + ", ".join(RAMP_KEYS)
        )

    steps = len(RAMP_KEYS) - 1

    if len(present) == 1:
        index = present[0]
        anchor = out[RAMP_KEYS[index]]
        for position in range(len(RAMP_KEYS)):
            if position == index:
                continue
            distance = abs(position - index) / steps
            if position < index:
                out[RAMP_KEYS[position]] = darken(anchor, distance)
            else:
                out[RAMP_KEYS[position]] = lighten(anchor, distance)
        return out

    for position in range(len(RAMP_KEYS)):
        if position in present:
            continue

        lower = [i for i in present if i < position]
        upper = [i for i in present if i > position]

        if lower and upper:
            low, high = max(lower), min(upper)
            out[RAMP_KEYS[position]] = mix(
                out[RAMP_KEYS[low]],
                out[RAMP_KEYS[high]],
                (position - low) / (high - low),
            )
            continue

        # Outside the known range: keep marching towards black or white so
        # the ramp stays monotonic instead of repeating a color.
        anchor_index = max(lower) if lower else min(upper)
        anchor = out[RAMP_KEYS[anchor_index]]
        distance = abs(position - anchor_index) / steps
        if position < anchor_index:
            out[RAMP_KEYS[position]] = darken(anchor, distance)
        else:
            out[RAMP_KEYS[position]] = lighten(anchor, distance)

    return out


def _derive_accents(primary: str) -> dict[str, str]:
    """Hue-rotate ``primary`` to generate distinguishable accents."""

    targets = {
        "ochre": 45.0,
        "rust": 8.0,
        "plum": 300.0,
        "blue_green": 185.0,
        "blue": 215.0,
    }
    _, lightness, saturation = colorsys.rgb_to_hls(*mcolors.to_rgb(primary)[:3])
    # Keep accents legible regardless of how dark the primary color is.
    lightness = min(max(lightness + 0.06, 0.34), 0.52)
    saturation = min(max(saturation * 1.1, 0.28), 0.7)
    return {
        name: to_hex(colorsys.hls_to_rgb(hue / 360.0, lightness, saturation))
        for name, hue in targets.items()
    }


def _derive_neutrals(primary: str, pale: str) -> dict[str, str]:
    """Generate text/grid/background neutrals tinted by the theme hue."""

    charcoal = mix("#2E3438", primary, 0.08)
    return {
        "charcoal": charcoal,
        "slate": mix(charcoal, pale, 0.38),
        "gray": mix(charcoal, pale, 0.62),
        "gray_light": mix(mix(charcoal, pale, 0.62), "#ffffff", 0.82),
        "background": mix("#ffffff", pale, 0.045),
        "white": "#ffffff",
    }


def _build_categorical(colors: Mapping[str, str]) -> list[str]:
    """Interleave the ramp with the supporting accents."""

    accents = ("ochre", "blue", "plum", "rust", "blue_green")
    present = [colors[name] for name in accents if colors.get(name)]
    order = ["dark", "primary", "medium", "accent", "light", "pale"]
    palette = [colors[name] for name in order]
    palette[3:3] = present[:4]
    return _dedupe(palette)[:10]


def _build_sequential(colors: Mapping[str, str]) -> list[str]:
    """Light -> dark, with intermediate steps for smooth gradients."""

    ramp = ["pale", "light", "accent", "medium", "primary", "dark"]
    stops = [colors[name] for name in ramp]
    palette: list[str] = []
    for index, value in enumerate(stops[:-1]):
        palette.append(value)
        palette.append(mix(value, stops[index + 1], 0.5))
    palette.append(stops[-1])
    return _dedupe(palette)


def _build_diverging(colors: Mapping[str, str]) -> list[str]:
    """Warm neutral -> cool, symmetric around the lightest neutral step."""

    rust = colors.get("rust") or shift_hue(colors["primary"], 165)
    neutral = colors.get("gray_light", "#E7EBE9")
    return _dedupe([
        darken(rust, 0.22),
        rust,
        lighten(rust, 0.42),
        neutral,
        lighten(colors["accent"], 0.45),
        colors["accent"],
        colors["medium"],
        colors["primary"],
    ])


def _dedupe(colors: Sequence[str]) -> list[str]:
    """Remove duplicate colors while preserving order."""

    seen: set[str] = set()
    out: list[str] = []
    for color in colors:
        value = to_hex(color)
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def make_theme(
    name: str,
    colors: Mapping[str, str] | Sequence[str] | str,
    *,
    categorical: Sequence[str] | None = None,
    sequential: Sequence[str] | None = None,
    diverging: Sequence[str] | None = None,
    serif: Sequence[str] | None = None,
    sans: Sequence[str] | None = None,
    math_fontset: str | None = None,
    label: str | None = None,
    description: str | None = None,
) -> Theme:
    """
    Build a complete :class:`Theme` from as little as one anchor color.

    ``colors`` accepts either

    * a single anchor color, e.g. ``"#1A4A9E"``,
    * a mapping of role names to colors (any subset of ``RAMP_KEYS``,
      ``ACCENT_KEYS`` and ``NEUTRAL_KEYS``), or
    * an ordered dark -> light list of colors, e.g. ``["#1a3a2a", "#e8f2ec"]``.

    Anything missing is derived automatically (hue rotation for accents,
    lightness interpolation for ramp steps, tinted neutrals for text/grid).

    Examples
    --------
    make_theme("mine", "#2F6F4E", label="My Green")

    make_theme("mine", {"primary": "#2F6F4E"}, label="My Green")

    make_theme("brand", ["#12261F", "#1E8C62", "#DDEBE3"])
    """

    key = _theme_key(name)
    if not key:
        raise ValueError("A theme name is required.")

    if isinstance(colors, str):
        supplied = {"primary": to_hex(colors)}
    elif isinstance(colors, Mapping):
        supplied = {str(k).strip().lower(): to_hex(v) for k, v in colors.items()}
    else:
        values = list(colors)
        if len(values) == 1:
            supplied = {"primary": to_hex(values[0])}
        else:
            supplied = _as_ramp(values)

    full = dict(supplied)
    full.update(_fill_ramp(supplied))

    for role in ACCENT_KEYS:
        if role not in full:
            full.update({role: _derive_accents(full["primary"])[role]})
    for role, value in _derive_neutrals(full["primary"], full["pale"]).items():
        full.setdefault(role, value)

    unknown = sorted(set(full) - set(RAMP_KEYS) - set(ACCENT_KEYS) - set(NEUTRAL_KEYS))
    if unknown:
        raise ValueError(
            f"Theme '{key}' has unknown color roles: {', '.join(unknown)}. "
            f"Valid roles are: "
            f"{', '.join(RAMP_KEYS + ACCENT_KEYS + NEUTRAL_KEYS)}"
        )

    if categorical is not None:
        palette_cat = _dedupe(list(categorical))
    else:
        palette_cat = _build_categorical(full)

    if sequential is not None:
        palette_seq = _dedupe(list(sequential))
    else:
        palette_seq = _build_sequential(full)

    if diverging is not None:
        palette_div = _dedupe(list(diverging))
    else:
        palette_div = _build_diverging(full)

    return Theme(
        name=key,
        colors=full,
        categorical=palette_cat,
        categorical_green=_dedupe([full[k] for k in RAMP_KEYS]),
        sequential=palette_seq,
        diverging=palette_div,
        serif=list(serif) if serif is not None else list(FONT_SERIF_FALLBACKS),
        sans=list(sans) if sans is not None else list(FONT_SANS_FALLBACKS),
        math_fontset=math_fontset or MATH_FONTSET,
        label=label or key.replace("_", " ").title(),
        description=description or "",
    )


# --- theme registry ---------------------------------------------------------


def _theme_key(name: str | Theme) -> str:
    """Normalize a theme name: 'Phthalo Green' -> 'phthalo_green'."""

    return str(name).strip().lower().replace("-", "_").replace(" ", "_")


THEMES: dict[str, Theme] = {}

DEFAULT_THEME_NAME = "phthalo_green"


def register_theme(theme: Theme, *, override: bool = False) -> Theme:
    """
    Register a :class:`Theme` so it can be selected by name.

    Raises
    ------
    ValueError
        If the name is already taken and ``override`` is False.
    """

    key = _theme_key(theme.name)
    if key in THEMES and not override:
        raise ValueError(
            f"Theme '{key}' is already registered. Pass override=True to replace it."
        )
    if key != theme.name:
        raise ValueError("Theme names must already be normalized.")
    if key in mpl.colormaps and key not in _REGISTERED_CMAPS:
        warnings.warn(
            f"Theme name '{key}' also names a built-in Matplotlib colormap; "
            "the theme's colormap will shadow it for this session.",
            stacklevel=2,
        )
    object.__setattr__(theme, "name", key)
    THEMES[key] = theme
    return theme


def register_palette(
    name: str,
    colors: Mapping[str, str] | Sequence[str] | str,
    *,
    override: bool = False,
    **kwargs: Any,
) -> Theme:
    """
    Create, register, and return a theme in one call.

    ``colors`` may be a single anchor color, an ordered dark->light ramp,
    or a role -> color mapping (see :func:`make_theme`).

    Examples
    --------
    register_palette("slate", "#28405A", label="Slate Blue")
    register_palette("slate", {"primary": "#28405A"}, label="Slate Blue")
    register_palette("brand", ["#12261F", "#1E8C62", "#DDEBE3"])

    Then use it anywhere:

        apply_style(theme="slate")
        fig, ax = pg.subplots(theme="brand")
    """

    theme = make_theme(name, colors, **kwargs)
    register_theme(theme, override=override)
    return theme


def get_theme(name: str | Theme | None = None) -> Theme:
    """
    Return a theme by name, or the active theme when ``name`` is None.

    Accepts a :class:`Theme` instance as a convenience, which is returned
    unchanged.
    """

    if name is None:
        if _ACTIVE_THEME is None:  # pragma: no cover - set during import
            raise RuntimeError("No active theme; call set_theme() first.")
        return _ACTIVE_THEME
    if isinstance(name, Theme):
        return name
    key = _theme_key(name)
    try:
        return THEMES[key]
    except KeyError as exc:
        available = ", ".join(list_themes())
        raise KeyError(
            f"Unknown theme '{name}'. Available themes: {available}"
        ) from exc


def list_themes() -> list[str]:
    """Names of all registered themes, default theme first."""

    return sorted(THEMES, key=lambda name: (not THEMES[name].is_default, name))


def active_theme() -> Theme:
    """The theme currently used for colors, palettes, and colormaps."""

    return get_theme(None)


_ACTIVE_THEME: Theme | None = None


def _sync_live_globals(theme: Theme) -> None:
    """
    Refresh the module level color containers in place.

    ``PALETTE``, ``CATEGORICAL``, ... are mutated rather than rebound so
    that ``from phthalo_green import PALETTE`` keeps working after a theme
    change.
    """

    PALETTE.clear()
    PALETTE.update(theme.colors)
    CATEGORICAL[:] = theme.categorical
    CATEGORICAL_GREEN[:] = theme.categorical_green
    SEQUENTIAL[:] = theme.sequential
    DIVERGING[:] = theme.diverging


def _apply_theme_rc(theme: Theme) -> None:
    """Push the theme colors into the live rcParams."""

    colors = theme.colors
    mpl.rcParams.update(
        {
            "figure.facecolor": colors["background"],
            "savefig.facecolor": colors["background"],
            "axes.facecolor": colors["background"],
            "axes.edgecolor": colors["charcoal"],
            "axes.labelcolor": colors["charcoal"],
            "axes.titlecolor": colors["charcoal"],
            "text.color": colors["charcoal"],
            "xtick.color": colors["slate"],
            "ytick.color": colors["slate"],
            "grid.color": colors["gray_light"],
            "axes.prop_cycle": cycler(color=theme.categorical),
            "image.cmap": theme.cmap("sequential").name,
        }
    )


def set_theme(name: str | Theme, *, apply: bool = True) -> Theme:
    """
    Switch the active theme used by every helper in this module.

    Parameters
    ----------
    name:
        Registered theme name, or a :class:`Theme` instance (registered
        on the fly if needed).
    apply:
        Also push the theme colors into the current rcParams so that
        already-created figures follow the new theme.

    Returns
    -------
    The theme that became active.

    Examples
    --------
    set_theme("indigo")
    set_theme(my_theme)
    """

    global _ACTIVE_THEME

    if isinstance(name, Theme) and _theme_key(name.name) not in THEMES:
        register_theme(name)

    theme = get_theme(name)

    _ACTIVE_THEME = theme
    _sync_live_globals(theme)
    register_colormaps(theme)

    if apply:
        _apply_theme_rc(theme)

    return theme


# Common alias: ``pg.use_theme("indigo")``.
use_theme = set_theme


@contextmanager
def with_theme(name: str | Theme) -> Iterator[Theme]:
    """
    Temporarily switch themes; restores the previous theme on exit.

    Example
    -------
    with with_theme("indigo"):
        fig, ax = subplots()
        ...
    """

    previous = active_theme()
    try:
        yield set_theme(name)
    finally:
        set_theme(previous, apply=True)


# =============================================================================
# 5. READY-TO-USE COLOR PALETTES
# =============================================================================
#
# These module level containers are live views of the active theme: they are
# updated in place by ``set_theme``. ``get_palette()`` is the equivalent
# function form.

CATEGORICAL: list[str] = []
CATEGORICAL_GREEN: list[str] = []
SEQUENTIAL: list[str] = []
DIVERGING: list[str] = []

# ---------------------------------------------------------------------------
# Default (Phthalo Green) palette definitions.
# Hand-curated, so they are passed explicitly to the theme and never
# auto-derived.
# ---------------------------------------------------------------------------

_DEFAULT_CATEGORICAL: list[str] = [
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
_DEFAULT_CATEGORICAL_GREEN: list[str] = [
    PALETTE["dark"],
    PALETTE["primary"],
    PALETTE["medium"],
    PALETTE["accent"],
    PALETTE["light"],
    PALETTE["pale"],
]

# Sequential:
# Low -> high, weak -> strong, low risk -> high risk, etc.
_DEFAULT_SEQUENTIAL: list[str] = [
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
_DEFAULT_DIVERGING: list[str] = [
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
# 6. COLORMAPS
# =============================================================================


# Tracks which colormap objects this process put in the Matplotlib registry.
_REGISTERED_CMAPS: dict[str, mcolors.Colormap] = {}


def register_colormaps(
    theme: str | Theme | None = None, *, force: bool = False
) -> list[str]:
    """
    Register a theme's colormaps with Matplotlib.

    Registration is what makes string colormap names such as
    ``cmap="phthalo_green"`` (or ``cmap="indigo_diverging"``) work, and it
    keeps those names in sync with the theme currently selected.

    Safe to call repeatedly: colormaps already registered from the same
    theme object are skipped, so switching themes back and forth never
    emits "Overwriting the cmap" warnings. Replacing a theme with
    ``register_theme(..., override=True)`` does re-register its colormaps.

    Returns the theme's colormap names.
    """

    resolved = get_theme(theme)
    names = [resolved.cmap_name(kind) for kind in _CMAP_KINDS]
    for cmap in resolved.cmaps().values():
        stale = _REGISTERED_CMAPS.get(cmap.name) is not cmap
        if force or stale or cmap.name not in mpl.colormaps:
            mpl.colormaps.register(cmap, force=cmap.name in mpl.colormaps)
            _REGISTERED_CMAPS[cmap.name] = cmap
    return names


# =============================================================================
# 7. DEFAULT THEME REGISTRATION
# =============================================================================

PHTHALO_GREEN_THEME: Theme = register_theme(
    Theme(
        name=DEFAULT_THEME_NAME,
        label="Phthalo Green",
        description=(
            "Default academic palette. Phthalo Green ramp with restrained "
            "supporting hues and tinted academic neutrals."
        ),
        colors=dict(PALETTE),
        categorical=list(_DEFAULT_CATEGORICAL),
        categorical_green=list(_DEFAULT_CATEGORICAL_GREEN),
        sequential=list(_DEFAULT_SEQUENTIAL),
        diverging=list(_DEFAULT_DIVERGING),
        is_default=True,
    )
)

# Seed the live palette containers and register the default colormaps.
set_theme(DEFAULT_THEME_NAME, apply=False)


# =============================================================================
# 8. STYLE PRESETS
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

# Numeric settings a preset can override.
SETTING_KEYS: tuple[str, ...] = (
    "font_size",
    "figure_width",
    "figure_height",
    "line_width",
    "marker_size",
)

# Keyword-only overrides understood by apply_style()/subplots()/figure().
STYLE_OVERRIDE_KEYS: tuple[str, ...] = (
    "font_family",
    "font_size",
    "figure_width",
    "figure_height",
    "line_width",
    "marker_size",
)


def get_preset(name: str = "thesis") -> dict[str, float]:
    """Return a copy of one preset's numeric settings."""

    return _resolve_settings(name)


def _resolve_settings(
    preset: str = "thesis", **overrides: float | None
) -> dict[str, float]:
    if preset not in STYLE_PRESETS:
        available = ", ".join(STYLE_PRESETS)
        raise ValueError(f"Unknown preset '{preset}'. Available presets: {available}")

    settings: dict[str, float] = dict(STYLE_PRESETS[preset])

    for key, value in overrides.items():
        if value is None:
            continue
        if key not in SETTING_KEYS:
            allowed = ", ".join(SETTING_KEYS)
            raise TypeError(f"Unknown style setting '{key}'. Allowed: {allowed}")
        settings[key] = float(value)

    return settings


# =============================================================================
# 9. RC PARAMETERS AND apply_style
# =============================================================================


def _style_rc(
    theme: Theme,
    settings: Mapping[str, float],
    font_family: str | None = None,
) -> dict[str, Any]:
    """Build the full Matplotlib rcParams dictionary for a theme+preset."""

    colors = theme.colors
    font_size = settings["font_size"]

    return {
        # -----------------------------------------------------------------
        # Figure
        # -----------------------------------------------------------------
        "figure.figsize": (settings["figure_width"], settings["figure_height"]),
        "figure.dpi": 120,
        "savefig.dpi": 300,
        "figure.facecolor": colors["background"],
        "savefig.facecolor": colors["background"],
        "savefig.edgecolor": colors["background"],
        "savefig.pad_inches": 0.05,
        "savefig.transparent": False,
        # -----------------------------------------------------------------
        # Typography
        # -----------------------------------------------------------------
        "font.family": font_family or FONT_FAMILY,
        "font.serif": list(theme.serif),
        "font.sans-serif": list(theme.sans),
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
        "mathtext.fontset": theme.math_fontset,
        # -----------------------------------------------------------------
        # Text
        # -----------------------------------------------------------------
        "text.color": colors["charcoal"],
        "axes.labelcolor": colors["charcoal"],
        "axes.titlecolor": colors["charcoal"],
        "axes.titlepad": 6.0,
        "axes.labelpad": 4.0,
        "axes.unicode_minus": True,
        # -----------------------------------------------------------------
        # Axes
        # -----------------------------------------------------------------
        "axes.facecolor": colors["background"],
        "axes.edgecolor": colors["charcoal"],
        "axes.linewidth": 0.8,
        "axes.axisbelow": True,
        "axes.xmargin": 0.05,
        "axes.ymargin": 0.05,
        "axes.autolimit_mode": "round_numbers",
        # -----------------------------------------------------------------
        # Grid
        # -----------------------------------------------------------------
        "axes.grid": True,
        "axes.grid.axis": "both",
        "grid.color": colors["gray_light"],
        "grid.linewidth": 0.6,
        # EPS/PostScript does not preserve transparency reliably.
        "grid.alpha": 1.0,
        # -----------------------------------------------------------------
        # Ticks
        # -----------------------------------------------------------------
        "xtick.color": colors["slate"],
        "ytick.color": colors["slate"],
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 3.5,
        "ytick.major.size": 3.5,
        "xtick.minor.size": 2.0,
        "ytick.minor.size": 2.0,
        "xtick.major.pad": 3.5,
        "ytick.major.pad": 3.5,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "xtick.minor.width": 0.5,
        "ytick.minor.width": 0.5,
        "xtick.minor.visible": True,
        "ytick.minor.visible": True,
        # -----------------------------------------------------------------
        # Lines / markers
        # -----------------------------------------------------------------
        "lines.linewidth": settings["line_width"],
        "lines.markersize": settings["marker_size"],
        "lines.markeredgewidth": 0.8,
        "lines.solid_capstyle": "round",
        "markers.fillstyle": "full",
        "patch.linewidth": 0.8,
        "patch.edgecolor": colors["dark"],
        # -----------------------------------------------------------------
        # Legend
        # -----------------------------------------------------------------
        "legend.frameon": False,
        "legend.fancybox": False,
        "legend.borderaxespad": 0.5,
        "legend.borderpad": 0.4,
        "legend.columnspacing": 1.2,
        "legend.labelspacing": 0.4,
        "legend.handlelength": 2.2,
        "legend.handleheight": 0.9,
        "legend.labelcolor": colors["charcoal"],
        "legend.numpoints": 1,
        "legend.scatterpoints": 1,
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
        "ps.distiller.res": 6000,
        "svg.fonttype": "none",
        "svg.hashsalt": "phthalo-green",
        # -----------------------------------------------------------------
        # Default color cycle and colormap
        # -----------------------------------------------------------------
        "axes.prop_cycle": cycler(color=list(theme.categorical)),
        "image.cmap": theme.cmap("sequential").name,
    }


def preset_rc(
    preset: str = "thesis",
    theme: str | Theme | None = None,
    *,
    font_family: str | None = None,
    **overrides: float | None,
) -> dict[str, Any]:
    """
    Return the rcParams dictionary for a preset without applying it.

    The result can be passed to anything that accepts a mapping of
    rcParams, which makes the library work with Matplotlib's own style
    machinery:

        plt.style.use(preset_rc("journal"))
        plt.style.context([preset_rc("single_column")])

    and can be dumped to a ``.mplstyle`` file:

        write_mplstyle("phthalo.mplstyle", preset="thesis")
    """

    resolved = get_theme(theme)
    settings = _resolve_settings(preset, **overrides)
    return _style_rc(resolved, settings, font_family)


def apply_style(
    *,
    preset: str = "thesis",
    theme: str | Theme | None = None,
    font_family: str | None = None,
    font_size: float | None = None,
    figure_width: float | None = None,
    figure_height: float | None = None,
    line_width: float | None = None,
    marker_size: float | None = None,
    rc: Mapping[str, Any] | None = None,
) -> None:
    """
    Apply the academic style globally to Matplotlib.

    Parameters
    ----------
    preset:
        One of:
            "thesis"
            "journal"
            "presentation"
            "single_column"
            "double_column"

    theme:
        Registered theme name (or :class:`Theme` instance). ``None`` keeps
        the currently active theme, which defaults to ``"phthalo_green"``.

    font_family:
        Default is "serif", using the theme's serif fallback chain.
        Pass ``"sans-serif"`` when a venue requires a sans-serif font.

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

    rc:
        Any additional rcParams, applied last, e.g.
        ``apply_style(preset="journal", rc={"axes.grid": False})``.

    Examples
    --------
    apply_style()

    apply_style(preset="journal")

    apply_style(theme="indigo", preset="single_column")

    apply_style(font_size=11, figure_width=7)
    """

    if theme is not None:
        set_theme(theme, apply=False)

    resolved = active_theme()
    settings = _resolve_settings(
        preset,
        font_size=font_size,
        figure_width=figure_width,
        figure_height=figure_height,
        line_width=line_width,
        marker_size=marker_size,
    )

    mpl.rcParams.update(_style_rc(resolved, settings, font_family))
    register_colormaps(resolved)

    if rc:
        mpl.rcParams.update(dict(rc))


# =============================================================================
# 10. OPTIONAL SEABORN / PLOTLY SUPPORT
# =============================================================================


def apply_seaborn_style(
    *,
    preset: str = "thesis",
    theme: str | Theme | None = None,
    palette: str = "categorical",
) -> None:
    """
    Apply the academic style to Seaborn.

    Seaborn is imported only when this function is called, so Seaborn is
    optional for users who work exclusively with Matplotlib.

    Parameters
    ----------
    palette:
        Any palette kind, e.g. "categorical", "categorical_green",
        "sequential", "diverging".
    """

    try:
        import seaborn as sns
    except ImportError as exc:
        raise ImportError(
            "Seaborn is not installed. Install it with "
            "`pip install seaborn`, or use apply_style() for Matplotlib."
        ) from exc

    if theme is not None:
        set_theme(theme, apply=False)

    resolved = active_theme()
    apply_style(preset=preset)

    sns.set_theme(
        style="whitegrid",
        rc={
            "axes.facecolor": resolved["background"],
            "figure.facecolor": resolved["background"],
            "grid.color": resolved["gray_light"],
            "grid.linewidth": 0.6,
            "axes.edgecolor": resolved["charcoal"],
            "text.color": resolved["charcoal"],
            "axes.labelcolor": resolved["charcoal"],
            "xtick.color": resolved["slate"],
            "ytick.color": resolved["slate"],
            "font.family": FONT_FAMILY,
            "font.serif": list(resolved.serif),
            "mathtext.fontset": resolved.math_fontset,
        },
    )

    sns.set_palette(resolved.palette(palette))


def _plotly_colorscale(colors: Sequence[str]) -> list[list[Any]]:
    """Convert a color list to a Plotly ``colorscale``."""

    if len(colors) == 1:
        scale = [(0.0, colors[0]), (1.0, colors[0])]
    else:
        scale = [
            (index / (len(colors) - 1), color)
            for index, color in enumerate(colors)
        ]
    return [[position, color] for position, color in scale]


def _plotly_axis(resolved: Theme) -> dict[str, Any]:
    return {
        "color": resolved["charcoal"],
        "linecolor": resolved["charcoal"],
        "linewidth": 0.8,
        "showgrid": True,
        "gridcolor": css_rgba(resolved["gray_light"], 1.0),
        "gridwidth": 0.7,
        "zeroline": False,
        "ticks": "outside",
        "ticklen": 4,
        "tickwidth": 0.8,
        "tickcolor": resolved["slate"],
        "title": {"color": resolved["charcoal"]},
        "mirror": False,
        "showline": True,
    }


def plotly_template(
    theme: str | Theme | None = None,
    *,
    name: str | None = None,
    font_size: float = 12,
) -> dict[str, Any]:
    """
    Return a Plotly layout template dictionary built from a theme.

    The dictionary can be used without Plotly installed (it is plain data):

        template = plotly_template()

    or registered as the active Plotly template:

        apply_plotly_theme()
    """

    resolved = get_theme(theme)
    return {
        "layout": {
            "font": {
                "family": resolved.font_stack(),
                "color": resolved["charcoal"],
                "size": font_size,
            },
            "title": {
                "font": {
                    "family": resolved.font_stack(),
                    "color": resolved["charcoal"],
                    "size": font_size + 2,
                },
                "x": 0.5,
                "xanchor": "center",
            },
            "paper_bgcolor": resolved["background"],
            "plot_bgcolor": resolved["background"],
            "colorway": list(resolved.categorical),
            "colorscale": {
                "sequential": _plotly_colorscale(resolved.sequential),
                "diverging": _plotly_colorscale(resolved.diverging),
                "categorical": _plotly_colorscale(resolved.categorical),
            },
            "hoverlabel": {
                "bgcolor": resolved["background"],
                "font": {"color": resolved["charcoal"]},
                "bordercolor": resolved["gray"],
            },
            "legend": {
                "bgcolor": css_rgba(resolved["background"], 0.0),
                "bordercolor": css_rgba(resolved["gray"], 0.0),
                "borderwidth": 0,
                "font": {"color": resolved["charcoal"]},
            },
            "xaxis": _plotly_axis(resolved),
            "yaxis": _plotly_axis(resolved),
            "coloraxis": {
                "colorscale": _plotly_colorscale(resolved.sequential),
                "colorbar": {
                    "outlinecolor": css_rgba(resolved["gray"], 0.0),
                    "tickcolor": resolved["slate"],
                    "tickfont": {"color": resolved["slate"]},
                },
            },
            "margin": {"l": 60, "r": 30, "t": 50, "b": 50},
        },
        "data": {
            "bar": [{"marker": {"line": {"color": resolved["dark"], "width": 0.6}},
                     "error_y": {"color": resolved["slate"]}}],
            "scatter": [{"line": {"width": 2.0},
                         "marker": {"line": {"width": 0.8}}}],
        },
    }


def apply_plotly_theme(
    theme: str | Theme | None = None,
    *,
    name: str | None = None,
    font_size: float = 12,
) -> dict[str, Any]:
    """
    Register the theme as a Plotly template and make it the default.

    Plotly is imported lazily, so it stays an optional dependency.
    """

    try:
        import plotly.io as pio
    except ImportError as exc:
        raise ImportError(
            "Plotly is not installed. Install it with `pip install plotly`, "
            "or use plotly_template() to build the template dictionary."
        ) from exc

    resolved = get_theme(theme)
    template_name = name or resolved.name
    template = plotly_template(resolved, name=template_name, font_size=font_size)
    pio.templates[template_name] = template
    pio.templates.default = template_name
    return template


# =============================================================================
# 11. PALETTE HELPERS
# =============================================================================


def get_color(name: str = "primary", theme: str | Theme | None = None) -> str:
    """
    Return a named color from the active (or given) theme.

    Example
    -------
    color = get_color("primary")
    color = get_color("accent", theme="indigo")
    """

    return get_theme(theme).color(name)


def get_palette(
    palette: str = "categorical",
    n: int | None = None,
    theme: str | Theme | None = None,
) -> list[str]:
    """
    Return a predefined palette as a list of hex colors.

    Parameters
    ----------
    palette:
        "categorical"
        "categorical_green" (aliases: "green", "mono")
        "sequential"     (alias: "seq")
        "diverging"      (alias: "div")

    n:
        Optional number of colors. ``n <= len(palette)`` returns the first
        ``n`` hand-picked colors; larger values interpolate.

    theme:
        Theme to read from; defaults to the active theme.

    Examples
    --------
    get_palette("categorical", 4)
    get_palette("sequential", 6)
    get_palette("diverging", theme="indigo")
    """

    return get_theme(theme).palette(palette, n)


def get_cmap(
    kind: str = "sequential",
    n: int | None = None,
    theme: str | Theme | None = None,
) -> mcolors.Colormap:
    """
    Return the active (or given) theme's colormap by kind.

    ``kind`` is one of "categorical", "categorical_green", "sequential" or
    "diverging". With ``n`` for a categorical kind, a discrete
    ``ListedColormap`` of exactly ``n`` colors is built.

    Examples
    --------
    ax.imshow(matrix, cmap=get_cmap("sequential"))
    ax.scatter(x, y, c=z, cmap=get_cmap("diverging"))
    sns.heatmap(matrix, cmap=get_cmap("categorical", n=4))
    """

    resolved = get_theme(theme)
    if n is None:
        return resolved.cmap(kind)

    colors = resolved.palette(kind, n)
    name = f"{resolved.cmap_name(kind)}_{len(colors)}"
    return mcolors.ListedColormap(colors, name=name)


# =============================================================================
# 12. FIGURE-SPECIFIC HELPERS
# =============================================================================


def style_axis(
    ax,
    *,
    grid: bool = True,
    remove_top_right_spines: bool = False,
    grid_axis: str = "both",
    minor: bool | None = None,
) -> None:
    """
    Apply final axis-level formatting.

    This is useful when you need more control than apply_style() provides.

    Parameters
    ----------
    grid:
        Whether to draw gridlines.

    remove_top_right_spines:
        Hide the top and right spines (Tufte-style, good for publications).

    grid_axis:
        "both", "x" or "y".

    minor:
        Override minor tick visibility; ``None`` keeps the preset default.
    """

    theme = active_theme()

    ax.set_facecolor(theme["background"])

    ax.tick_params(
        colors=theme["slate"],
        width=0.7,
    )

    if minor is not None:
        if minor:
            ax.minorticks_on()
        else:
            ax.minorticks_off()

    for spine in ax.spines.values():
        spine.set_color(theme["charcoal"])
        spine.set_linewidth(0.8)

    if remove_top_right_spines:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    if grid:
        ax.grid(
            True,
            axis=grid_axis,
            color=theme["gray_light"],
            linewidth=0.6,
            alpha=1.0,
        )
    else:
        ax.grid(False, axis=grid_axis)
    ax.set_axisbelow(True)


def despine(
    ax,
    *,
    spines: Sequence[str] = ("top", "right"),
    grid: bool = False,
) -> None:
    """
    Remove spines for a clean publication look, optionally hiding the grid.

    Example
    -------
    fig, ax = pg.subplots()
    ax.plot(x, y)
    pg.despine(ax)
    """

    for name in spines:
        if name in ax.spines:
            ax.spines[name].set_visible(False)
    if grid:
        ax.grid(False)


def style_legend(
    legend,
    *,
    frameon: bool = False,
    title: str | None = None,
) -> None:
    """Apply restrained academic formatting to a Matplotlib legend."""

    if legend is None:
        return

    theme = active_theme()
    legend.set_frame_on(frameon)

    for text in legend.get_texts():
        text.set_color(theme["charcoal"])

    if title is not None:
        legend.set_title(title)


# =============================================================================
# 13. PUBLICATION EXPORT
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

VECTOR_FORMATS: tuple[str, ...] = ("pdf", "svg", "eps", "ps", "ps2")
RASTER_FORMATS: tuple[str, ...] = ("png", "jpg", "jpeg", "tiff", "tif", "webp")


def export_dpi(fmt: str, *, png_dpi: int = 600, vector_dpi: int = 300) -> int:
    """DPI used for one export format."""

    fmt = str(fmt).lower().lstrip(".")
    return int(png_dpi if fmt in RASTER_FORMATS else vector_dpi)


def save_publication_figure(
    fig,
    filename: str,
    *,
    transparent: bool = False,
    dpi: int | None = None,
    bbox_inches: str | None = "tight",
    metadata: Mapping[str, str] | None = None,
) -> Path:
    """
    Save a Matplotlib figure using publication-friendly defaults.

    Parent directories are created automatically, so ``figures/ch1/fig.pdf``
    works even when ``figures/ch1/`` does not exist yet.

    Parameters
    ----------
    transparent:
        Render without background (useful for slides).

    dpi:
        Raster DPI; ignored for vector formats. ``None`` picks 600 for
        raster output and 300 for vector output.

    metadata:
        PDF metadata, e.g. ``{"Author": "Me", "Title": "Figure 1"}``.

    Examples
    --------
    save_publication_figure(fig, "results.pdf")
    save_publication_figure(fig, "results.png", dpi=600)
    """

    path = Path(filename)
    if str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)

    if dpi is None:
        dpi = export_dpi(path.suffix)

    fig.savefig(
        path,
        dpi=dpi,
        bbox_inches=bbox_inches,
        transparent=transparent,
        metadata=dict(metadata) if metadata else None,
    )
    return path


def export_figure(
    fig,
    basename: str | Path,
    *,
    formats: Sequence[str] = ("pdf", "png"),
    dpi: int | None = None,
    png_dpi: int = 600,
    vector_dpi: int = 300,
    transparent: bool = False,
    bbox_inches: str | None = "tight",
    close: bool = True,
    metadata: Mapping[str, str] | None = None,
) -> list[Path]:
    """
    Save one figure in several publication formats at once.

    Parameters
    ----------
    fig:
        Matplotlib figure to save.

    basename:
        Path without extension, e.g. ``figures/01_trend``.
        Extensions are appended, so dots in the name are preserved
        (``figures/01.trend.v2`` keeps ``.trend.v2``).

    formats:
        Any combination of ``"pdf"``, ``"svg"``, ``"png"``, ``"eps"``.

    dpi:
        Force one DPI for every format (overrides ``png_dpi``/``vector_dpi``).

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

    if not formats:
        raise ValueError("formats must contain at least one format.")

    resolved: list[str] = []
    for fmt in formats:
        key = str(fmt).lower().lstrip(".")
        if key not in PUBLICATION_FORMATS:
            available = ", ".join(PUBLICATION_FORMATS)
            raise ValueError(f"Unknown format '{fmt}'. Available: {available}")
        if key not in resolved:
            resolved.append(key)

    written: list[Path] = []
    for key in resolved:
        path = base.with_name(f"{base.name}.{key}")
        save_publication_figure(
            fig,
            str(path),
            transparent=transparent,
            dpi=dpi if dpi is not None else export_dpi(key, png_dpi=png_dpi,
                                                       vector_dpi=vector_dpi),
            bbox_inches=bbox_inches,
            metadata=metadata,
        )
        written.append(path)

    if close:
        import matplotlib.pyplot as plt

        plt.close(fig)

    return written


# =============================================================================
# 14. LATEX COMPATIBILITY
# =============================================================================


def configure_latex(
    *,
    use_tex: bool = False,
    preamble: Sequence[str] | None = None,
) -> None:
    """
    Configure optional LaTeX rendering.

    By default this does NOT enable LaTeX because a working LaTeX
    installation is required on the machine.

    Set use_tex=True only when your system has a functional LaTeX
    installation and you want Matplotlib text rendered through LaTeX.

    Parameters
    ----------
    preamble:
        Extra LaTeX preamble lines, e.g. ``[r"\\usepackage{siunitx}"]``.
    """

    theme = active_theme()

    mpl.rcParams["text.usetex"] = bool(use_tex)

    if use_tex:
        mpl.rcParams.update(
            {
                "font.family": "serif",
                "font.serif": list(theme.serif),
                "text.latex.preamble": "\n".join(preamble or []),
            }
        )


# =============================================================================
# 15. INFORMATION / DIAGNOSTICS
# =============================================================================


def describe_theme(theme: str | Theme | None = None) -> dict[str, Any]:
    """Return a machine-readable summary of a theme."""

    return get_theme(theme).summary()


def print_style_info(theme: str | Theme | None = None) -> None:
    """Print a concise summary of a theme and its settings."""

    resolved = get_theme(theme)
    settings = get_preset("thesis")

    print(f"{resolved.label} Academic Visualization Style")
    print("=" * 48)
    print(f"Theme         : {resolved.name}")
    if resolved.description:
        print(f"Description   : {resolved.description}")
    print(f"Primary color : {resolved.color('primary')}")
    print(f"Font family   : {FONT_FAMILY}")
    print(f"Resolved font : {resolved_serif_font()}")
    print(f"Figure size   : {settings['figure_width']} x "
          f"{settings['figure_height']} in")
    print()
    print("Available presets:")
    for preset in STYLE_PRESETS:
        print(f"  - {preset}")
    print()
    print("Available palettes:")
    for kind in PALETTE_KINDS:
        print(f"  - {kind} ({len(resolved.palette(kind))} colors)")
    print()
    print("Registered themes:")
    for name in list_themes():
        marker = "*" if name == resolved.name else " "
        print(f" {marker} {name}")


# =============================================================================
# 16. MPLSTYLE FILES
# =============================================================================


def _mplstyle_value(key: str, value: Any) -> str:
    """Format one rcParams value for a ``.mplstyle`` file.

    Matplotlib's style parser treats ``#`` as a comment start, so hex
    colors are written as *bare* 6/8-digit hex (the validators accept
    ``FAFBFA`` and normalize it back to ``#FAFBFA``), ``axes.prop_cycle``
    must be a real ``cycler(...)``, and font stacks must be comma
    separated without brackets or quotes.
    """

    if key == "axes.prop_cycle":
        entries = []
        for color in value.by_key()["color"]:
            text = color if isinstance(color, str) else mcolors.to_hex(color)
            entries.append(f"'{text.lstrip('#')}'")
        return f"cycler('color', [{', '.join(entries)}])"

    if isinstance(value, mcolors.Colormap):
        return value.name

    if isinstance(value, (list, tuple)):
        if all(isinstance(item, str) for item in value):
            return ", ".join(value)
        return ", ".join(str(item) for item in value)

    if isinstance(value, str) and value.startswith("#"):
        return value.lstrip("#")

    return str(value)


def write_mplstyle(
    path: str | Path,
    *,
    preset: str = "thesis",
    theme: str | Theme | None = None,
) -> Path:
    """
    Write the style to a Matplotlib ``.mplstyle`` file.

    Hand this to collaborators who do not want the dependency, or load it
    from a template project:

        write_mplstyle("phthalo_green.mplstyle", preset="journal")
        plt.style.use("phthalo_green.mplstyle")

    The file is round-trip safe: loading it with ``plt.style.use()``
    reproduces the same colors, fonts, and sizes.
    """

    target = Path(path)
    if str(target.parent) not in ("", "."):
        target.parent.mkdir(parents=True, exist_ok=True)

    rc = preset_rc(preset, theme)
    lines = ["# Generated by phthalo-green", ""]
    for key in sorted(rc):
        lines.append(f"{key}: {_mplstyle_value(key, rc[key])}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


# =============================================================================
# 17. TEMPLATE HELPERS (new-project friendly)
# =============================================================================
#
# These are thin conveniences on top of apply_style() so that every future
# project starts from the same two lines:
#
#     import phthalo_green as pg
#     fig, ax = pg.subplots()
#     ...
#     pg.export_figure(fig, "figures/my_fig")
#


@contextmanager
def styled(
    preset: str = "thesis",
    *,
    theme: str | Theme | None = None,
    rc: Mapping[str, Any] | None = None,
    **overrides: float | None,
) -> Iterator[None]:
    """
    Temporarily apply the academic style.

    Restores the previous rcParams *and* theme on exit. Useful in notebooks
    or when mixing styles in one process.

    Example
    -------
    with styled("journal"):
        fig, ax = plt.subplots()
        ...
    """

    previous_rc = mpl.rcParams.copy()
    previous_theme = active_theme()
    try:
        apply_style(preset=preset, theme=theme, rc=rc, **overrides)
        yield
    finally:
        mpl.rcParams.update(previous_rc)
        set_theme(previous_theme, apply=False)


def _split_style_kwargs(
    kwargs: dict[str, Any],
) -> tuple[dict[str, float | None], dict[str, Any]]:
    """Separate style overrides from arguments meant for Matplotlib."""

    style_kwargs = {
        key: kwargs.pop(key) for key in list(kwargs) if key in STYLE_OVERRIDE_KEYS
    }
    return style_kwargs, kwargs


def figure(preset: str = "thesis", *args, theme: str | Theme | None = None,
           **kwargs):
    """
    Create a new figure with the style applied.

    Equivalent to ``apply_style(preset, theme=theme)`` + ``plt.figure()``.
    Style overrides (font_size, figure_width, ...) are consumed;
    remaining kwargs go to ``plt.figure()``.

    Like ``apply_style``, this affects matplotlib's global rcParams; pass
    ``theme=`` only when you intend to switch the active theme, or use
    ``with_theme()`` / ``styled()`` for a temporary switch.
    """
    import matplotlib.pyplot as plt

    style_kwargs, kwargs = _split_style_kwargs(kwargs)
    apply_style(preset=preset, theme=theme, **style_kwargs)
    return plt.figure(*args, **kwargs)


def subplots(preset: str = "thesis", *args, theme: str | Theme | None = None,
             **kwargs):
    """
    Create ``fig, ax`` (or arrays) with the style applied.

    All extra args are forwarded to ``plt.subplots`` except style overrides
    (font_size, figure_width, figure_height, line_width, marker_size,
    font_family) and ``theme``.

    ``theme`` switches the *active theme* globally (matplotlib rcParams are
    process-global); use ``with_theme()`` or ``styled()`` when you only want
    the switch for a block of code.

    Example
    -------
    fig, ax = subplots(preset="journal")
    fig, axes = subplots(preset="thesis", nrows=2, ncols=2)
    fig, ax = subplots("journal", figsize=(8, 4))
    fig, ax = subplots(theme="indigo")          # global switch
    with with_theme("indigo"):                  # temporary switch
        fig, ax = subplots()
    """
    import matplotlib.pyplot as plt

    style_kwargs, kwargs = _split_style_kwargs(kwargs)
    apply_style(preset=preset, theme=theme, **style_kwargs)
    return plt.subplots(*args, **kwargs)


# =============================================================================
# 18. DYNAMIC MODULE ATTRIBUTES
# =============================================================================

#
# Color-name constants and colormap objects are resolved lazily so that
# ``pg.PHTHALO_GREEN`` and ``pg.SEQUENTIAL_CMAP`` always follow the active
# theme. Prefer attribute access (``pg.X``) over ``from phthalo_green import
# X`` if you plan to switch themes at runtime; the palette containers
# ``PALETTE``, ``CATEGORICAL``, ``CATEGORICAL_GREEN``, ``SEQUENTIAL`` and
# ``DIVERGING`` are live either way, because they are updated in place.

_COLOR_ALIASES: dict[str, str] = {
    "PHTHALO_GREEN": "primary",
    "DEEP_PHTHALO_GREEN": "dark",
    "MEDIUM_PHTHALO_GREEN": "medium",
    "EMERALD_GREEN": "accent",
    "LIGHT_GREEN": "light",
    "PALE_GREEN": "pale",
}

_CMAP_ALIASES: dict[str, str] = {
    "SEQUENTIAL_CMAP": "sequential",
    "DIVERGING_CMAP": "diverging",
    "CATEGORICAL_CMAP": "categorical",
}


# Color-name constants and colormap objects are resolved lazily. Declaring
# them under TYPE_CHECKING keeps ``__all__`` (and type checkers) happy.
if TYPE_CHECKING:
    CATEGORICAL_CMAP: mcolors.Colormap
    DEEP_PHTHALO_GREEN: str
    DIVERGING_CMAP: mcolors.Colormap
    EMERALD_GREEN: str
    LIGHT_GREEN: str
    MEDIUM_PHTHALO_GREEN: str
    PALE_GREEN: str
    PHTHALO_GREEN: str
    SEQUENTIAL_CMAP: mcolors.Colormap


def __getattr__(name: str) -> Any:
    if name in _COLOR_ALIASES:
        return active_theme().color(_COLOR_ALIASES[name])
    if name in _CMAP_ALIASES:
        return active_theme().cmap(_CMAP_ALIASES[name])
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_COLOR_ALIASES) | set(_CMAP_ALIASES))


# =============================================================================
# 19. MODULE EXPORTS
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
    # Roles
    "RAMP_KEYS",
    "ACCENT_KEYS",
    "NEUTRAL_KEYS",
    "PALETTE_KINDS",
    # Typography
    "FONT_FAMILY",
    "FONT_SERIF_FALLBACKS",
    "WORDCLOUD_FONT_PATH",
    "FONT_SANS_FALLBACKS",
    "MATH_FONTSET",
    # Palettes (live views of the active theme)
    "CATEGORICAL",
    "CATEGORICAL_GREEN",
    "SEQUENTIAL",
    "DIVERGING",
    # Colormaps
    "SEQUENTIAL_CMAP",
    "DIVERGING_CMAP",
    "CATEGORICAL_CMAP",
    # Themes
    "Theme",
    "THEMES",
    "DEFAULT_THEME_NAME",
    "PHTHALO_GREEN_THEME",
    "make_theme",
    "register_theme",
    "register_palette",
    "set_theme",
    "use_theme",
    "with_theme",
    "get_theme",
    "list_themes",
    "active_theme",
    "describe_theme",
    # Presets
    "STYLE_PRESETS",
    "SETTING_KEYS",
    "STYLE_OVERRIDE_KEYS",
    "get_preset",
    "preset_rc",
    # Color utilities
    "to_hex",
    "mix",
    "lighten",
    "darken",
    "shift_hue",
    "with_alpha",
    "css_rgba",
    "relative_luminance",
    "contrast_ratio",
    # Publication
    "PUBLICATION_FORMATS",
    "VECTOR_FORMATS",
    "RASTER_FORMATS",
    "export_dpi",
    # Functions
    "apply_style",
    "apply_seaborn_style",
    "plotly_template",
    "apply_plotly_theme",
    "register_colormaps",
    "get_color",
    "get_palette",
    "get_cmap",
    "style_axis",
    "despine",
    "style_legend",
    "save_publication_figure",
    "export_figure",
    "write_mplstyle",
    "configure_latex",
    "print_style_info",
    "styled",
    "figure",
    "subplots",
]


# =============================================================================
# 20. SELF TEST
# =============================================================================

if __name__ == "__main__":
    print_style_info()
    print()
    print("Module loaded successfully.")
