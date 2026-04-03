import re
import sys
import os
import urllib.request
import urllib.parse
import json
from pathlib import Path

DEEPL_API_KEY = os.environ.get('DEEPL_API_KEY', '').strip()

# 【数式・記号共存ルール】
# 1. 顔文字によく使われる特殊記号（ω, Д, ﾟ, ∀ など）を含む塊
# 2. または、通常の記号が3文字以上連続している塊（例: (^^) や (T_T) ）
# これらを「顔文字」と判定し、単発の + や = はスルーします。
KAOMOJI_PATTERN = re.compile(
    r'[|｜]?[（(][^a-zA-Z0-9\sぁ-んァ-ヶ亜-熙]{1,15}[）)][ﾉ┐]?["\'`]*|'
    r'[^a-zA-Z0-9\sぁ-んァ-ヶ亜-熙]*[ω∀дﾟ；;･・ー≡*＊][^a-zA-Z0-9\sぁ-んァ-ヶ亜-熙]*|'
    r'[^a-zA-Z0-9\sぁ-んァ-ヶ亜-熙]{3,}'
)

def translate(text):
    if not text: return ""
    api_url = 'https://api-free.deepl.com/v2/translate' if DEEPL_API_KEY.endswith(':fx') else 'https://api.deepl.com/v2/translate'

    placeholders = []
    def substitute(match):
        # 記号の塊を __K0__ のような目印に置き換える
        ph = f" __K{len(placeholders)}__ "
        placeholders.append(match.group(0))
        return ph

    # 翻訳前に記号を避難
    protected_text = KAOMOJI_PATTERN.sub(substitute, text)

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
            
            # 避難させていた記号を元に戻す（小文字に変換された場合も考慮）
            for i, original in enumerate(placeholders):
                result = result.replace(f"__K{i}__", original).replace(f"__k{i}__", original)
            
            # 余計な空白を整えて返す
            return result.replace("  ", " ").strip()
    except Exception as e:
        print(f"Error: {e}")
        return text

def process_file(ja_path):
    p = Path(ja_path)
    if not p.is_file(): return
    
    try:
        content = p.read_text(encoding='utf-8')
        if not content.startswith('---'): return
        
        # Front Matterを安全に分割
        parts = content.split('---')
        if len(parts) < 3: return
        
        fm = parts[1]
        body = '---'.join(parts[2:]).strip()
        
        # タイトル
        title_match = re.search(r'title:\s*"(.+)"', fm)
        if title_match:
            ja_title = title_match.group(1)
            en_title = translate(ja_title)
            fm = re.sub(r'(title:\s*").+(")', rf'\1{en_title}\2', fm)
        
        # 本文
        en_body = translate(body)
        
        en_path = Path('content/en/posts') / p.name
        en_path.parent.mkdir(parents=True, exist_ok=True)
        en_path.write_text(f'---{fm}---\n\n{en_body}\n', encoding='utf-8')
        print(f'✓ {en_path}')
    except Exception as e:
        print(f"Error processing {ja_path}: {e}")

if __name__ == "__main__":
    for filepath in sys.argv[1:]:
        process_file(filepath)