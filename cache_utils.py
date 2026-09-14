import json
import os

def load_cache(cache_file):
    if not os.path.exists(cache_file):
        return {}
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def save_cache(cache, cache_file):
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def make_cache_key(text):
    return ' '.join(
        str(text)
        .lower()
        .replace(',', ' ')
        .split()
    )