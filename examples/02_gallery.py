"""Full Phthalo Green gallery: one function per chart type.

Every function is self-contained — copy the one you need into your own
``make_figures.py`` and replace the synthetic data with yours.

Run:
    uv run python examples/02_gallery.py                 # thesis preset
    uv run python examples/02_gallery.py --preset journal
    uv run python examples/02_gallery.py --preset presentation

Output:
    figures/gallery/*.pdf + *.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from phthalo_green import (
    CATEGORICAL,
    DIVERGING_CMAP,
    PALETTE,
    SEQUENTIAL_CMAP,
    WORDCLOUD_FONT_PATH,
    apply_style,
    export_figure,
    style_axis,
    style_legend,
)

OUT = Path(__file__).resolve().parents[1] / "figures" / "gallery"
FORMATS = ("pdf", "png")


def _save(fig, name: str):
    return export_figure(fig, OUT / name, formats=FORMATS)


# ---------------------------------------------------------------------------
# 1. Line + Bar charts
# ---------------------------------------------------------------------------

def fig_line_single():
    x = np.arange(2018, 2026)
    y = np.array([12, 18, 25, 31, 40, 52, 61, 74])
    fig, ax = plt.subplots()
    ax.plot(x, y, marker="o", color=PALETTE["primary"])
    ax.set_title("Single-Series Trend")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    style_axis(ax, remove_top_right_spines=True)
    _save(fig, "01_line_single")


def fig_line_multi():
    x = np.arange(2018, 2026)
    series = {
        "Method A": [10, 14, 19, 24, 30, 38, 45, 55],
        "Method B": [8, 11, 15, 18, 24, 29, 36, 44],
        "Method C": [5, 7, 9, 13, 17, 22, 28, 35],
    }
    fig, ax = plt.subplots()
    for i, (label, y) in enumerate(series.items()):
        ax.plot(x, y, marker=["o", "s", "^"][i], label=label,
                color=CATEGORICAL[i])
    ax.set_title("Multi-Series Comparison")
    ax.set_xlabel("Year")
    ax.set_ylabel("F1 Score (%)")
    style_axis(ax, remove_top_right_spines=True)
    style_legend(ax.legend())
    _save(fig, "02_line_multi")


def fig_bar_vertical():
    cats = ["A", "B", "C", "D"]
    vals = [34, 52, 41, 63]
    fig, ax = plt.subplots()
    bars = ax.bar(cats, vals, color=PALETTE["medium"],
                  edgecolor=PALETTE["dark"])
    ax.bar_label(bars)
    ax.set_title("Vertical Bar")
    ax.set_ylabel("Count")
    style_axis(ax, remove_top_right_spines=True)
    _save(fig, "03_bar_vertical")


def fig_bar_horizontal():
    cats = ["Journal X", "Journal Y", "Journal Z", "Conf W"]
    vals = [42, 35, 28, 19]
    fig, ax = plt.subplots()
    ax.barh(cats, vals, color=CATEGORICAL[: len(cats)])
    ax.set_title("Horizontal Bar (Top Journals)")
    ax.set_xlabel("Papers")
    style_axis(ax, remove_top_right_spines=True)
    _save(fig, "04_bar_horizontal")


def fig_bar_grouped():
    labels = ["2022", "2023", "2024"]
    a = [20, 28, 35]
    b = [15, 22, 30]
    x = np.arange(len(labels))
    w = 0.35
    fig, ax = plt.subplots()
    ax.bar(x - w / 2, a, w, label="Group 1", color=PALETTE["primary"])
    ax.bar(x + w / 2, b, w, label="Group 2", color=PALETTE["light"],
           edgecolor=PALETTE["dark"])
    ax.set_xticks(x, labels)
    ax.set_title("Grouped Bar")
    ax.set_ylabel("Count")
    style_axis(ax, remove_top_right_spines=True)
    style_legend(ax.legend())
    _save(fig, "05_bar_grouped")


def fig_bar_stacked():
    years = ["2022", "2023", "2024"]
    df = pd.DataFrame(
        {"Type A": [10, 14, 18], "Type B": [8, 11, 13], "Type C": [5, 7, 9]},
        index=years,
    )
    fig, ax = plt.subplots()
    df.plot(kind="bar", stacked=True, color=CATEGORICAL, ax=ax)
    ax.set_title("Stacked Bar per Year")
    ax.set_ylabel("Count")
    ax.set_xlabel("Year")
    style_axis(ax, remove_top_right_spines=True)
    style_legend(ax.legend())
    fig.tight_layout()
    _save(fig, "06_bar_stacked")


# ---------------------------------------------------------------------------
# 2. Statistical plots
# ---------------------------------------------------------------------------

def fig_scatter():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 120)
    y = 2 * x + rng.normal(0, 0.8, 120)
    fig, ax = plt.subplots()
    ax.scatter(x, y, s=28, color=PALETTE["medium"],
               edgecolors=PALETTE["dark"], linewidths=0.5, alpha=0.85)
    ax.set_title("Scatter")
    ax.set_xlabel("Feature X")
    ax.set_ylabel("Target Y")
    style_axis(ax, remove_top_right_spines=True)
    _save(fig, "07_scatter")


def fig_scatter_errorbar():
    x = np.arange(5)
    y = np.array([3.1, 4.4, 4.0, 5.2, 6.1])
    yerr = np.array([0.4, 0.5, 0.3, 0.6, 0.4])
    fig, ax = plt.subplots()
    ax.errorbar(x, y, yerr=yerr, fmt="o-", capsize=3,
                color=PALETTE["primary"], ecolor=PALETTE["slate"])
    ax.set_title("Line + Error Bars")
    ax.set_xlabel("Condition")
    ax.set_ylabel("Mean ± SD")
    style_axis(ax, remove_top_right_spines=True)
    _save(fig, "08_errorbar")


def fig_histogram():
    rng = np.random.default_rng(1)
    data = np.concatenate([rng.normal(0, 1, 400), rng.normal(3, 1.2, 300)])
    fig, ax = plt.subplots()
    ax.hist(data, bins=30, color=PALETTE["primary"],
            edgecolor=PALETTE["dark"], linewidth=0.5)
    ax.set_title("Histogram")
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")
    style_axis(ax, remove_top_right_spines=True)
    _save(fig, "09_histogram")


def fig_box_violin():
    rng = np.random.default_rng(2)
    groups = [rng.normal(loc, 1.0, 100) for loc in (0, 1.5, 3.0)]
    fig, axes = plt.subplots(1, 2)
    bp = axes[0].boxplot(groups, tick_labels=["A", "B", "C"], patch_artist=True)
    for patch in bp["boxes"]:
        patch.set_facecolor(PALETTE["pale"])
        patch.set_edgecolor(PALETTE["dark"])
    axes[0].set_title("Boxplot")
    axes[0].set_ylabel("Score")
    axes[1].violinplot(groups, showmeans=True)
    axes[1].set_xticks([1, 2, 3], ["A", "B", "C"])
    axes[1].set_title("Violin")
    for ax in axes:
        style_axis(ax, remove_top_right_spines=True)
    fig.tight_layout()
    _save(fig, "10_box_violin")


# ---------------------------------------------------------------------------
# 3. Heatmap + WordCloud
# ---------------------------------------------------------------------------

def fig_heatmap_sequential():
    rng = np.random.default_rng(3)
    mat = np.abs(rng.normal(5, 3, size=(6, 8)))
    fig, ax = plt.subplots()
    im = ax.imshow(mat, cmap=SEQUENTIAL_CMAP, aspect="auto")
    fig.colorbar(im, ax=ax, label="Frequency")
    ax.set_title("Sequential Heatmap")
    ax.set_xlabel("Year")
    ax.set_ylabel("Keyword")
    ax.set_xticks(range(8), [str(2018 + i) for i in range(8)], rotation=45)
    ax.set_yticks(range(6), [f"KW{i+1}" for i in range(6)])
    _save(fig, "11_heatmap_sequential")


def fig_heatmap_diverging():
    rng = np.random.default_rng(4)
    mat = rng.normal(0, 1, size=(6, 6))
    fig, ax = plt.subplots()
    im = ax.imshow(mat, cmap=DIVERGING_CMAP, aspect="auto",
                   vmin=-2, vmax=2)
    fig.colorbar(im, ax=ax, label="Std. dev. from mean")
    ax.set_title("Diverging Heatmap")
    _save(fig, "12_heatmap_diverging")


def fig_wordcloud():
    from wordcloud import WordCloud

    text = ("phthalo green academic visualization thesis journal paper "
            "research method result analysis figure data " * 12)
    cloud = WordCloud(
        width=800, height=400,
        font_path=WORDCLOUD_FONT_PATH,
        background_color=PALETTE["background"],
        colormap=SEQUENTIAL_CMAP,
        contour_width=3,
        contour_color=PALETTE["medium"],
    ).generate(text)
    fig, ax = plt.subplots()
    ax.imshow(cloud, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Word Cloud")
    _save(fig, "13_wordcloud")


# ---------------------------------------------------------------------------
# 4. Thesis extras
# ---------------------------------------------------------------------------

def fig_subplots_grid():
    x = np.arange(10)
    fig, axes = plt.subplots(2, 2)
    axes[0, 0].plot(x, x, color=PALETTE["primary"])
    axes[0, 0].set_title("Linear")
    axes[0, 1].plot(x, x ** 2, color=PALETTE["medium"])
    axes[0, 1].set_title("Quadratic")
    axes[1, 0].bar(x[:5], x[:5] + 1, color=PALETTE["accent"])
    axes[1, 0].set_title("Bars")
    axes[1, 1].scatter(x, np.sin(x), color=PALETTE["dark"])
    axes[1, 1].set_title("Scatter")
    for ax in axes.flat:
        style_axis(ax, remove_top_right_spines=True)
    fig.suptitle("2x2 Subplots Grid")
    fig.tight_layout()
    _save(fig, "14_subplots_grid")


def fig_twin_axis():
    x = np.arange(2018, 2026)
    counts = [12, 18, 25, 31, 40, 52, 61, 74]
    share = [22, 25, 28, 31, 35, 38, 41, 45]
    fig, ax1 = plt.subplots()
    ax1.plot(x, counts, marker="o", color=PALETTE["primary"], label="Count")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Papers", color=PALETTE["primary"])
    ax2 = ax1.twinx()
    ax2.plot(x, share, marker="s", color=PALETTE["ochre"] if "ochre" in PALETTE else CATEGORICAL[5], label="Share")
    ax2.set_ylabel("Share (%)")
    fig.suptitle("Twin Axis")
    style_axis(ax1, remove_top_right_spines=True)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    style_legend(ax1.legend(lines1 + lines2, labels1 + labels2))
    _save(fig, "15_twin_axis")


def fig_pie_donut():
    sizes = [40, 30, 20, 10]
    labels = ["Green", "Teal", "Ochre", "Rust"]
    fig, axes = plt.subplots(1, 2)
    axes[0].pie(sizes, labels=labels,
                colors=[PALETTE["primary"], PALETTE["medium"],
                        PALETTE["ochre"], PALETTE["rust"]],
                autopct="%1.0f%%")
    axes[0].set_title("Pie")
    axes[1].pie(sizes, colors=[PALETTE["primary"], PALETTE["medium"],
                               PALETTE["light"], PALETTE["pale"]],
                wedgeprops={"width": 0.45, "edgecolor": PALETTE["background"]})
    axes[1].legend(labels, loc="center")
    axes[1].set_title("Donut")
    fig.suptitle("Composition")
    fig.tight_layout()
    _save(fig, "16_pie_donut")


def fig_seaborn():
    import seaborn as sns

    from phthalo_green import apply_seaborn_style

    apply_seaborn_style(preset="thesis")
    df = pd.DataFrame({
        "year": np.repeat([2022, 2023, 2024], 30),
        "score": np.concatenate([
            np.random.default_rng(0).normal(70, 8, 30),
            np.random.default_rng(1).normal(75, 7, 30),
            np.random.default_rng(2).normal(80, 6, 30),
        ]),
    })
    fig, ax = plt.subplots()
    sns.barplot(data=df, x="year", y="score", hue="year", legend=False,
                errorbar="sd", palette=CATEGORICAL[:3], ax=ax)
    ax.set_title("Seaborn Bar (mean ± SD)")
    style_axis(ax, remove_top_right_spines=True)
    _save(fig, "17_seaborn")


GALLERY = [
    fig_line_single, fig_line_multi, fig_bar_vertical, fig_bar_horizontal,
    fig_bar_grouped, fig_bar_stacked, fig_scatter, fig_scatter_errorbar,
    fig_histogram, fig_box_violin, fig_heatmap_sequential,
    fig_heatmap_diverging, fig_wordcloud, fig_subplots_grid,
    fig_twin_axis, fig_pie_donut, fig_seaborn,
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", default="thesis",
                        choices=["thesis", "journal", "presentation",
                                 "single_column", "double_column"])
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    apply_style(preset=args.preset)

    for fn in GALLERY:
        fn()
        print(f"  wrote {fn.__name__}")

    print(f"Done: {len(GALLERY)} figures x {len(FORMATS)} formats -> {OUT}/")


if __name__ == "__main__":
    main()
