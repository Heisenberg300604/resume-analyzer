# =============================================================================
# utils/pdf_extractor.py
# PURPOSE: Handles all PDF reading logic using the pdfplumber library.
# =============================================================================

import pdfplumber


def extract_text_from_pdf(file) -> str:
    """
    Extracts and returns all text from a PDF file object.

    Args:
        file: A file-like object (e.g., from Streamlit's file_uploader).

    Returns:
        A single string containing all text extracted from every page of the PDF.
        Returns an empty string if extraction fails.
    """
    full_text = ""  # We'll accumulate text from all pages here

    try:
        # pdfplumber.open() can accept a file path OR a file-like object.
        # Streamlit's UploadedFile is a file-like object, so this works directly.
        with pdfplumber.open(file) as pdf:

            # Loop through every page in the PDF document
            for page in pdf.pages:

                # extract_text() returns the text on a single page as a string,
                # or None if no text is found on that page.
                page_text = page.extract_text()

                if page_text:  # Only add if text was actually found on the page
                    full_text += page_text + "\n"  # Add a newline between pages

    except Exception as e:
        # If anything goes wrong (e.g., corrupted PDF), we print the error
        # and return an empty string, which the main app will handle gracefully.
        print(f"Error extracting text from PDF: {e}")
        return ""

    return full_text