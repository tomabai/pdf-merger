# PDF Merger Streamlit App

A simple web application to merge multiple PDF files with custom ordering capabilities.

## Features

- 📄 Upload multiple PDF files simultaneously
- 🔄 Reorder files before merging using up/down buttons
- 🔀 Reverse order option for quick reordering
- 📥 Download merged PDF with timestamp
- 📊 File size information and merge statistics

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser to the displayed URL (typically http://localhost:8501)

3. Upload multiple PDF files using the file uploader

4. Reorder the files using the ⬆️ and ⬇️ buttons if needed

5. Click "Merge PDFs" to combine all files

6. Download your merged PDF file

## Additional Files

- `pdf_merger.py` - Command-line PDF merger utility
- `pdf_splitter.py` - PDF splitting utility (if needed)

## Tips

- Files are merged in the order shown in the interface
- Use "Reset Order" to return to original upload sequence
- Use "Reverse Order" to quickly flip the entire sequence
- The merged file will be named with a timestamp for uniqueness 