import streamlit as st
import zlib
import csv
import io
from datetime import datetime


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CRC-32 Error Detection System",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# SESSION STATE
# =========================================================

default_values = {
    "file_name": None,
    "original_data": None,
    "current_data": None,
    "reference_crc": None,
    "current_crc": None,
    "last_result": "READY",
    "report_data": None
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CRC-32 CALCULATION
# =========================================================

def calculate_crc32(data):
    """
    Calculate CRC-32 checksum using 4096-byte chunks.
    """

    crc = 0

    for i in range(0, len(data), 4096):
        chunk = data[i:i + 4096]
        crc = zlib.crc32(chunk, crc)

    return crc & 0xFFFFFFFF


def format_crc(crc):
    """
    Convert CRC-32 value to 8-character hexadecimal format.
    """

    if crc is None:
        return "—"

    return f"{crc:08X}"


def format_file_size(size):
    """
    Format file size in a readable way.
    """

    if size < 1024:
        return f"{size} bytes"

    if size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"

    return f"{size / (1024 * 1024):.2f} MB"


def reset_dashboard():
    """
    Reset all dashboard values.
    """

    st.session_state.file_name = None
    st.session_state.original_data = None
    st.session_state.current_data = None
    st.session_state.reference_crc = None
    st.session_state.current_crc = None
    st.session_state.last_result = "READY"
    st.session_state.report_data = None


# =========================================================
# HEADER
# =========================================================

st.title("🔐 CRC-32 ERROR DETECTION SYSTEM")

st.write(
    "File integrity verification using CRC-32 checksum comparison."
)

st.divider()


# =========================================================
# FILE SELECTION
# =========================================================

st.subheader("📁 File Selection")

st.write(
    "Upload a file to generate and verify its CRC-32 checksum."
)

uploaded_file = st.file_uploader(
    "Choose a file",
    type=None,
    help="Select a file for CRC-32 error detection."
)


# =========================================================
# PROCESS FILE
# =========================================================

if uploaded_file is not None:

    uploaded_data = uploaded_file.getvalue()

    # Detect a new file
    if (
        st.session_state.file_name != uploaded_file.name
        or st.session_state.original_data != uploaded_data
    ):

        st.session_state.file_name = uploaded_file.name

        st.session_state.original_data = uploaded_data

        st.session_state.current_data = uploaded_data

        # Generate original/reference CRC
        reference_crc = calculate_crc32(uploaded_data)

        st.session_state.reference_crc = reference_crc

        st.session_state.current_crc = reference_crc

        st.session_state.last_result = "READY"

        st.session_state.report_data = None


# =========================================================
# CURRENT VALUES
# =========================================================

file_name = st.session_state.file_name
original_data = st.session_state.original_data
current_data = st.session_state.current_data
reference_crc = st.session_state.reference_crc
current_crc = st.session_state.current_crc
last_result = st.session_state.last_result


# =========================================================
# CRC-32 STATUS
# =========================================================

st.subheader("📊 CRC-32 Status")

status1, status2, status3, status4 = st.columns(4)


with status1:

    st.metric(
        label="Verification Status",
        value=last_result
    )


with status2:

    st.metric(
        label="Current CRC-32",
        value=format_crc(current_crc)
    )


with status3:

    st.metric(
        label="Reference CRC-32",
        value=format_crc(reference_crc)
    )


with status4:

    st.metric(
        label="Selected File",
        value=file_name if file_name else "NO FILE"
    )


# =========================================================
# FILE INFORMATION
# =========================================================

if file_name is not None and current_data is not None:

    st.divider()

    st.subheader("📄 File Information")

    info1, info2, info3 = st.columns(3)

    with info1:

        st.write("**File Name**")

        st.info(file_name)

    with info2:

        st.write("**File Size**")

        st.info(
            format_file_size(len(current_data))
        )

    with info3:

        st.write("**Reference CRC-32**")

        st.code(
            format_crc(reference_crc),
            language=None
        )


else:

    st.info(
        "📌 Upload a file above to begin CRC-32 error detection."
    )


# =========================================================
# CRC-32 OPERATIONS
# =========================================================

st.divider()

st.subheader("⚙️ CRC-32 Operations")

st.write(
    "Generate the checksum, verify file integrity, or simulate "
    "a file modification for error detection."
)

operation1, operation2, operation3 = st.columns(3)


# ---------------------------------------------------------
# GENERATE CRC-32
# ---------------------------------------------------------

with operation1:

    if st.button(
        "🔢 Generate CRC-32",
        type="primary",
        use_container_width=True
    ):

        if current_data is None:

            st.warning(
                "Please upload a file first."
            )

        else:

            calculated_crc = calculate_crc32(
                current_data
            )

            st.session_state.current_crc = calculated_crc

            if st.session_state.reference_crc is None:

                st.session_state.reference_crc = calculated_crc

            st.session_state.last_result = "CRC GENERATED"

            st.success(
                f"CRC-32 generated: {format_crc(calculated_crc)}"
            )

            st.rerun()


# ---------------------------------------------------------
# VERIFY CRC-32
# ---------------------------------------------------------

with operation2:

    if st.button(
        "🔍 Verify CRC-32",
        type="primary",
        use_container_width=True
    ):

        if current_data is None:

            st.warning(
                "Please upload a file first."
            )

        elif reference_crc is None:

            st.warning(
                "Generate a CRC-32 reference value first."
            )

        else:

            calculated_crc = calculate_crc32(
                current_data
            )

            st.session_state.current_crc = calculated_crc

            if calculated_crc == reference_crc:

                st.session_state.last_result = "FILE INTACT"

                st.success(
                    "✅ FILE INTACT — NO ERROR DETECTED"
                )

            else:

                st.session_state.last_result = "ERROR DETECTED"

                st.error(
                    "❌ FILE MODIFIED — ERROR DETECTED"
                )

            st.rerun()


# ---------------------------------------------------------
# SIMULATE ERROR
# ---------------------------------------------------------

with operation3:

    if st.button(
        "⚠️ Simulate Error",
        use_container_width=True
    ):

        if current_data is None:

            st.warning(
                "Please upload a file first."
            )

        elif len(current_data) == 0:

            st.warning(
                "The selected file is empty."
            )

        else:

            modified_data = bytearray(
                current_data
            )

            # Flip one bit in the first byte
            modified_data[0] ^= 1

            st.session_state.current_data = bytes(
                modified_data
            )

            modified_crc = calculate_crc32(
                st.session_state.current_data
            )

            st.session_state.current_crc = modified_crc

            st.session_state.last_result = "FILE MODIFIED"

            st.warning(
                "⚠️ A simulated modification has been "
                "introduced into the file."
            )

            st.rerun()


# =========================================================
# VERIFICATION RESULT
# =========================================================

if last_result == "FILE INTACT":

    st.divider()

    st.success(
        "### ✅ FILE INTACT\n\n"
        "The current CRC-32 matches the reference CRC-32. "
        "No error was detected."
    )


elif last_result == "ERROR DETECTED":

    st.divider()

    st.error(
        "### ❌ ERROR DETECTED\n\n"
        "The current CRC-32 does not match the reference CRC-32. "
        "The file has been modified."
    )


elif last_result == "FILE MODIFIED":

    st.divider()

    st.warning(
        "### ⚠️ FILE MODIFIED\n\n"
        "A simulated modification has been introduced. "
        "Click **Verify CRC-32** to detect the error."
    )


elif last_result == "CRC GENERATED":

    st.divider()

    st.info(
        "### ℹ️ CRC-32 GENERATED\n\n"
        "The checksum has been calculated successfully."
    )


# =========================================================
# CRC COMPARISON
# =========================================================

if reference_crc is not None and current_crc is not None:

    st.divider()

    st.subheader("🔎 CRC-32 Comparison")

    comparison1, comparison2 = st.columns(2)

    with comparison1:

        st.write("**Reference CRC-32**")

        st.code(
            format_crc(reference_crc),
            language=None
        )

    with comparison2:

        st.write("**Current CRC-32**")

        st.code(
            format_crc(current_crc),
            language=None
        )


    if current_crc == reference_crc:

        st.success(
            "✓ CRC-32 values match — File integrity maintained."
        )

    else:

        st.error(
            "✗ CRC-32 values differ — File modification detected."
        )


# =========================================================
# FILE MANAGEMENT
# =========================================================

st.divider()

st.subheader("🛠️ File Management")

management1, management2, management3 = st.columns(3)


# ---------------------------------------------------------
# RESTORE ORIGINAL
# ---------------------------------------------------------

with management1:

    if st.button(
        "♻️ Restore Original",
        use_container_width=True
    ):

        if original_data is None:

            st.warning(
                "Please upload a file first."
            )

        else:

            st.session_state.current_data = original_data

            restored_crc = calculate_crc32(
                original_data
            )

            st.session_state.current_crc = restored_crc

            st.session_state.last_result = "FILE INTACT"

            st.success(
                "♻️ Original file restored successfully."
            )

            st.rerun()


# ---------------------------------------------------------
# CREATE CSV REPORT
# ---------------------------------------------------------

with management2:

    if st.button(
        "📋 Create CSV Report",
        use_container_width=True
    ):

        if file_name is None:

            st.warning(
                "Please upload a file first."
            )

        else:

            calculated_current_crc = calculate_crc32(
                current_data
            )

            st.session_state.current_crc = (
                calculated_current_crc
            )

            if (
                reference_crc is not None
                and calculated_current_crc == reference_crc
            ):

                result = "NO ERROR DETECTED"

            else:

                result = "ERROR DETECTED"


            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )


            st.session_state.report_data = {
                "Date and Time": timestamp,
                "File": file_name,
                "Reference CRC-32": format_crc(
                    reference_crc
                ),
                "Current CRC-32": format_crc(
                    calculated_current_crc
                ),
                "Result": result
            }


            st.success(
                "📋 CSV report created successfully."
            )


# ---------------------------------------------------------
# CLEAR DASHBOARD
# ---------------------------------------------------------

with management3:

    if st.button(
        "🗑️ Clear Dashboard",
        use_container_width=True
    ):

        reset_dashboard()

        st.success(
            "Dashboard cleared successfully."
        )

        st.rerun()


# =========================================================
# CSV REPORT DOWNLOAD
# =========================================================

if st.session_state.report_data is not None:

    st.divider()

    st.subheader("📥 CSV Report")

    report = st.session_state.report_data

    csv_buffer = io.StringIO()

    writer = csv.DictWriter(
        csv_buffer,
        fieldnames=[
            "Date and Time",
            "File",
            "Reference CRC-32",
            "Current CRC-32",
            "Result"
        ]
    )

    writer.writeheader()

    writer.writerow(report)

    csv_data = csv_buffer.getvalue()


    st.download_button(
        label="⬇️ Download CSV Report",
        data=csv_data,
        file_name="error_detection_report.csv",
        mime="text/csv"
    )


# =========================================================
# PROJECT INFORMATION
# =========================================================

st.divider()

st.subheader("ℹ️ About the System")

about1, about2, about3 = st.columns(3)

with about1:

    st.write("**Purpose**")

    st.write(
        "Detect file modifications by comparing "
        "CRC-32 checksum values."
    )


with about2:

    st.write("**Technique**")

    st.write(
        "CRC-32 checksum generation and "
        "comparison."
    )


with about3:

    st.write("**Application Area**")

    st.write(
        "Operating Systems / Computer Networks "
        "error detection."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "CRC-32 Error Detection System | "
    "Operating Systems / Computer Networks | "
    "Error Detection"
)