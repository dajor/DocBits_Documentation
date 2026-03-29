import argparse
import os
import sys
import openai
import requests
import logging
from typing import List

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

def estimate_tokens(text):
    """Estimate token count for a given text."""
    return len(text.split()) * 1.5

def chunk_text(text, max_tokens, overlap=100):
    """
    Split text into chunks that fit within token limit.
    Tries to split at paragraph boundaries (double newlines).
    """
    chunks = []
    paragraphs = text.split('\n\n')
    current_chunk = []
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = estimate_tokens(para)
        if para_tokens > max_tokens * 0.9:
            # Paragraph itself is too large, split by lines
            lines = para.split('\n')
            temp_chunk = []
            temp_tokens = 0
            for line in lines:
                line_tokens = estimate_tokens(line)
                if temp_tokens + line_tokens > max_tokens * 0.9:
                    chunks.append('\n'.join(temp_chunk))
                    temp_chunk = [line]
                    temp_tokens = line_tokens
                else:
                    temp_chunk.append(line)
                    temp_tokens += line_tokens
            if temp_chunk:
                chunks.append('\n'.join(temp_chunk))
        elif current_tokens + para_tokens > max_tokens * 0.9:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_tokens = para_tokens
        else:
            current_chunk.append(para)
            current_tokens += para_tokens
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

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

def translate_markdown(markdown_text, target_lang, model):
    try:
    # Translate the entire markdown text
        translated_markdown = translate_text(markdown_text, target_lang, model)
    except Exception as e:
        logging.error(f"Error fetching models: {e}")
        sys.exit(1)

    return translated_markdown

def main():
    parser = argparse.ArgumentParser(description="Translate a Markdown file from English to a specified language.")
    parser.add_argument('language', nargs='?', help='Target language (e.g., "French")')
    parser.add_argument('input_file', nargs='?', help='Input Markdown file')
    parser.add_argument('output_file', nargs='?', help='Output Markdown file', default=None)
    parser.add_argument('--model', help='OpenAI model to use (default: gpt-3.5-turbo)', default='gpt-3.5-turbo')
    parser.add_argument('--list-models', action='store_true', help='List available OpenAI models and exit')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

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

    # Check if the content exceeds token limits and handle chunking
    approx_tokens = len(markdown_text.split()) * 1.5  # Approximate token count
    model_token_limits = {
        'gpt-3.5-turbo': 4096,
        'gpt-3.5-turbo-16k': 16384,
        'gpt-4': 8192,
        'gpt-4-32k': 32768,
        'gpt-4o-mini-2024-07-18': 4096,
        'gpt-4o-mini': 4096,
        'gpt-4o': 128000,
    }
    max_tokens = model_token_limits.get(args.model, 4096)

    # Use chunking for large files instead of failing
    if approx_tokens > max_tokens:
        # Auto-switch to gpt-4o (128k limit) if file exceeds 4096 tokens and we're using gpt-4o-mini
        if args.model in ['gpt-4o-mini-2024-07-18', 'gpt-4o-mini'] and approx_tokens <= 128000:
            logging.warning(f"File exceeds {args.model} limit ({approx_tokens:.0f} > {max_tokens}). Auto-switching to gpt-4o (128k limit).")
            args.model = 'gpt-4o'
            max_tokens = 128000
            logging.info(f"Using gpt-4o for large file translation.")
        
        # If still exceeds limit (or not using gpt-4o-mini), use chunking
        if approx_tokens > max_tokens:
            logging.warning(f"File exceeds token limit ({approx_tokens:.0f} > {max_tokens}). Chunking enabled.")
            chunks = chunk_text(markdown_text, max_tokens)
            logging.info(f"Split file into {len(chunks)} chunks for translation.")
            
            translated_chunks = []
            for i, chunk in enumerate(chunks, 1):
                logging.info(f"Translating chunk {i}/{len(chunks)}...")
                try:
                    translated_chunk = translate_markdown(chunk, args.language, args.model)
                    translated_chunks.append(translated_chunk)
                except Exception as e:
                    logging.error(f"Error translating chunk {i}: {e}")
                    raise
            
            # Join translated chunks
            translated_markdown = '\n\n'.join(translated_chunks)
    else:
        try:
            translated_markdown = translate_markdown(markdown_text, args.language, args.model)
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
