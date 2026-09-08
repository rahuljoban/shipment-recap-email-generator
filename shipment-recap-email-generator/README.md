# Shipment Recap Email Generator

A small desktop tool that turns a daily "Delivery Accuracy" CSV export into a
ready-to-send shipment recap email — no more manually retyping transfer
numbers, calculating accuracy percentages, or copying stats by hand.

Built for an inventory team that received this report daily and had to
hand-assemble the same style of email every time. This repo uses sample data
and a placeholder logo/font in place of the original company's branding.

## What it does

Given a `DeliveryAccuracy.csv` export, the tool:

- Lists every transfer number received that day
- Flags any transfer at or below 80% accuracy with its percentage next to it
  (e.g. `023577 - 0%`)
- Calculates overall accuracy as total received ÷ total expected
- Pulls the received time from the report
- Counts "unexpected" shipments (rows without a normal transfer number)
- Lets you fill in the two fields that aren't in the spreadsheet: who
  received the shipment, and how many boxes
- Outputs a formatted email ready to paste into Outlook, with one click to
  copy it to your clipboard

## Two versions

- **`Shipment recap generator.pyw`** — a point-and-click desktop app
  (built with Tkinter). Double-click to launch, no command line needed.
- **`generate_transfer_email.py`** — the same logic as a command-line script,
  for anyone who prefers that or wants to automate it further.

## Running it

Both scripts are pure Python standard library — no installs needed beyond
Python itself.

**GUI:**
```
python "Shipment recap generator.pyw"
```
Keep `SampleLogo.png` in the same folder — the app looks for it there to
display the logo, and skips it gracefully if it's missing.

**Command line:**
```
python generate_transfer_email.py SampleDeliveryAccuracy.csv --received-by "Jane Doe" --boxes 12 --sign-off "Sample Name"
```
Omit any of the flags and it'll prompt you for them instead.

## Notes

- The GUI tries to use "Bahnschrift" for the header/branding and falls back
  to a system font if that's not installed on your machine — it's cosmetic
  only and won't break anything if it's missing. Swap in your own brand font
  by editing `PREFERRED_FONT` near the top of the script.
- `SampleDeliveryAccuracy.csv` and `SampleLogo.png` are placeholders included
  so the app runs out of the box — swap in your own CSV export and logo.
- The accuracy-flag threshold (80%) is set as a constant near the top of
  each script if you want to adjust it.
