import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 日本時間（UTC+9）
JST = timezone(timedelta(hours=9))
posts_dir = Path('content/ja/posts')

for md_file in posts_dir.rglob('*.md'):
    content = md_file.read_text(encoding='utf-8')

    # すでに Front Matter がある場合はスキップ
    if content.startswith('---'):
        continue

    # 先頭の # 見出しからタイトルを取得
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        # タイトル行を本文から除去（Front Matter に移すため）
        content = content.replace(title_match.group(0), '', 1).lstrip('\n')
    else:
        # # 見出しがない場合はファイル名をタイトルに
        title = md_file.stem.replace('-', ' ').replace('_', ' ')

    # 現在の日本時間
    now = datetime.now(JST)
    date_str = now.strftime('%Y-%m-%dT%H:%M:%S+09:00')

    # Front Matter を生成して先頭に追加
    front_matter = f'---\ntitle: "{title}"\ndate: {date_str}\ndraft: false\n---\n\n'
    md_file.write_text(front_matter + content, encoding='utf-8')
    print(f'✓ Front Matter を追加: {md_file}')
