"""Tests for phthalo-green."""

from __future__ import annotations

import warnings

import matplotlib

matplotlib.use("Agg")

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest


@pytest.fixture(autouse=True)
def restore_active_theme():
    """Every test starts from the default theme and leaves it there."""

    import phthalo_green as pg

    # Use the theme object, not its name: a test may replace the name.
    default = pg.PHTHALO_GREEN_THEME
    pg.set_theme(default)
    yield
    pg.set_theme(default)


def test_import():
    import phthalo_green

    assert phthalo_green.__version__ == "0.1.1"
    assert "primary" in phthalo_green.PALETTE


def test_default_palette_is_unchanged():
    from phthalo_green import PALETTE

    assert PALETTE == {
        "dark": "#0B2418",
        "primary": "#123524",
        "medium": "#176B45",
        "accent": "#2E8B57",
        "light": "#72A98F",
        "pale": "#C7DED3",
        "charcoal": "#263238",
        "slate": "#607D76",
        "gray": "#9AA7A2",
        "gray_light": "#E7EBE9",
        "background": "#FAFBFA",
        "white": "#FFFFFF",
        "blue_green": "#2F6F6D",
        "blue": "#3E6B7C",
        "ochre": "#A58A45",
        "rust": "#9A5B4A",
        "plum": "#6F596F",
    }


def test_default_palettes_are_unchanged():
    import phthalo_green as pg

    assert pg.CATEGORICAL[0] == "#0B2418"
    assert pg.CATEGORICAL_GREEN == [
        "#0B2418",
        "#123524",
        "#176B45",
        "#2E8B57",
        "#72A98F",
        "#C7DED3",
    ]
    assert pg.SEQUENTIAL[:2] == ["#C7DED3", "#A8C9B9"]
    assert pg.DIVERGING[3] == "#E7EBE9"
    assert pg.get_color("primary") == "#123524"


def test_apply_style_presets():
    from phthalo_green import STYLE_PRESETS, apply_style

    for preset in STYLE_PRESETS:
        apply_style(preset=preset)

    with pytest.raises(ValueError):
        apply_style(preset="not_a_preset")


def test_apply_style_overrides_and_rc():
    from phthalo_green import apply_style

    apply_style(preset="journal", font_size=12, figure_width=8, rc={"axes.grid": False})
    assert plt.rcParams["font.size"] == 12
    assert tuple(plt.rcParams["figure.figsize"]) == (8, 4.0)
    assert plt.rcParams["axes.grid"] is False

    with pytest.raises(TypeError):
        apply_style(preset="thesis", nope=1)


def test_apply_style_font_family():
    from phthalo_green import apply_style

    apply_style(preset="thesis", font_family="sans-serif")
    assert plt.rcParams["font.family"] == ["sans-serif"] or (
        plt.rcParams["font.family"] == "sans-serif"
    )
    apply_style(preset="thesis")
    assert "serif" in plt.rcParams["font.family"]


def test_helpers():
    from phthalo_green import get_color, get_palette, styled, subplots

    assert get_color("primary").startswith("#")
    with pytest.raises(KeyError):
        get_color("nope")

    assert len(get_palette("categorical", 4)) == 4
    assert len(get_palette("sequential", 20)) == 20
    assert get_palette("categorical") == get_palette("cat")
    with pytest.raises(KeyError):
        get_palette("nope")
    with pytest.raises(ValueError):
        get_palette("categorical", 0)

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
    assert written[0].suffix == ".pdf"

    # Dots in the basename must survive.
    fig, ax = subplots()
    written = export_figure(fig, tmp_path / "v1.2.results", formats=("png",))
    assert written[0].name == "v1.2.results.png"

    with pytest.raises(ValueError):
        export_figure(fig, tmp_path / "bad", formats=("docx",))
    with pytest.raises(ValueError):
        export_figure(fig, tmp_path / "bad", formats=())

    assert plt.get_fignums() == []


def test_save_publication_figure_creates_parents(tmp_path):
    from phthalo_green import save_publication_figure, subplots

    fig, _ax = subplots()
    path = save_publication_figure(
        fig, tmp_path / "ch1" / "deep" / "fig.pdf", metadata={"Title": "Fig 1"}
    )
    assert path.exists()
    plt.close(fig)


def test_export_dpi():
    from phthalo_green import export_dpi

    assert export_dpi("png") == 600
    assert export_dpi("pdf") == 300
    assert export_dpi("png", png_dpi=1200) == 1200


def test_themes_registry():
    import phthalo_green as pg

    assert pg.DEFAULT_THEME_NAME in pg.THEMES
    assert pg.list_themes()[0] == "phthalo_green"
    assert pg.get_theme("phthalo_green") is pg.THEMES["phthalo_green"]

    with pytest.raises(KeyError):
        pg.get_theme("does_not_exist")


def test_set_theme_updates_everything():
    import phthalo_green as pg

    assert pg.PALETTE["primary"] == "#123524"
    green_cmap = pg.SEQUENTIAL_CMAP

    pg.set_theme("indigo")

    assert pg.PALETTE["primary"] == "#123A5C"
    assert pg.CATEGORICAL[1] == "#123A5C"
    assert pg.get_color("accent") == "#3390B8"
    assert pg.SEQUENTIAL_CMAP.name == "indigo"
    assert pg.SEQUENTIAL_CMAP is not green_cmap
    assert plt.rcParams["figure.facecolor"] == "#F8FAFC"

    pg.set_theme("phthalo_green")

    assert pg.PALETTE["primary"] == "#123524"
    assert pg.SEQUENTIAL_CMAP.name == "phthalo_green"


def test_with_theme_restores():
    import phthalo_green as pg

    with pg.with_theme("indigo") as theme:
        assert theme.label == "Indigo Ink"
        assert pg.PALETTE["primary"] == "#123A5C"
    assert pg.PALETTE["primary"] == "#123524"


def test_styled_restores_theme():
    import phthalo_green as pg

    with pg.styled("journal", theme="indigo"):
        assert pg.PALETTE["primary"] == "#123A5C"
    assert pg.PALETTE["primary"] == "#123524"


def test_subplots_theme_argument():
    import phthalo_green as pg

    fig, _ax = pg.subplots(theme="indigo")
    assert pg.PALETTE["primary"] == "#123A5C"
    assert fig is not None
    plt.close(fig)


def test_register_palette_from_single_color():
    import phthalo_green as pg

    theme = pg.register_palette("brand", {"primary": "#2F6F4E"}, label="Brand")
    assert theme in pg.THEMES.values()
    assert pg.get_theme("brand")["primary"] == pg.to_hex("#2F6F4E")

    colors = pg.get_theme("brand").colors
    assert set(pg.RAMP_KEYS).issubset(colors)
    assert set(pg.NEUTRAL_KEYS).issubset(colors)
    assert set(pg.ACCENT_KEYS).issubset(colors)
    assert len(pg.get_theme("brand").palette("categorical")) >= 6
    assert len(pg.get_theme("brand").palette("sequential")) >= 6


def test_make_theme_from_ramp_stays_monotonic():
    import phthalo_green as pg

    theme = pg.make_theme("ramp", ["#12261F", "#1E8C62", "#DDEBE3"])
    palette = theme.palette("categorical_green")
    assert len(set(palette)) == len(palette), "ramp roles must stay distinct"

    single = pg.make_theme("single", {"medium": "#176B45"})
    assert len(set(single.categorical_green)) == 6


def test_make_theme_errors():
    import phthalo_green as pg

    with pytest.raises(ValueError):
        pg.make_theme("bad", {})
    with pytest.raises(ValueError):
        pg.make_theme("bad", {"primary": "#fff", "not_a_role": "#000"})
    with pytest.raises(ValueError):
        pg.make_theme("", {"primary": "#fff"})


def test_register_theme_requires_override():
    import phthalo_green as pg

    theme = pg.make_theme("phthalo_green", {"primary": "#123524"})
    with pytest.raises(ValueError):
        pg.register_theme(theme)
    pg.register_theme(theme, override=True)
    assert pg.get_theme("phthalo_green") is theme


def test_colormaps_registered():
    import phthalo_green as pg

    pg.set_theme("phthalo_green")
    for name in ("phthalo_green", "phthalo_green_diverging"):
        assert name in mpl.colormaps

    pg.set_theme("indigo")
    for name in ("indigo", "indigo_diverging", "indigo_categorical"):
        assert name in mpl.colormaps

    pg.set_theme("phthalo_green")
    assert mpl.colormaps["phthalo_green"].name == "phthalo_green"


def test_get_cmap():
    import phthalo_green as pg

    assert pg.get_cmap("sequential").name == "phthalo_green"
    assert pg.get_cmap("diverging", theme="indigo").name == "indigo_diverging"
    discrete = pg.get_cmap("categorical", n=3)
    assert discrete.N == 3
    with pytest.raises(KeyError):
        pg.get_cmap("nope")


def test_dynamic_aliases_follow_theme():
    import phthalo_green as pg

    assert pg.PHTHALO_GREEN == "#123524"
    assert pg.EMERALD_GREEN == "#2E8B57"
    assert pg.DIVERGING_CMAP.name == "phthalo_green_diverging"

    with pg.with_theme("indigo"):
        assert pg.PHTHALO_GREEN == "#123A5C"
        assert pg.DIVERGING_CMAP.name == "indigo_diverging"

    with pytest.raises(AttributeError):
        _ = pg.NOT_A_REAL_NAME


def test_color_utilities():
    import phthalo_green as pg

    assert pg.to_hex("#ABC") == "#aabbcc"
    assert pg.mix("#000000", "#ffffff") == "#808080"
    assert pg.mix("#123524", "#123524") == "#123524"
    assert pg.lighten("#000000", 1.0) == "#ffffff"
    assert pg.darken("#ffffff", 1.0) == "#000000"
    assert pg.shift_hue("#123524", 180) != "#123524"
    assert pg.with_alpha("#123524", 0.5)[3] == 0.5
    assert pg.css_rgba("#123524", 0.5).startswith("rgba(")
    assert pg.contrast_ratio("#123524", "#FAFBFA") > 4.5
    assert pg.contrast_ratio("#000000", "#000000") == 1.0


def test_preset_rc_and_mplstyle(tmp_path):
    import phthalo_green as pg

    rc = pg.preset_rc("journal", "indigo", font_size=10)
    assert rc["figure.figsize"] == (6.3, 4.0)
    assert rc["font.size"] == 10

    path = pg.write_mplstyle(tmp_path / "style.mplstyle", preset="thesis")
    text = path.read_text()
    assert "figure.figsize" in text
    assert "phthalo_green" in text

    # Round-trip: the file must load without losing any colors. The style
    # parser treats "#" as a comment, so hex values are written bare and
    # the prop_cycle must be a real cycler(...) construction.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with plt.style.context(str(path)):
            loaded = {
                "facecolor": plt.rcParams["axes.facecolor"],
                "edgecolor": plt.rcParams["axes.edgecolor"],
                "cycle": plt.rcParams["axes.prop_cycle"].by_key()["color"],
                "figsize": plt.rcParams["figure.figsize"],
                "serif": plt.rcParams["font.serif"],
                "cmap": plt.rcParams["image.cmap"],
            }
    bad = [str(w.message) for w in caught if "Bad value" in str(w.message)]
    assert not bad, bad
    assert loaded["facecolor"] == pg.get_color("background")
    assert loaded["edgecolor"] == pg.get_color("charcoal")
    assert loaded["cycle"][0].upper() == pg.CATEGORICAL[0].upper()
    assert tuple(loaded["figsize"]) == (6.5, 4.2)
    assert "Times New Roman" in loaded["serif"]
    assert loaded["cmap"] == "phthalo_green"

    with pg.styled("single_column"):
        plt.style.use(pg.preset_rc("single_column", "indigo"))
        assert plt.rcParams["font.size"] == 8.5


def test_describe_theme():
    import phthalo_green as pg

    summary = pg.describe_theme("phthalo_green")
    assert summary["name"] == "phthalo_green"
    assert set(summary["palettes"]) == set(pg.PALETTE_KINDS)
    assert summary["colors"]["primary"] == "#123524"
    assert summary["colormaps"]["sequential"] == "phthalo_green"


def test_print_style_info(capsys):
    from phthalo_green import print_style_info

    print_style_info()
    out = capsys.readouterr().out
    assert "Phthalo Green" in out
    assert "thesis" in out


def test_style_axis_and_despine():
    import phthalo_green as pg

    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    pg.style_axis(ax, remove_top_right_spines=True)
    assert ax.spines["top"].get_visible() is False
    pg.style_axis(ax, grid=False, grid_axis="x", minor=True)
    pg.despine(ax)
    pg.style_legend(ax.legend(["one"]))
    pg.style_legend(None)
    plt.close(fig)


def test_plotly_template_structure():
    import phthalo_green as pg

    template = pg.plotly_template("indigo")
    layout = template["layout"]
    assert layout["colorway"][1] == "#123A5C"
    assert layout["colorscale"]["sequential"][0][1] == template[
        "layout"
    ]["colorscale"]["sequential"][0][1]
    assert layout["xaxis"]["gridcolor"].startswith("rgba(")
    assert "serif" in layout["font"]["family"]
    assert len(layout["colorscale"]["diverging"]) >= 3


def test_plotly_theme_requires_plotly():
    plotly = pytest.importorskip("plotly")
    import phthalo_green as pg

    pg.apply_plotly_theme("indigo")
    assert plotly.io.templates["indigo"] == pg.plotly_template("indigo")


def test_seaborn_style():
    pytest.importorskip("seaborn")
    import phthalo_green as pg

    pg.apply_seaborn_style(preset="thesis", theme="indigo")
    assert pg.PALETTE["primary"] == "#123A5C"
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    plt.close(fig)


def test_configure_latex():
    import phthalo_green as pg

    pg.configure_latex(use_tex=False)
    assert plt.rcParams["text.usetex"] is False
    pg.configure_latex(use_tex=True, preamble=[r"\usepackage{siunitx}"])
    assert plt.rcParams["text.usetex"] is True
    assert "siunitx" in plt.rcParams["text.latex.preamble"]
    pg.configure_latex(use_tex=False)


def test_cli(capsys):
    from phthalo_green.cli import main

    assert main(["--version"]) == 0
    assert main(["info"]) == 0
    assert main(["themes"]) == 0
    assert main(["show", "indigo"]) == 0
    assert main(["fonts"]) == 0

    out = capsys.readouterr().out
    assert "phthalo-green 0.1.1" in out
    assert "indigo" in out
    assert "#C4DCE9" in out

    assert main([]) == 0


def test_cli_write_style_and_preview(tmp_path):
    from phthalo_green.cli import main

    target = tmp_path / "cli.mplstyle"
    assert main(["write-style", str(target), "--preset", "journal"]) == 0
    assert target.exists()

    assert main(["preview", str(tmp_path), "--theme", "indigo"]) == 0
    assert (tmp_path / "preview_indigo.png").exists()


def test_example_scripts_run():
    """The minimal example is the documented copy-paste starting point."""

    import os
    import subprocess
    import sys
    from pathlib import Path

    repo = Path(__file__).resolve().parents[1]
    src = repo / "src"
    env = dict(os.environ, PYTHONPATH=str(src))
    result = subprocess.run(
        [sys.executable, "examples/01_minimal.py"],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
