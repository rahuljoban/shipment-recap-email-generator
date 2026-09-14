"""
Transfer Email Generator - GUI version

Double-click this file (or a shortcut to it) to launch a simple window where
you can pick the CSV export, type in "Received by" and "Boxes", and get the
finished email text ready to copy into Outlook.

No command line needed.
"""

import csv
import os
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, scrolledtext

# Make the app DPI-aware on Windows so images/fonts don't render squished or
# blurry on machines using 125%/150% display scaling.
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass  # older Windows versions without shcore; safe to ignore

LOW_ACCURACY_THRESHOLD = 80.0

# Preferred brand font, with fallbacks if it isn't installed on this machine.
# (Swap PREFERRED_FONT for your own company's brand font if you have one.)
PREFERRED_FONT = "Bahnschrift"
FONT_FALLBACKS = ["Segoe UI", "Arial"]

# Regular, easy-to-read font for everyday text (labels, entries, output).
# The brand font above is heavy/wide by design, so we reserve it for the
# headline only and use a normal-weight font everywhere else.
BODY_FONT_CANDIDATES = ["Segoe UI", "Calibri", "Arial", "TkDefaultFont"]

# Logo file must sit in the same folder as this script
LOGO_FILENAME = "SampleLogo.png"


def is_unexpected_row(reference: str) -> bool:
    return not reference.strip().isdigit()


def load_rows(csv_path: str):
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def build_email(rows, received_by: str, boxes: str, sign_off: str) -> str:
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


def pick_available_font(preferred: str, fallbacks: list) -> str:
    """Return the first font family that's actually installed on this machine."""
    available = set(tkfont.families())
    for name in [preferred] + fallbacks:
        if name in available:
            return name
    return "TkDefaultFont"  # last resort, always exists


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shipment Recap Email Generator")
        self.geometry("800x680")
        self.minsize(760, 560)
        self.resizable(True, True)
        self.csv_path = tk.StringVar()

        self.brand_font = pick_available_font(PREFERRED_FONT, FONT_FALLBACKS)
        self.body_font_name = pick_available_font(BODY_FONT_CANDIDATES[0], BODY_FONT_CANDIDATES[1:])
        base_font = (self.body_font_name, 10)
        bold_font = (self.body_font_name, 10, "bold")
        mono_font = (self.body_font_name, 10)

        self.option_add("*Font", base_font)

        pad = {"padx": 10, "pady": 6}

        # Header row with logo top-right (grid, so the logo column always
        # keeps its full width and never gets clipped as the window resizes)
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        header_frame.columnconfigure(0, weight=1)
        header_frame.columnconfigure(1, weight=0)

        tk.Label(
            header_frame, text="Shipment Recap Email Generator", font=(self.brand_font, 13, "bold"), anchor="w"
        ).grid(row=0, column=0, sticky="w")

        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOGO_FILENAME)
        if os.path.exists(logo_path):
            try:
                self.logo_image = tk.PhotoImage(file=logo_path)
                tk.Label(header_frame, image=self.logo_image).grid(row=0, column=1, sticky="e")
            except tk.TclError:
                pass  # logo failed to load; just skip it silently

        # File picker row
        file_frame = tk.Frame(self)
        file_frame.pack(fill="x", **pad)
        tk.Label(file_frame, text="Delivery Accuracy:", width=16, anchor="w").pack(side="left")
        tk.Entry(file_frame, textvariable=self.csv_path).pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Button(file_frame, text="Browse...", command=self.browse_file).pack(side="left")

        # Received by
        rb_frame = tk.Frame(self)
        rb_frame.pack(fill="x", **pad)
        tk.Label(rb_frame, text="Received by:", width=12, anchor="w").pack(side="left")
        self.received_by = tk.Entry(rb_frame)
        self.received_by.pack(side="left", fill="x", expand=True)

        # Boxes
        boxes_frame = tk.Frame(self)
        boxes_frame.pack(fill="x", **pad)
        tk.Label(boxes_frame, text="Boxes:", width=12, anchor="w").pack(side="left")
        self.boxes = tk.Entry(boxes_frame)
        self.boxes.pack(side="left", fill="x", expand=True)

        # Sign-off name
        sign_frame = tk.Frame(self)
        sign_frame.pack(fill="x", **pad)
        tk.Label(sign_frame, text="Sign off as:", width=12, anchor="w").pack(side="left")
        self.sign_off = tk.Entry(sign_frame)
        self.sign_off.pack(side="left", fill="x", expand=True)

        # Generate button
        tk.Button(
            self, text="Generate Email", command=self.generate, bg="#2d6cdf", fg="white",
            font=bold_font, height=2
        ).pack(fill="x", **pad)

        # Output box
        tk.Label(self, text="Email text:", anchor="w").pack(fill="x", padx=10)
        self.output = scrolledtext.ScrolledText(self, wrap="word", font=mono_font, height=18)
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        # Copy button
        tk.Button(self, text="Copy to Clipboard", command=self.copy_to_clipboard, height=2).pack(fill="x", **pad)

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Select DeliveryAccuracy CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.csv_path.set(path)

    def generate(self):
        path = self.csv_path.get().strip()
        received_by = self.received_by.get().strip()
        boxes = self.boxes.get().strip()
        sign_off = self.sign_off.get().strip()

        if not path:
            messagebox.showerror("Missing file", "Please choose the CSV file first.")
            return
        if not received_by or not boxes or not sign_off:
            messagebox.showerror("Missing info", "Please fill in Received by, Boxes, and Sign off as.")
            return

        try:
            rows = load_rows(path)
            email_text = build_email(rows, received_by, boxes, sign_off)
        except Exception as e:
            messagebox.showerror("Error generating email", str(e))
            return

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, email_text)

    def copy_to_clipboard(self):
        text = self.output.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Nothing to copy", "Generate the email first.")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Email text copied to clipboard!")


if __name__ == "__main__":
    App().mainloop()
