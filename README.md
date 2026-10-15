# Phthalo Green

Publication-ready Matplotlib style for theses, papers, and talks — now with
swappable palettes (*themes*), an rcParams/mplstyle export, and adapters for
Seaborn and Plotly.

```python
import matplotlib.pyplot as plt
import phthalo_green as pg

fig, ax = pg.subplots(preset="thesis")               # style applied
ax.plot(x, y, color=pg.PALETTE["primary"])
pg.export_figure(fig, "figures/01_my_result")        # -> .pdf + .png
```

`pg.` (attribute access) is the recommended import style: palette constants and
colormaps follow the active theme. `pg.PALETTE`, `pg.CATEGORICAL`,
`pg.SEQUENTIAL`, ... are live containers, so `from phthalo_green import PALETTE`
also stays valid after a theme switch.

## Install

### Option A — GitHub only (simplest, no PyPI)

Publish this repo to GitHub, tag a version, then in any other project:

```powershell
# with uv (recommended)
uv add "phthalo-green @ git+https://github.com/YOUR_USERNAME/phthalo-green.git@v0.1.0"

# with pip
pip install "git+https://github.com/YOUR_USERNAME/phthalo-green.git@v0.1.0"
```

Update `YOUR_USERNAME` in `pyproject.toml` (`[project.urls]`) before pushing.
Create the tag after pushing:

```powershell
git tag v0.1.0
git push origin v0.1.0
```

Depend on a branch/commit during development:

```powershell
uv add "phthalo-green @ git+https://github.com/YOUR_USERNAME/phthalo-green.git@main"
```

Optional extras in the consumer project:

```powershell
uv add "phthalo-green[seaborn] @ git+https://github.com/YOUR_USERNAME/phthalo-green.git@v0.1.0"
uv add "phthalo-green[plotly]  @ git+https://github.com/YOUR_USERNAME/phthalo-green.git@v0.1.0"
uv add "phthalo-green[gallery] @ git+https://github.com/YOUR_USERNAME/phthalo-green.git@v0.1.0"
```

### Option B — Vendor single file (no install, best for submission repos)

```powershell
Copy-Item "src/phthalo_green/style.py" "MyNewProject/phthalo_green.py"
```

```python
from phthalo_green import subplots, export_figure
```

`style.py` is self-contained (only needs `matplotlib`) and carries the default
Phthalo Green palette plus `register_palette()` for your own.

> PyPI (`uv add phthalo-green` with no URL) is intentionally not set up yet.
> It will be added later with `uv build` + `uv publish`. GitHub install above is all you need.

## Daily use

```python
import phthalo_green as pg

fig, ax = pg.subplots(preset="thesis")   # thesis | journal | single_column | double_column | presentation
ax.plot(x, y, marker="o", color=pg.PALETTE["primary"])
ax.set_title("My Result")
pg.despine(ax)
pg.export_figure(fig, "figures/my_fig", formats=("pdf", "png"))
```

| Helper | Purpose |
| --- | --- |
| `apply_style(preset, theme, **overrides)` | Global style |
| `subplots(preset, theme, ...)` | `apply_style` + `plt.subplots` |
| `figure(preset, theme, ...)` | `apply_style` + `plt.figure` |
| `styled("journal")` | `with`-block temporary style |
| `export_figure(fig, basename, formats=("pdf","png"))` | Multi-format save + close |
| `save_publication_figure(fig, path)` | Single-file save |
| `get_color("primary")` | Named color from the active theme |
| `get_palette("categorical", n)` | Palette as hex list |
| `get_cmap("sequential")` | Registered colormap (also usable as a string name) |
| `despine(ax)` / `style_axis(ax)` / `style_legend(leg)` | Per-figure finishing |
| `preset_rc("journal")` | rcParams dict for `plt.style.use()` |
| `write_mplstyle(path)` | Dump the style to a `.mplstyle` file |
| `apply_seaborn_style(...)` | Seaborn colors + fonts |
| `apply_plotly_theme(...)` | Plotly template + colorscales |

## Presets

| Preset | Size (in) | Use |
| --- | --- | --- |
| `thesis` | 6.5 × 4.2 | Default thesis/report |
| `journal` | 6.3 × 4.0 | Conservative journal |
| `single_column` | 3.4 × 2.6 | Narrow single column |
| `double_column` | 7.0 × 4.2 | Wide two-column |
| `presentation` | 10.0 × 6.0 | Slides/talks |

Override anything inline:

```python
fig, ax = pg.subplots(preset="journal", font_size=11, figure_width=7)
pg.apply_style(preset="thesis", rc={"axes.grid": False})
```

## Themes (palettes)

`phthalo_green` is the default theme: the original Phthalo Green ramp with
restrained supporting hues and tinted neutrals. It is unchanged — the default
palette is asserted in `tests/test_style.py`.

`indigo` ships as a worked example of a *different* palette, and any new palette
is plain data:

```python
import phthalo_green as pg

# 1. derived from a single anchor colour (ramp, accents and neutrals are built
#    for you)
pg.register_palette("slate", {"primary": "#28405A"}, label="Slate Blue")

# 2. derived from an ordered dark -> light ramp
pg.register_palette("sandstone", ["#241A0C", "#7A5B24", "#B9903C", "#E3D3A6"])

# 3. full control: hand-tuned palettes
pg.register_theme(pg.make_theme(
    "monochrome",
    {"dark": "#1C1C1C", "primary": "#3F3F3F"},
    categorical=["#1C1C1C", "#3F3F3F", "#6E6E6E", "#A6A6A6", "#D6D6D6"],
    sequential=["#F5F5F5", "#C8C8C8", "#9C9C9C", "#6E6E6E", "#3F3F3F", "#1C1C1C"],
))

fig, ax = pg.subplots(theme="slate")     # style + palette in one call
```

Switch or scope themes at runtime:

```python
pg.set_theme("indigo")                    # everything follows

with pg.with_theme("phthalo_green"):      # temporary
    fig, ax = pg.subplots()

with pg.styled("journal", theme="indigo"):# temporary style + theme
    ...
```

A theme owns: the colour dictionary (`RAMP_KEYS`, `ACCENT_KEYS`,
`NEUTRAL_KEYS`), the four palettes (`categorical`, `categorical_green`,
`sequential`, `diverging`), the font stacks, and registered colormaps
(`indigo`, `indigo_diverging`, `indigo_categorical` — usable as strings).

CLI:

```powershell
phthalo-green themes                       # list themes
phthalo-green show indigo                  # swatches + hex values
phthalo-green info                         # active theme + presets
phthalo-green fonts                        # which serif font resolved
phthalo-green write-style pg.mplstyle --preset journal
phthalo-green preview figures/preview      # one sheet per theme
```

## Palettes

| Kind | Use |
| --- | --- |
| `categorical` | Independent series/datasets/models |
| `categorical_green` | Strictly monochromatic identity |
| `sequential` | Magnitude, heatmaps, word clouds |
| `diverging` | Values around a meaningful midpoint |

```python
colors = pg.get_palette("sequential", 5)
ax.imshow(matrix, cmap=pg.get_cmap("diverging"))
ax.scatter(x, y, c=z, cmap=pg.get_cmap("categorical", n=4))
```

Color utilities for custom figure elements: `pg.mix`, `lighten`, `darken`,
`shift_hue`, `with_alpha`, `css_rgba`, `contrast_ratio`.

## Other libraries

```python
pg.apply_seaborn_style(preset="thesis", palette="categorical")
sns.boxplot(data=df, palette=pg.get_palette("categorical", 3))

template = pg.plotly_template()            # plain dict, no plotly needed
# with plotly installed:
pg.apply_plotly_theme()                    # registers + sets default template
```

Pandas `.plot()` and other Matplotlib wrappers need nothing extra — they read
the rcParams set by `apply_style()`.

## Export

```python
pg.save_publication_figure(fig, "figures/fig1.pdf")
pg.save_publication_figure(fig, "figures/fig1.png", dpi=600, metadata={"Title": "Figure 1"})
pg.export_figure(fig, "figures/fig1", formats=("pdf", "png", "svg"))
```

Directories are created automatically; dots in filenames are preserved
(`figures/fig.v2` → `fig.v2.pdf`); `png` defaults to 600 dpi and vector formats
to 300 dpi.

Matplotlib-native alternative: `plt.style.use(pg.preset_rc("thesis"))`.

## Develop this repo

```powershell
uv sync --extra gallery --extra dev
uv run ruff check src tests examples
uv run pytest -q
uv run python examples/01_minimal.py
uv run python examples/02_gallery.py --preset thesis
uv run python examples/03_themes.py
uv run phthalo-green preview figures/preview
uv build
```

`pytest` also works without installing (`conftest.py` adds `src/` to the path).
Gallery output goes to `figures/gallery/` (git-ignored). Core library needs
only `matplotlib`; `numpy/pandas/seaborn/wordcloud/plotly` are optional extras
for `examples/` and the CLI.

## Layout

```text
src/phthalo_green/
   __init__.py   public API + theme-aware attribute forwarding
   style.py      self-contained style + theme engine (vendoring-friendly)
   themes.py     optional extra palettes (the "indigo" example)
   cli.py        command line interface
   py.typed      type information
examples/
   01_minimal.py starter pattern
   02_gallery.py 17 chart recipes
   03_themes.py  palette/theme recipes
tests/
   test_style.py smoke + palette-stability tests
```
