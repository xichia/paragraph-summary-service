from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from paragraph_summary_service.cache.keys import sha256_text
from paragraph_summary_service.models.domain import ParagraphRecord

ATX_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


@dataclass(frozen=True)
class SplitBlock:
    text: str
    line_start: int
    line_end: int
    heading_path: list[str]


def split_uploaded_text(
    *,
    filename: str,
    content: str,
    content_type: str = "text/plain",
) -> tuple[str, list[ParagraphRecord]]:
    suffix = Path(filename).suffix.lower()
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    file_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    document_id = f"upload_{file_hash[:12]}"
    if suffix == ".md":
        blocks = _split_markdown(normalized)
        splitter_version = "lightweight_md_v1"
    else:
        blocks = _split_plain_text(normalized)
        splitter_version = "lightweight_txt_v1"
    records: list[ParagraphRecord] = []
    for idx, block in enumerate(blocks, start=1):
        text_hash = sha256_text(block.text).split(":", 1)[1]
        record_id = f"standalone/{document_id}/para_{idx:06d}_{text_hash[:8]}"
        heading = " > ".join(block.heading_path)
        source_ref = f"{heading}, paragraph {idx}" if heading else f"paragraph {idx}"
        records.append(
            ParagraphRecord(
                document_id=document_id,
                record_id=record_id,
                source_ref=source_ref,
                text=block.text,
                checksum=f"sha256:{text_hash}",
                provenance="llm_summariser_lightweight_splitter",
                metadata={
                    "filename": filename,
                    "content_type": content_type,
                    "line_start": block.line_start,
                    "line_end": block.line_end,
                    "heading_path": block.heading_path,
                    "splitter_version": splitter_version,
                },
            )
        )
    return document_id, records


def _split_plain_text(content: str) -> list[SplitBlock]:
    lines = content.split("\n")
    blocks: list[SplitBlock] = []
    buffer: list[str] = []
    start_line = 1
    for lineno, line in enumerate(lines, start=1):
        if line.strip():
            if not buffer:
                start_line = lineno
            buffer.append(line.strip())
        elif buffer:
            text = " ".join(buffer).strip()
            if text:
                blocks.append(
                    SplitBlock(
                        text=text,
                        line_start=start_line,
                        line_end=lineno - 1,
                        heading_path=[],
                    )
                )
            buffer = []
    if buffer:
        text = " ".join(buffer).strip()
        blocks.append(
            SplitBlock(
                text=text,
                line_start=start_line,
                line_end=len(lines),
                heading_path=[],
            )
        )
    return blocks


def _split_markdown(content: str) -> list[SplitBlock]:
    lines = content.split("\n")
    blocks: list[SplitBlock] = []
    heading_stack: list[str] = []
    buffer: list[str] = []
    start_line = 1
    in_code_fence = False

    def flush(end_line: int) -> None:
        nonlocal buffer, start_line
        if buffer:
            text = " ".join(line.strip() for line in buffer).strip()
            if text:
                blocks.append(
                    SplitBlock(
                        text=text,
                        line_start=start_line,
                        line_end=end_line,
                        heading_path=list(heading_stack),
                    )
                )
            buffer = []

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            flush(lineno - 1)
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        heading = ATX_HEADING_RE.match(stripped)
        if heading:
            flush(lineno - 1)
            level = len(heading.group(1))
            title = heading.group(2).strip()
            heading_stack = heading_stack[: level - 1]
            heading_stack.append(title)
            continue
        if stripped:
            if not buffer:
                start_line = lineno
            buffer.append(stripped)
        else:
            flush(lineno - 1)
    flush(len(lines))
    return blocks
