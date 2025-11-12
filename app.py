import streamlit as st
import tempfile
import os
from PyPDF2 import PdfMerger
from datetime import datetime
import base64
from io import BytesIO
from pdf2docx import Converter


def merge_pdfs_from_uploaded_files(uploaded_files):
    """
    Merge uploaded PDF files and return the merged PDF as bytes.
    """
    merger = PdfMerger()

    for uploaded_file in uploaded_files:
        merger.append(uploaded_file)

    # Create bytes buffer to store merged PDF
    output_buffer = BytesIO()
    merger.write(output_buffer)
    merger.close()

    output_buffer.seek(0)
    return output_buffer.getvalue()


def get_download_link(pdf_bytes, filename):
    """Generate a download link for the PDF."""
    b64 = base64.b64encode(pdf_bytes).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📥 Download Merged PDF</a>'


def convert_pdf_to_docx(pdf_file):
    """
    Convert a PDF file to DOCX format.
    """
    # Create temporary files
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
        tmp_pdf.write(pdf_file.read())
        tmp_pdf_path = tmp_pdf.name
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_docx:
        tmp_docx_path = tmp_docx.name
    
    try:
        # Convert PDF to DOCX
        cv = Converter(tmp_pdf_path)
        cv.convert(tmp_docx_path)
        cv.close()
        
        # Read the DOCX file
        with open(tmp_docx_path, 'rb') as f:
            docx_bytes = f.read()
        
        return docx_bytes
    finally:
        # Clean up temporary files
        if os.path.exists(tmp_pdf_path):
            os.unlink(tmp_pdf_path)
        if os.path.exists(tmp_docx_path):
            os.unlink(tmp_docx_path)


def main():
    st.set_page_config(
        page_title="העזרים של חן",
        page_icon="📄",
        layout="wide"
    )

    # Add RTL CSS
    st.markdown("""
        <style>
        .stApp {
            direction: rtl;
        }
        .stTabs [data-baseweb="tab-list"] {
            direction: rtl;
        }
        .stTabs [data-baseweb="tab"] {
            direction: rtl;
        }
        .stButton button {
            direction: rtl;
        }
        .stDownloadButton button {
            direction: rtl;
        }
        div[data-testid="stFileUploader"] {
            direction: rtl;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📄 העזרים של חן")
    
    # Create tabs for different operations
    tab1, tab2 = st.tabs(["🔗 מיזוג PDF", "📝 PDF ל-DOCX"])
    
    with tab1:
        st.markdown(
            "העלה מספר קבצי PDF ומזג אותם למסמך אחד עם סידור מותאם אישית.")

        # File uploader
        uploaded_files = st.file_uploader(
            "בחר קבצי PDF",
            type="pdf",
            accept_multiple_files=True,
            help="העלה מספר קבצי PDF למיזוג",
            key="merge_uploader"
        )

        if uploaded_files:
            st.subheader("📋 קבצים שהועלו")

            # Create a list to store file order
            if 'file_order' not in st.session_state:
                st.session_state.file_order = list(range(len(uploaded_files)))

            # Reset file order if number of files changed
            if len(st.session_state.file_order) != len(uploaded_files):
                st.session_state.file_order = list(range(len(uploaded_files)))

            # Display files with reordering capability
            st.markdown("**סדר הקבצים (השתמש בכפתורים לשינוי הסדר):**")

            # Display current order with better UI
            ordered_files = [uploaded_files[i]
                             for i in st.session_state.file_order]

            # Show files in a more visual way
            for idx, file in enumerate(ordered_files):
                file_size = len(file.getvalue()) / 1024  # KB

                # Create columns for each file row
                col1, col2, col3, col4 = st.columns([0.5, 3, 1, 1])

                with col1:
                    st.write(f"**{idx + 1}.**")

                with col2:
                    st.write(f"**{file.name}** ({file_size:.1f} ק״ב)")

                with col3:
                    if st.button("⬆️", key=f"up_{idx}", disabled=(idx == 0), help="הזז למעלה"):
                        # Swap with previous
                        current_order = st.session_state.file_order[:]
                        current_order[idx], current_order[idx -
                                                          1] = current_order[idx-1], current_order[idx]
                        st.session_state.file_order = current_order
                        st.rerun()

                with col4:
                    if st.button("⬇️", key=f"down_{idx}", disabled=(idx == len(uploaded_files)-1), help="הזז למטה"):
                        # Swap with next
                        current_order = st.session_state.file_order[:]
                        current_order[idx], current_order[idx +
                                                          1] = current_order[idx+1], current_order[idx]
                        st.session_state.file_order = current_order
                        st.rerun()

            st.markdown("---")

            # Control buttons row
            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                if st.button("🔄 אפס סדר", help="אפס לסדר המקורי"):
                    st.session_state.file_order = list(range(len(uploaded_files)))
                    st.rerun()

            with col2:
                if st.button("🔀 הפוך סדר", help="הפוך את הסדר הנוכחי"):
                    st.session_state.file_order = st.session_state.file_order[::-1]
                    st.rerun()

            st.divider()

            # Merge button
            if st.button("🔗 מזג קבצים", type="primary", use_container_width=True):
                with st.spinner("ממזג קבצי PDF..."):
                    try:
                        # Get files in the specified order
                        ordered_files = [uploaded_files[i]
                                         for i in st.session_state.file_order]

                        # Merge PDFs
                        merged_pdf_bytes = merge_pdfs_from_uploaded_files(
                            ordered_files)

                        # Generate filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"merged_pdf_{timestamp}.pdf"

                        st.success("✅ הקבצים מוזגו בהצלחה!")

                        # Download button
                        st.download_button(
                            label="📥 הורד PDF ממוזג",
                            data=merged_pdf_bytes,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True
                        )

                        # Show file info
                        merged_size = len(merged_pdf_bytes) / 1024  # KB
                        st.info(
                            f"📊 גודל הקובץ הממוזג: {merged_size:.1f} ק״ב | קבצים שמוזגו: {len(ordered_files)}")

                    except Exception as e:
                        st.error(f"❌ שגיאה במיזוג הקבצים: {str(e)}")

        else:
            st.info("👆 אנא העלה קבצי PDF כדי להתחיל")

            # Add some helpful information
            with st.expander("ℹ️ איך להשתמש"):
                st.markdown("""
                1. **העלאת קבצים**: לחץ על 'בחר קבצי PDF' ובחר מספר קבצי PDF
                2. **שינוי סדר**: השתמש בכפתורים ↑ ו-↓ כדי לשנות את סדר הקבצים
                3. **מיזוג**: לחץ על 'מזג קבצים' כדי לאחד את כל הקבצים
                4. **הורדה**: לחץ על כפתור ההורדה כדי לשמור את ה-PDF הממוזג
                
                **טיפים:**
                - הסדר המוצג הוא הסדר שבו הם יופיעו ב-PDF הסופי
                - אפשר להעלות קבצים בגדלים שונים
                - השתמש בכפתור האיפוס כדי לחזור לסדר המקורי
                """)
    
    with tab2:
        st.markdown("המר קבצי PDF לפורמט DOCX (Word) הניתן לעריכה.")
        
        # File uploader for conversion
        pdf_to_convert = st.file_uploader(
            "בחר קובץ PDF להמרה",
            type="pdf",
            help="העלה קובץ PDF בודד להמרה ל-DOCX",
            key="convert_uploader"
        )
        
        if pdf_to_convert:
            st.subheader("📄 קובץ להמרה")
            file_size = len(pdf_to_convert.getvalue()) / 1024  # KB
            st.write(f"**{pdf_to_convert.name}** ({file_size:.1f} ק״ב)")
            
            st.divider()
            
            # Convert button
            if st.button("📝 המר ל-DOCX", type="primary", use_container_width=True):
                with st.spinner("ממיר PDF ל-DOCX..."):
                    try:
                        # Convert PDF to DOCX
                        docx_bytes = convert_pdf_to_docx(pdf_to_convert)
                        
                        # Generate filename
                        original_name = os.path.splitext(pdf_to_convert.name)[0]
                        filename = f"{original_name}.docx"
                        
                        st.success("✅ הקובץ הומר בהצלחה!")
                        
                        # Download button
                        st.download_button(
                            label="📥 הורד DOCX",
                            data=docx_bytes,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                        
                        # Show file info
                        docx_size = len(docx_bytes) / 1024  # KB
                        st.info(f"📊 גודל קובץ DOCX: {docx_size:.1f} ק״ב")
                        
                    except Exception as e:
                        st.error(f"❌ שגיאה בהמרת הקובץ: {str(e)}")
        else:
            st.info("👆 אנא העלה קובץ PDF להמרה")
            
            with st.expander("ℹ️ איך להשתמש"):
                st.markdown("""
                1. **העלאת קובץ**: לחץ על 'בחר קובץ PDF' ובחר קובץ PDF
                2. **המרה**: לחץ על 'המר ל-DOCX' כדי להמיר את הקובץ
                3. **הורדה**: לחץ על כפתור ההורדה כדי לשמור את קובץ ה-DOCX
                
                **הערה:**
                - ההמרה שומרת על טקסט, תמונות ועיצוב בסיסי
                - פריסות מורכבות עשויות לדרוש התאמה ידנית
                - עובד הכי טוב עם קבצי PDF מבוססי טקסט (לא תמונות סרוקות)
                """)


if __name__ == "__main__":
    main()
