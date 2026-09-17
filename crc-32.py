import os
import json
import zlib
import csv
from datetime import datetime


# ============================================================
# CRC-32 CALCULATION
# ============================================================

def calculate_crc32(file_path):
    """Calculate CRC-32 value of a file."""

    crc = 0

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(4096)

            if not chunk:
                break

            crc = zlib.crc32(chunk, crc)

    return crc & 0xFFFFFFFF


# ============================================================
# FILE LOCATIONS
# ============================================================

REFERENCE_FILE = "reference/crc_references.json"
REPORT_FILE = "reference/error_detection_report.csv"


# ============================================================
# REFERENCE FUNCTIONS
# ============================================================

def load_references():
    """Load stored CRC reference values."""

    if not os.path.exists(REFERENCE_FILE):
        return {}

    try:
        with open(REFERENCE_FILE, "r") as file:
            return json.load(file)

    except (json.JSONDecodeError, PermissionError) as error:
        print("ERROR loading reference file:", error)
        return {}


def save_references(references):
    """Save CRC reference values."""

    os.makedirs("reference", exist_ok=True)

    with open(REFERENCE_FILE, "w") as file:
        json.dump(references, file, indent=4)


# ============================================================
# CREATE REFERENCE
# ============================================================

def create_reference(file_path, record_id=None):
    """Create and store CRC reference for a file."""

    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError("Invalid file input.")

    if not os.path.isfile(file_path):
        raise FileNotFoundError("File does not exist.")

    crc = calculate_crc32(file_path)

    references = load_references()

    key = os.path.abspath(file_path)

    references[key] = {
        "filename": os.path.basename(file_path),
        "record_id": record_id,
        "size": os.path.getsize(file_path),
        "crc32": f"{crc:08X}",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    save_references(references)

    print("\nREFERENCE CREATED")
    print("------------------------------")
    print("File       :", file_path)
    print("Record ID  :", record_id)
    print("Size       :", os.path.getsize(file_path), "bytes")
    print("CRC-32     :", f"{crc:08X}")


# ============================================================
# VERIFY FILE
# ============================================================

def verify_file(file_path):
    """Compare current CRC with stored reference CRC."""

    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError("Invalid file input.")

    if not os.path.isfile(file_path):
        raise FileNotFoundError("File does not exist.")

    current_crc = calculate_crc32(file_path)

    references = load_references()

    key = os.path.abspath(file_path)

    # Missing reference condition
    if key not in references:
        print("\nMISSING REFERENCE")
        print("------------------------------")
        print("No reference record exists for:", file_path)
        return "MISSING REFERENCE"

    reference_crc = references[key]["crc32"]

    print("\nCRC-32 VERIFICATION")
    print("------------------------------")
    print("File          :", file_path)
    print("Reference CRC :", reference_crc)
    print("Current CRC   :", f"{current_crc:08X}")

    if reference_crc == f"{current_crc:08X}":

        print("STATUS        : FILE INTACT")
        return "DETECTED: NO ERROR"

    else:

        print("STATUS        : FILE MODIFIED")
        return "DETECTED: ERROR"


# ============================================================
# ERROR SIMULATION
# ============================================================

def simulate_character_error(file_path):
    """Change one character in a text file."""

    if not os.path.isfile(file_path):
        raise FileNotFoundError("File does not exist.")

    with open(file_path, "r") as file:
        content = file.read()

    if not content:
        raise ValueError("File is empty.")

    # Change the first character
    if content[0] == "A":
        new_first_character = "B"
    else:
        new_first_character = "A"

    corrupted_content = new_first_character + content[1:]

    with open(file_path, "w") as file:
        file.write(corrupted_content)

    print("\nERROR SIMULATION 1")
    print("------------------------------")
    print("Changed one character.")


def simulate_byte_error(file_path):
    """Change one byte in the file."""

    if not os.path.isfile(file_path):
        raise FileNotFoundError("File does not exist.")

    with open(file_path, "rb") as file:
        data = bytearray(file.read())

    if len(data) == 0:
        raise ValueError("File is empty.")

    # Flip bits in the first byte
    data[0] = data[0] ^ 1

    with open(file_path, "wb") as file:
        file.write(data)

    print("\nERROR SIMULATION 2")
    print("------------------------------")
    print("Changed one byte.")


def simulate_record_error(file_path):
    """Simulate a record change in a text/CSV-like file."""

    if not os.path.isfile(file_path):
        raise FileNotFoundError("File does not exist.")

    with open(file_path, "r") as file:
        lines = file.readlines()

    if not lines:
        raise ValueError("File has no records.")

    lines[0] = lines[0].rstrip("\n") + " CORRUPTED\n"

    with open(file_path, "w") as file:
        file.writelines(lines)

    print("\nERROR SIMULATION 3")
    print("------------------------------")
    print("Changed one record.")


def simulate_append_error(file_path):
    """Simulate additional data being added."""

    if not os.path.isfile(file_path):
        raise FileNotFoundError("File does not exist.")

    with open(file_path, "a") as file:
        file.write("\nCORRUPTED DATA")

    print("\nERROR SIMULATION 4")
    print("------------------------------")
    print("Added extra data.")


def simulate_truncation_error(file_path):
    """Simulate data loss by removing part of the file."""

    if not os.path.isfile(file_path):
        raise FileNotFoundError("File does not exist.")

    with open(file_path, "rb") as file:
        data = file.read()

    if len(data) < 2:
        raise ValueError("File is too small for truncation test.")

    # Remove approximately the last 20% of data
    new_length = max(1, int(len(data) * 0.8))

    with open(file_path, "wb") as file:
        file.write(data[:new_length])

    print("\nERROR SIMULATION 5")
    print("------------------------------")
    print("Removed part of the file.")


# ============================================================
# ERROR-DETECTION TABLE
# ============================================================

def create_report(results):
    """Create CSV error-detection result table."""

    os.makedirs("reference", exist_ok=True)

    with open(REPORT_FILE, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Test Case",
            "Error Type",
            "Reference CRC",
            "Current CRC",
            "Result"
        ])

        for result in results:
            writer.writerow([
                result["test_case"],
                result["error_type"],
                result["reference_crc"],
                result["current_crc"],
                result["result"]
            ])

    print("\nERROR-DETECTION REPORT CREATED")
    print("------------------------------")
    print("Report:", REPORT_FILE)


# ============================================================
# RUN ONE ERROR TEST
# ============================================================

def run_error_test(test_case, error_type, original_file):

    references = load_references()

    key = os.path.abspath(original_file)

    if key not in references:
        print("Reference record missing.")
        return None

    reference_crc = references[key]["crc32"]

    try:

        current_crc = calculate_crc32(original_file)
        current_crc_text = f"{current_crc:08X}"

        if reference_crc == current_crc_text:

            result = "NOT DETECTED"

        else:

            result = "DETECTED"

        print("\n----------------------------------------")
        print("Test Case     :", test_case)
        print("Error Type    :", error_type)
        print("Reference CRC :", reference_crc)
        print("Current CRC   :", current_crc_text)
        print("Result        :", result)
        print("----------------------------------------")

        return {
            "test_case": test_case,
            "error_type": error_type,
            "reference_crc": reference_crc,
            "current_crc": current_crc_text,
            "result": result
        }

    except FileNotFoundError:
        print("FileNotFoundError: File does not exist.")

    except PermissionError:
        print("PermissionError: Permission denied.")

    except ValueError as error:
        print("Invalid input:", error)

    return None


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("==========================================")
    print("          CRC-32 ERROR DETECTOR")
    print("==========================================")

    file_path = "test_files/sample.txt"

    # --------------------------------------------------------
    # Check input
    # --------------------------------------------------------

    try:

        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("Invalid file path.")

        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                "test_files/sample.txt was not found."
            )

    except FileNotFoundError as error:

        print("\nERROR:", error)
        print("Please create test_files/sample.txt.")
        return

    except PermissionError:

        print("\nERROR: Permission denied.")
        return

    except ValueError as error:

        print("\nERROR:", error)
        return

    # --------------------------------------------------------
    # Create reference if it does not exist
    # --------------------------------------------------------

    references = load_references()

    key = os.path.abspath(file_path)

    if key not in references:

        print("\nNo reference found.")
        print("Creating original reference...")

        try:
            create_reference(file_path, "SAMPLE-001")

        except FileNotFoundError:
            print("ERROR: File not found.")

        except PermissionError:
            print("ERROR: Permission denied.")

        except ValueError as error:
            print("ERROR:", error)

        return

    # --------------------------------------------------------
    # Normal verification
    # --------------------------------------------------------

    print("\nORIGINAL FILE VERIFICATION")

    try:
        verify_file(file_path)

    except FileNotFoundError:
        print("ERROR: File not found.")

    except PermissionError:
        print("ERROR: Permission denied.")

    except ValueError as error:
        print("ERROR:", error)

    # --------------------------------------------------------
    # Five error simulation test cases
    # --------------------------------------------------------

    print("\n==========================================")
    print("       FIVE ERROR SIMULATION TESTS")
    print("==========================================")

    print("\nIMPORTANT:")
    print("The program will temporarily modify sample.txt.")
    print("The original reference CRC remains unchanged.")

    results = []

    # --------------------------------------------------------
    # TEST 1 - Character change
    # --------------------------------------------------------

    try:

        # Restore original file before test
        restore_original_file(file_path)

        simulate_character_error(file_path)

        result = run_error_test(
            1,
            "Character changed",
            file_path
        )

        if result:
            results.append(result)

    except Exception as error:
        print("Test 1 error:", error)

    # --------------------------------------------------------
    # TEST 2 - Byte change
    # --------------------------------------------------------

    try:

        restore_original_file(file_path)

        simulate_byte_error(file_path)

        result = run_error_test(
            2,
            "Byte changed",
            file_path
        )

        if result:
            results.append(result)

    except Exception as error:
        print("Test 2 error:", error)

    # --------------------------------------------------------
    # TEST 3 - Record change
    # --------------------------------------------------------

    try:

        restore_original_file(file_path)

        simulate_record_error(file_path)

        result = run_error_test(
            3,
            "Record changed",
            file_path
        )

        if result:
            results.append(result)

    except Exception as error:
        print("Test 3 error:", error)

    # --------------------------------------------------------
    # TEST 4 - Additional data
    # --------------------------------------------------------

    try:

        restore_original_file(file_path)

        simulate_append_error(file_path)

        result = run_error_test(
            4,
            "Additional data added",
            file_path
        )

        if result:
            results.append(result)

    except Exception as error:
        print("Test 4 error:", error)

    # --------------------------------------------------------
    # TEST 5 - Truncation
    # --------------------------------------------------------

    try:

        restore_original_file(file_path)

        simulate_truncation_error(file_path)

        result = run_error_test(
            5,
            "Data truncated",
            file_path
        )

        if result:
            results.append(result)

    except Exception as error:
        print("Test 5 error:", error)

    # --------------------------------------------------------
    # Restore original file
    # --------------------------------------------------------

    restore_original_file(file_path)

    # --------------------------------------------------------
    # Create final CSV report
    # --------------------------------------------------------

    if results:
        create_report(results)

    # --------------------------------------------------------
    # Final verification
    # --------------------------------------------------------

    print("\n==========================================")
    print("          FINAL VERIFICATION")
    print("==========================================")

    verify_file(file_path)

    print("\n==========================================")
    print("              PROGRAM COMPLETE")
    print("==========================================")

    print("\nFiles created:")
    print("1. reference/crc_references.json")
    print("2. reference/error_detection_report.csv")


# ============================================================
# RESTORE ORIGINAL FILE
# ============================================================

def restore_original_file(file_path):

    """Restore sample.txt to the original laboratory text."""

    original_text = "This is my original laboratory file."

    with open(file_path, "w") as file:
        file.write(original_text)


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    main()