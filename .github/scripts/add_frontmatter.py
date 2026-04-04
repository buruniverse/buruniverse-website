import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))
posts_dir = Path('content/ja/posts')

def strip_ia_writer_annotations(content):
    lines = content.split('\n')
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == '---':
            block = '\n'.join(lines[i + 1:])
            if re.search(r'(注釈:|&\w|@\w)', block):
                return '\n'.join(lines[:i]).rstrip()
            break
    return content

def extract_hashtags(content):
    hashtag_pattern = re.compile(r'^#(\S+)\s*$', re.MULTILINE)
    tags = hashtag_pattern.findall(content)
    content = hashtag_pattern.sub('', content).strip()
    return content, tags

def fix_image_references(content):
    img_pattern = re.compile(
        r'^(?!\!\[)([^\n]+\.(?:png|jpg|jpeg|gif|webp|PNG|JPG|JPEG|GIF|WEBP))\s*$',
        re.MULTILINE
    )
    def replace_img(m):
        filename = m.group(1).strip()
        return f'![]( /images/{filename})'
    content = img_pattern.sub(replace_img, content)
    return content

for md_file in posts_dir.rglob('*.md'):
    if md_file.name == '_index.md':
        continue
    content = md_file.read_text(encoding='utf-8')
    if content.startswith('---'):
        continue

    content = strip_ia_writer_annotations(content)
    content, tags = extract_hashtags(content)
    content = fix_image_references(content)

    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        content = content.replace(title_match.group(0), '', 1).lstrip('\n')
    else:
        title = md_file.stem.replace('-', ' ').replace('_', ' ')

    # 5. 日時
    now = datetime.now(JST)
    date_str = now.strftime('%Y-%m-%dT%H:%M:%S+09:00')
    # slug: 日付+時刻でASCIIのURLを生成（例: 20260404-143022）
    slug = now.strftime('%Y%m%d-%H%M%S')

    # 6. Front Matter を生成
    fm_lines = ['---', f'title: "{title}"', f'date: {date_str}', f'slug: "{slug}"', 'draft: false']
    if tags:
        tags_str = ', '.join(f'"{t}"' for t in tags)
        fm_lines.append(f'tags: [{tags_str}]')
    fm_lines.append('---')
    front_matter = '\n'.join(fm_lines) + '\n\n'
    md_file.write_text(front_matter + content, encoding='utf-8')
    print(f'✓ Front Matter を追加: {md_file} (tags: {tags}, slug: {slug})')
