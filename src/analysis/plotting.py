from pathlib import Path

import matplotlib.pyplot as plt


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# VISUAL DESIGN SYSTEM
# ============================================================

COLORS = {
    "consumer_need": "#4F8EF7",
    "ingredient": "#F4A261",
    "product_format": "#2A9D8F",
    "highlight": "#E76F51",
    "dark": "#222222",
    "secondary": "#6B7280",
    "grid": "#E5E7EB",
    "light_background": "#F8FAFC",
    "white": "#FFFFFF",
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
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "axes.titlesize": 20,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "axes.spines.bottom": False,
            "axes.grid": True,
            "grid.color": COLORS["grid"],
            "grid.alpha": 0.65,
            "grid.linewidth": 0.8,
            "legend.frameon": False,
        }
    )


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
        facecolor="white",
    )

    plt.close(fig)

    print(f"Saved: {output_path}")

    return output_path