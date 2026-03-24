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

# Default chunk size (tokens) - safe margin below model limits
DEFAULT_CHUNK_SIZE = 3500

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

def split_into_chunks(text: str, chunk_size: int) -> List[str]:
    """
    Split markdown text into chunks that respect markdown structure.
    Splits at heading boundaries (lines starting with #) when possible.
    
    Parameters:
        text: The markdown text to split
        chunk_size: Maximum approximate tokens per chunk
    
    Returns:
        List of text chunks
    """
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_words = 0
    max_words = int(chunk_size / 1.5)  # Convert tokens to words
    
    for line in lines:
        line_words = len(line.split())
        
        # Check if this is a heading line (potential split point)
        is_heading = line.strip().startswith('#')
        
        if is_heading and current_words > 0:
            # Start new chunk at heading
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_words = line_words
        elif current_words + line_words > max_words and current_words > 0:
            # Force split if we exceed limit
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_words = line_words
        else:
            current_chunk.append(line)
            current_words += line_words
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
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
    if model in ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4', 'gpt-4-32k']:  # Models that support 'system' role
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

def translate_markdown(markdown_text, target_lang, model, chunk_size: int = None):
    """
    Translate markdown text, automatically chunking if it exceeds model limits.
    
    Parameters:
        markdown_text: The markdown content to translate
        target_lang: Target language
        model: OpenAI model to use
        chunk_size: Optional chunk size in tokens (uses model limit if not specified)
    
    Returns:
        Translated markdown text
    """
    try:
        # Determine chunk size based on model if not specified
        if chunk_size is None:
            model_token_limits = {
                'gpt-3.5-turbo': 4096,
                'gpt-3.5-turbo-16k': 16384,
                'gpt-4': 8192,
                'gpt-4-32k': 32768,
                'gpt-4o-mini': 4096,
                'gpt-4o': 128000,
            }
            max_tokens = model_token_limits.get(model, 4096)
            chunk_size = min(max_tokens - 500, DEFAULT_CHUNK_SIZE)  # Leave margin
        
        approx_tokens = len(markdown_text.split()) * 1.5
        
        if approx_tokens <= chunk_size:
            # File fits in single chunk
            logging.info(f"Translating file as single chunk ({approx_tokens:.0f} tokens)")
            translated_markdown = translate_text(markdown_text, target_lang, model)
        else:
            # Split into chunks and translate separately
            logging.info(f"File too large ({approx_tokens:.0f} tokens), splitting into chunks of ~{chunk_size} tokens")
            chunks = split_into_chunks(markdown_text, chunk_size)
            logging.info(f"Split into {len(chunks)} chunks")
            
            translated_chunks = []
            for i, chunk in enumerate(chunks, 1):
                chunk_tokens = len(chunk.split()) * 1.5
                logging.info(f"Translating chunk {i}/{len(chunks)} ({chunk_tokens:.0f} tokens)")
                translated_chunk = translate_text(chunk, target_lang, model)
                translated_chunks.append(translated_chunk)
            
            # Join translated chunks
            translated_markdown = '\n\n'.join(translated_chunks)
            
    except Exception as e:
        logging.error(f"Error during translation: {e}")
        raise

    return translated_markdown

def main():
    parser = argparse.ArgumentParser(description="Translate a Markdown file from English to a specified language.")
    parser.add_argument('language', nargs='?', help='Target language (e.g., "French")')
    parser.add_argument('input_file', nargs='?', help='Input Markdown file')
    parser.add_argument('output_file', nargs='?', help='Output Markdown file', default=None)
    parser.add_argument('--model', help='OpenAI model to use (default: gpt-3.5-turbo)', default='gpt-3.5-turbo')
    parser.add_argument('--list-models', action='store_true', help='List available OpenAI models and exit')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--chunk-size', type=int, help='Override chunk size in tokens (default: auto based on model)', default=None)

    args = parser.parse_args()

    if args.list_models:
        list_available_models()
        return


    # Set up logging based on '--debug' argument
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    if args.list_models:
        list_available_models()
        sys.exit(0)

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
        translated_markdown = translate_markdown(markdown_text, args.language, args.model, chunk_size=args.chunk_size)
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
        # Add other models as needed
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
