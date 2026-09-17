import streamlit as st
import zlib
import csv
import io
from datetime import datetime


# ============================================================
# CRC-32 CORE LOGIC
# ============================================================

def calculate_crc32(data):
    """
    Calculate CRC-32 using the same core logic
    as the original Tkinter project.
    """
    crc = 0

    for i in range(0, len(data), 4096):
        chunk = data[i:i + 4096]
        crc = zlib.crc32(chunk, crc)

    return crc & 0xFFFFFFFF


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session():
    if "file_name" not in st.session_state:
        st.session_state.file_name = None

    if "original_data" not in st.session_state:
        st.session_state.original_data = None

    if "current_data" not in st.session_state:
        st.session_state.current_data = None

    if "reference_crc" not in st.session_state:
        st.session_state.reference_crc = None

    if "last_result" not in st.session_state:
        st.session_state.last_result = None


initialize_session()


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CRC-32 Error Detection Dashboard",
    page_icon="🔐",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 38px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .status-box {
        padding: 20px;
        border-radius: 10px;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .success-box {
        border: 2px solid #28a745;
        background-color: #eaf8ee;
    }

    .error-box {
        border: 2px solid #dc3545;
        background-color: #fdecec;
    }

    .info-box {
        border: 2px solid #0d6efd;
        background-color: #eef5ff;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">🔐 CRC-32 ERROR DETECTION DASHBOARD</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Cyclic Redundancy Check - File Integrity Verification</div>',
    unsafe_allow_html=True
)


# ============================================================
# FILE UPLOAD
# ============================================================

st.subheader("📁 Select File")

uploaded_file = st.file_uploader(
    "Upload a file to calculate and verify its CRC-32 checksum",
    type=None
)


# ============================================================
# HANDLE NEW FILE
# ============================================================

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
        st.session_state.reference_crc = None
        st.session_state.last_result = None

        st.success(
            f"File loaded successfully: {uploaded_file.name}"
        )


# ============================================================
# FILE INFORMATION
# ============================================================

if st.session_state.current_data is not None:

    file_size = len(st.session_state.current_data)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "📄 File",
            st.session_state.file_name
        )

    with col2:
        st.metric(
            "📦 File Size",
            f"{file_size} bytes"
        )

    with col3:
        if st.session_state.reference_crc:
            st.metric(
                "🔢 Reference CRC-32",
                st.session_state.reference_crc
            )
        else:
            st.metric(
                "🔢 Reference CRC-32",
                "Not Generated"
            )


    st.divider()


    # ========================================================
    # MAIN BUTTONS
    # ========================================================

    st.subheader("⚙️ File Integrity Operations")

    col1, col2, col3 = st.columns(3)

    # --------------------------------------------------------
    # GENERATE CRC
    # --------------------------------------------------------

    with col1:

        if st.button(
            "🔢 Generate CRC-32",
            use_container_width=True
        ):

            crc = calculate_crc32(
                st.session_state.current_data
            )

            st.session_state.reference_crc = f"{crc:08X}"

            st.session_state.last_result = (
                "CRC reference generated successfully."
            )

            st.success(
                f"Reference CRC-32: {crc:08X}"
            )


    # --------------------------------------------------------
    # VERIFY CRC
    # --------------------------------------------------------

    with col2:

        if st.button(
            "🔍 Verify CRC-32",
            use_container_width=True
        ):

            if st.session_state.reference_crc is None:

                st.warning(
                    "Please generate the CRC-32 reference first."
                )

            else:

                current_crc = calculate_crc32(
                    st.session_state.current_data
                )

                current_crc_hex = f"{current_crc:08X}"

                if (
                    current_crc_hex
                    == st.session_state.reference_crc
                ):

                    st.session_state.last_result = "NO ERROR DETECTED"

                    st.success(
                        "✅ FILE INTACT\n\n"
                        "RESULT: NO ERROR DETECTED"
                    )

                else:

                    st.session_state.last_result = "ERROR DETECTED"

                    st.error(
                        "❌ FILE MODIFIED\n\n"
                        "RESULT: ERROR DETECTED"
                    )


    # --------------------------------------------------------
    # SIMULATE ERROR
    # --------------------------------------------------------

    with col3:

        if st.button(
            "⚠️ Simulate Error",
            use_container_width=True
        ):

            if len(st.session_state.current_data) == 0:

                st.warning("The selected file is empty.")

            else:

                corrupted_data = bytearray(
                    st.session_state.current_data
                )

                # Change one byte exactly like the
                # original error simulation.
                corrupted_data[0] = corrupted_data[0] ^ 1

                st.session_state.current_data = bytes(
                    corrupted_data
                )

                st.session_state.last_result = None

                st.warning(
                    "⚠️ One byte has been modified "
                    "to simulate a file error."
                )


    st.write("")


    # ========================================================
    # SECOND ROW OF OPERATIONS
    # ========================================================

    col1, col2, col3 = st.columns(3)


    # --------------------------------------------------------
    # CREATE CSV REPORT
    # --------------------------------------------------------

    with col1:

        if st.button(
            "📊 Create CSV Report",
            use_container_width=True
        ):

            if st.session_state.reference_crc is None:

                st.warning(
                    "Please generate the CRC-32 reference first."
                )

            else:

                current_crc = calculate_crc32(
                    st.session_state.current_data
                )

                current_crc_hex = f"{current_crc:08X}"

                if (
                    current_crc_hex
                    == st.session_state.reference_crc
                ):
                    result = "NO ERROR"
                else:
                    result = "ERROR DETECTED"

                output = io.StringIO()

                writer = csv.writer(output)

                writer.writerow(
                    [
                        "Date and Time",
                        "File",
                        "Reference CRC-32",
                        "Current CRC-32",
                        "Result"
                    ]
                )

                writer.writerow(
                    [
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        st.session_state.file_name,
                        st.session_state.reference_crc,
                        current_crc_hex,
                        result
                    ]
                )

                st.session_state.report_data = (
                    output.getvalue()
                )

                st.success(
                    "CSV report created successfully."
                )


    # --------------------------------------------------------
    # RESTORE FILE
    # --------------------------------------------------------

    with col2:

        if st.button(
            "♻️ Restore File",
            use_container_width=True
        ):

            if st.session_state.original_data is not None:

                st.session_state.current_data = (
                    st.session_state.original_data
                )

                st.session_state.last_result = None

                st.success(
                    "File restored to its original uploaded state."
                )


    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    with col3:

        if st.button(
            "🗑️ Clear",
            use_container_width=True
        ):

            for key in list(st.session_state.keys()):
                del st.session_state[key]

            st.rerun()


    # ========================================================
    # CSV DOWNLOAD
    # ========================================================

    if "report_data" in st.session_state:

        st.download_button(
            label="⬇️ Download CSV Report",
            data=st.session_state.report_data,
            file_name="error_detection_report.csv",
            mime="text/csv",
            use_container_width=True
        )


    st.divider()


    # ========================================================
    # CURRENT CRC INFORMATION
    # ========================================================

    st.subheader("🔎 Current File Integrity Information")

    current_crc = calculate_crc32(
        st.session_state.current_data
    )

    current_crc_hex = f"{current_crc:08X}"

    col1, col2 = st.columns(2)

    with col1:

        st.info(
            f"**Current CRC-32:** `{current_crc_hex}`"
        )

    with col2:

        if st.session_state.reference_crc:

            st.info(
                f"**Reference CRC-32:** "
                f"`{st.session_state.reference_crc}`"
            )

        else:

            st.info(
                "**Reference CRC-32:** Not generated"
            )


    # ========================================================
    # RESULT
    # ========================================================

    if st.session_state.last_result == "NO ERROR DETECTED":

        st.markdown(
            """
            <div class="status-box success-box">

            <h3>✅ STATUS: FILE INTACT</h3>

            <b>RESULT: NO ERROR DETECTED</b>

            <p>
            The current CRC-32 matches the stored reference CRC-32.
            The file integrity has been verified.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )


    elif st.session_state.last_result == "ERROR DETECTED":

        st.markdown(
            """
            <div class="status-box error-box">

            <h3>❌ STATUS: FILE MODIFIED</h3>

            <b>RESULT: ERROR DETECTED</b>

            <p>
            The current CRC-32 does not match the stored reference CRC-32.
            The file has been modified or corrupted.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# INSTRUCTIONS WHEN NO FILE IS SELECTED
# ============================================================

else:

    st.info(
        """
        ### How to use the dashboard

        1. Upload a file.
        2. Click **Generate CRC-32** to create the original reference checksum.
        3. Click **Verify CRC-32** to check file integrity.
        4. Click **Simulate Error** to intentionally modify one byte.
        5. Click **Verify CRC-32** again to detect the modification.
        6. Click **Restore File** to return to the original uploaded file.
        7. Create and download a CSV report.
        """
    )