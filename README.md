# 生活習慣アドバイザーAI

GitHub Pagesの画面からCloudflare Workers AIを呼び出す、無料枠を使ったサーバー側中継です。プロバイダーAPIキーは不要です。AI呼び出しはCloudflare Workers AIの無料枠を消費します。

## Cloudflare Workerの公開

1. Cloudflareにサインインし、**Workers & Pages**から新しいWorkerを作成して、GitHub連携を選びます。
2. `yuuki0405/seikatsu-habit-advisor` の `main` ブランチを選択し、リポジトリのルートをデプロイ元にします。
3. Worker名を `seikatsu-habit-advisor-ai` にします。リポジトリの `wrangler.toml` にあるWorkers AI binding（`AI`）が設定に反映されていることを確認し、デプロイします。
4. Workerの `workers.dev` URLを確認します。形式は `https://seikatsu-habit-advisor-ai.<アカウントのサブドメイン>.workers.dev` です。
5. `index.html` の `API_BASE_URL` に実際のURLを入れて `main` ブランチへ反映します。GitHub Pagesのデプロイ後、次を開いて `{"ok":true,"ai_binding_configured":true}` が返ることを確認します。

   `https://<WorkerのURL>/health`

6. [公開ページ](https://yuuki0405.github.io/seikatsu-habit-advisor/)から記録・相談をテストします。

Workers AIのbindingは[公式手順](https://developers.cloudflare.com/workers-ai/configuration/bindings/)を参照してください。Git連携によるWorkerの自動デプロイは[Workers Builds](https://developers.cloudflare.com/workers/ci-cd/builds/)に説明があります。

## 無料枠と制限

- Workers AIの無料割当は、アカウント合計で**1日10,000 Neurons**です。UTC 00:00にリセットされます。無料プランでは割当を超えるとAIリクエストが失敗します。Workers Paidプランでは無料割当超過分が課金されるため、無料だけで使うならWorkers Freeプランを利用してください。Worker AI bindingそのものにAnthropicやGeminiのAPIキーは不要です。
- 使用モデルは `@cf/meta/llama-3.1-8b-instruct` です。Cloudflareの[料金表](https://developers.cloudflare.com/workers-ai/platform/pricing/)と[利用上限](https://developers.cloudflare.com/workers-ai/platform/limits/)を確認してください。無料割当やモデル提供条件は変更されることがあります。
- WorkerにはOriginチェックと簡易レート制限があります。ただしCORSは認証ではなく、レート制限はWorkerインスタンス内の一時的な制限です。完全な不正利用防止ではありません。公開前にCloudflareの利用量を確認してください。

生活・健康に関する内容を扱うため、個人を特定できる情報や共有したくない情報は入力しないでください。

## ローカルテスト

Node.jsの組み込みテストランナーでテストできます。外部依存のインストールは不要です。

```powershell
npm test
```
