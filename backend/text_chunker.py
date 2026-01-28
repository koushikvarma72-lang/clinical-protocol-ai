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
                # Look for sentence endings within the last 100 characters
                last_period = chunk_text.rfind('. ')
                last_exclamation = chunk_text.rfind('! ')
                last_question = chunk_text.rfind('? ')
                
                sentence_end = max(last_period, last_exclamation, last_question)
                if sentence_end > len(chunk_text) - 100:  # If found near the end
                    end = start + sentence_end + 2
                    chunk_text = page_text[start:end]
            
            chunks.append({
                "id": f"chunk_{chunk_id}",
                "text": chunk_text.strip(),
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
