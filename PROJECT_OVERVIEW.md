# Buruniverse プロジェクト概要（AI引き継ぎ用）

## サイト概要

- **サイト名**: ∴Buruniverse∵（英語）/ ∴ぶるニバース∵（日本語）
- **URL**: https://buruniverse.pages.dev
- **目的**: 個人ブログ。iPhoneで書いてそのまま公開できるワークフローを構築中。

---

## 使用プラットフォーム・アプリ一覧

| 役割 | ツール |
|------|--------|
| 静的サイトジェネレーター | Hugo |
| ホスティング | Cloudflare Pages |
| リポジトリ | GitHub（buruniverse/buruniverse-website） |
| 記事執筆（iPhone） | iA Writer 7.3 |
| iPhone→GitHubへのプッシュ | Working Copy（有料プランに移行済み） |
| Front Matter自動生成 | GitHub Actions + Python |
| 日→英自動翻訳 | GitHub Actions + DeepL API（無料プランキー末尾`:fx`） |

---

## フォルダ構成

```
buruniverse-website/
├── hugo.toml                        # Hugo設定（baseURL, タイトル, 言語設定）
├── content/
│   ├── ja/
│   │   ├── posts/                   # 日本語記事（iA Writerで書いてここにプッシュ）
│   │   │   ├── _index.md
│   │   │   ├── ぷくぷくゴジラ.md   # ファイル名＝記事タイトル
│   │   │   └── ...
│   │   └── tokushoho.md             # 特定商取引法ページ（type: "page"）
│   └── en/
│       └── posts/                   # 英語記事（GitHub Actionsが自動生成）
│           └── ぷくぷくゴジラ.md   # 日本語と同名ファイル、内容が英訳
├── static/
│   └── images/                      # 画像置き場（Hugo では /images/ファイル名 でアクセス）
│       ├── IMG_3732.png
│       └── ...
├── layouts/
│   ├── _default/
│   │   ├── list.html                # ブログ一覧テンプレート（本棚UI）
│   │   └── single.html
│   ├── page/
│   │   └── single.html              # type: "page" 用テンプレート
│   └── partials/
│       ├── head.html
│       ├── header.html
│       └── scripts.html
└── .github/
    ├── workflows/
    │   └── auto-frontmatter.yml     # GitHub Actionsワークフロー（下記参照）
    └── scripts/
        ├── add_frontmatter.py       # Front Matter自動追加スクリプト
        └── translate.py             # DeepL翻訳スクリプト
```

---

## GitHub Actionsワークフロー（auto-frontmatter.yml）

**トリガー**: `content/ja/posts/**` へのプッシュ

**処理の流れ**:
1. `add_frontmatter.py` — Front Matterのない記事に自動でtitle/date/draft/tagsを追加
2. `translate.py` — 変更されたJA記事をDeepL APIで英訳してEN版を生成
3. git-auto-commit-action — 変更をコミット（「Auto: Front Matter + EN翻訳」）

```yaml
- name: 英語に翻訳
  env:
    DEEPL_API_KEY: ${{ secrets.DEEPL_API_KEY }}
  run: |
    git -c core.quotepath=false diff --name-only HEAD -- content/ja/posts/ > changed.txt
    cat changed.txt
    if [ -s changed.txt ]; then
      xargs -d '\n' python3 .github/scripts/translate.py < changed.txt
    else
      echo "翻訳対象ファイルなし"
    fi
```

**GitHub Secrets**: `DEEPL_API_KEY`（Repository Secret に登録済み）

---

## iA Writer記事の書き方ルール

- **ファイル名** → Hugoのtitleに自動変換（`ぷくぷくゴジラ.md` → `title: "ぷくぷくゴジラ"`）
- **`#タグ名`**（スペースなし、行全体） → Hugoのtagsに自動変換、本文からは除去
- **`# 見出し`**（スペースあり） → H1見出しとして扱い、titleとして抽出後本文から除去
- **Front Matter** → 書かなくてよい（自動追加）
- **画像** → Working Copyで `static/images/` に追加し、記事内で `![](/images/ファイル名)` と記述
- **iA Writer注釈ブロック**（`---`〜`...` のメタデータ） → 自動除去済み

---

## 現在動いていること ✅

- Hugo多言語サイト（日本語・英語）の表示
- Cloudflare Pagesによる自動デプロイ（GitHubへのプッシュで自動更新）
- Front Matterの自動追加（日本語ファイル名対応済み）
- iA Writer → Working Copy → GitHub → 自動処理 → 公開のフロー
- DeepL APIによる日→英自動翻訳
- 顔文字の一部保護（バッククォート方式を試行中）
- 特定商取引法ページがブログ一覧に出ないよう修正済み

---

## 現在の課題・未解決 🔧

### ① 顔文字（kaomoji）の翻訳保護

**問題**: DeepLが顔文字を変換・消去してしまう。

**試したこと**:
- 正規表現で顔文字を検出してプレースホルダーに置換 → 新しいパターンへの対応が無限に発生
- バッククォートで囲む方式（`` `|ω･ )` ``） → 英語版では保護されるが**日本語の表示にもバッククォートがそのまま出てしまう**

**translate.pyの現状**: バッククォート内の内容を保護してバッククォートを除去する処理を書いたが、日本語側（元ファイル）のバッククォートは除去されていない。

**求める挙動**:
- 記事内で `` `|ω･ )` `` と書く
- 日本語表示: `|ω･ )` （バッククォートなし）
- 英語翻訳: `|ω･ )` （そのまま、翻訳されない）

**ヒント**: `add_frontmatter.py` が記事を処理する際にバッククォートを除去するか、HugoのMarkdownレンダリングで別途対応するか。あるいはDeepLの `tag_handling=xml` + `ignore_tags` を使う方法もある。

---

### ② 将来やりたいこと（未着手）

- 画像ファイルの自動整理（Working CopyでJA記事と一緒にプッシュした画像を `static/images/` へ自動移動）
- SNS（X/Bluesky）への自動投稿
- 英語以外の言語への対応

---

## 補足：重要な設定メモ

- `list.html` では `.Site.RegularPages` を `where .Site.RegularPages "Section" "posts"` でフィルタ済み（これをしないと特定商取引法ページ等がブログ一覧に出る）
- Cloudflare PagesとCloudflare Workersは**別物**。間違えてWorkers側で作ると動かない。Pages側で作成すること。
- DeepL無料APIのエンドポイントは `https://api-free.deepl.com/v2/translate`（`:fx`で終わるキーの場合）
- `git diff --name-only HEAD -- content/ja/posts/` は必ず `git -c core.quotepath=false` を付けること（日本語ファイル名がエスケープされて認識不能になるため）
