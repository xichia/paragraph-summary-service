from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    template_id: str
    version: str
    summary_style: str
    system_instruction: str
    user_template: str
    expected_output_format: str


TEMPLATES: dict[str, PromptTemplate] = {
    "paragraph_sentence_batch_v1": PromptTemplate(
        template_id="paragraph_sentence_batch_v1",
        version="v1",
        summary_style="paragraph_sentence",
        system_instruction=(
            "You summarise source paragraphs for retrieval enhancement. Return only valid JSON. "
            "Do not add facts not present in the paragraph. Preserve every record_id."
        ),
        user_template=(
            "For each record, write exactly one sentence that captures the paragraph's main claim, "
            "function, or important information. Do not merge records. Return JSON with a "
            "'summaries' array containing record_id, summary, and status.\n\n"
            "Records:\n{records_json}"
        ),
        expected_output_format=(
            '{"summaries":[{"record_id":"...","summary":"one sentence","status":"completed"}]}'
        ),
    ),
}


def get_template(template_id: str) -> PromptTemplate:
    try:
        return TEMPLATES[template_id]
    except KeyError as exc:
        raise KeyError(f"unknown prompt template: {template_id}") from exc
