import fitz  # PyMuPDF

def load_pdf_text(pdf_path: str) -> str:
    """
    Reads the PDF and returns all text as one string.
    """
    doc = fitz.open(pdf_path)

    full_text = ""
    for page in doc:
        full_text += page.get_text()

    doc.close()
    return full_text


def load_pdf_with_pages(pdf_path: str) -> list:
    """
    Reads the PDF and returns text with page information.
    Returns list of dictionaries with page_num and text.
    """
    doc = fitz.open(pdf_path)
    
    pages_data = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        if text.strip():  # Only include pages with text
            pages_data.append({
                "page_number": page_num + 1,  # 1-based page numbering
                "text": text.strip()
            })
    
    doc.close()
    return pages_data
