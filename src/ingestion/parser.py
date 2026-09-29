import json
import logging
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional

from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import pdfplumber

logger = logging.getLogger(__name__)

@dataclass
class Section:
    heading: str
    content: str
    section_type: str  # "prose" | "table" | "list"

@dataclass
class ParsedDocument:
    doc_id: str
    title: str
    publisher: str
    year: int
    source_url: str
    sections: List[Section]

    def to_dict(self) -> dict:
        return asdict(self)

    def save_to_json(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


def parse_html(file_path: Path, metadata: Dict[str, Any]) -> ParsedDocument:
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    # Strip boilerplates
    for tag in soup(["nav", "footer", "header", "aside", "script", "style", "noscript"]):
        tag.decompose()

    # Remove elements that are likely cookie banners or sidebars
    for tag in soup.find_all(class_=re.compile(r"cookie|banner|sidebar|nav|menu", re.I)):
        if tag.name not in ["body", "html", "main", "article"]:
            tag.decompose()

    sections: List[Section] = []
    heading_stack = {0: metadata.get("title", "Introduction")}
    def get_breadcrumb():
        return " > ".join([heading_stack[k] for k in sorted(heading_stack.keys())])
        
    current_heading = get_breadcrumb()
    current_content = []
    current_type = "prose"
    
    body = soup.body if soup.body else soup

    def flush_section():
        nonlocal current_content, current_heading, current_type, sections
        text = "\n".join(current_content).strip()
        if text:
            sections.append(Section(heading=current_heading, content=text, section_type=current_type))
        current_content = []
        current_type = "prose"

    for element in body.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "table"]):
        # skip if this element is nested inside a table or list to avoid duplicates
        if element.find_parent(["table", "ul", "ol"]):
            continue
            
        if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            flush_section()
            level = int(element.name[1])
            text = element.get_text(strip=True)
            if text:
                heading_stack[level] = text
                keys_to_delete = [k for k in heading_stack.keys() if k > level]
                for k in keys_to_delete:
                    del heading_stack[k]
                current_heading = get_breadcrumb()
            current_type = "prose"
        elif element.name == "p":
            text = element.get_text(separator=" ", strip=True)
            if text:
                current_content.append(text)
        elif element.name in ["ul", "ol"]:
            flush_section()
            items = []
            for li in element.find_all("li"):
                items.append("- " + li.get_text(separator=" ", strip=True))
            if items:
                sections.append(Section(heading=current_heading, content="\n".join(items), section_type="list"))
        elif element.name == "table":
            flush_section()
            rows = []
            for tr in element.find_all("tr"):
                cells = [td.get_text(separator=" ", strip=True) for td in tr.find_all(["td", "th"])]
                if any(cells):
                    rows.append(" | ".join(cells))
            if rows:
                sections.append(Section(heading=current_heading, content="\n".join(rows), section_type="table"))
                
    flush_section()

    return ParsedDocument(
        doc_id=metadata["doc_id"],
        title=metadata["title"],
        publisher=metadata["publisher"],
        year=int(metadata.get("year", 2024)),
        source_url=metadata["source_url"],
        sections=sections
    )


def parse_pdf(file_path: Path, metadata: Dict[str, Any]) -> ParsedDocument:
    sections: List[Section] = []
    
    doc_title = metadata.get("title", "Introduction")
    current_heading = doc_title
    current_content = []
    
    def flush_section():
        nonlocal current_content, current_heading, sections
        text = "\n".join(current_content).strip()
        if text:
            sections.append(Section(heading=current_heading, content=text, section_type="prose"))
        current_content = []

    try:
        doc = fitz.open(file_path)
    except Exception as e:
        logger.error(f"Failed to open PDF {file_path}: {e}")
        raise e

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 1. Extract text blocks using PyMuPDF
        blocks = page.get_text("dict").get("blocks", [])
        for b in blocks:
            if b.get("type") == 0:  # text block
                text = ""
                is_bold = False
                max_size = 0
                for l in b.get("lines", []):
                    for s in l.get("spans", []):
                        text += s.get("text", "") + " "
                        if s.get("size", 0) > max_size:
                            max_size = s.get("size", 0)
                        if "bold" in s.get("font", "").lower() or "black" in s.get("font", "").lower():
                            is_bold = True
                
                text = text.strip()
                if not text:
                    continue
                    
                # Heuristic for heading: large font size or bold, relatively short
                if (max_size > 12 or is_bold) and len(text) < 100 and not text.endswith("."):
                    flush_section()
                    if text != doc_title:
                        current_heading = f"{doc_title} > {text}"
                else:
                    # check if it looks like a list
                    if text.startswith("•") or text.startswith("- ") or re.match(r"^\d+\.", text):
                        flush_section()
                        sections.append(Section(heading=current_heading, content=text, section_type="list"))
                    else:
                        current_content.append(text)

        flush_section()
        
        # 2. Extract tables for this page using pdfplumber
        try:
            with pdfplumber.open(file_path) as pdf:
                if page_num < len(pdf.pages):
                    p_page = pdf.pages[page_num]
                    tables = p_page.extract_tables()
                    for table in tables:
                        rows = []
                        for row in table:
                            clean_row = [str(cell).strip().replace("\n", " ") if cell else "" for cell in row]
                            if any(clean_row):
                                rows.append(" | ".join(clean_row))
                        if rows:
                            sections.append(Section(
                                heading=f"{current_heading} - Table", 
                                content="\n".join(rows), 
                                section_type="table"
                            ))
        except Exception as e:
            logger.warning(f"Error extracting tables on page {page_num} of {file_path}: {e}")

    return ParsedDocument(
        doc_id=metadata["doc_id"],
        title=metadata["title"],
        publisher=metadata["publisher"],
        year=int(metadata.get("year", 2024)),
        source_url=metadata["source_url"],
        sections=sections
    )

def parse_document(file_path: Path, metadata: Dict[str, Any]) -> ParsedDocument:
    """Parses a document based on its extension."""
    ext = file_path.suffix.lower()
    if ext in [".html", ".htm"]:
        return parse_html(file_path, metadata)
    elif ext == ".pdf":
        return parse_pdf(file_path, metadata)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def parse_all(registry_path: Path = Path("data/corpus_registry.json"), output_dir: Path = Path("data/parsed")):
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)
    
    output_dir.mkdir(parents=True, exist_ok=True)

    for doc_meta in registry.get("documents", []):
        doc_id = doc_meta["doc_id"]
        local_path = Path(doc_meta["local_path"])
        
        if not local_path.exists():
            logger.warning(f"File not found for {doc_id}: {local_path}")
            continue
            
        logger.info(f"Parsing {doc_id}...")
        try:
            parsed_doc = parse_document(local_path, doc_meta)
            out_path = output_dir / f"{doc_id}.json"
            parsed_doc.save_to_json(out_path)
            logger.info(f"Saved parsed document to {out_path}")
        except Exception as e:
            logger.error(f"Error parsing {doc_id}: {e}")

