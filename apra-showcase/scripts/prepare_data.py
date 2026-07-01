"""
Prepare experiment data for the APRA showcase website.

Reads raw experiment results from ../../main/re_result_6-29_APRA/ and
generates cleaned CSV files + summary.json in public/data/.
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

# Map raw attack-name suffixes to short codes used in the frontend
ATTACK_MAP = {
    "a3fl": "a3fl",
    "sin-adv_DOBA": "doba",
    "doba": "doba",
    "neurotoxin": "neurotoxin",
    "modelreplace": "modelreplace",
    "modelreplace_2": "modelreplace",
}

DEFENSE_METHODS = ["apra", "avg", "clip", "deepsight", "foolsgold", "rflbat"]


def parse_dirname(dirname: str):
    """Parse the new directory naming:
    {dataset}_{epochs}_{date}_{time}_{method}_fix_True_{mia}_{mia_class}_{noise}_{attack}
    """
    parts = dirname.split("_")
    defense = None
    for dm in DEFENSE_METHODS:
        if dm in parts:
            defense = dm
            dm_idx = parts.index(dm)
            break
    if defense is None:
        return None, None

    # Attack is parts[10:] — after dataset,epochs,date,time,method,fix,True,mia,mia_class,noise
    attack_parts = parts[10:]
    remaining = "_".join(attack_parts)

    attack = None
    for key, val in ATTACK_MAP.items():
        if remaining.startswith(key) or key in remaining:
            attack = val
            break
    return defense, attack


def main():
    ACCURACY_DIR.mkdir(parents=True, exist_ok=True)
    TRAJECTORY_DIR.mkdir(parents=True, exist_ok=True)
    summary = {}

    for entry in sorted(RESULT_DIR.iterdir()):
        if not entry.is_dir():
            continue

        defense, attack = parse_dirname(entry.name)
        if defense is None or attack is None:
            print(f"SKIP (cannot parse): {entry.name}")
            continue

        # ---- Accuracy CSV ----
        accuracy_files = list(entry.glob("*_accuracy.csv"))
        if not accuracy_files:
            print(f"SKIP (no accuracy CSV): {entry.name}")
            continue

        src = accuracy_files[0]
        dst_name = f"{defense}_{attack}.csv"
        dst = ACCURACY_DIR / dst_name
        shutil.copy2(src, dst)
        print(f"COPY acc  {src.name} -> accuracy/{dst_name}")

        # ---- Trajectory CSV ----
        traj_files = list(entry.glob("*_trajectory.csv"))
        if traj_files:
            traj_dst = TRAJECTORY_DIR / dst_name
            shutil.copy2(traj_files[0], traj_dst)
            print(f"COPY traj {traj_files[0].name} -> trajectory/{dst_name}")

        # Read last row for summary
        with open(src) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                last = rows[-1]
                test_acc = float(last.get("main", last.get("test_acc", last.get("test acc", 0)) or 0))
                bkd_acc = float(last.get("backdoor", last.get("bkd_acc", last.get("bkd acc", 0)) or 0))

        summary.setdefault(defense, {})[attack] = {
            "asr": round(bkd_acc, 2),
            "accuracy": round(test_acc, 2),
        }

    # Write summary.json
    summary_path = ACCURACY_DIR / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"WROTE summary.json with {sum(len(v) for v in summary.values())} entries")

    print(f"Trajectory CSVs: {len(list(TRAJECTORY_DIR.glob('*.csv')))} files")


if __name__ == "__main__":
    main()
