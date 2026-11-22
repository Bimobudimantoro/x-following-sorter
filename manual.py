#!/usr/bin/env python3
"""
X Following Sorter — Manual review tool.
Review uncategorized accounts one by one and assign categories.

Usage:
  python manual.py <input.csv> [categories.toml]
  python manual.py following_xxx_sorted/Uncategorized.csv

Keys:
  1-9, a-z  Select category (shown on screen)
  s         Skip (keep uncategorized)
  q         Quit and save progress
  u         Undo last assignment

Progress is saved to .manual_progress.json so you can resume.
"""

import csv
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def load_categories(config_path):
    data = tomllib.loads(Path(config_path).read_text())
    return [c["label"] for c in data["categories"]]


def get_key(i):
    """Map index to key: 0-8 → 1-9, 9-34 → a-z."""
    if i < 9:
        return str(i + 1)
    elif i < 35:
        return chr(ord('a') + i - 9)
    return "?"


def main():
    if len(sys.argv) < 2:
        print("Usage: python manual.py <input.csv> [categories.toml]")
        sys.exit(1)

    csv_path = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else "categories.toml"

    categories = load_categories(config_path)
    categories.append("📦 Keep Uncategorized")

    # Build key → label map
    key_map = {}
    for i, cat in enumerate(categories):
        k = get_key(i)
        key_map[k] = cat

    # Read accounts
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_accounts = [row for row in reader]

    # Load progress
    progress_file = ".manual_progress.json"
    assigned = {}  # screen_name → category_label
    review_since = 0
    if Path(progress_file).exists():
        progress = json.loads(Path(progress_file).read_text())
        assigned = progress.get("assigned", {})
        review_since = progress.get("reviewed", 0)

    # Filter out already-assigned
    remaining = []
    for acc in all_accounts:
        if acc["screen_name"] not in assigned:
            remaining.append(acc)

    total = len(all_accounts)
    done = total - len(remaining)
    print(f"\n📋 Manual Review: {total} total | {done} done | {len(remaining)} remaining")
    print(f"   Progress saved to: {progress_file}")
    print()

    # Show categories
    print("── Categories ──")
    for i, cat in enumerate(categories):
        k = get_key(i)
        print(f"  [{k}] {cat}")
    print(f"  [s] Skip  [u] Undo  [q] Quit & Save")
    print()

    history = []  # (screen_name, old_category, new_category)

    idx = review_since
    while idx < len(all_accounts):
        acc = all_accounts[idx]
        sn = acc["screen_name"]

        # Already assigned?
        if sn in assigned:
            idx += 1
            continue

        # Display account
        bio = (acc.get("bio") or "").strip()
        if len(bio) > 120:
            bio = bio[:117] + "..."
        name = (acc.get("name") or "").strip()

        print(f"── [{idx+1}/{total}] ──────────────────────────────")
        print(f"  🐦 @{sn}")
        print(f"  📛 {name}")
        print(f"  📝 {bio if bio else '(no bio)'}")
        print()

        choice = input("  Category [1-9/a-z/s/u/q]: ").strip().lower()

        if choice == "q":
            break
        elif choice == "u":
            if history:
                prev_sn, prev_old, prev_new = history.pop()
                del assigned[prev_sn]
                print(f"  ↩ Undo: @{prev_sn} back to uncategorized")
            else:
                print("  ⚠ Nothing to undo")
            continue
        elif choice == "s":
            assigned[sn] = "📦 Keep Uncategorized"
            history.append((sn, "", "📦 Keep Uncategorized"))
            idx += 1
            continue
        elif choice in key_map:
            label = key_map[choice]
            assigned[sn] = label
            history.append((sn, "", label))
            print(f"  ✅ @{sn} → {label}")
            idx += 1
        else:
            print(f"  ⚠ Invalid key: '{choice}'")
            continue

        # Save progress every 10 reviews
        if len(history) % 10 == 0:
            progress = {"assigned": assigned, "reviewed": idx}
            Path(progress_file).write_text(json.dumps(progress, indent=2))

    # Final save
    progress = {"assigned": assigned, "reviewed": idx}
    Path(progress_file).write_text(json.dumps(progress, indent=2))

    # Write output: merge assigned back into category CSVs
    out_dir = Path(csv_path).parent

    # Build merged results
    merged = {}
    for cat in categories:
        merged[cat] = []

    # Read original category CSVs
    for cat in categories[:-1]:  # skip "Keep Uncategorized"
        slug = re.sub(r"[^\w]", "_", cat).strip("_")
        cat_csv = out_dir / f"{slug}.csv"
        if cat_csv.exists():
            with open(cat_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    merged[cat].append(row)

    # Add manually assigned
    for sn, label in assigned.items():
        if label == "📦 Keep Uncategorized":
            merged[label].append({"screen_name": sn, "name": "", "verified_type": "", "bio": ""})
        elif label in merged:
            # Find original row data
            acc = next((a for a in all_accounts if a["screen_name"] == sn), None)
            if acc:
                merged[label].append({
                    "screen_name": acc.get("screen_name", ""),
                    "name": acc.get("name", ""),
                    "verified_type": acc.get("verified_type", ""),
                    "bio": acc.get("bio", ""),
                })

    # Write merged CSVs
    manual_dir = out_dir / "manual_reviewed"
    manual_dir.mkdir(exist_ok=True)
    for cat, accounts in merged.items():
        if not accounts:
            continue
        slug = re.sub(r"[^\w]", "_", cat).strip("_")
        path = manual_dir / f"{slug}.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["screen_name", "name", "verified_type", "bio"])
            w.writeheader()
            w.writerows(accounts)

    # Summary
    print(f"\n🏁 Saved: {len(assigned)} manually assigned")
    print(f"   Merged CSVs: {manual_dir}/")
    print(f"   Progress: {progress_file}")

    # Stats
    stats = {}
    for sn, label in assigned.items():
        stats[label] = stats.get(label, 0) + 1
    print("   Manual review breakdown:")
    for label, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"     {label}: {count}")


if __name__ == "__main__":
    main()