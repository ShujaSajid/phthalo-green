# Phthalo Green

Publication-ready Matplotlib style for theses, papers, and talks.
Single import, five presets, PDF+PNG export helpers.

```python
from phthalo_green import PALETTE, export_figure, subplots

fig, ax = subplots(preset="thesis")
ax.plot(x, y, marker="o", color=PALETTE["primary"])
ax.set_title("My Result")
export_figure(fig, "figures/01_my_result")  # -> .pdf + .png
```

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
uv add "phthalo-green[gallery] @ git+https://github.com/YOUR_USERNAME/phthalo-green.git@v0.1.0"
```

### Option B — Vendor single file (no install, best for submission repos)

```powershell
Copy-Item "src/phthalo_green/style.py" "MyNewProject/phthalo_green.py"
```

```python
from phthalo_green import subplots, export_figure
```

`style.py` is self-contained (only needs `matplotlib`).

> PyPI (`uv add phthalo-green` with no URL) is intentionally not set up yet.
> It will be added later with `uv build` + `uv publish`. GitHub install above is all you need.

## Daily use

```python
from phthalo_green import PALETTE, subplots, export_figure

fig, ax = subplots(preset="thesis")  # thesis | journal | single_column | double_column | presentation
ax.plot(x, y, marker="o", color=PALETTE["primary"])
export_figure(fig, "figures/my_fig", formats=("pdf", "png"))
```

| Helper | Purpose |
| --- | --- |
| `apply_style(preset)` | Global style |
| `subplots(preset, ...)` | `apply_style` + `plt.subplots` |
| `figure(preset, ...)` | `apply_style` + `plt.figure` |
| `styled("journal")` | `with`-block temporary style |
| `export_figure(fig, basename, formats=("pdf","png"))` | Multi-format save + close |
| `save_publication_figure(fig, path)` | Single-file save |
| `get_palette("categorical", n)` | Interpolated palette |
| `SEQUENTIAL_CMAP` / `DIVERGING_CMAP` | Heatmaps, word clouds |

## Presets

| Preset | Size (in) | Use |
| --- | --- | --- |
| `thesis` | 6.5 × 4.2 | Default thesis/report |
| `journal` | 6.3 × 4.0 | Conservative journal |
| `single_column` | 3.4 × 2.6 | Narrow single column |
| `double_column` | 7.0 × 4.2 | Wide two-column |
| `presentation` | 10.0 × 6.0 | Slides/talks |

## Develop this repo

```powershell
uv sync --extra gallery --extra dev
uv run ruff check src tests examples
uv run pytest -q
uv run python examples/01_minimal.py
uv run python examples/02_gallery.py --preset thesis
uv build
```

Gallery output goes to `figures/gallery/` (git-ignored).
Core library needs only `matplotlib`; `numpy/pandas/seaborn/wordcloud` are only for `examples/` via the `gallery` extra.

## Layout

```text
src/phthalo_green/
  __init__.py   public API + __version__
  style.py      self-contained style (vendoring-friendly)
examples/
  01_minimal.py starter pattern
  02_gallery.py 17 chart recipes
tests/
  test_style.py smoke tests
```
