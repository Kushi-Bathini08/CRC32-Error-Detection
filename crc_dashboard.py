import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import zlib
import csv
from datetime import datetime


# ============================================================
# FILE LOCATIONS
# ============================================================

REFERENCE_FILE = "reference/crc_references.json"
REPORT_FILE = "reference/error_detection_report.csv"


# ============================================================
# CRC-32 CALCULATION
# ============================================================

def calculate_crc32(file_path):
    crc = 0

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(4096)

            if not chunk:
                break

            crc = zlib.crc32(chunk, crc)

    return crc & 0xFFFFFFFF


# ============================================================
# REFERENCE FUNCTIONS
# ============================================================

def load_references():
    if not os.path.exists(REFERENCE_FILE):
        return {}

    try:
        with open(REFERENCE_FILE, "r") as file:
            return json.load(file)

    except (json.JSONDecodeError, PermissionError):
        return {}


def save_references(references):
    os.makedirs("reference", exist_ok=True)

    with open(REFERENCE_FILE, "w") as file:
        json.dump(references, file, indent=4)


# ============================================================
# DISPLAY MESSAGE
# ============================================================

def display(message):
    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, message)


# ============================================================
# SELECT FILE
# ============================================================

def select_file():
    file_path = filedialog.askopenfilename(
        title="Select a file"
    )

    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

        display(
            "FILE SELECTED\n"
            "------------------------------\n"
            f"{file_path}"
        )


# ============================================================
# GENERATE CRC-32 REFERENCE
# ============================================================

def generate_crc():
    file_path = file_entry.get().strip()

    try:

        if not file_path:
            raise ValueError("Please select a file.")

        if not os.path.isfile(file_path):
            raise FileNotFoundError("File does not exist.")

        crc = calculate_crc32(file_path)

        references = load_references()

        key = os.path.abspath(file_path)

        references[key] = {
            "filename": os.path.basename(file_path),
            "record_id": "GUI-001",
            "size": os.path.getsize(file_path),
            "crc32": f"{crc:08X}",
            "created_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        save_references(references)

        display(
            "CRC-32 REFERENCE GENERATED\n"
            "================================\n\n"
            f"File:\n{file_path}\n\n"
            f"CRC-32:\n{crc:08X}\n\n"
            "Reference saved successfully."
        )

    except FileNotFoundError as error:

        messagebox.showerror("File Error", str(error))

    except PermissionError:

        messagebox.showerror(
            "Permission Error",
            "Permission denied."
        )

    except ValueError as error:

        messagebox.showerror(
            "Invalid Input",
            str(error)
        )


# ============================================================
# VERIFY FILE
# ============================================================

def verify_file():
    file_path = file_entry.get().strip()

    try:

        if not file_path:
            raise ValueError("Please select a file.")

        if not os.path.isfile(file_path):
            raise FileNotFoundError("File does not exist.")

        current_crc = calculate_crc32(file_path)

        references = load_references()

        key = os.path.abspath(file_path)

        if key not in references:

            display(
                "MISSING REFERENCE\n"
                "================================\n\n"
                "No CRC-32 reference exists for this file.\n\n"
                "Click 'Generate CRC-32' first."
            )

            return

        reference_crc = references[key]["crc32"]
        current_crc_text = f"{current_crc:08X}"

        if reference_crc == current_crc_text:

            display(
                "CRC-32 VERIFICATION\n"
                "================================\n\n"
                f"File:\n{file_path}\n\n"
                f"Reference CRC-32:\n{reference_crc}\n\n"
                f"Current CRC-32:\n{current_crc_text}\n\n"
                "STATUS: FILE INTACT\n"
                "RESULT: NO ERROR DETECTED"
            )

        else:

            display(
                "CRC-32 VERIFICATION\n"
                "================================\n\n"
                f"File:\n{file_path}\n\n"
                f"Reference CRC-32:\n{reference_crc}\n\n"
                f"Current CRC-32:\n{current_crc_text}\n\n"
                "STATUS: FILE MODIFIED\n"
                "RESULT: ERROR DETECTED"
            )

    except FileNotFoundError as error:

        messagebox.showerror(
            "File Error",
            str(error)
        )

    except PermissionError:

        messagebox.showerror(
            "Permission Error",
            "Permission denied."
        )

    except ValueError as error:

        messagebox.showerror(
            "Invalid Input",
            str(error)
        )


# ============================================================
# SIMULATE CHARACTER ERROR
# ============================================================

def simulate_error():
    file_path = file_entry.get().strip()

    try:

        if not file_path:
            raise ValueError("Please select a file.")

        if not os.path.isfile(file_path):
            raise FileNotFoundError("File does not exist.")

        with open(file_path, "rb") as file:
            data = bytearray(file.read())

        if len(data) == 0:
            raise ValueError("File is empty.")

        # Change the first byte
        data[0] = data[0] ^ 1

        with open(file_path, "wb") as file:
            file.write(data)

        display(
            "ERROR SIMULATION\n"
            "================================\n\n"
            "One byte of the selected file was changed.\n\n"
            "The file is now intentionally corrupted.\n\n"
            "Click 'Verify CRC-32' to detect the error."
        )

    except FileNotFoundError as error:

        messagebox.showerror(
            "File Error",
            str(error)
        )

    except PermissionError:

        messagebox.showerror(
            "Permission Error",
            "Permission denied."
        )

    except ValueError as error:

        messagebox.showerror(
            "Invalid Input",
            str(error)
        )


# ============================================================
# CREATE CSV REPORT
# ============================================================

def create_report():
    file_path = file_entry.get().strip()

    try:

        if not file_path:
            raise ValueError("Please select a file.")

        if not os.path.isfile(file_path):
            raise FileNotFoundError("File does not exist.")

        references = load_references()

        key = os.path.abspath(file_path)

        if key not in references:

            display(
                "REPORT ERROR\n"
                "================================\n\n"
                "No reference CRC found.\n\n"
                "Generate a CRC-32 reference first."
            )

            return

        reference_crc = references[key]["crc32"]

        current_crc = calculate_crc32(file_path)

        current_crc_text = f"{current_crc:08X}"

        if reference_crc == current_crc_text:
            result = "NO ERROR"
        else:
            result = "ERROR DETECTED"

        os.makedirs("reference", exist_ok=True)

        with open(
            REPORT_FILE,
            "w",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Date and Time",
                "File",
                "Reference CRC-32",
                "Current CRC-32",
                "Result"
            ])

            writer.writerow([
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                os.path.basename(file_path),
                reference_crc,
                current_crc_text,
                result
            ])

        display(
            "CSV REPORT CREATED\n"
            "================================\n\n"
            f"Report:\n{REPORT_FILE}\n\n"
            f"Reference CRC:\n{reference_crc}\n\n"
            f"Current CRC:\n{current_crc_text}\n\n"
            f"Result:\n{result}"
        )

    except FileNotFoundError as error:

        messagebox.showerror(
            "File Error",
            str(error)
        )

    except PermissionError:

        messagebox.showerror(
            "Permission Error",
            "Permission denied."
        )

    except ValueError as error:

        messagebox.showerror(
            "Invalid Input",
            str(error)
        )


# ============================================================
# RESTORE SAMPLE FILE
# ============================================================

def restore_sample():

    file_path = file_entry.get().strip()

    if not file_path:
        messagebox.showerror(
            "Error",
            "Please select a file."
        )
        return

    try:

        with open(file_path, "w") as file:
            file.write(
                "This is my original laboratory file."
            )

        display(
            "FILE RESTORED\n"
            "================================\n\n"
            "The file has been restored.\n\n"
            "You can now click 'Verify CRC-32'."
        )

    except PermissionError:

        messagebox.showerror(
            "Permission Error",
            "Permission denied."
        )


# ============================================================
# CLEAR DISPLAY
# ============================================================

def clear_display():
    file_entry.delete(0, tk.END)
    result_box.delete("1.0", tk.END)


# ============================================================
# GUI WINDOW
# ============================================================

root = tk.Tk()

root.title("CRC-32 Error Detection Dashboard")

root.geometry("850x650")

root.resizable(False, False)


# ============================================================
# TITLE
# ============================================================

title_label = tk.Label(
    root,
    text="CRC-32 ERROR DETECTION DASHBOARD",
    font=("Arial", 20, "bold")
)

title_label.pack(pady=20)


subtitle_label = tk.Label(
    root,
    text="Cyclic Redundancy Check - File Integrity Verification",
    font=("Arial", 11)
)

subtitle_label.pack(pady=5)


# ============================================================
# FILE SECTION
# ============================================================

file_frame = tk.Frame(root)

file_frame.pack(pady=20)


file_label = tk.Label(
    file_frame,
    text="Selected File:",
    font=("Arial", 11, "bold")
)

file_label.grid(
    row=0,
    column=0,
    padx=10
)


file_entry = tk.Entry(
    file_frame,
    width=55,
    font=("Arial", 10)
)

file_entry.grid(
    row=0,
    column=1,
    padx=10
)


browse_button = tk.Button(
    file_frame,
    text="Browse",
    width=12,
    command=select_file
)

browse_button.grid(
    row=0,
    column=2,
    padx=5
)


# ============================================================
# BUTTON SECTION
# ============================================================

button_frame = tk.Frame(root)

button_frame.pack(pady=10)


generate_button = tk.Button(
    button_frame,
    text="Generate CRC-32",
    width=20,
    command=generate_crc
)

generate_button.grid(
    row=0,
    column=0,
    padx=8,
    pady=8
)


verify_button = tk.Button(
    button_frame,
    text="Verify CRC-32",
    width=20,
    command=verify_file
)

verify_button.grid(
    row=0,
    column=1,
    padx=8,
    pady=8
)


error_button = tk.Button(
    button_frame,
    text="Simulate Error",
    width=20,
    command=simulate_error
)

error_button.grid(
    row=1,
    column=0,
    padx=8,
    pady=8
)


report_button = tk.Button(
    button_frame,
    text="Create CSV Report",
    width=20,
    command=create_report
)

report_button.grid(
    row=1,
    column=1,
    padx=8,
    pady=8
)


restore_button = tk.Button(
    button_frame,
    text="Restore File",
    width=20,
    command=restore_sample
)

restore_button.grid(
    row=2,
    column=0,
    padx=8,
    pady=8
)


clear_button = tk.Button(
    button_frame,
    text="Clear",
    width=20,
    command=clear_display
)

clear_button.grid(
    row=2,
    column=1,
    padx=8,
    pady=8
)


# ============================================================
# RESULT SECTION
# ============================================================

result_label = tk.Label(
    root,
    text="RESULT",
    font=("Arial", 13, "bold")
)

result_label.pack(pady=10)


result_box = tk.Text(
    root,
    width=90,
    height=15,
    font=("Consolas", 10)
)

result_box.pack(padx=20, pady=5)


# ============================================================
# START DASHBOARD
# ============================================================

root.mainloop()