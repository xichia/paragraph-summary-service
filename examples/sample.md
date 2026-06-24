# Safety Model

The service must not log raw source text. It should use hashes, record IDs, provider names, model names, and timing metadata instead.

## Retrieval Enhancement

One-sentence paragraph summaries help retrieval systems match conceptual queries against dense or technical source paragraphs.

The original paragraph remains the evidence to cite, while the summary acts as an additional search signal.
