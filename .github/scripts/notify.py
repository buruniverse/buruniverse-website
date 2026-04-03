import os, sys, re, json
import urllib.request, urllib.parse
from pathlib import Path

# Threads
THREADS_TOKEN = os.environ.get('THREADS_ACCESS_TOKEN', '')
THREADS_USER_ID = os.environ.get('THREADS_USER_ID', '')

# Bluesky
BSKY_HANDLE = os.environ.get('BSKY_HANDLE', '')
BSKY_APP_PASSWORD = os.environ.get('BSKY_APP_PASSWORD', '')

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
    data = urllib.parse.urlencode({
        'text': text, 'media_type': 'TEXT',
        'access_token': THREADS_TOKEN
    }).encode()
    req = urllib.request.Request(
        f'https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads', data=data)
    with urllib.request.urlopen(req) as res:
        creation_id = json.loads(res.read())['id']
    data = urllib.parse.urlencode({
        'creation_id': creation_id,
        'access_token': THREADS_TOKEN
    }).encode()
    req = urllib.request.Request(
        f'https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish', data=data)
    with urllib.request.urlopen(req) as res:
        print(f'✓ Threads投稿完了: {json.loads(res.read())}')

def post_to_bluesky(text):
    # Step1: ログインしてアクセストークン取得
    data = json.dumps({
        'identifier': BSKY_HANDLE,
        'password': BSKY_APP_PASSWORD
    }).encode()
    req = urllib.request.Request(
        'https://bsky.social/xrpc/com.atproto.server.createSession',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as res:
        session = json.loads(res.read())
    access_token = session['accessJwt']
    did = session['did']

    # Step2: 投稿
    import datetime
    post_data = json.dumps({
        '$type': 'app.bsky.feed.post',
        'text': text,
        'createdAt': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    }).encode()
    req = urllib.request.Request(
        'https://bsky.social/xrpc/com.atproto.repo.createRecord',
        data=json.dumps({
            'repo': did,
            'collection': 'app.bsky.feed.post',
            'record': json.loads(post_data)
        }).encode(),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    with urllib.request.urlopen(req) as res:
        print(f'✓ Bluesky投稿完了: {json.loads(res.read())}')

for filepath in sys.argv[1:]:
    if not Path(filepath).exists():
        continue
    title, url = get_post_info(filepath)
    if not title:
        continue
    message = f'New blog post is up! 📝\n\n{title}\n{url}'
    if THREADS_TOKEN:
        post_to_threads(message)
    if BSKY_HANDLE:
        post_to_bluesky(message)