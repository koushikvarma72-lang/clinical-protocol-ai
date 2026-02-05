# pdf_loader.py - Line-by-Line Explanation

**What is this file?**  
This file reads PDF files and extracts the text from them. Think of it like a scanner that reads a paper document and converts it to digital text.

---

## Complete Code with Explanations

```python
import fitz  # PyMuPDF
```
**Line 1**: Import the fitz library (also called PyMuPDF). This is a tool that can read PDF files.
- `fitz`: The library name
- `PyMuPDF`: What it stands for (Python Mu PDF)

---

## Function 1: load_pdf_text()

```python
def load_pdf_text(pdf_path: str) -> str:
```
**Line 3**: Define a function called `load_pdf_text()`.
- `pdf_path: str`: Takes a file path (like "document.pdf") as input
- `-> str`: Returns a string (all the text from the PDF)

```python
    """
    Reads the PDF and returns all text as one string.
    """
```
**Lines 4-6**: Documentation explaining what this function does.

```python
    doc = fitz.open(pdf_path)
```
**Line 7**: Open the PDF file.
- `fitz.open()`: Opens a PDF file
- `pdf_path`: The location of the PDF file
- `doc`: The opened PDF document

```python
    full_text = ""
```
**Line 9**: Create an empty string to store all the text.

```python
    for page in doc:
```
**Line 10**: Loop through each page in the PDF document.
- `for page in doc`: Go through each page one by one

```python
        full_text += page.get_text()
```
**Line 11**: Get the text from the current page and add it to `full_text`.
- `page.get_text()`: Extract text from this page
- `+=`: Add it to the existing text

```python
    doc.close()
```
**Line 13**: Close the PDF file (like closing a book).
- This frees up memory and resources

```python
    return full_text
```
**Line 14**: Return all the text that was extracted from the PDF.

---

## Function 2: load_pdf_with_pages()

```python
def load_pdf_with_pages(pdf_path: str) -> list:
```
**Line 17**: Define a function called `load_pdf_with_pages()`.
- `pdf_path: str`: Takes a file path as input
- `-> list`: Returns a list (multiple items)

```python
    """
    Reads the PDF and returns text with page information.
    Returns list of dictionaries with page_num and text.
    """
```
**Lines 18-21**: Documentation explaining what this function does.

```python
    doc = fitz.open(pdf_path)
```
**Line 22**: Open the PDF file.

```python
    pages_data = []
```
**Line 24**: Create an empty list to store page information.

```python
    for page_num in range(len(doc)):
```
**Line 25**: Loop through each page using a number.
- `range(len(doc))`: Create numbers from 0 to the number of pages
- `page_num`: The current page number (0, 1, 2, ...)

```python
        page = doc[page_num]
```
**Line 26**: Get the current page from the document.
- `doc[page_num]`: Access the page at this number

```python
        text = page.get_text()
```
**Line 27**: Extract text from the current page.

```python
        if text.strip():  # Only include pages with text
```
**Line 29**: Check if the page has text (not empty).
- `text.strip()`: Remove spaces and check if anything is left
- `if`: Only continue if there's text

```python
            pages_data.append({
                "page_number": page_num + 1,  # 1-based page numbering
                "text": text.strip()
            })
```
**Lines 30-33**: Add the page information to the list.
- `pages_data.append()`: Add a new item to the list
- `"page_number": page_num + 1`: The page number (starting from 1, not 0)
- `"text": text.strip()`: The text from the page (with spaces removed)
- `{}`: This is a dictionary (a container with labels and values)

```python
    doc.close()
```
**Line 35**: Close the PDF file.

```python
    return pages_data
```
**Line 36**: Return the list of pages with their text and page numbers.

---

## What This File Does (Summary)

### Function 1: `load_pdf_text()`
1. Opens a PDF file
2. Loops through each page
3. Extracts text from each page
4. Combines all text into one string
5. Returns the combined text

### Function 2: `load_pdf_with_pages()`
1. Opens a PDF file
2. Loops through each page
3. Extracts text from each page
4. Keeps track of which page the text came from
5. Returns a list of pages with their text and page numbers

## How It's Used

Other files call these functions to:
- Get text from PDF documents
- Know which page each piece of text came from
- Process the text for storage in the database

## Simple Analogy

Imagine reading a book:
- **`load_pdf_text()`**: Read the entire book and give me all the words
- **`load_pdf_with_pages()`**: Read the entire book and tell me which page each sentence came from

## Key Differences

| Function | Returns | Includes Page Info |
|----------|---------|-------------------|
| `load_pdf_text()` | One big string | No |
| `load_pdf_with_pages()` | List of dictionaries | Yes |

## Example Output

### `load_pdf_text()` returns:
```
"This is page 1 text. This is page 2 text. This is page 3 text."
```

### `load_pdf_with_pages()` returns:
```python
[
    {"page_number": 1, "text": "This is page 1 text."},
    {"page_number": 2, "text": "This is page 2 text."},
    {"page_number": 3, "text": "This is page 3 text."}
]
```

---

**Total Lines**: 36  
**Complexity**: ⭐ Easy  
**Purpose**: Extract text from PDF files with or without page information
