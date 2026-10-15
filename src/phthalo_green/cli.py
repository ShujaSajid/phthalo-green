"""
Command line interface for phthalo-green.

    phthalo-green info                       # active theme + presets
    phthalo-green themes                     # list registered themes
    phthalo-green show indigo                # palette swatches + hex values
    phthalo-green fonts                      # which fonts resolved
    phthalo-green write-style out.mplstyle --preset journal
    phthalo-green preview figures/preview    # sample figure sheet
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _swatch(color: str, width: int = 3) -> str:
    """Colored square for terminals, plain hex otherwise."""

    if not sys.stdout.isatty():
        return ""
    r, g, b = (round(channel * 255) for channel in _rgb(color))
    return f"\033[48;2;{r};{g};{b}m{' ' * width}\033[0m"


def _rgb(color: str) -> tuple[float, float, float]:
    import matplotlib.colors as mcolors

    r, g, b, _ = mcolors.to_rgba(color)
    return r, g, b


def _cmd_info(args: argparse.Namespace) -> int:
    from . import style

    style.print_style_info(args.theme)
    if args.theme:
        resolved = style.get_theme(args.theme)
    else:
        resolved = style.active_theme()
    print()
    print("Colors:")
    for name, value in resolved.colors.items():
        print(f"  {_swatch(value)} {name:<16} {value}")
    return 0


def _cmd_themes(args: argparse.Namespace) -> int:
    from . import style

    for name in style.list_themes():
        theme = style.get_theme(name)
        marker = "*" if theme is style.active_theme() else " "
        default = " (default)" if theme.is_default else ""
        print(f"{marker} {name:<20} {theme.label}{default}")
        if theme.description:
            print(f"    {theme.description}")
    print()
    print("* = active theme")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    from . import style

    theme = style.get_theme(args.theme)
    print(f"{theme.label} ({theme.name})")
    for kind in style.PALETTE_KINDS:
        colors = theme.palette(kind)
        print(f"\n{kind} ({len(colors)}):")
        for color in colors:
            print(f"  {_swatch(color)} {color}")
    return 0


def _cmd_fonts(args: argparse.Namespace) -> int:
    from . import style

    print("Serif resolution order:")
    for index, font in enumerate(style.FONT_SERIF_FALLBACKS, start=1):
        print(f"  {index}. {font}")
    print(f"\nMatplotlib will use: {style.resolved_serif_font()}")
    print(f"WordCloud font path: {style.WORDCLOUD_FONT_PATH}")
    print("\nSans-serif chain: " + ", ".join(style.FONT_SANS_FALLBACKS))
    return 0


def _cmd_write_style(args: argparse.Namespace) -> int:
    from . import style

    path = style.write_mplstyle(
        args.path, preset=args.preset, theme=args.theme
    )
    print(f"Wrote {path}")
    print("Use it with: plt.style.use(...)")
    return 0


def _cmd_preview(args: argparse.Namespace) -> int:
    from . import style

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - numpy is a gallery extra
        raise SystemExit(
            "The preview command needs numpy: pip install numpy "
            "(or install the 'gallery' extra)."
        ) from exc

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    style.apply_style(preset=args.preset, theme=args.theme)

    themes = [args.theme] if args.theme else style.list_themes()

    for name in themes:
        theme = style.get_theme(name)
        fig, axes = plt.subplots(2, 3, figsize=(12, 7))
        fig.suptitle(f"{theme.label} — {name}", fontsize=16)

        swatches = theme.palette("categorical")
        for index, color in enumerate(swatches):
            ax = axes.flat[0]
            ax.bar(index, 1, color=color, edgecolor=theme["dark"], linewidth=0.5)
            ax.text(index, 1.02, color, rotation=90, fontsize=6, ha="center")
        ax = axes.flat[0]
        ax.set_title("categorical")
        ax.set_ylim(0, 1.2)
        ax.set_xticks([])
        ax.set_yticks([])

        x = np.linspace(0, 1, 10)
        for index, color in enumerate(theme.palette("categorical")):
            axes.flat[1].plot(x, x ** (0.4 + index * 0.2), color=color, marker="o")
        axes.flat[1].set_title("line ramp")

        for index, color in enumerate(theme.palette("sequential")):
            axes.flat[2].barh(index, 1, color=color)
        axes.flat[2].set_title("sequential")
        axes.flat[2].set_xticks([])
        axes.flat[2].set_yticks([])

        data = np.random.default_rng(4).normal(size=(8, 8))
        axes.flat[3].imshow(data, cmap=theme.cmap("diverging"))
        axes.flat[3].set_title("diverging heatmap")
        axes.flat[3].set_xticks([])
        axes.flat[3].set_yticks([])

        data2 = np.abs(np.random.default_rng(7).normal(size=(8, 8)))
        axes.flat[4].imshow(data2, cmap=theme.cmap("sequential"))
        axes.flat[4].set_title("sequential heatmap")
        axes.flat[4].set_xticks([])
        axes.flat[4].set_yticks([])

        for ax in axes[0]:
            style.despine(ax)

        written = style.export_figure(fig, out / f"preview_{name}")
        print("Wrote " + ", ".join(str(p) for p in written))

    print(f"Done: {len(themes)} theme(s) -> {out}/")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phthalo-green",
        description="Phthalo Green academic visualization style toolkit.",
    )
    parser.add_argument(
        "--version", action="store_true", help="print the library version"
    )
    sub = parser.add_subparsers(dest="command")

    info = sub.add_parser("info", help="describe a theme and its settings")
    info.add_argument("--theme", default=None, help="theme name (default: active)")
    info.set_defaults(func=_cmd_info)

    themes = sub.add_parser("themes", help="list registered themes")
    themes.set_defaults(func=_cmd_themes)

    show = sub.add_parser("show", help="print palettes as hex swatches")
    show.add_argument("theme", nargs="?", default=None)
    show.set_defaults(func=_cmd_show)

    fonts = sub.add_parser("fonts", help="show resolved fonts")
    fonts.set_defaults(func=_cmd_fonts)

    write = sub.add_parser("write-style", help="write a .mplstyle file")
    write.add_argument("path", help="output path, e.g. phthalo_green.mplstyle")
    write.add_argument("--preset", default="thesis")
    write.add_argument("--theme", default=None)
    write.set_defaults(func=_cmd_write_style)

    preview = sub.add_parser("preview", help="render a preview figure sheet")
    preview.add_argument("output", help="output directory")
    preview.add_argument("--preset", default="thesis")
    preview.add_argument("--theme", default=None, help="preview one theme only")
    preview.set_defaults(func=_cmd_preview)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        from . import __version__

        print(f"phthalo-green {__version__}")
        return 0

    if not getattr(args, "command", None):
        parser.print_help()
        return 0

    return args.func(args) or 0


if __name__ == "__main__":
    raise SystemExit(main())
