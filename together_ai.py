import requests
import logging
import json

logger = logging.getLogger('terminusa_logger')

TOGETHER_API_URL = "https://api.together.xyz/v1/completions"

def generate_text(api_key, prompt, model="mistralai/Mixtral-8x7B-Instruct-v0.1", max_tokens=1000, temperature=0.7):
    """
    Generate text using Together AI API.
    
    Args:
        api_key (str): Together AI API key
        prompt (str): The prompt text
        model (str): Model name to use
        max_tokens (int): Maximum tokens to generate
        temperature (float): Sampling temperature
    
    Returns:
        str: Generated text or None if error
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    try:
        logger.info("Sending request to Together AI API...")
        response = requests.post(TOGETHER_API_URL, headers=headers, data=json.dumps(data), timeout=30)
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("choices", [{}])[0].get("text", "")
            logger.info("Received response from Together AI API.")
            return generated_text.strip()
        else:
            logger.error(f"Together AI API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception calling Together AI API: {e}")
        return None
