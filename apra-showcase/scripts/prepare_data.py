"""
Prepare experiment data for the APRA showcase website.

Reads raw experiment results from ../../main/re_result_APRA/ and
generates cleaned CSV files + summary.json in public/data/.
"""
import csv
import json
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RESULT_DIR = BASE_DIR.parent / "main" / "re_result_APRA"
PUBLIC_DATA = BASE_DIR / "public" / "data"
ACCURACY_DIR = PUBLIC_DATA / "accuracy"

ATTACK_MAP = {
    "a3fl": "a3fl",
    "sin-adv": "doba",
    "sin-adv_DOBA": "doba",
    "neurotoxin": "neurotoxin",
    "reba": "reba",
    "modelreplace": "modelreplace",
}

def parse_dirname(dirname: str):
    parts = dirname.split("_")
    defense_methods = ["apra", "avg", "clip", "deepsight", "foolsgold", "rflbat"]
    defense = None
    for dm in defense_methods:
        if dm in parts:
            defense = dm
            dm_idx = parts.index(dm)
            break

    if defense is None:
        return None, None

    remaining = "_".join(parts[dm_idx + 3:])
    attack = None
    for key, val in ATTACK_MAP.items():
        if remaining.startswith(key) or key in remaining:
            attack = val
            break

    return defense, attack

def main():
    ACCURACY_DIR.mkdir(parents=True, exist_ok=True)

    summary = {}

    for entry in sorted(RESULT_DIR.iterdir()):
        if not entry.is_dir():
            continue

        defense, attack = parse_dirname(entry.name)
        if defense is None or attack is None:
            print(f"SKIP (cannot parse): {entry.name}")
            continue

        accuracy_files = list(entry.glob("*_accuracy.csv"))
        if not accuracy_files:
            print(f"SKIP (no accuracy CSV): {entry.name}")
            continue

        src = accuracy_files[0]
        dst_name = f"{defense}_{attack}.csv"
        dst = ACCURACY_DIR / dst_name
        shutil.copy2(src, dst)
        print(f"COPY {src.name} -> accuracy/{dst_name}")

        with open(src) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                last = rows[-1]
                test_acc = float(last.get("main", last.get("test_acc", last.get("test acc", 0))))
                bkd_acc = float(last.get("backdoor", last.get("bkd_acc", last.get("bkd acc", 0))))

        if defense not in summary:
            summary[defense] = {}
        summary[defense][attack] = {
            "asr": round(bkd_acc, 2),
            "accuracy": round(test_acc, 2),
        }

    summary_path = ACCURACY_DIR / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"WROTE summary.json with {sum(len(v) for v in summary.values())} entries")

    apra_dirs = [d for d in RESULT_DIR.iterdir() if d.is_dir() and "_apra_" in d.name]
    if apra_dirs:
        apra_dir = apra_dirs[0]
        trace_files = list(apra_dir.glob("apra_client_trace.csv"))
        round_files = list(apra_dir.glob("apra_round_summary.csv"))
        if trace_files:
            shutil.copy2(trace_files[0], PUBLIC_DATA / "apra_client_trace.csv")
            print("COPY apra_client_trace.csv")
        if round_files:
            shutil.copy2(round_files[0], PUBLIC_DATA / "apra_round_summary.csv")
            print("COPY apra_round_summary.csv")

if __name__ == "__main__":
    main()
