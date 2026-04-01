import re
import sys
import os
import urllib.request
import urllib.parse
import json
from pathlib import Path

DEEPL_API_KEY = os.environ['DEEPL_API_KEY'].strip()
# 無料プランのURL（キーが :fx で終わる）
API_URL = 'https://api-free.deepl.com/v2/translate'

KAOMOJI_PATTERN = re.compile(
    r'[（(|｜][ω∀дﾟ；;･・ー≡*＊]{1,15}\s?[）)\'`]'
)

def protect_kaomoji(text):
    return KAOMOJI_PATTERN.sub(r'<notranslate>\g<0></notranslate>', text)

def restore_kaomoji(text):
    return re.sub(r'</?notranslate>', '', text)

def translate(text):
    api_url = (
        'https://api-free.deepl.com/v2/translate'
        if DEEPL_API_KEY.endswith(':fx')
        else 'https://api.deepl.com/v2/translate'
    )
    protected_text = protect_kaomoji(text)
    data = urllib.parse.urlencode({
        'text': protected_text,
        'source_lang': 'JA',
        'target_lang': 'EN-US',
        'tag_handling': 'xml',
        'ignore_tags': 'notranslate',
    }).encode()
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

# 引数で渡されたファイル一覧を処理
for filepath in sys.argv[1:]:
    if Path(filepath).exists():
        process_file(filepath)
