import re
from ftfy import fix_text
import os
import sys
from PIL import Image
import numpy as np

def batch_inference(images, model, processor, temperature=0.0, max_tokens=384):
    try:
        images = [image.convert("RGB") for image in images]
        encodings = processor(images=images, return_tensors="pt", add_special_tokens=False)
        pixel_values = encodings["pixel_values"].to(model.dtype)
        pixel_values = pixel_values.to(model.device)
        additional_kwargs = {}
        if temperature > 0:
            additional_kwargs["temperature"] = temperature
            additional_kwargs["do_sample"] = True
            additional_kwargs["top_p"] = 0.95
        generated_ids = model.generate(
            pixel_values=pixel_values,
            max_new_tokens=max_tokens,
            decoder_start_token_id=processor.tokenizer.bos_token_id,
            **additional_kwargs,
        )
        generated_text = processor.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        generated_text = [postprocess(text) for text in generated_text]
    except Exception as e:
        print('推理错误')
        print(e)
    return generated_text

def remove_labels(text):
    pattern = r'\\label\{[^}]*\}'
    text = re.sub(pattern, '', text)
    ref_pattern = r'\\ref\{[^}]*\}'
    text = re.sub(ref_pattern, '', text)
    pageref_pattern = r'\\pageref\{[^}]*\}'
    text = re.sub(pageref_pattern, '', text)
    return text

def postprocess(text):
    text = fix_text(text)
    text = remove_labels(text)
    pattern = r'(?<!\\)\$'
    text = re.sub(pattern, '', text)
    return text
