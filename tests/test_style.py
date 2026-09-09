"""Smoke tests for phthalo-green library."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest


def test_import():
    import phthalo_green

    assert phthalo_green.__version__ == "0.1.0"
    assert "primary" in phthalo_green.PALETTE


def test_apply_style_presets():
    from phthalo_green import STYLE_PRESETS, apply_style

    for preset in STYLE_PRESETS:
        apply_style(preset=preset)

    with pytest.raises(ValueError):
        apply_style(preset="not_a_preset")


def test_helpers():
    from phthalo_green import get_color, get_palette, styled, subplots

    assert get_color("primary").startswith("#")
    with pytest.raises(KeyError):
        get_color("nope")

    assert len(get_palette("categorical", 4)) == 4

    with styled("journal"):
        fig, ax = subplots(preset="journal")
        ax.plot([0, 1], [0, 1])
        plt.close(fig)


def test_export_figure(tmp_path):
    from phthalo_green import PALETTE, export_figure, subplots

    fig, ax = subplots(preset="thesis")
    ax.plot([2019, 2020], [1, 2], color=PALETTE["primary"])
    written = export_figure(fig, tmp_path / "fig", formats=("pdf", "png"))
    assert len(written) == 2
    assert all(p.exists() for p in written)
