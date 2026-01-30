import re
def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append({
            "text": chunk,
            "start": start,
            "end": end
        })

        start = end - overlap

    return chunks


def chunk_pages_with_metadata(pages_data, chunk_size=1000, overlap=200):
    """
    Chunk text from pages while preserving page number metadata.
    """
    chunks = []
    chunk_id = 0
    
    for page_data in pages_data:
        page_num = page_data["page_number"]
        page_text = page_data["text"]
        
        # Split page text into chunks
        start = 0
        text_length = len(page_text)
        
        while start < text_length:
            end = start + chunk_size
            chunk_text = page_text[start:end]
            
            # Find sentence boundaries to avoid cutting mid-sentence
            if end < text_length:
                # Look for terminal punctuation followed by a space and a Capital Letter
                # This regex ensures we don't break on "mg." or "Dr."
                pattern = r'[.!?]\s+(?=[A-Z])'
                matches = list(re.finditer(pattern, chunk_text))
                
                if matches:
                    # last_match.end() points to just after the punctuation/space
                    sentence_end = matches[-1].end()
                    
                    # If valid boundary found in the last 150 chars, snap to it
                    if sentence_end > len(chunk_text) - 150:
                        end = start + sentence_end
                        chunk_text = page_text[start:end]
            
            chunks.append({
                "id": f"chunk_{chunk_id}",
                "text": f"search_document: {chunk_text.strip()}",
                "page_number": page_num,
                "start_pos": start,
                "end_pos": end,
                "source": f"Page {page_num}"
            })
            
            chunk_id += 1
            start = end - overlap
            
            # Prevent infinite loop
            if start >= text_length:
                break
    
    return chunks
