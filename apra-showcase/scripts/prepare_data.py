"""
Prepare experiment data for the APRA showcase website.

Reads raw experiment results from ../../main/re_result_6-29_APRA/ and
generates cleaned CSV files + summary.json in public/data/.

Supports both CIFAR-10 and CIFAR-100 datasets with separate file naming.
"""
import csv
import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RESULT_DIR = BASE_DIR.parent / "main" / "re_result_6-29_APRA"
PUBLIC_DATA = BASE_DIR / "public" / "data"
ACCURACY_DIR = PUBLIC_DATA / "accuracy"
TRAJECTORY_DIR = PUBLIC_DATA / "trajectory"

ATTACK_MAP = {
    "a3fl": "a3fl",
    "sin-adv_DOBA": "doba",
    "doba": "doba",
    "sin-adv": "doba",
    "neurotoxin": "neurotoxin",
    "modelreplace": "modelreplace",
    "modelreplace_2": "modelreplace",
    "modelreplace_5": "modelreplace",
    "reba": "reba",
}

DEFENSE_METHODS = ["apra", "avg", "clip", "deepsight", "foolsgold", "rflbat"]
DATASETS = ["cifar10", "cifar100"]


def parse_dirname(dirname: str):
    """Parse directory naming patterns:
    - Standard: {dataset}_{epochs}_{date}_{time}_{method}_fix_True_{mia}_{mia_class}_{noise}_{attack}
    - ReBA:     {dataset}_{epochs}_{date}_{time}_{method}_True_no-noise_{attack}
    Returns (dataset, defense, attack) or (None, None, None).
    """
    parts = dirname.split("_")

    # Identify dataset
    dataset = None
    for ds in DATASETS:
        if dirname.startswith(ds + "_"):
            dataset = ds
            break
    if dataset is None:
        return None, None, None

    # Identify defense method
    defense = None
    for dm in DEFENSE_METHODS:
        if dm in parts:
            defense = dm
            break
    if defense is None:
        return None, None, None

    # Find attack: after defense, look for "fix" or "True" marker, then attack follows
    attack_raw = None
    try:
        dm_idx = parts.index(defense)
        # ReBA pattern: parts after defense: ["True", "no-noise", "reba"]
        # Standard pattern: parts after defense: ["fix", "True", "no-mia", "no-mia-class", "no-noise", "attack..."]
        after_def = parts[dm_idx + 1:]
        # Find the attack by checking remaining parts against ATTACK_MAP
        for i, p in enumerate(after_def):
            if p in ATTACK_MAP:
                attack_raw = p
                break
        # If not found as single token, try combining remaining parts
        if attack_raw is None and len(after_def) >= 1:
            # For patterns like sin-adv_DOBA which split across underscores
            remaining = "_".join(after_def)
            for key in sorted(ATTACK_MAP.keys(), key=len, reverse=True):
                if key in remaining:
                    attack_raw = key
                    break
    except (ValueError, IndexError):
        pass

    if attack_raw is None:
        return None, None, None

    attack = ATTACK_MAP.get(attack_raw)
    return dataset, defense, attack


def copy_csv(pattern: str, src_dir: Path, dst: Path):
    """Find a file matching pattern in src_dir and copy to dst."""
    matches = list(src_dir.glob(pattern))
    if matches:
        shutil.copy2(matches[0], dst)
        return matches[0].name
    return None


def main():
    ACCURACY_DIR.mkdir(parents=True, exist_ok=True)
    TRAJECTORY_DIR.mkdir(parents=True, exist_ok=True)

    summary: dict[str, dict[str, dict[str, dict[str, float]]]] = {
        ds: {} for ds in DATASETS
    }

    for entry in sorted(RESULT_DIR.iterdir()):
        if not entry.is_dir():
            continue

        dataset, defense, attack = parse_dirname(entry.name)
        if dataset is None or defense is None or attack is None:
            print(f"SKIP (cannot parse): {entry.name}")
            continue

        # Accuracy CSV — use dataset prefix to avoid overwrites
        acc_dst_name = f"{dataset}_{defense}_{attack}.csv"
        acc_dst = ACCURACY_DIR / acc_dst_name
        acc_src_name = copy_csv("*_accuracy.csv", entry, acc_dst)
        if acc_src_name is None:
            print(f"SKIP (no accuracy CSV): {entry.name}")
            continue
        print(f"COPY acc  {acc_src_name} -> accuracy/{acc_dst_name}")

        # Trajectory CSV
        traj_dst = TRAJECTORY_DIR / acc_dst_name
        traj_src_name = copy_csv("*_trajectory.csv", entry, traj_dst)
        if traj_src_name:
            print(f"COPY traj {traj_src_name} -> trajectory/{acc_dst_name}")

        # Read last row for summary
        with open(acc_dst) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                last = rows[-1]
                test_acc = float(last.get("main", last.get("test_acc", last.get("test acc", 0)) or 0))
                bkd_acc = float(last.get("backdoor", last.get("bkd_acc", last.get("bkd acc", 0)) or 0))

        summary[dataset].setdefault(defense, {})[attack] = {
            "asr": round(bkd_acc, 2),
            "accuracy": round(test_acc, 2),
        }

    # Write per-dataset summaries
    for ds in DATASETS:
        if summary[ds]:
            sp = ACCURACY_DIR / f"summary_{ds}.json"
            with open(sp, "w") as f:
                json.dump(summary[ds], f, indent=2)
            n = sum(len(v) for v in summary[ds].values())
            print(f"WROTE summary_{ds}.json with {n} entries")

    # Default summary: merge both datasets, cifar10 preferred on conflict
    default_summary: dict = {}
    for ds in reversed(DATASETS):  # cifar100 first, then cifar10 overrides
        for defense, attacks in summary[ds].items():
            default_summary.setdefault(defense, {}).update(attacks)
    with open(ACCURACY_DIR / "summary.json", "w") as f:
        json.dump(default_summary, f, indent=2)
    print(f"WROTE summary.json (merged, cifar10 preferred)")

    # Also write a combined summary with both datasets for the frontend
    combined = {}
    for ds in DATASETS:
        if summary[ds]:
            combined[ds] = summary[ds]
    with open(ACCURACY_DIR / "summary_all.json", "w") as f:
        json.dump(combined, f, indent=2)
    print(f"WROTE summary_all.json with both datasets")

    n_traj = len(list(TRAJECTORY_DIR.glob("*.csv")))
    print(f"Trajectory CSVs: {n_traj} files")


if __name__ == "__main__":
    main()
