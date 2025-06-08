import streamlit as st
import tempfile
import os
from PyPDF2 import PdfMerger
from datetime import datetime
import base64
from io import BytesIO


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


def main():
    st.set_page_config(
        page_title="PDF Merger",
        page_icon="📄",
        layout="wide"
    )

    st.title("📄 PDF Merger")
    st.markdown(
        "Upload multiple PDF files and merge them into a single document with custom ordering.")

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True,
        help="Upload multiple PDF files to merge"
    )

    if uploaded_files:
        st.subheader("📋 Uploaded Files")

        # Create a list to store file order
        if 'file_order' not in st.session_state:
            st.session_state.file_order = list(range(len(uploaded_files)))

        # Reset file order if number of files changed
        if len(st.session_state.file_order) != len(uploaded_files):
            st.session_state.file_order = list(range(len(uploaded_files)))

        # Display files with reordering capability
        st.markdown("**File Order (use buttons to reorder):**")

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
                st.write(f"**{file.name}** ({file_size:.1f} KB)")

            with col3:
                if st.button("⬆️", key=f"up_{idx}", disabled=(idx == 0), help="Move up"):
                    # Swap with previous
                    current_order = st.session_state.file_order[:]
                    current_order[idx], current_order[idx -
                                                      1] = current_order[idx-1], current_order[idx]
                    st.session_state.file_order = current_order
                    st.rerun()

            with col4:
                if st.button("⬇️", key=f"down_{idx}", disabled=(idx == len(uploaded_files)-1), help="Move down"):
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
            if st.button("🔄 Reset Order", help="Reset to original upload order"):
                st.session_state.file_order = list(range(len(uploaded_files)))
                st.rerun()

        with col2:
            if st.button("🔀 Reverse Order", help="Reverse current order"):
                st.session_state.file_order = st.session_state.file_order[::-1]
                st.rerun()

        st.divider()

        # Merge button
        if st.button("🔗 Merge PDFs", type="primary", use_container_width=True):
            with st.spinner("Merging PDFs..."):
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

                    st.success("✅ PDFs merged successfully!")

                    # Download button
                    st.download_button(
                        label="📥 Download Merged PDF",
                        data=merged_pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )

                    # Show file info
                    merged_size = len(merged_pdf_bytes) / 1024  # KB
                    st.info(
                        f"📊 Merged PDF size: {merged_size:.1f} KB | Files merged: {len(ordered_files)}")

                except Exception as e:
                    st.error(f"❌ Error merging PDFs: {str(e)}")

    else:
        st.info("👆 Please upload PDF files to get started")

        # Add some helpful information
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            1. **Upload Files**: Click 'Browse files' and select multiple PDF files
            2. **Reorder**: Use the ↑ and ↓ buttons to change the order of files
            3. **Merge**: Click 'Merge PDFs' to combine all files
            4. **Download**: Click the download button to save your merged PDF
            
            **Tips:**
            - The order shown is the order they'll appear in the final PDF
            - You can upload files of different sizes
            - Use the reset button to return to the original upload order
            """)


if __name__ == "__main__":
    main()
