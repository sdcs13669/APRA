"""
Generate academic-style figures for the APRA competition document.
Follows nature-figure conventions: restrained palette, hero panel, clean layout.
"""
import json
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

# --- rcParams (nature-figure Python quick-start) ---
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 7,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "legend.frameon": False,
})

# --- Palette ---
PALETTE = {
    "blue_main": "#0F4D92", "blue_secondary": "#3775BA",
    "green_2": "#AADCA9", "green_3": "#8BCF8B",
    "red_1": "#F6CFCB", "red_2": "#E9A6A1", "red_strong": "#B64342",
    "neutral_light": "#CFCECE", "neutral_mid": "#767676",
    "neutral_dark": "#4D4D4D", "neutral_black": "#272727",
    "teal": "#42949E", "violet": "#9A4D8E", "gold": "#D4A017",
}
DEFENSE_COLORS = {
    "apra": PALETTE["blue_main"],
    "avg": PALETTE["red_strong"],
    "clip": PALETTE["neutral_mid"],
    "deepsight": PALETTE["teal"],
    "foolsgold": PALETTE["gold"],
    "rflbat": PALETTE["violet"],
}
DEFENSE_LABELS = {
    "apra": "APRA\n(ours)", "avg": "FedAvg", "clip": "Clip",
    "deepsight": "DeepSight", "foolsgold": "FoolsGold", "rflbat": "RFLBAT",
}
ATTACK_LABELS = {
    "a3fl": "A3FL", "doba": "DOBA", "modelreplace": "ModelReplace",
    "neurotoxin": "Neurotoxin", "reba": "ReBA",
}
ATTACK_ORDER = ["a3fl", "doba", "modelreplace", "neurotoxin", "reba"]
DEFENSE_ORDER = ["apra", "avg", "clip", "deepsight", "foolsgold", "rflbat"]
DATASET_LABELS = {"cifar10": "CIFAR-10", "cifar100": "CIFAR-100"}


def load_summary(dataset):
    path = Path(f"apra-showcase/public/data/accuracy/summary_{dataset}.json")
    with open(path) as f:
        return json.load(f)


def save_pub(fig, filename):
    fig.savefig(f"{filename}.svg", bbox_inches="tight")
    fig.savefig(f"{filename}.pdf", bbox_inches="tight")
    fig.savefig(f"{filename}.png", dpi=300, bbox_inches="tight")
    print(f"Saved: {filename}.svg/.pdf/.png")


# ================================================================
# Figure 1: ASR comparison — hero panel
# ================================================================
def figure_asr_comparison():
    data = {ds: load_summary(ds) for ds in ["cifar10", "cifar100"]}

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6), sharey=False)
    fig.subplots_adjust(wspace=0.12)

    for col, (ds, ax) in enumerate(zip(["cifar10", "cifar100"], axes)):
        x = np.arange(len(ATTACK_ORDER))
        n_def = len(DEFENSE_ORDER)
        w = 0.8 / n_def

        for i, defense in enumerate(DEFENSE_ORDER):
            vals = [data[ds].get(defense, {}).get(a, {}).get("asr", 0) for a in ATTACK_ORDER]
            offset = (i - (n_def - 1) / 2) * w
            bars = ax.bar(x + offset, vals, w, color=DEFENSE_COLORS[defense],
                         edgecolor="white", linewidth=0.3, label=DEFENSE_LABELS.get(defense, defense),
                         zorder=2 if defense == "apra" else 1)
            # APRA bar slightly more prominent
            if defense == "apra":
                for bar in bars:
                    bar.set_edgecolor(PALETTE["neutral_dark"])
                    bar.set_linewidth(0.6)

        ax.set_xticks(x)
        ax.set_xticklabels([ATTACK_LABELS[a] for a in ATTACK_ORDER], fontsize=6)
        ax.set_ylabel("Backdoor ASR (%)" if col == 0 else "", fontsize=7)
        ax.set_title(DATASET_LABELS[ds], fontsize=8, fontweight="bold", color=PALETTE["neutral_black"], pad=4)
        ax.set_ylim(0, 105)
        ax.grid(axis="y", color=PALETTE["neutral_light"], linewidth=0.4, alpha=0.6)
        ax.set_axisbelow(True)

    # Single centered legend below
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncols=6, fontsize=5.5,
               bbox_to_anchor=(0.5, -0.08), columnspacing=0.6)

    fig.suptitle("Backdoor Attack Success Rate (ASR) — All Defenses × All Attacks",
                 fontsize=9, fontweight="bold", color=PALETTE["neutral_black"], y=1.01)
    return fig


# ================================================================
# Figure 2: Accuracy comparison
# ================================================================
def figure_accuracy_comparison():
    data = {ds: load_summary(ds) for ds in ["cifar10", "cifar100"]}

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6), sharey=False)
    fig.subplots_adjust(wspace=0.12)

    for col, (ds, ax) in enumerate(zip(["cifar10", "cifar100"], axes)):
        x = np.arange(len(ATTACK_ORDER))
        n_def = len(DEFENSE_ORDER)
        w = 0.8 / n_def

        for i, defense in enumerate(DEFENSE_ORDER):
            vals = [data[ds].get(defense, {}).get(a, {}).get("accuracy", 0) for a in ATTACK_ORDER]
            offset = (i - (n_def - 1) / 2) * w
            ax.bar(x + offset, vals, w, color=DEFENSE_COLORS[defense],
                   edgecolor="white", linewidth=0.3, label=DEFENSE_LABELS.get(defense, defense),
                   zorder=2 if defense == "apra" else 1)

        ax.set_xticks(x)
        ax.set_xticklabels([ATTACK_LABELS[a] for a in ATTACK_ORDER], fontsize=6)
        ax.set_ylabel("Main Task Accuracy (%)" if col == 0 else "", fontsize=7)
        ax.set_title(DATASET_LABELS[ds], fontsize=8, fontweight="bold", color=PALETTE["neutral_black"], pad=4)

        if ds == "cifar10":
            ax.set_ylim(80, 98)
        else:
            ax.set_ylim(58, 72)

        ax.grid(axis="y", color=PALETTE["neutral_light"], linewidth=0.4, alpha=0.6)
        ax.set_axisbelow(True)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncols=6, fontsize=5.5,
               bbox_to_anchor=(0.5, -0.08), columnspacing=0.6)

    fig.suptitle("Main Task Accuracy — All Defenses × All Attacks",
                 fontsize=9, fontweight="bold", color=PALETTE["neutral_black"], y=1.01)
    return fig


# ================================================================
# Figure 3: ASR reduction summary (APRA vs baselines)
# ================================================================
def figure_asr_reduction_summary():
    data = {ds: load_summary(ds) for ds in ["cifar10", "cifar100"]}

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
    fig.subplots_adjust(wspace=0.2)

    for col, (ds, ax) in enumerate(zip(["cifar10", "cifar100"], axes)):
        # Compute average ASR per defense across all 5 attacks
        avg_asr = {}
        for defense in DEFENSE_ORDER:
            vals = [data[ds].get(defense, {}).get(a, {}).get("asr", 0) for a in ATTACK_ORDER]
            avg_asr[defense] = np.mean(vals)

        colors = [DEFENSE_COLORS[d] for d in DEFENSE_ORDER]
        labels = [DEFENSE_LABELS[d] for d in DEFENSE_ORDER]
        values = [avg_asr[d] for d in DEFENSE_ORDER]

        bars = ax.bar(range(len(DEFENSE_ORDER)), values, color=colors, edgecolor="white", linewidth=0.4, width=0.6)
        # Annotate values on bars
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                    f"{val:.1f}%", ha="center", va="bottom", fontsize=6.5, fontweight="bold",
                    color=PALETTE["neutral_dark"])

        ax.set_xticks(range(len(DEFENSE_ORDER)))
        ax.set_xticklabels(labels, fontsize=6)
        ax.set_ylabel("Average ASR (%)" if col == 0 else "", fontsize=7)
        ax.set_title(DATASET_LABELS[ds], fontsize=8, fontweight="bold", color=PALETTE["neutral_black"], pad=4)
        ax.grid(axis="y", color=PALETTE["neutral_light"], linewidth=0.4, alpha=0.6)
        ax.set_axisbelow(True)

        # Highlight APRA
        bars[0].set_edgecolor(PALETTE["neutral_dark"])
        bars[0].set_linewidth(1.0)

    fig.suptitle("Average ASR Across All Five Attacks — Lower Is Better",
                 fontsize=9, fontweight="bold", color=PALETTE["neutral_black"], y=1.01)

    # Add annotation: % reduction vs FedAvg
    for col, ds in enumerate(["cifar10", "cifar100"]):
        apra_avg = np.mean([data[ds].get("apra", {}).get(a, {}).get("asr", 0) for a in ATTACK_ORDER])
        avg_avg = np.mean([data[ds].get("avg", {}).get(a, {}).get("asr", 0) for a in ATTACK_ORDER])
        reduction = (1 - apra_avg / avg_avg) * 100 if avg_avg > 0 else 0
        axes[col].annotate(f"APRA reduces ASR\nby {reduction:.0f}% vs FedAvg",
                          xy=(0.5, 0.95), xycoords="axes fraction",
                          ha="center", va="top", fontsize=6.5, fontweight="bold",
                          color=PALETTE["blue_main"],
                          bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                                   edgecolor=PALETTE["blue_main"], alpha=0.9, linewidth=0.6))

    return fig


# ================================================================
# Figure 4: Accuracy maintenance summary
# ================================================================
def figure_accuracy_summary():
    data = {ds: load_summary(ds) for ds in ["cifar10", "cifar100"]}

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
    fig.subplots_adjust(wspace=0.2)

    for col, (ds, ax) in enumerate(zip(["cifar10", "cifar100"], axes)):
        avg_acc = {}
        for defense in DEFENSE_ORDER:
            vals = [data[ds].get(defense, {}).get(a, {}).get("accuracy", 0) for a in ATTACK_ORDER]
            avg_acc[defense] = np.mean(vals)

        colors = [DEFENSE_COLORS[d] for d in DEFENSE_ORDER]
        labels = [DEFENSE_LABELS[d] for d in DEFENSE_ORDER]
        values = [avg_acc[d] for d in DEFENSE_ORDER]

        bars = ax.bar(range(len(DEFENSE_ORDER)), values, color=colors, edgecolor="white", linewidth=0.4, width=0.6)

        # Annotate
        for bar, val in zip(bars, values):
            offset = -3.5 if col == 0 else -2.5
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + offset,
                    f"{val:.1f}%", ha="center", va="top", fontsize=6.5, fontweight="bold",
                    color=PALETTE["neutral_dark"])

        ax.set_xticks(range(len(DEFENSE_ORDER)))
        ax.set_xticklabels(labels, fontsize=6)
        ax.set_ylabel("Average Accuracy (%)" if col == 0 else "", fontsize=7)
        ax.set_title(DATASET_LABELS[ds], fontsize=8, fontweight="bold", color=PALETTE["neutral_black"], pad=4)
        ax.grid(axis="y", color=PALETTE["neutral_light"], linewidth=0.4, alpha=0.6)
        ax.set_axisbelow(True)

        if ds == "cifar10":
            ax.set_ylim(80, 96)
        else:
            ax.set_ylim(55, 72)

        # Highlight APRA
        bars[0].set_edgecolor(PALETTE["neutral_dark"])
        bars[0].set_linewidth(1.0)

    fig.suptitle("Average Main Task Accuracy Across All Five Attacks — Higher Is Better",
                 fontsize=9, fontweight="bold", color=PALETTE["neutral_black"], y=1.01)
    return fig


# ================================================================
# Main
# ================================================================
if __name__ == "__main__":
    out_dir = Path("APRA_Presentation_meaningful_images")
    out_dir.mkdir(exist_ok=True)

    print("Generating Figure 1: ASR comparison...")
    save_pub(figure_asr_comparison(), out_dir / "fig_asr_comparison")

    print("Generating Figure 2: Accuracy comparison...")
    save_pub(figure_accuracy_comparison(), out_dir / "fig_accuracy_comparison")

    print("Generating Figure 3: ASR reduction summary...")
    save_pub(figure_asr_reduction_summary(), out_dir / "fig_asr_reduction")

    print("Generating Figure 4: Accuracy maintenance summary...")
    save_pub(figure_accuracy_summary(), out_dir / "fig_accuracy_maintenance")

    print("Done — all figures generated.")
