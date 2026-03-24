import argparse
import os
import sys
import openai
import requests
import logging
from typing import List, Tuple

# Initialize total_tokens_used
total_tokens_used = 0

import re

def remove_markdown_code_blocks(text):
    """
    Entfernt ```markdown am Anfang und ``` am Ende des Textes, falls vorhanden.
    
    Parameters:
        text (str): Der zu bereinigende Text.
    
    Returns:
        str: Der bereinigte Text ohne die spezifischen Markdown-Codeblöcke.
    """
    # Entfernt ```markdown am Anfang
    text = re.sub(r'^```markdown\s*\n?', '', text)
    # Entfernt ``` am Ende
    text = re.sub(r'\n?```$', '', text)
    return text.strip()

def count_tokens_approximate(text: str) -> int:
    """
    Approximate token count for a text string.
    Uses a simple heuristic: ~1 token per 4 characters or ~1.5 tokens per word.
    """
    words = len(text.split())
    return int(words * 1.5)

def split_markdown_into_chunks(text: str, max_tokens: int = 3500) -> List[str]:
    """
    Split markdown content into chunks that fit within the token limit.
    Preserves markdown structure by splitting on headings where possible.
    
    Args:
        text: The markdown content to split
        max_tokens: Maximum tokens per chunk (default 3500 to stay under 4k limit)
    
    Returns:
        List of text chunks, each under max_tokens
    """
    chunks = []
    lines = text.split('\n')
    
    current_chunk = []
    current_tokens = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        line_tokens = count_tokens_approximate(line)
        
        # Check if adding this line would exceed the limit
        if current_tokens + line_tokens > max_tokens and current_chunk:
            # Save current chunk and start new one
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
            current_tokens = 0
        
        # Special handling for headings - try to start new chunk at heading
        if line.strip().startswith('#') and current_chunk:
            # If we're at a heading and have content, this is a good split point
            if current_tokens + line_tokens > max_tokens * 0.7:  # If chunk is getting large
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_tokens = 0
        
        current_chunk.append(line)
        current_tokens += line_tokens
        i += 1
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    logging.info(f"Split content into {len(chunks)} chunks")
    for idx, chunk in enumerate(chunks):
        logging.info(f"  Chunk {idx + 1}: ~{count_tokens_approximate(chunk)} tokens")
    
    return chunks

def list_available_models():
    # Set up your OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("Error: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    try:
        response = requests.get("https://api.openai.com/v1/models", headers=headers)
        response.raise_for_status()
        models = response.json()["data"]
        model_ids = [model['id'] for model in models]
        print("Available models:")
        for model_id in model_ids:
            print(f"- {model_id}")
    except Exception as e:
        logging.error(f"Error fetching models: {e}")
        sys.exit(1)

def translate_text(text, target_lang, model):
    # Set up your OpenAI API key
    openai.api_key = os.getenv("OPENAI_API_KEY")

    logging.debug(f"Translating text with length {len(text)} characters.")

    # Define the prompt with explicit instructions
    prompt = f"""
You are a professional translator specializing in software documentation.

Translate the following English Markdown text to {target_lang}.

- Preserve all Markdown formatting, including headings, lists, links, code blocks, inline code, HTML tags, and embedded syntax.
- Do not translate or alter code blocks, inline code, HTML tags, URLs, or embedded syntax
- Only translate the human-readable text content.
- Ensure that the translated text aligns with the original formatting and structure.

Text to translate:
```markdown
{text}

"""

    # Prepare messages based on model capabilities
    messages = []
    if model in ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4', 'gpt-4-32k', 'gpt-4o', 'gpt-4o-mini']:  # Models that support 'system' role
        messages.append({"role": "system", "content": "You are a helpful assistant that translates English Markdown documents to other languages while preserving formatting and not altering code or special syntax."})
        messages.append({"role": "user", "content": prompt})
    else:
        # For models that do not support 'system' role
        messages.append({"role": "user", "content": prompt})

    try:
        # Set parameters based on model capabilities
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.2
        )
        logging.debug(f"Received response: {response}")
    except openai.error.OpenAIError as e:
        # Catch all OpenAI-related errors
        logging.error(f"OpenAI API error: {e}")
        raise
    except Exception as e:
        logging.error(f"Error fetching models: {e}")
        sys.exit(1)

    translated_text = response.choices[0].message.content.strip()

    # Update total tokens used
    global total_tokens_used
    if 'usage' in response:
        total_tokens_used += response['usage']['total_tokens']
    else:
        logging.warning("Token usage information not available in the response.")

    return translated_text

def translate_markdown(markdown_text, target_lang, model):
    try:
    # Translate the entire markdown text
        translated_markdown = translate_text(markdown_text, target_lang, model)
    except Exception as e:
        logging.error(f"Error fetching models: {e}")
        sys.exit(1)

    return translated_markdown

def translate_markdown_with_chunking(markdown_text, target_lang, model, max_tokens_per_chunk=3500):
    """
    Translate markdown content by splitting into chunks if it exceeds token limit.
    
    Args:
        markdown_text: The full markdown content
        target_lang: Target language
        model: OpenAI model to use
        max_tokens_per_chunk: Maximum tokens per chunk
    
    Returns:
        Translated markdown content
    """
    approx_tokens = count_tokens_approximate(markdown_text)
    model_token_limits = {
        'gpt-3.5-turbo': 4096,
        'gpt-3.5-turbo-16k': 16384,
        'gpt-4': 8192,
        'gpt-4-32k': 32768,
        'gpt-4o': 128000,
        'gpt-4o-mini': 4096,
    }
    max_tokens = model_token_limits.get(model, 4096)
    
    if approx_tokens <= max_tokens:
        logging.info(f"Content fits within token limit ({approx_tokens} <= {max_tokens}), translating directly")
        return translate_markdown(markdown_text, target_lang, model)
    
    logging.warning(f"Content exceeds token limit ({approx_tokens} > {max_tokens}), using chunking")
    
    # Split into chunks
    chunks = split_markdown_into_chunks(markdown_text, max_tokens_per_chunk)
    
    # Translate each chunk
    translated_chunks = []
    for idx, chunk in enumerate(chunks):
        logging.info(f"Translating chunk {idx + 1}/{len(chunks)}...")
        translated_chunk = translate_text(chunk, target_lang, model)
        translated_chunk = remove_markdown_code_blocks(translated_chunk)
        translated_chunks.append(translated_chunk)
    
    # Reassemble
    result = '\n\n'.join(translated_chunks)
    logging.info(f"Successfully translated {len(chunks)} chunks")
    
    return result

def main():
    parser = argparse.ArgumentParser(description="Translate a Markdown file from English to a specified language.")
    parser.add_argument('language', nargs='?', help='Target language (e.g., "French")')
    parser.add_argument('input_file', nargs='?', help='Input Markdown file')
    parser.add_argument('output_file', nargs='?', help='Output Markdown file', default=None)
    parser.add_argument('--model', help='OpenAI model to use (default: gpt-4o-mini)', default='gpt-4o-mini')
    parser.add_argument('--list-models', action='store_true', help='List available OpenAI models and exit')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--no-chunking', action='store_true', help='Disable automatic chunking for large files')

    args = parser.parse_args()

    if args.list_models:
        list_available_models()
        return


    # Set up logging based on '--debug' argument
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    if not args.language or not args.input_file:
        parser.print_help()
        sys.exit(1)

    if not os.getenv("OPENAI_API_KEY"):
        logging.error("Error: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    logging.info("Starting translation process...")

    with open(args.input_file, 'r', encoding='utf-8') as f:
        markdown_text = f.read()

    try:
        if args.no_chunking:
            translated_markdown = translate_markdown(markdown_text, args.language, args.model)
        else:
            translated_markdown = translate_markdown_with_chunking(markdown_text, args.language, args.model)
    except Exception as e:
        logging.error(f"An error occurred during translation:\n\n{e}")
        sys.exit(1)

    logging.info("Translation process completed.")

    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            # Entfernen von ```markdown und ``` nur am Anfang und Ende des übersetzten Textes
            translated_markdown = remove_markdown_code_blocks(translated_markdown)  
            f.write(translated_markdown)
        logging.info(f"Translated markdown saved to {args.output_file}")
    else:
        print(translated_markdown)

    # Print total tokens used and estimated cost
    global total_tokens_used
    logging.info(f"Total tokens used: {total_tokens_used}")

    # Estimate cost
    # Define pricing per 1000 tokens for different models (in USD)
    pricing = {
        'gpt-3.5-turbo': 0.0015,          # $0.0015 per 1K tokens
        'gpt-3.5-turbo-16k': 0.003,       # $0.003 per 1K tokens
        'gpt-4': 0.03,                    # $0.03 per 1K tokens
        'gpt-4-32k': 0.06,                # $0.06 per 1K tokens
        'gpt-4o': 0.005,                  # $0.005 per 1K tokens
        'gpt-4o-mini': 0.00015,           # $0.00015 per 1K tokens
    }

    # Determine price per 1K tokens
    model_price_per_1k = pricing.get(args.model, 0.002)  # Default to $0.002 per 1K tokens

    # Calculate cost in USD
    cost_usd = (total_tokens_used / 1000) * model_price_per_1k

    # Convert USD to Euro (assuming 1 USD = 0.85 Euro, adjust as needed)
    usd_to_eur = 0.85
    cost_eur = cost_usd * usd_to_eur

    logging.info(f"Estimated cost: ${cost_usd:.4f} USD ({cost_eur:.4f} EUR)")
        

if __name__ == '__main__':
    main()
