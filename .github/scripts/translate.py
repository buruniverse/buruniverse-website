import re
import sys
import os
import urllib.request
import urllib.parse
import json
from pathlib import Path

# 環境変数からAPIキーを取得
DEEPL_API_KEY = os.environ['DEEPL_API_KEY'].strip()

# 【鉄壁ガード Ver.2】
# 顔文字のパターンを強化： | で始まるもの、腕（ﾉや┐）、特殊記号を幅広くカバー
KAOMOJI_PATTERN = re.compile(
    r'[|｜]?[（(]?[^a-zA-Z0-9\s]{1,15}[）)]?[ﾉ┐]?["\'`]*'
)

def protect_kaomoji(text):
    # DeepLに「ここは無視して！」と伝えるための <keep> タグで囲む
    return KAOMOJI_PATTERN.sub(r'<keep>\g<0></keep>', text)

def restore_kaomoji(text):
    # 翻訳後にタグだけをきれいに消す
    return re.sub(r'</?keep>', '', text)

def translate(text):
    # 無料版と有料版のURL自動判定
    api_url = (
        'https://api-free.deepl.com/v2/translate'
        if DEEPL_API_KEY.endswith(':fx')
        else 'https://api.deepl.com/v2/translate'
    )
    
    protected_text = protect_kaomoji(text)
    
    # DeepLへのリクエスト設定
    params = {
        'text': protected_text,
        'source_lang': 'JA',
        'target_lang': 'EN-US',
        'tag_handling': 'xml',        # XMLタグを解釈させる
        'ignore_tags': 'keep',         # <keep>の中身は翻訳しない
        'split_sentences': '0',       # ★重要：勝手に改行（文分割）させない
    }
    
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(
        api_url, data=data,
        headers={'Authorization': f'DeepL-Auth-Key {DEEPL_API_KEY}'}
    )
    
    with urllib.request.urlopen(req) as res:
        result = json.loads(res.read())['translations'][0]['text']
    
    return restore_kaomoji(result)

def process_file(ja_path):
    content = Path(ja_path).read_text(encoding='utf-8')

    if not content.startswith('---'):
        print(f'Front Matterなし、スキップ: {ja_path}')
        return

    # Front Matterと本文を分離
    _, fm, body = content.split('---', 2)
    body = body.strip()

    # タイトルを翻訳
    title_match = re.search(r'^title:\s*"(.+)"', fm, re.MULTILINE)
    if title_match:
        ja_title = title_match.group(1)
        en_title = translate(ja_title)
        fm_en = fm.replace(f'title: "{ja_title}"', f'title: "{en_title}"')
    else:
        fm_en = fm

    # 本文を翻訳
    en_body = translate(body) if body else ''

    # content/en/posts/ に保存
    en_path = Path('content/en/posts') / Path(ja_path).name
    en_path.parent.mkdir(parents=True, exist_ok=True)
    en_path.write_text(f'---{fm_en}---\n\n{en_body}\n', encoding='utf-8')
    print(f'✓ 翻訳完了: {en_path}')

# 実行部分
for filepath in sys.argv[1:]:
    if Path(filepath).exists():
        process_file(filepath)