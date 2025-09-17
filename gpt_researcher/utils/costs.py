import tiktoken

# Per OpenAI Pricing Page: https://openai.com/api/pricing/
ENCODING_MODEL = "cl100k_base"  # More widely available encoding
INPUT_COST_PER_TOKEN = 0.000005
OUTPUT_COST_PER_TOKEN = 0.000015
IMAGE_INFERENCE_COST = 0.003825
EMBEDDING_COST = 0.02 / 1000000 # Assumes new ada-3-small


# Cost estimation is via OpenAI libraries and models. May vary for other models
def estimate_llm_cost(input_content: str, output_content: str) -> float:
    # Safety check to prevent NoneType errors
    if input_content is None:
        input_content = ""
    if output_content is None:
        output_content = ""
    
    try:
        encoding = tiktoken.get_encoding(ENCODING_MODEL)
    except (KeyError, ValueError):
        # Fallback to a more basic encoding if specific encoding is not available
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
        except (KeyError, ValueError):
            # Final fallback to gpt2 encoding which should always be available
            try:
                encoding = tiktoken.get_encoding("gpt2")
            except (KeyError, ValueError):
                # If no encoding is available, return a basic estimate
                # Rough estimate: ~4 chars per token
                input_tokens_approx = len(str(input_content)) // 4
                output_tokens_approx = len(str(output_content)) // 4
                input_costs = input_tokens_approx * INPUT_COST_PER_TOKEN
                output_costs = output_tokens_approx * OUTPUT_COST_PER_TOKEN
                return input_costs + output_costs
    
    input_tokens = encoding.encode(str(input_content))
    output_tokens = encoding.encode(str(output_content))
    input_costs = len(input_tokens) * INPUT_COST_PER_TOKEN
    output_costs = len(output_tokens) * OUTPUT_COST_PER_TOKEN
    return input_costs + output_costs


def estimate_embedding_cost(model, docs):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except (KeyError, ValueError):
        # Fallback to a more basic encoding
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
        except (KeyError, ValueError):
            try:
                encoding = tiktoken.get_encoding("gpt2")
            except (KeyError, ValueError):
                # If no encoding is available, return a basic estimate
                # Rough estimate: ~4 chars per token
                total_chars = sum(len(str(doc if doc is not None else "")) for doc in docs)
                total_tokens = total_chars // 4
                return total_tokens * EMBEDDING_COST
    
    total_tokens = sum(len(encoding.encode(str(doc if doc is not None else ""))) for doc in docs)
    return total_tokens * EMBEDDING_COST

