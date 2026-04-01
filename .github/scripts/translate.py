import re
import sys
import os
import urllib.request
import urllib.parse
import json
from pathlib import Path

DEEPL_API_KEY = os.environ.get('DEEPL_API_KEY', '').strip()

# 顔文字を見つける強力なパターン
KAOMOJI_PATTERN = re.compile(r'[|｜]?[（(][^a-zA-Z0-9\s]{1,15}[）)][ﾉ┐]?["\'`]*|[|｜][ω∀дﾟ][^a-zA-Z0-9\s]{0,5}[）)]')

def translate(text):
    if not text: return ""
    api_url = 'https://api-free.deepl.com/v2/translate' if DEEPL_API_KEY.endswith(':fx') else 'https://api.deepl.com/v2/translate'

    # 【新戦略】タグを使わず、一度顔文字を __K0__ のような記号に置き換えて避難させる
    placeholders = []
    def substitute(match):
        ph = f" __K{len(placeholders)}__ "
        placeholders.append(match.group(0))
        return ph

    protected_text = KAOMOJI_PATTERN.sub(substitute, text)

    # 翻訳実行
    params = {
        'text': protected_text,
        'source_lang': 'JA',
        'target_lang': 'EN-US',
    }
    
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(api_url, data=data, headers={'Authorization': f'DeepL-Auth-Key {DEEPL_API_KEY}'})
    
    try:
        with urllib.request.urlopen(req) as res:
            result = json.loads(res.read())['translations'][0]['text']
            
            # 避難させていた顔文字を順番に戻す
            for i, original in enumerate(placeholders):
                result = result.replace(f"__K{i}__", original).replace(f"__k{i}__", original)
            return result
    except Exception as e:
        print(f"Error: {e}")
        return text

def process_file(ja_path):
    p = Path(ja_path)
    if not p.exists(): return
    content = p.read_text(encoding='utf-8')
    if not content.startswith('---'): return
    
    parts = content.split('---', 2)
    fm, body = parts[1], parts[2].strip()
    
    # タイトル
    title_match = re.search(r'title:\s*"(.+)"', fm)
    if title_match:
        ja_title = title_match.group(1)
        en_title = translate(ja_title)
        fm = fm.replace(f'title: "{ja_title}"', f'title: "{en_title}"')
    
    # 本文
    en_body = translate(body)
    
    en_path = Path('content/en/posts') / p.name
    en_path.parent.mkdir(parents=True, exist_ok=True)
    en_path.write_text(f'---{fm}---\n\n{en_body}\n', encoding='utf-8')
    print(f'✓ {en_path}')

if __name__ == "__main__":
    for filepath in sys.argv[1:]:
        process_file(filepath)