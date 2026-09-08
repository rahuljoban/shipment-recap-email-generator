"""
Generate the daily "transfers received" email from a DeliveryAccuracy CSV export.

Usage:
    python generate_transfer_email.py DeliveryAccuracy.csv

You'll be prompted for the two manual fields (Received by, Boxes) unless you
pass them as arguments:

    python generate_transfer_email.py DeliveryAccuracy.csv --received-by Devin --boxes 31
"""

import argparse
import csv
import sys

LOW_ACCURACY_THRESHOLD = 80.0  # flag any transfer at or below this %


def is_unexpected_row(reference: str) -> bool:
    """Rows for unexpected freight have a non-numeric Reference 1 value
    (e.g. 'Unexpected_NY1_2026-09-06 16-15-39') instead of a transfer number."""
    return not reference.strip().isdigit()


def load_rows(csv_path: str):
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def build_email(rows, received_by: str, boxes: str, sign_off: str = "Sophia") -> str:
    expected_total = 0
    received_total = 0
    unexpected_total = 0
    transfer_lines = []
    received_time = None

    for row in rows:
        reference = row["Reference 1"].strip()
        expected = int(row["# Expected"])
        received = int(row["# Received"])

        if received_time is None:
            # "09/06/2026 12:15:39 PM" -> take the time portion
            received_time = row["Received Date"].split(" ", 1)[1]

        if is_unexpected_row(reference):
            unexpected_total += received
            continue

        expected_total += expected
        received_total += received

        pct = int(row["# Correct"]) / expected * 100 if expected else 0
        if pct <= LOW_ACCURACY_THRESHOLD:
            transfer_lines.append(f"{reference} - {pct:.0f}%")
        else:
            transfer_lines.append(reference)

    overall_accuracy = (received_total / expected_total * 100) if expected_total else 0
    # Trim the time down to something like "12:15 PM"
    time_parts = received_time.split(":")
    display_time = f"{time_parts[0]}:{time_parts[1]} {received_time.split(' ')[-1]}"

    lines = [
        "Good afternoon,",
        "",
        "1. Today we received the following transfers:",
        "",
    ]
    lines.extend(transfer_lines)
    lines.extend([
        "",
        f"1. Received by: {received_by}",
        f"2. Accuracy: {overall_accuracy:.1f}%",
        f"3. Boxes: {boxes}",
        f"4. Received at: {display_time}",
        "5. All transfers closed in AIMS: YES",
        f"6. Unexpected: {unexpected_total}",
        "",
        "Best,",
        sign_off,
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", help="Path to the DeliveryAccuracy CSV export")
    parser.add_argument("--received-by", help="Name of the person who received the transfers")
    parser.add_argument("--boxes", help="Number of boxes received")
    parser.add_argument("--sign-off", help="Name to sign the email with")
    args = parser.parse_args()

    received_by = args.received_by or input("Received by: ").strip()
    boxes = args.boxes or input("Boxes: ").strip()
    sign_off = args.sign_off or input("Sign off name: ").strip()

    rows = load_rows(args.csv_path)
    email_text = build_email(rows, received_by, boxes, sign_off)

    print("\n" + email_text + "\n")


if __name__ == "__main__":
    main()
