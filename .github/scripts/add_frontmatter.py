import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 日本時間（UTC+9）
JST = timezone(timedelta(hours=9))
posts_dir = Path('content/ja/posts')


def strip_ia_writer_annotations(content):
    """iA Writerの注釈ブロックを末尾から除去する。
    例: --- \n 注釈: ... \n &作文ツール: ... \n @user: ... \n ...
    """
    lines = content.split('\n')
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == '---':
            block = '\n'.join(lines[i + 1:])
            if re.search(r'(注釈:|&\w|@\w)', block):
                return '\n'.join(lines[:i]).rstrip()
            break
    return content


def extract_hashtags(content):
    """行全体が #タグ 形式の行を抽出し、本文から除去する。
    （iA Writerのハッシュタグ: スペースなし、行全体）
    通常のMarkdown見出し # タイトル（スペースあり）は対象外。
    """
    hashtag_pattern = re.compile(r'^#(\S+)\s*$', re.MULTILINE)
    tags = hashtag_pattern.findall(content)
    content = hashtag_pattern.sub('', content).strip()
    return content, tags


def fix_image_references(content):
    """iA Writerが出力する画像ファイル名をMarkdown画像記法に変換する。
    例: IMG_3732.PNG → ![](/images/IMG_3732.PNG)
    すでに ![]() 形式になっているものはスキップ。
    """
    # 行全体が画像ファイル名だけのパターン（拡張子で判別）
    img_pattern = re.compile(
        r'^(?!\!\[)([^\n]+\.(?:png|jpg|jpeg|gif|webp|PNG|JPG|JPEG|GIF|WEBP))\s*$',
        re.MULTILINE
    )
    def replace_img(m):
        filename = m.group(1).strip()
        # スペースや "2" などのiPhone命名ゆれを正規化（任意）
        return f'![]( /images/{filename})'
    content = img_pattern.sub(replace_img, content)
    return content


for md_file in posts_dir.rglob('*.md'):
    if md_file.name == '_index.md':
        continue

    content = md_file.read_text(encoding='utf-8')

    # すでに Front Matter がある場合はスキップ
    if content.startswith('---'):
        continue

    # 1. iA Writer注釈ブロックを除去
    content = strip_ia_writer_annotations(content)

    # 2. ハッシュタグ（#tag）を抽出して本文から除去
    content, tags = extract_hashtags(content)

    # 3. 画像ファイル名をMarkdown記法に変換
    content = fix_image_references(content)

    # 4. # 見出し（スペースあり）からタイトルを取得
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        content = content.replace(title_match.group(0), '', 1).lstrip('\n')
    else:
        title = md_file.stem.replace('-', ' ').replace('_', ' ')

    # 5. 日時
    now = datetime.now(JST)
    date_str = now.strftime('%Y-%m-%dT%H:%M:%S+09:00')

    # 6. Front Matter を生成（タグがあれば追加）
    fm_lines = ['---', f'title: "{title}"', f'date: {date_str}', 'draft: false']
    if tags:
        tags_str = ', '.join(f'"{t}"' for t in tags)
        fm_lines.append(f'tags: [{tags_str}]')
    fm_lines.append('---')
    front_matter = '\n'.join(fm_lines) + '\n\n'

    md_file.write_text(front_matter + content, encoding='utf-8')
    print(f'✓ Front Matter を追加: {md_file} (tags: {tags})')
