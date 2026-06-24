from paragraph_summary_service.models.domain import Usage

PROVIDER_COST_PER_1K_TOKENS: dict[tuple[str, str], tuple[float, float]] = {
    ("mock", "mock-deterministic-v1"): (0.0, 0.0),
}


def estimate_cost(provider: str, model: str, input_tokens: int, output_tokens: int) -> Usage:
    input_price, output_price = PROVIDER_COST_PER_1K_TOKENS.get((provider, model), (0.0, 0.0))
    cost = (input_tokens / 1000.0 * input_price) + (output_tokens / 1000.0 * output_price)
    return Usage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        estimated_cost_usd=round(cost, 8),
    )
