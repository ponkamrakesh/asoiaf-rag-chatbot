"""
ASOIAF RAG Ingestion Pipeline
Processes the 4,068-page 'got.pdf' (5 books: A Game of Thrones, A Clash of Kings,
A Storm of Swords, A Feast for Crows, A Dance with Dragons).

Features:
- Book boundary identification
- POV chapter and appendix section tagging
- Context-prefixed semantic recursive chunking
- FastEmbed (BAAI/bge-small-en-v1.5, 384 dimensions)
- Batch upserting to Pinecone (batches of 200)
- Dry-run & limit-pages testing modes
"""

import os
import sys
import re
import argparse
import time
from typing import List, Dict, Any, Generator

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF is required. Run: pip install pymupdf")
    sys.exit(1)


# Book Page Ranges in got.pdf (1-indexed page numbers)
BOOK_RANGES = [
    {"book": "A Game of Thrones", "start_page": 1, "end_page": 749, "book_num": 1},
    {"book": "A Clash of Kings", "start_page": 750, "end_page": 1483, "book_num": 2},
    {"book": "A Storm of Swords", "start_page": 1484, "end_page": 2419, "book_num": 3},
    {"book": "A Feast for Crows", "start_page": 2420, "end_page": 3113, "book_num": 4},
    {"book": "A Dance with Dragons", "start_page": 3114, "end_page": 4068, "book_num": 5},
]

# Common Martin POV chapter headers & section markers
KNOWN_POV_CHARACTERS = {
    "PROLOGUE", "EPILOGUE", "BRAN", "CATELYN", "DAENERYS", "EDDARD", "JON", "ARYA",
    "TYRION", "SANSA", "DAVOS", "THEON", "JAIME", "SAMWELL", "CERSEI", "BRIENNE",
    "AERYS", "ASHA", "VICTARION", "AERON", "AREO", "ARIANNE", "QUENTYN", "BARRISTAN",
    "MELISANDRE", "THE PROPHET", "THE CAPTAIN OF GUARDS", "THE DROWNED MAN",
    "THE QUEENMAKER", "THE SOILLED KNIGHT", "THE KRAKEN'S DAUGHTER", "THE IRON SUITOR",
    "THE BLIND GIRL", "THE DISCARDED KNIGHT", "THE KING'S PRIZE", "THE SENTRY",
    "THE QUEEN'S GUARD", "THE UGLY LITTLE GIRL", "THE BLOWING BLOW", "THE DRAGON TAMER",
    "THE PRINCE OF WINTERFELL", "THE LOST LORD", "THE WAYWARD BRIDE", "THE GRIFFIN REBORN",
    "APPENDIX", "HOUSE BARATHEON", "HOUSE STARK", "HOUSE LANNISTER", "HOUSE ARRYN",
    "HOUSE TULLY", "HOUSE TYRELL", "HOUSE GREYJOY", "HOUSE MARTELL", "HOUSE TARGARYEN"
}


def get_book_for_page(page_num: int) -> Dict[str, Any]:
    """Find the book corresponding to a given 1-indexed page number."""
    for b in BOOK_RANGES:
        if b["start_page"] <= page_num <= b["end_page"]:
            return b
    return {"book": "A Song of Ice and Fire", "start_page": 1, "end_page": 4068, "book_num": 0}


def detect_chapter_header(text: str) -> str:
    """Detect if the page begins with a known POV character chapter heading or Appendix."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    
    # Check top 4 lines
    for line in lines[:4]:
        clean = re.sub(r'[^A-Z\s\']', '', line.upper()).strip()
        if clean in KNOWN_POV_CHARACTERS:
            return clean
        if clean.startswith("CHAPTER") or clean.startswith("HOUSE "):
            return clean
    return ""


def recursive_split_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> List[str]:
    """
    Recursively split text into chunks respecting paragraphs, sentences, and words.
    """
    text = text.strip()
    if len(text) <= chunk_size:
        return [text] if text else []

    separators = ["\n\n", "\n", ". ", "? ", "! ", "; ", " ", ""]
    
    def _split(txt: str, sep_idx: int) -> List[str]:
        if len(txt) <= chunk_size or sep_idx >= len(separators):
            return [txt] if txt else []
        
        sep = separators[sep_idx]
        if sep == "":
            chunks = []
            start = 0
            while start < len(txt):
                end = min(start + chunk_size, len(txt))
                chunks.append(txt[start:end])
                start += chunk_size - overlap
            return chunks

        parts = txt.split(sep)
        result = []
        current = ""

        for part in parts:
            candidate = current + (sep if current else "") + part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    result.append(current)
                    # Keep overlap from current end
                    overlap_str = current[-overlap:] if len(current) > overlap else current
                    current = overlap_str + (sep if overlap_str else "") + part
                else:
                    # Single part is larger than chunk_size, split with next separator
                    sub_chunks = _split(part, sep_idx + 1)
                    result.extend(sub_chunks)
                    current = ""

        if current:
            result.append(current)
        return result

    return _split(text, 0)


def extract_chunks(
    pdf_path: str,
    max_pages: int = None,
    chunk_size: int = 1200,
    overlap: int = 200
) -> List[Dict[str, Any]]:
    """
    Extracts text from PDF, segments into books and chapters,
    and returns context-prefixed chunks ready for embedding.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")

    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"Total PDF pages: {total_pages}")

    pages_to_process = min(total_pages, max_pages) if max_pages else total_pages
    chunks = []
    
    current_chapter = "PROLOGUE"
    is_appendix = False

    for page_idx in range(pages_to_process):
        page_num = page_idx + 1
        page = doc[page_idx]
        text = page.get_text()
        
        if not text or len(text.strip()) < 40:
            # Skip blank, cover, or pure image pages
            continue

        book_info = get_book_for_page(page_num)
        
        # Check if new chapter starts here
        detected_ch = detect_chapter_header(text)
        if detected_ch:
            current_chapter = detected_ch
            if "APPENDIX" in detected_ch or "HOUSE " in detected_ch:
                is_appendix = True
            elif detected_ch in KNOWN_POV_CHARACTERS:
                is_appendix = False

        # Split text into chunks
        page_chunks = recursive_split_text(text, chunk_size=chunk_size, overlap=overlap)

        for chunk_idx, raw_chunk in enumerate(page_chunks):
            chunk_id = f"got_b{book_info['book_num']}_p{page_num}_c{chunk_idx+1}"
            
            # Context-prefixed text for embedding
            context_prefix = (
                f"Source: [Book: {book_info['book']} | "
                f"Chapter: {current_chapter} | "
                f"Page: {page_num}"
                f"{' | Appendix' if is_appendix else ''}]\n"
            )
            embed_text = context_prefix + raw_chunk

            chunks.append({
                "id": chunk_id,
                "text": raw_chunk,
                "embed_text": embed_text,
                "metadata": {
                    "book": book_info["book"],
                    "book_num": book_info["book_num"],
                    "chapter": current_chapter,
                    "page": page_num,
                    "is_appendix": is_appendix,
                    "chunk_id": chunk_id,
                    "text": raw_chunk[:1000],  # Pinecone metadata size safeguard
                }
            })

        if page_num % 500 == 0 or page_num == pages_to_process:
            print(f"Parsed {page_num}/{pages_to_process} pages -> {len(chunks)} chunks extracted.")

    return chunks


def batch_generator(iterable: List[Any], batch_size: int = 200) -> Generator[List[Any], None, None]:
    """Yield successive batch_size chunks from iterable."""
    for i in range(0, len(iterable), batch_size):
        yield iterable[i : i + batch_size]


def upsert_to_pinecone(
    chunks: List[Dict[str, Any]],
    index_name: str,
    api_key: str,
    batch_size: int = 200
):
    """
    Embeds chunks using FastEmbed and batch upserts into Pinecone.
    """
    try:
        from pinecone import Pinecone, ServerlessSpec
        from fastembed import TextEmbedding
    except ImportError as e:
        print(f"Error: Missing dependency for Pinecone upsert ({e}). Run: pip install pinecone-client fastembed")
        sys.exit(1)

    print(f"\nInitializing Pinecone Client...")
    pc = Pinecone(api_key=api_key)

    existing_indexes = [idx["name"] for idx in pc.list_indexes()]
    dimension = 384  # FastEmbed BAAI/bge-small-en-v1.5 dimension

    if index_name not in existing_indexes:
        print(f"Creating Pinecone index '{index_name}' (dimension={dimension}, metric=cosine)...")
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        time.sleep(5)

    index = pc.Index(index_name)
    print(f"Connected to Pinecone index: {index_name}")

    print("\nLoading FastEmbed model: BAAI/bge-small-en-v1.5...")
    embed_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    total_chunks = len(chunks)
    print(f"Total chunks to embed and upsert: {total_chunks}")

    start_time = time.time()
    upserted_count = 0

    for batch in batch_generator(chunks, batch_size=batch_size):
        # Generate embeddings for batch
        texts_to_embed = [item["embed_text"] for item in batch]
        embeddings = list(embed_model.embed(texts_to_embed))

        vectors = []
        for item, emb in zip(batch, embeddings):
            vectors.append({
                "id": item["id"],
                "values": emb.tolist(),
                "metadata": item["metadata"]
            })

        index.upsert(vectors=vectors)
        upserted_count += len(vectors)
        print(f"Upserted: {upserted_count}/{total_chunks} vectors ({(upserted_count/total_chunks)*100:.1f}%)")

    elapsed = time.time() - start_time
    print(f"\nSuccessfully upserted {upserted_count} vectors into Pinecone in {elapsed:.1f}s!")


def main():
    parser = argparse.ArgumentParser(description="ASOIAF PDF Ingestion to Pinecone")
    parser.add_argument("--pdf", default="data/got.pdf", help="Path to PDF")
    parser.add_argument("--max-pages", type=int, default=None, help="Limit pages for testing")
    parser.add_argument("--dry-run", action="store_true", help="Extract and preview chunks without upserting")
    parser.add_argument("--batch-size", type=int, default=200, help="Batch size for Pinecone upsert")
    args = parser.parse_args()

    pdf_path = args.pdf
    if not os.path.isabs(pdf_path):
        # Resolve relative to repo root
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        pdf_path = os.path.join(root_dir, args.pdf)

    chunks = extract_chunks(pdf_path, max_pages=args.max_pages)
    print(f"\nExtraction complete! Total chunks ready: {len(chunks)}")

    if chunks:
        sample = chunks[0]
        print("\n--- Sample Chunk Preview ---")
        print(f"ID: {sample['id']}")
        print(f"Metadata: {sample['metadata']}")
        print(f"Embed Text Sample:\n{sample['embed_text'][:350]}...\n")

    if args.dry_run:
        print("[DRY-RUN] Finished without calling Pinecone API.")
        return

    pinecone_key = os.getenv("PINECONE_API_KEY")
    pinecone_index = os.getenv("PINECONE_INDEX_NAME", "asoiaf-books")

    if not pinecone_key:
        print("\n[Notice] PINECONE_API_KEY not found in environment.")
        print("To upsert to Pinecone, set PINECONE_API_KEY and run without --dry-run.")
        print("Example: PINECONE_API_KEY=xxx PINECONE_INDEX_NAME=asoiaf-books python scripts/ingest.py")
        return

    upsert_to_pinecone(chunks, pinecone_index, pinecone_key, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
