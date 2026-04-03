import os, sys, re, json, datetime
import urllib.request, urllib.parse
from urllib.error import HTTPError
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
    try:
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
    except HTTPError as e:
        print(f'× Threads投稿エラー: {e.code} {e.reason}')
        print(f'  Detail: {e.read().decode()}')
    except Exception as e:
        print(f'× Threads投稿エラー: {e}')

def post_to_bluesky(text):
    if not BSKY_HANDLE or not BSKY_APP_PASSWORD:
        print("! Blueskyの認証情報（BSKY_HANDLE / BSKY_APP_PASSWORD）が不足しているためスキップします")
        return

    try:
        # Step1: ログインしてアクセストークン取得
        auth_data = json.dumps({
            'identifier': BSKY_HANDLE,
            'password': BSKY_APP_PASSWORD
        }).encode()
        auth_req = urllib.request.Request(
            'https://bsky.social/xrpc/com.atproto.server.createSession',
            data=auth_data,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(auth_req) as res:
            session = json.loads(res.read())
        access_token = session['accessJwt']
        did = session['did']

        # Step2: 投稿
        now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        payload = json.dumps({
            'repo': did,
            'collection': 'app.bsky.feed.post',
            'record': {
                '$type': 'app.bsky.feed.post',
                'text': text,
                'createdAt': now
            }
        }).encode()
        
        post_req = urllib.request.Request(
            'https://bsky.social/xrpc/com.atproto.repo.createRecord',
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
        )
        with urllib.request.urlopen(post_req) as res:
            print(f'✓ Bluesky投稿完了: {json.loads(res.read())}')
    except HTTPError as e:
        print(f'× Bluesky投稿エラー: {e.code} {e.reason}')
        print(f'  Detail: {e.read().decode()}')
    except Exception as e:
        print(f'× Bluesky投稿エラー: {e}')

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