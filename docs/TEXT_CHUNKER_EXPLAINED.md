# text_chunker.py - Line-by-Line Explanation

**What is this file?**  
This file breaks long text into smaller pieces (chunks). Think of it like cutting a long rope into smaller pieces that are easier to handle.

---

## Complete Code with Explanations

```python
import re
```
**Line 1**: Import the `re` library (regular expressions). This helps find patterns in text.

---

## Function 1: chunk_text()

```python
def chunk_text(text, chunk_size=1000, overlap=200):
```
**Line 2**: Define a function that breaks text into chunks.
- `text`: The text to break up
- `chunk_size=1000`: Each chunk is 1000 characters (default)
- `overlap=200`: Chunks overlap by 200 characters (default)

```python
    chunks = []
```
**Line 3**: Create an empty list to store the chunks.

```python
    start = 0
    text_length = len(text)
```
**Lines 5-6**: Set up variables.
- `start = 0`: Start at the beginning of the text
- `text_length`: How many characters are in the text

```python
    while start < text_length:
```
**Line 8**: Loop while we haven't reached the end of the text.

```python
        end = start + chunk_size
        chunk = text[start:end]
```
**Lines 9-10**: Create a chunk.
- `end`: The ending position (start + 1000)
- `chunk`: The text from start to end

```python
        chunks.append({
            "text": chunk,
            "start": start,
            "end": end
        })
```
**Lines 12-16**: Add the chunk to the list.
- `chunks.append()`: Add a new item
- `"text"`: The actual text
- `"start"`: Where it starts in the original text
- `"end"`: Where it ends in the original text

```python
        start = end - overlap
```
**Line 18**: Move to the next chunk position.
- `end - overlap`: Move forward but overlap with the previous chunk
- Example: If end=1000 and overlap=200, start becomes 800

```python
    return chunks
```
**Line 20**: Return all the chunks.

---

## Function 2: chunk_pages_with_metadata()

```python
def chunk_pages_with_metadata(pages_data, chunk_size=1000, overlap=200):
```
**Line 23**: Define a function that chunks text while keeping page information.
- `pages_data`: List of pages with text and page numbers
- `chunk_size=1000`: Each chunk is 1000 characters
- `overlap=200`: Chunks overlap by 200 characters

```python
    """
    Chunk text from pages while preserving page number metadata.
    """
```
**Lines 24-26**: Documentation explaining what this function does.

```python
    chunks = []
    chunk_id = 0
```
**Lines 27-28**: Set up variables.
- `chunks`: Empty list to store chunks
- `chunk_id`: Counter for naming chunks (chunk_0, chunk_1, etc.)

```python
    for page_data in pages_data:
```
**Line 30**: Loop through each page.

```python
        page_num = page_data["page_number"]
        page_text = page_data["text"]
```
**Lines 31-32**: Extract information from the current page.
- `page_num`: The page number
- `page_text`: The text from this page

```python
        # Split page text into chunks
        start = 0
        text_length = len(page_text)
```
**Lines 34-36**: Set up variables for chunking this page.
- `start = 0`: Start at the beginning of the page
- `text_length`: How many characters in this page

```python
        while start < text_length:
```
**Line 38**: Loop while we haven't reached the end of the page.

```python
            end = start + chunk_size
            chunk_text = page_text[start:end]
```
**Lines 39-40**: Create a chunk.
- `end`: The ending position
- `chunk_text`: The text from start to end

```python
            # Find sentence boundaries to avoid cutting mid-sentence
            if end < text_length:
```
**Lines 42-43**: Check if we're not at the end of the page.
- This helps us avoid cutting text in the middle of a sentence

```python
                # Look for terminal punctuation followed by a space and a Capital Letter
                # This regex ensures we don't break on "mg." or "Dr."
                pattern = r'[.!?]\s+(?=[A-Z])'
```
**Lines 44-46**: Create a pattern to find sentence endings.
- `[.!?]`: Find periods, exclamation marks, or question marks
- `\s+`: Followed by one or more spaces
- `(?=[A-Z])`: Followed by a capital letter (but don't include it)

```python
                matches = list(re.finditer(pattern, chunk_text))
```
**Line 47**: Find all places where the pattern matches in the chunk.
- `re.finditer()`: Find all matches
- `list()`: Convert to a list

```python
                if matches:
```
**Line 49**: If we found any sentence endings.

```python
                    # last_match.end() points to just after the punctuation/space
                    sentence_end = matches[-1].end()
```
**Lines 50-51**: Get the position of the last sentence ending.
- `matches[-1]`: The last match
- `.end()`: The position after the match

```python
                    # If valid boundary found in the last 150 chars, snap to it
                    if sentence_end > len(chunk_text) - 150:
```
**Lines 52-53**: Check if the sentence ending is near the end of the chunk.
- If it's in the last 150 characters, use it as the boundary

```python
                        end = start + sentence_end
                        chunk_text = page_text[start:end]
```
**Lines 54-55**: Adjust the chunk to end at the sentence boundary.

```python
            chunks.append({
                "id": f"chunk_{chunk_id}",
                "text": f"search_document: {chunk_text.strip()}",
                "page_number": page_num,
                "start_pos": start,
                "end_pos": end,
                "source": f"Page {page_num}"
            })
```
**Lines 57-64**: Add the chunk to the list with metadata.
- `"id"`: Unique identifier (chunk_0, chunk_1, etc.)
- `"text"`: The actual text with "search_document: " prefix
- `"page_number"`: Which page this came from
- `"start_pos"`: Starting position in the page
- `"end_pos"`: Ending position in the page
- `"source"`: Human-readable source (e.g., "Page 1")

```python
            chunk_id += 1
            start = end - overlap
```
**Lines 66-67**: Move to the next chunk.
- `chunk_id += 1`: Increment the counter
- `start = end - overlap`: Move forward with overlap

```python
            # Prevent infinite loop
            if start >= text_length:
                break
```
**Lines 69-71**: Stop if we've reached the end.
- This prevents the loop from running forever

```python
    return chunks
```
**Line 73**: Return all the chunks with metadata.

---

## What This File Does (Summary)

### Function 1: `chunk_text()`
1. Takes a long text
2. Breaks it into 1000-character pieces
3. Makes pieces overlap by 200 characters
4. Returns a list of chunks

### Function 2: `chunk_pages_with_metadata()`
1. Takes pages with text and page numbers
2. Breaks each page into 1000-character chunks
3. Tries to break at sentence boundaries (not mid-sentence)
4. Keeps track of page numbers and positions
5. Returns chunks with metadata

## How It's Used

Other files call these functions to:
- Break long documents into manageable pieces
- Keep track of where each piece came from
- Prepare text for embedding and storage

## Simple Analogy

Imagine cutting a book into pieces:
- **`chunk_text()`**: Cut the book into equal-sized pieces
- **`chunk_pages_with_metadata()`**: Cut the book into pieces, but remember which page each piece came from and try not to cut mid-sentence

## Why Overlap?

Overlap (200 characters) helps because:
- Information at chunk boundaries isn't lost
- Searches can find relevant information even if it spans chunks
- Context is preserved

## Example

**Original text**: "The patient has diabetes. The treatment is insulin. The dosage is 10mg."

**With chunk_size=30, overlap=10**:
```
Chunk 1: "The patient has diabetes. The"
Chunk 2: "diabetes. The treatment is ins"
Chunk 3: "is insulin. The dosage is 10mg"
```

Notice how "diabetes" and "insulin" appear in multiple chunks (overlap).

---

**Total Lines**: 73  
**Complexity**: ⭐⭐ Medium  
**Purpose**: Break long text into smaller chunks while preserving metadata and sentence boundaries
