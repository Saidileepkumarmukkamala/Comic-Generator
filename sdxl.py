import requests
import json
import requests
import base64
import uuid
from PIL import Image
import io
import re
import streamlit as st


def save_image_from_asset_url(asset_url):
    base64_data = re.sub('^data:image/.+;base64,', '', asset_url)
    image_data = base64.b64decode(base64_data)
    image = Image.open(io.BytesIO(image_data))
    #image.save(save_path, 'PNG')
    return image



def fetch_data_from_hf(prompt, model):
    url = f"https://api-inference.huggingface.co/models/{model}"

    headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer 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"
            }
    
    body = json.dumps({
        "inputs": ", ".join([
            "beautiful",
            "intricate details",
            "high quality",
            "high resolution",
            "colorful",
            "Long shot",
            "comic book art of",
            str(prompt),
            "precise ink lineart", 
            "hyper detailed", 
            "octane render", 
            "high contrast",
            "graphic novel",
            "illustration",
        ]),
        "parameters": {
            "num_inference_steps": 25,
            "guidance_scale": 8,
            "width": 1024,
            "height": 1024,
        }
    })

    res = requests.post(url, headers=headers, data=json.dumps(body))
    
    if res.status_code != 200:
        raise ConnectionError("Failed to fetch data from Hugging Face API. "
                              f"Status Code: {res.status_code}, Response: {res.text}")
    
    return res.content, res.headers.get('content-type')