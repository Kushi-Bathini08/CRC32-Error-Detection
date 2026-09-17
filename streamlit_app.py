
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
    page_icon="CRC",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# SESSION STATE
# =========================================================

DEFAULT_STATE = {
    "file_name": None,
    "original_data": None,
    "current_data": None,
    "reference_crc": None,
    "current_crc": None,
    "last_result": "READY",
    "report_data": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CRC-32 FUNCTIONS
# =========================================================

def calculate_crc32(data):
    """Calculate CRC-32 checksum."""
    return zlib.crc32(data) & 0xFFFFFFFF


def format_crc(value):
    """Format CRC-32 as uppercase hexadecimal."""
    if value is None:
        return "—"

    return f"{value:08X}"


def format_file_size(size):
    """Convert bytes into readable file size."""
    if size < 1024:
        return f"{size} B"

    if size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"

    return f"{size / (1024 * 1024):.2f} MB"


def reset_dashboard():
    """Reset dashboard state."""
    for key, value in DEFAULT_STATE.items():
        st.session_state[key] = value


# =========================================================
# PROFESSIONAL DARK THEME
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
    ===================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 50% -10%,
                rgba(124, 92, 255, 0.13),
                transparent 35%
            ),
            radial-gradient(
                circle at 0% 35%,
                rgba(124, 92, 255, 0.05),
                transparent 25%
            ),
            #08080D;

        color: #F5F5F7;
    }

    .main .block-container {
        max-width: 1180px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }


    /* =====================================================
       TYPOGRAPHY
    ===================================================== */

    html,
    body,
    [class*="css"] {
        font-family:
            Inter,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
    }

    h1,
    h2,
    h3 {
        color: #F5F5F7 !important;
    }


    /* =====================================================
       HERO MARKDOWN
    ===================================================== */

    .hero-kicker {
        color: #A78BFA !important;
        font-size: 0.72rem !important;
        font-weight: 750 !important;
        letter-spacing: 0.22em !important;
        text-transform: uppercase !important;
        margin-bottom: 0.6rem !important;
    }

    .hero-title {
        color: #FFFFFF !important;
        font-size: 3.35rem !important;
        line-height: 1.05 !important;
        font-weight: 760 !important;
        letter-spacing: -0.045em !important;
        margin-bottom: 0.8rem !important;
    }

    .hero-highlight {
        color: #A78BFA !important;
        text-shadow:
            0 0 25px rgba(167, 139, 250, 0.20);
    }

    .hero-description {
        color: #9696A3 !important;
        max-width: 700px;
        font-size: 1rem !important;
        line-height: 1.75 !important;
    }

    .hero-line {
        height: 1px;
        margin-top: 2.5rem;
        margin-bottom: 2.5rem;
        background: rgba(255, 255, 255, 0.07);
    }


    /* =====================================================
       SECTION HEADINGS
    ===================================================== */

    .section-number {
        color: #A78BFA !important;
        font-family: "Courier New", monospace !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.12em !important;
    }

    .section-title {
        color: #F5F5F7 !important;
        font-size: 1.18rem !important;
        font-weight: 680 !important;
    }

    .section-description {
        color: #777783 !important;
        font-size: 0.88rem !important;
        line-height: 1.6 !important;
        margin-bottom: 1rem !important;
    }


    /* =====================================================
       FILE UPLOADER
    ===================================================== */

    [data-testid="stFileUploader"] {
        background:
            linear-gradient(
                145deg,
                rgba(255, 255, 255, 0.035),
                rgba(255, 255, 255, 0.015)
            );

        border: 1px solid rgba(167, 139, 250, 0.22);
        border-radius: 16px;
        padding: 0.8rem;

        box-shadow:
            0 12px 40px rgba(0, 0, 0, 0.20),
            0 0 25px rgba(124, 92, 255, 0.025);
    }

    [data-testid="stFileUploader"]:hover {
        border-color: rgba(167, 139, 250, 0.42);

        box-shadow:
            0 12px 40px rgba(0, 0, 0, 0.25),
            0 0 30px rgba(124, 92, 255, 0.08);
    }

    [data-testid="stFileUploaderDropzone"] {
        background: rgba(10, 10, 15, 0.55);
        border-radius: 11px;
        border: 1px dashed rgba(255, 255, 255, 0.12);
    }


    /* =====================================================
       METRIC CARDS
    ===================================================== */

    [data-testid="stMetric"] {
        background:
            linear-gradient(
                145deg,
                rgba(255, 255, 255, 0.045),
                rgba(255, 255, 255, 0.018)
            );

        border: 1px solid rgba(255, 255, 255, 0.075);
        border-radius: 15px;
        padding: 1.25rem;

        box-shadow:
            0 15px 45px rgba(0, 0, 0, 0.20);
    }

    [data-testid="stMetric"]:hover {
        border-color: rgba(167, 139, 250, 0.25);

        box-shadow:
            0 18px 50px rgba(0, 0, 0, 0.25),
            0 0 22px rgba(124, 92, 255, 0.05);
    }

    [data-testid="stMetricLabel"] {
        color: #777783 !important;
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
    }

    [data-testid="stMetricValue"] {
        color: #EDEDF2 !important;
        font-family: "Courier New", monospace !important;
        font-weight: 700 !important;
    }


    /* =====================================================
       BUTTONS
    ===================================================== */

    .stButton > button,
    .stDownloadButton > button {
        min-height: 48px !important;
        border-radius: 11px !important;

        background:
            linear-gradient(
                145deg,
                rgba(255, 255, 255, 0.055),
                rgba(255, 255, 255, 0.025)
            ) !important;

        color: #EDEDF2 !important;

        border: 1px solid rgba(167, 139, 250, 0.25) !important;

        font-size: 0.88rem !important;
        font-weight: 650 !important;

        box-shadow:
            0 8px 25px rgba(0, 0, 0, 0.20),
            0 0 18px rgba(124, 92, 255, 0.035);

        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease,
            border-color 0.18s ease,
            background 0.18s ease !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-2px);

        background:
            linear-gradient(
                145deg,
                rgba(124, 92, 255, 0.17),
                rgba(167, 139, 250, 0.07)
            ) !important;

        border-color: rgba(167, 139, 250, 0.70) !important;

        box-shadow:
            0 12px 30px rgba(0, 0, 0, 0.28),
            0 0 24px rgba(124, 92, 255, 0.18),
            0 0 6px rgba(167, 139, 250, 0.20);
    }

    .stButton > button[kind="primary"] {
        background:
            linear-gradient(
                135deg,
                #7455E8,
                #8B6AF2
            ) !important;

        color: #FFFFFF !important;

        border: 1px solid rgba(196, 181, 253, 0.70) !important;

        box-shadow:
            0 8px 28px rgba(124, 92, 255, 0.22),
            0 0 22px rgba(124, 92, 255, 0.12);
    }

    .stButton > button[kind="primary"]:hover {
        background:
            linear-gradient(
                135deg,
                #8061F2,
                #9A7BFF
            ) !important;

        border-color: #C4B5FD !important;

        box-shadow:
            0 12px 35px rgba(124, 92, 255, 0.30),
            0 0 35px rgba(124, 92, 255, 0.22);
    }


    /* =====================================================
       ALERTS
    ===================================================== */

    [data-testid="stAlert"] {
        border-radius: 11px !important;
        background: rgba(255, 255, 255, 0.025) !important;
    }


    /* =====================================================
       CODE / CRC VALUES
    ===================================================== */

    .crc-display {
        text-align: center;
        padding: 1.1rem;
        margin: 0.3rem 0 1rem 0;

        background:
            linear-gradient(
                145deg,
                rgba(124, 92, 255, 0.085),
                rgba(255, 255, 255, 0.018)
            );

        border: 1px solid rgba(167, 139, 250, 0.22);
        border-radius: 15px;

        box-shadow:
            0 15px 45px rgba(0, 0, 0, 0.22),
            0 0 30px rgba(124, 92, 255, 0.035);
    }

    .crc-label {
        color: #858593 !important;
        font-size: 0.67rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.13em !important;
        text-transform: uppercase !important;
    }

    .crc-value {
        color: #C4B5FD !important;
        font-family: "Courier New", monospace !important;
        font-size: 1.55rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.10em !important;
        text-shadow:
            0 0 18px rgba(167, 139, 250, 0.16);
    }


    /* =====================================================
       RESULT BOXES
    ===================================================== */

    .result-intact {
        padding: 1.25rem;
        border-radius: 15px;

        background:
            linear-gradient(
                145deg,
                rgba(52, 211, 153, 0.075),
                rgba(52, 211, 153, 0.025)
            );

        border: 1px solid rgba(52, 211, 153, 0.25);
    }

    .result-error {
        padding: 1.25rem;
        border-radius: 15px;

        background:
            linear-gradient(
                145deg,
                rgba(248, 113, 113, 0.075),
                rgba(248, 113, 113, 0.025)
            );

        border: 1px solid rgba(248, 113, 113, 0.25);
    }

    .result-generated {
        padding: 1.25rem;
        border-radius: 15px;

        background:
            linear-gradient(
                145deg,
                rgba(167, 139, 250, 0.075),
                rgba(167, 139, 250, 0.025)
            );

        border: 1px solid rgba(167, 139, 250, 0.25);
    }


    /* =====================================================
       FOOTER
    ===================================================== */

    .footer-text {
        color: #5F5F6B !important;
        text-align: center !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.045em !important;
        line-height: 1.8 !important;
    }


    /* =====================================================
       MOBILE
    ===================================================== */

    @media (max-width: 768px) {

        .main .block-container {
            padding-top: 1.4rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero-title {
            font-size: 2.25rem !important;
        }

        .hero-description {
            font-size: 0.9rem !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HERO
# =========================================================

st.markdown(
    '<p class="hero-kicker">CRC-32 / FILE INTEGRITY</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<h1 class="hero-title">Error Detection <span class="hero-highlight">System</span></h1>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="hero-description">'
    'Generate and verify CRC-32 checksums to detect '
    'accidental modifications in files.'
    '</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-line"></div>',
    unsafe_allow_html=True
)


# =========================================================
# STEP 01 — SELECT FILE
# =========================================================

st.markdown(
    '<p class="section-number">01</p>',
    unsafe_allow_html=True
)

st.markdown(
    "### Select File"
)

st.markdown(
    '<p class="section-description">'
    'Upload a file to begin CRC-32 generation and verification.'
    '</p>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Choose a file",
    type=None,
    help="Select a file for CRC-32 error detection.",
    label_visibility="collapsed"
)


# =========================================================
# PROCESS FILE
# =========================================================

if uploaded_file is not None:

    uploaded_data = uploaded_file.getvalue()

    if (
        st.session_state.file_name != uploaded_file.name
        or st.session_state.original_data != uploaded_data
    ):

        st.session_state.file_name = uploaded_file.name
        st.session_state.original_data = uploaded_data
        st.session_state.current_data = uploaded_data

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
# STEP 02 — FILE INFORMATION
# =========================================================

if file_name is not None and current_data is not None:

    st.markdown(
        '<p class="section-number">02</p>',
        unsafe_allow_html=True
    )

    st.markdown("### File Information")

    info1, info2, info3 = st.columns(3)

    with info1:
        st.metric(
            label="Selected File",
            value=file_name
        )

    with info2:
        st.metric(
            label="File Size",
            value=format_file_size(len(current_data))
        )

    with info3:
        st.markdown(
            '<div class="crc-display">'
            '<p class="crc-label">Reference CRC-32</p>'
            f'<p class="crc-value">{format_crc(reference_crc)}</p>'
            '</div>',
            unsafe_allow_html=True
        )

else:

    st.info(
        "Upload a file above to begin CRC-32 error detection."
    )


# =========================================================
# STEP 03 — CRC-32 OPERATIONS
# =========================================================

st.markdown(
    '<p class="section-number">03</p>',
    unsafe_allow_html=True
)

st.markdown("### CRC-32 Operations")

st.markdown(
    '<p class="section-description">'
    'Generate the checksum, verify file integrity, or simulate '
    'a file modification for error detection.'
    '</p>',
    unsafe_allow_html=True
)

operation1, operation2, operation3 = st.columns(3)


# =========================================================
# GENERATE CRC-32
# =========================================================

with operation1:

    if st.button(
        "Generate CRC-32",
        type="primary",
        use_container_width=True
    ):

        if current_data is None:

            st.warning(
                "Please upload a file first."
            )

        else:

            calculated_crc = calculate_crc32(current_data)

            st.session_state.current_crc = calculated_crc

            if st.session_state.reference_crc is None:
                st.session_state.reference_crc = calculated_crc

            st.session_state.last_result = "CRC GENERATED"

            st.rerun()


# =========================================================
# VERIFY CRC-32
# =========================================================

with operation2:

    if st.button(
        "Verify CRC-32",
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

            calculated_crc = calculate_crc32(current_data)

            st.session_state.current_crc = calculated_crc

            if calculated_crc == reference_crc:
                st.session_state.last_result = "FILE INTACT"
            else:
                st.session_state.last_result = "ERROR DETECTED"

            st.rerun()


# =========================================================
# SIMULATE ERROR
# =========================================================

with operation3:

    if st.button(
        "Simulate Error",
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

            modified_data = bytearray(current_data)

            # Flip one bit in the first byte.
            modified_data[0] ^= 1

            st.session_state.current_data = bytes(
                modified_data
            )

            modified_crc = calculate_crc32(
                st.session_state.current_data
            )

            st.session_state.current_crc = modified_crc
            st.session_state.last_result = "FILE MODIFIED"

            st.rerun()


# =========================================================
# VERIFICATION RESULT
# =========================================================

if last_result == "FILE INTACT":

    st.markdown(
        '<div class="result-intact">'
        '<strong>FILE INTACT</strong><br>'
        'The current CRC-32 matches the reference CRC-32. '
        'No error was detected.'
        '</div>',
        unsafe_allow_html=True
    )


elif last_result == "ERROR DETECTED":

    st.markdown(
        '<div class="result-error">'
        '<strong>ERROR DETECTED</strong><br>'
        'The current CRC-32 does not match the reference CRC-32. '
        'The file modification has been detected.'
        '</div>',
        unsafe_allow_html=True
    )


elif last_result == "CRC GENERATED":

    st.markdown(
        '<div class="result-generated">'
        '<strong>CRC-32 GENERATED</strong><br>'
        'The checksum has been calculated successfully.'
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# STEP 04 — CRC-32 COMPARISON
# =========================================================

if reference_crc is not None and current_crc is not None:

    st.markdown(
        '<p class="section-number">04</p>',
        unsafe_allow_html=True
    )

    st.markdown("### CRC-32 Comparison")

    comparison1, comparison2 = st.columns(2)

    with comparison1:

        st.markdown(
            '<div class="crc-display">'
            '<p class="crc-label">Reference CRC-32</p>'
            f'<p class="crc-value">{format_crc(reference_crc)}</p>'
            '</div>',
            unsafe_allow_html=True
        )

    with comparison2:

        st.markdown(
            '<div class="crc-display">'
            '<p class="crc-label">Current CRC-32</p>'
            f'<p class="crc-value">{format_crc(current_crc)}</p>'
            '</div>',
            unsafe_allow_html=True
        )

    if current_crc == reference_crc:

        st.success(
            "CRC-32 values match — File integrity maintained."
        )

    else:

        st.error(
            "CRC-32 values differ — File modification detected."
        )


# =========================================================
# STEP 05 — FILE MANAGEMENT
# =========================================================

st.markdown(
    '<p class="section-number">05</p>',
    unsafe_allow_html=True
)

st.markdown("### File Management")

st.markdown(
    '<p class="section-description">'
    'Restore the original file or prepare the verification report.'
    '</p>',
    unsafe_allow_html=True
)

management1, management2, management3 = st.columns(3)


# =========================================================
# RESTORE ORIGINAL
# =========================================================

with management1:

    if st.button(
        "Restore Original",
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

            st.rerun()


# =========================================================
# CREATE CSV REPORT
# =========================================================

with management2:

    if st.button(
        "Create CSV Report",
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
                "CSV report created successfully."
            )


# =========================================================
# CLEAR DASHBOARD
# =========================================================

with management3:

    if st.button(
        "Clear Dashboard",
        use_container_width=True
    ):

        reset_dashboard()

        st.rerun()


# =========================================================
# STEP 06 — CSV REPORT
# =========================================================

if st.session_state.report_data is not None:

    st.markdown(
        '<p class="section-number">06</p>',
        unsafe_allow_html=True
    )

    st.markdown("### CSV Report")

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
        label="Download CSV Report",
        data=csv_data,
        file_name="error_detection_report.csv",
        mime="text/csv",
        use_container_width=True
    )


# =========================================================
# STEP 07 — ABOUT THE SYSTEM
# =========================================================

st.markdown(
    '<p class="section-number">07</p>',
    unsafe_allow_html=True
)

st.markdown("### About the System")

about1, about2, about3 = st.columns(3)

with about1:

    st.markdown("**Purpose**")

    st.write(
        "Detect file modifications by comparing "
        "CRC-32 checksum values."
    )


with about2:

    st.markdown("**Technique**")

    st.write(
        "CRC-32 checksum generation and comparison."
    )


with about3:

    st.markdown("**Application Area**")

    st.write(
        "Operating Systems / Computer Networks "
        "error detection."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
    <p class="footer-text">
        CRC-32 Error Detection System<br>
        Operating Systems / Computer Networks
        &nbsp;•&nbsp;
        Error Detection
    </p>
    """,
    unsafe_allow_html=True
)

