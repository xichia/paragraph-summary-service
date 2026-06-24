from __future__ import annotations

import argparse
import json

from paragraph_summary_service.config.settings import get_settings
from paragraph_summary_service.models.requests import ParagraphSummaryRequest
from paragraph_summary_service.services.paragraph_summarise import ParagraphSummaryService


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate paragraph summary artifacts.")
    parser.add_argument("request_json", help="Path to a ParagraphSummaryRequest JSON file")
    args = parser.parse_args()
    with open(args.request_json, encoding="utf-8") as handle:
        request = ParagraphSummaryRequest.model_validate(json.load(handle))
    result = ParagraphSummaryService(get_settings()).summarise_request(request)
    print(result.response.model_dump_json(indent=2))
