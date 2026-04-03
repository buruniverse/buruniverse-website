import os, sys, re, json
import urllib.request, urllib.parse
from pathlib import Path

THREADS_TOKEN = os.environ['THREADS_ACCESS_TOKEN']
THREADS_USER_ID = os.environ['THREADS_USER_ID']
BASE_URL = 'https://buruniverse.pages.dev'

def get_post_info(filepath):
    content = Path(filepath).read_text(encoding='utf-8')
    if not content.startswith('---'):
        return None, None
    _, fm, _ = content.split('---', 2)
    m = re.search(r'^title:\s*"(.+)"', fm, re.MULTILINE)
    title = m.group(1) if m else Path(filepath).stem
    slug = urllib.parse.quote(Path(filepath).stem)
    url = f'{BASE_URL}/en/posts/{slug}/'
    return title, url

def post_to_threads(text):
    # Step1: コンテナ作成
    data = urllib.parse.urlencode({
        'text': text, 'media_type': 'TEXT',
        'access_token': THREADS_TOKEN
    }).encode()
    req = urllib.request.Request(
        f'https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads', data=data)
    with urllib.request.urlopen(req) as res:
        creation_id = json.loads(res.read())['id']
    # Step2: 公開
    data = urllib.parse.urlencode({
        'creation_id': creation_id,
        'access_token': THREADS_TOKEN
    }).encode()
    req = urllib.request.Request(
        f'https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish', data=data)
    with urllib.request.urlopen(req) as res:
        print(f'✓ Threads投稿完了: {json.loads(res.read())}')

for filepath in sys.argv[1:]:
    if not Path(filepath).exists():
        continue
    title, url = get_post_info(filepath)
    if title:
        post_to_threads(f'New blog post is up! 📝\n\n{title}\n{url}')