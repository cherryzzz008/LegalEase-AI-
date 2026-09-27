import sys
import os
import html
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import streamlit as st
from dotenv import load_dotenv

from backend.utils.document_formatter import (
    format_docx,
    format_pdf,
    format_txt,
)

from backend.utils.helpers import safe_filename


# --------------------------------------------------
# ENVIRONMENT
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# STREAMLIT CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
)


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


LOGO_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "logo.png",
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""

if "editing" not in st.session_state:
    st.session_state.editing = False


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
<style>

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #6b7280;
    font-size: 17px;
    margin-bottom: 25px;
}

.info-box {
    background: #eef2ff;
    padding: 16px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.preview-box {
    background: #111827;
    color: #f9fafb;
    padding: 25px;
    border-radius: 12px;
    max-height: 650px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.7;
    font-family: Georgia, serif;
}

</style>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

if os.path.exists(LOGO_PATH):

    left, center, right = st.columns([1, 2, 1])

    with center:
        st.image(
            LOGO_PATH,
            width=130,
        )

else:

    st.markdown(
        "<h1 style='text-align:center;'>⚖️</h1>",
        unsafe_allow_html=True,
    )


st.markdown(
    "<div class='main-title'>LegalEase</div>",
    unsafe_allow_html=True,
)


st.markdown(
    """
<div class="subtitle">
AI-Powered Legal Document Generator
</div>
""",
    unsafe_allow_html=True,
)


st.markdown(
    """
<div class="info-box">
Create structured legal document drafts using AI.
Enter the details below and generate an editable document.
</div>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# INPUTS
# --------------------------------------------------

st.subheader("Document Details")


document_type = st.selectbox(
    "Document Type",
    [
        "Employment Contract",
        "Non-Disclosure Agreement (NDA)",
        "Lease Agreement",
        "Freelance Work Contract",
        "Service Agreement",
        "Employment Offer Letter",
        "Partnership Agreement",
        "General Agreement",
        "Custom Legal Document",
    ],
)


if document_type == "Custom Legal Document":

    custom_type = st.text_input(
        "Enter custom document type",
        placeholder="Example: Software Development Agreement",
    )

    if custom_type.strip():
        document_type = custom_type.strip()


parties = st.text_area(
    "Parties Involved",
    placeholder=(
        "Example:\n"
        "Jane Doe (Service Provider)\n"
        "TechNova Inc. (Client)"
    ),
    height=120,
)


terms = st.text_area(
    "Terms & Conditions",
    placeholder=(
        "Separate terms using semicolons.\n\n"
        "Example:\n"
        "Payment within 30 days; "
        "Confidentiality must be maintained; "
        "Either party may terminate with 15 days notice"
    ),
    height=180,
)


effective_date = st.date_input(
    "Effective Date",
    value=date.today(),
)


# --------------------------------------------------
# GENERATE BUTTON
# --------------------------------------------------

st.divider()


generate = st.button(
    "⚡ Generate Document",
    type="primary",
    use_container_width=True,
)


if generate:

    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    elif not terms.strip():

        st.error(
            "Please enter the terms and conditions."
        )

    else:

        # IMPORTANT:
        # Backend expects "effective_date"
        payload = {
            "document_type": document_type,
            "parties": parties.strip(),
            "terms": terms.strip(),
            "effective_date": effective_date.strftime(
                "%B %d, %Y"
            ),
        }

        with st.spinner(
            "Generating your legal document..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=180,
                )

                if response.ok:

                    data = response.json()

                    # Backend returns {"document": "..."}
                    st.session_state.generated_text = data.get(
                        "document",
                        "",
                    )

                    if not st.session_state.generated_text:
                        st.error(
                            "Backend returned an empty document."
                        )
                    else:
                        st.session_state.editing = False

                        st.success(
                            "Document generated successfully."
                        )

                else:

                    try:

                        error = response.json()

                        detail = error.get(
                            "detail",
                            response.text,
                        )

                    except Exception:

                        detail = response.text

                    st.error(
                        f"Backend error: {detail}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "FastAPI backend is not running. "
                    "Start the backend first."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out. "
                    "Please try again."
                )

            except Exception as exc:

                st.error(
                    f"Unexpected error: {exc}"
                )


# --------------------------------------------------
# DOCUMENT OUTPUT
# --------------------------------------------------

if st.session_state.generated_text:

    st.divider()

    st.subheader(
        "Generated Document"
    )


    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "✏️ Edit Document",
            use_container_width=True,
        ):

            st.session_state.editing = True


    with col2:

        if st.button(
            "👁️ Preview Document",
            use_container_width=True,
        ):

            st.session_state.editing = False


    # --------------------------------------------------
    # EDIT MODE
    # --------------------------------------------------

    if st.session_state.editing:

        edited_text = st.text_area(
            "Edit Document",
            value=st.session_state.generated_text,
            height=650,
        )


        if st.button(
            "💾 Save Changes",
            type="primary",
        ):

            st.session_state.generated_text = edited_text

            st.session_state.editing = False

            st.success(
                "Changes saved successfully."
            )

            st.rerun()


    # --------------------------------------------------
    # PREVIEW MODE
    # --------------------------------------------------

    else:

        safe_text = html.escape(
            st.session_state.generated_text
        )

        st.markdown(
            f"""
            <div class="preview-box">
            {safe_text}
            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------
    # EXPORT
    # --------------------------------------------------

    st.divider()

    st.subheader(
        "Download Document"
    )


    current_text = (
        st.session_state.generated_text
    )


    txt_data = format_txt(
        current_text,
        document_type,
    )


    docx_data = format_docx(
        current_text,
        document_type,
        LOGO_PATH,
        terms,
    )


    pdf_data = format_pdf(
        current_text,
        document_type,
        LOGO_PATH,
    )


    filename = safe_filename(
        document_type
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.download_button(
            "📄 Download TXT",
            data=txt_data,
            file_name=f"{filename}.txt",
            mime="text/plain",
            use_container_width=True,
        )


    with col2:

        st.download_button(
            "📝 Download DOCX",
            data=docx_data,
            file_name=f"{filename}.docx",
            mime=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True,
        )


    with col3:

        st.download_button(
            "📕 Download PDF",
            data=pdf_data,
            file_name=f"{filename}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "LegalEase — AI-powered legal document drafting. "
    "AI-generated drafts should be reviewed by a qualified "
    "legal professional before use."
)
