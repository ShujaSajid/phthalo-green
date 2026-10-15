"""
Optional themes shipped with phthalo-green
===========================================

``phthalo_green`` (see ``style.py``) is the default identity. This module
shows how additional, completely independent palettes are added, which is the
hook for a second/third colour scheme: a theme is pure data, so a new palette
never requires touching the styling code.

``INDIGO`` below is a *hand-curated example* of a non-green palette. It is a
starting point, not a recommendation — edit or replace it freely. Registrations
are idempotent, so importing this module twice is safe.
"""

from __future__ import annotations

from .style import Theme, register_theme

# ---------------------------------------------------------------------------
# Indigo / ink blue — example of a palette from another hue family.
# ---------------------------------------------------------------------------

INDIGO_COLORS: dict[str, str] = {
    # ramp (dark -> light)
    "dark": "#0A1B2A",
    "primary": "#123A5C",
    "medium": "#1E5C86",
    "accent": "#3390B8",
    "light": "#7FB2CC",
    "pale": "#C4DCE9",
    # neutrals
    "charcoal": "#212C33",
    "slate": "#5A6B75",
    "gray": "#8D9AA1",
    "gray_light": "#E4EAEE",
    "background": "#F8FAFC",
    "white": "#FFFFFF",
    # supporting hues
    "blue_green": "#2C7A70",
    "blue": "#2E6BA8",
    "ochre": "#B08A3E",
    "rust": "#A25C46",
    "plum": "#6E5A70",
}

INDIGO_CATEGORICAL: list[str] = [
    "#0A1B2A",
    "#123A5C",
    "#1E5C86",
    "#B08A3E",
    "#3390B8",
    "#2C7A70",
    "#6E5A70",
    "#A25C46",
    "#7FB2CC",
    "#C4DCE9",
]

INDIGO_SEQUENTIAL: list[str] = [
    "#C4DCE9",
    "#A9CBDD",
    "#7FB2CC",
    "#55A1C2",
    "#3390B8",
    "#2276A0",
    "#1E5C86",
    "#17496A",
    "#123A5C",
    "#0F2E4B",
    "#0A1B2A",
]

INDIGO_DIVERGING: list[str] = [
    "#7A3E33",
    "#A25C46",
    "#C89A8E",
    "#E4EAEE",
    "#B5D3C4",
    "#7FB2CC",
    "#3390B8",
    "#1E5C86",
    "#123A5C",
]

INDIGO: Theme = Theme(
    name="indigo",
    label="Indigo Ink",
    description=(
        "Alternative hue family (deep blue). Legend kept as an example of a "
        "fully independent theme; replace or extend as needed."
    ),
    colors=dict(INDIGO_COLORS),
    categorical=list(INDIGO_CATEGORICAL),
    categorical_green=[INDIGO_COLORS[key] for key in
                       ("dark", "primary", "medium", "accent", "light", "pale")],
    sequential=list(INDIGO_SEQUENTIAL),
    diverging=list(INDIGO_DIVERGING),
)


def register_builtin_themes() -> list[str]:
    """Register the optional themes. Returns the names registered now."""

    return [register_theme(INDIGO, override=True).name]


__all__ = [
    "INDIGO",
    "INDIGO_CATEGORICAL",
    "INDIGO_COLORS",
    "INDIGO_DIVERGING",
    "INDIGO_SEQUENTIAL",
    "register_builtin_themes",
]
