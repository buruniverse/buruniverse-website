import os, sys, re, json, datetime, time
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
    path = Path(filepath)
    # 一覧ページ用のファイルなどはスキップ
    if path.name == '_index.md' or not path.suffix == '.md':
        return None, None

    try:
        # 基準となるディレクトリを特定
        base_dir = 'content/en/posts' if 'content/en/posts' in str(path) else 'content/ja/posts'
        
        # 通知は常に英語版を参照するようにパスを差し替える
        en_path = Path(str(path).replace('content/ja/posts', 'content/en/posts'))
        target_path = en_path if en_path.exists() else path

        content = target_path.read_text(encoding='utf-8')
        if not content.startswith('---'):
            return None, None
        
        parts = content.split('---')
        if len(parts) < 3:
            return None, None
            
        fm = parts[1]
        m = re.search(r'title:\s*"(.+)"', fm)
        title = m.group(1) if m else target_path.stem
        
        # デフォルト言語(en)がルートになるURL構造に対応
        rel_path = target_path.relative_to('content/en/posts' if en_path.exists() else 'content/ja/posts')
        url_path = '/'.join([urllib.parse.quote(p) for p in rel_path.with_suffix('').parts])
        
        # 英語はデフォルトなので /en/ は不要
        url = f'{BASE_URL}/posts/{url_path}/'
        return title, url
    except Exception:
        return None, None

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
        
        # コンテナ作成直後だと "Media Not Found" になることがあるため、少し待機する
        print(f'  ...Threadsコンテナ作成完了(ID: {creation_id})。5秒待機して公開します...')
        time.sleep(5)

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

def post_to_bluesky(text, url):
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
        now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        
        # リンクカードとFacetsの設定
        facets = []
        encoded_text = text.encode('utf-8')
        encoded_url = url.encode('utf-8')
        start = encoded_text.find(encoded_url)

        # リンクをカード形式で見せるためのEmbed設定
        embed = {
            '$type': 'app.bsky.embed.external',
            'external': {
                'uri': url,
                'title': title, # URLを含まない純粋なタイトルを使用
                'description': ""
            }
        }

        if start != -1:
            facets.append({
                'index': { 'byteStart': start, 'byteEnd': start + len(encoded_url) },
                'features': [{ '$type': 'app.bsky.richtext.facet#link', 'uri': url }]
            })

        payload = json.dumps({
            'repo': did,
            'collection': 'app.bsky.feed.post',
            'record': {
                '$type': 'app.bsky.feed.post',
                'text': text,
                'facets': facets,
                'embed': embed,
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
    path = Path(filepath)
    if not path.exists() or not path.is_file():
        continue
    title, url = get_post_info(path)
    if not title:
        continue
    message = f'New blog post is up! 📝\n\n{title}\n{url}'
    print(f'--- Sending Notification ---\nURL: {url}\nMessage:\n{message}\n----------------------------')
    if THREADS_TOKEN:
        post_to_threads(message)
    if BSKY_HANDLE:
        post_to_bluesky(message, url)