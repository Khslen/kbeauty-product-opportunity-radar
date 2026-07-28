from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# FONTS
# ============================================================
# Lora (serif) for headlines - editorial, soft, not shouting.
# Poppins (geometric sans) for everything else - clean and warm,
# very common in beauty/lifestyle branding.

FONT_TITLE = "Lora"
FONT_BODY = "Poppins"

_GOOGLE_FONTS_DIR = Path("/usr/share/fonts/truetype/google-fonts")

for _font_file in ("Lora-Variable.ttf", "Poppins-Regular.ttf", "Poppins-Medium.ttf", "Poppins-Bold.ttf"):
    _font_path = _GOOGLE_FONTS_DIR / _font_file
    if _font_path.exists():
        fm.fontManager.addfont(str(_font_path))


# ============================================================
# VISUAL DESIGN SYSTEM — soft K-beauty pastel
# ============================================================

COLORS = {
    "consumer_need": "#D98C93",     # dusty rose
    "ingredient": "#E3AD73",        # warm apricot
    "product_format": "#93AD82",    # muted sage
    "highlight": "#C3696A",         # deeper terracotta-rose, for emphasis
    "neutral": "#D9C9BE",           # warm taupe, for non-emphasized bars
    "dark": "#4A3F3D",              # warm charcoal (not pure black)
    "secondary": "#A69890",         # warm gray for ticks/secondary text
    "grid": "#EEE1D8",              # soft warm grid lines
    "light_background": "#FBF3EE", # card/panel fill
    "white": "#FFFCFA",             # near-white, warm figure background
}

CATEGORY_LABELS = {
    "consumer_need": "Consumer Need",
    "ingredient": "Ingredient",
    "product_format": "Product Format",
}


def apply_project_style() -> None:
    """
    Apply a consistent Matplotlib style across all project charts.
    """

    plt.rcParams.update(
        {
            "figure.facecolor": COLORS["white"],
            "axes.facecolor": COLORS["white"],
            "axes.edgecolor": COLORS["grid"],
            "axes.labelcolor": COLORS["dark"],
            "axes.titlecolor": COLORS["dark"],
            "xtick.color": COLORS["secondary"],
            "ytick.color": COLORS["secondary"],
            "text.color": COLORS["dark"],
            "font.family": "sans-serif",
            "font.sans-serif": [FONT_BODY, "DejaVu Sans"],
            "font.size": 11,
            "axes.titlesize": 20,
            "axes.titleweight": "regular",
            "axes.labelsize": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "axes.spines.bottom": False,
            "axes.grid": True,
            "grid.color": COLORS["grid"],
            "grid.alpha": 0.7,
            "grid.linewidth": 0.8,
            "legend.frameon": False,
        }
    )


def draw_header(
    fig,
    title: str,
    subtitle: str | None = None,
    x: float = 0.07,
    title_y: float = 0.965,
    subtitle_y: float = 0.925,
    title_size: float = 22,
    subtitle_size: float = 11,
) -> None:
    """
    Draw a consistent title (serif, Lora) + subtitle (sans, Poppins)
    header used across every chart in the project.
    """

    fig.text(
        x,
        title_y,
        title,
        fontsize=title_size,
        fontfamily=FONT_TITLE,
        weight="normal",
        color=COLORS["dark"],
        ha="left",
        va="top",
    )

    if subtitle:
        fig.text(
            x,
            subtitle_y,
            subtitle,
            fontsize=subtitle_size,
            fontfamily=FONT_BODY,
            color=COLORS["secondary"],
            ha="left",
            va="top",
        )


def make_bars_rounded(ax, bars, colors) -> None:
    """
    Replace flat bar rectangles with soft, pill-shaped bars
    (rounded on both ends) to match a softer visual style.
    Keeps the original bar objects' position data intact for
    any downstream label placement.
    """

    for bar, color in zip(bars, colors):

        x0, y0 = bar.get_xy()
        width = bar.get_width()
        height = bar.get_height()

        bar.set_visible(False)

        radius = min(height / 2, max(abs(width) / 2, 0.01))

        rounded = FancyBboxPatch(
            (x0, y0),
            width,
            height,
            boxstyle=f"round,pad=0,rounding_size={radius}",
            linewidth=0,
            facecolor=color,
            alpha=0.95,
            zorder=3,
            mutation_aspect=1,
        )

        ax.add_patch(rounded)


def rounded_card(ax, x, y, width, height, facecolor, edgecolor, radius=0.12, linewidth=1):
    """
    Draw a soft rounded-corner card (used in dashboard/summary charts)
    instead of a sharp-cornered rectangle.
    """

    card = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
    )

    ax.add_patch(card)

    return card


def format_keyword(value: str) -> str:
    """
    Convert values such as 'skin_barrier' into 'Skin Barrier'.
    """

    return str(value).replace("_", " ").strip().title()


def save_figure(fig, filename: str) -> Path:
    """
    Save a figure in the outputs folder using portfolio-quality settings.
    """

    output_path = OUTPUT_DIR / filename

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
        facecolor=COLORS["white"],
    )

    plt.close(fig)

    print(f"Saved: {output_path}")

    return output_path