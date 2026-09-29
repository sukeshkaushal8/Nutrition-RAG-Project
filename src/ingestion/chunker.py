import json
import logging
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

from src.ingestion.parser import ParsedDocument, Section

logger = logging.getLogger(__name__)

MAX_CHUNK_TOKENS = 512
MIN_CHUNK_TOKENS = 50
OVERLAP_TOKENS = 50

@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    document_name: str
    publisher: str
    year: int
    source_url: str
    section_heading: str
    content: str
    chunk_index: int
    token_count: int

    def to_dict(self):
        return asdict(self)

def count_tokens(text: str) -> int:
    return len(text.split())

def split_into_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def chunk_prose(text: str) -> List[str]:
    sentences = split_into_sentences(text)
    if not sentences:
        return []
        
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)
        if current_tokens + sentence_tokens > MAX_CHUNK_TOKENS and current_chunk:
            chunks.append(" ".join(current_chunk))
            
            overlap_sentences = []
            overlap_count = 0
            for s in reversed(current_chunk):
                s_tokens = count_tokens(s)
                if overlap_count + s_tokens > OVERLAP_TOKENS:
                    if not overlap_sentences: 
                        overlap_sentences.insert(0, s)
                    break
                overlap_sentences.insert(0, s)
                overlap_count += s_tokens
            
            current_chunk = list(overlap_sentences)
            current_tokens = overlap_count
            
        current_chunk.append(sentence)
        current_tokens += sentence_tokens
        
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    if len(chunks) > 1:
        merged_chunks = []
        i = 0
        while i < len(chunks):
            if i == len(chunks) - 1:
                if count_tokens(chunks[i]) < MIN_CHUNK_TOKENS and merged_chunks:
                    # Avoid duplicated overlap if we simply append. But simple append is fine for now as per instructions.
                    # Wait, if we append, we might duplicate the overlap. Let's just append.
                    merged_chunks[-1] = merged_chunks[-1] + " " + chunks[i]
                else:
                    merged_chunks.append(chunks[i])
                i += 1
            else:
                if count_tokens(chunks[i]) < MIN_CHUNK_TOKENS:
                    chunks[i+1] = chunks[i] + " " + chunks[i+1]
                else:
                    merged_chunks.append(chunks[i])
                i += 1
        chunks = merged_chunks
        
    return chunks

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def chunk_table(content: str) -> List[str]:
    rows = content.strip().split('\n')
    if len(rows) <= 1 or count_tokens(content) <= MAX_CHUNK_TOKENS:
        return [content]
        
    header = rows[0]
    chunks = []
    current_chunk = [header]
    current_tokens = count_tokens(header)
    
    for row in rows[1:]:
        row_tokens = count_tokens(row)
        if current_tokens + row_tokens > MAX_CHUNK_TOKENS and len(current_chunk) > 1:
            chunks.append("\n".join(current_chunk))
            current_chunk = [header, row]
            current_tokens = count_tokens(header) + row_tokens
        else:
            current_chunk.append(row)
            current_tokens += row_tokens
            
    if len(current_chunk) > 1:
        chunks.append("\n".join(current_chunk))
        
    return chunks

def chunk_document(parsed_doc: ParsedDocument) -> List[Chunk]:
    chunks = []
    chunk_index = 0
    
    for section in parsed_doc.sections:
        if section.section_type == "table":
            text_chunks = chunk_table(section.content)
        elif section.section_type == "list":
            text_chunks = [section.content]
        else:
            text_chunks = chunk_prose(section.content)
            
        heading_parts = section.heading.split(" > ")
        last_heading = heading_parts[-1] if heading_parts else section.heading
        heading_slug = slugify(last_heading)
        if not heading_slug:
            heading_slug = "section"
            
        for text in text_chunks:
            if not text.strip():
                continue
                
            chunk_id = f"{parsed_doc.doc_id}__{heading_slug}__{chunk_index}"
            
            # Inject breadcrumb metadata into content
            final_text = f"[{section.heading}]\n{text.strip()}"
            
            chunks.append(Chunk(
                chunk_id=chunk_id,
                doc_id=parsed_doc.doc_id,
                document_name=parsed_doc.title,
                publisher=parsed_doc.publisher,
                year=parsed_doc.year,
                source_url=parsed_doc.source_url,
                section_heading=section.heading,
                content=final_text,
                chunk_index=chunk_index,
                token_count=count_tokens(final_text)
            ))
            chunk_index += 1
            
    return chunks

def chunk_all(parsed_dir: Path = Path("data/parsed"), output_dir: Path = Path("data/chunks")):
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for json_file in parsed_dir.glob("*.json"):
        logger.info(f"Chunking {json_file.name}...")
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            sections = [Section(**s) for s in data["sections"]]
            parsed_doc = ParsedDocument(
                doc_id=data["doc_id"],
                title=data["title"],
                publisher=data["publisher"],
                year=data["year"],
                source_url=data["source_url"],
                sections=sections
            )
            
            chunks = chunk_document(parsed_doc)
            
            out_path = output_dir / f"{parsed_doc.doc_id}_chunks.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump([c.to_dict() for c in chunks], f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved {len(chunks)} chunks to {out_path}")
        except Exception as e:
            logger.error(f"Error chunking {json_file.name}: {e}")
