# 生活習慣アドバイザーAI API

GitHub Pages上の確認用画面からAnthropic APIへ接続するための小さな中継APIです。Anthropic APIキーはRenderの環境変数にのみ設定し、HTMLやGitHubには保存しません。

## Renderへのデプロイ

1. Renderにサインインし、**New + → Blueprint**からこのGitHubリポジトリを選びます。
2. `render.yaml` の内容を確認してデプロイします。
3. サービスのEnvironmentで `ANTHROPIC_API_KEY` にAnthropic Consoleで発行したキーを設定し、再デプロイします。キーはソースコードやチャットに貼らないでください。
4. `https://seikatsu-habit-advisor-api.onrender.com/health` を開き、`{"ok":true,"api_key_configured":true}` が返ることを確認します。
5. サービス名が変わった場合は、そのサービスの `onrender.com` URLに合わせて `index.html` の `API_BASE_URL` を更新し、GitHub Pagesへ再デプロイします。

Anthropic Console側で利用上限を設定してください。このAPIにはIPごとの制限（1分6回、24時間40回）とサービス全体の制限（24時間100回）がありますが、公開エンドポイントの完全な不正利用防止を保証するものではありません。制限はサービス再起動時にリセットされます。

## ローカルテスト

```powershell
python -m pip install -r requirements.txt
python -m unittest
```

ローカルでHTTP経由のAI呼び出しを試す場合は `ANTHROPIC_API_KEY` を環境変数に設定してから `python app.py` を実行します。
