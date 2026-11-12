# 生活習慣アドバイザーAI

GitHub Pagesの画面からCloudflare Workers AIを呼び出す、無料枠を使ったサーバー側中継です。プロバイダーAPIキーは不要です。AI呼び出しはCloudflare Workers AIの無料枠を消費します。

## Cloudflare Workerの公開

1. Cloudflareにサインインし、**Workers & Pages**から新しいWorkerを作成して、GitHub連携を選びます。
2. `yuuki0405/seikatsu-habit-advisor` の `main` ブランチを選択し、リポジトリのルートをデプロイ元にします。
3. Worker名を `seikatsu-habit-advisor-ai` にします。リポジトリの `wrangler.toml` にあるWorkers AI binding（`AI`）が設定に反映されていることを確認し、デプロイします。
4. Workerの `workers.dev` URLは `https://seikatsu-habit-advisor-ai.suiginyu.workers.dev` です。`index.html` には設定済みです。
5. デプロイ後、次を開いて `{"ok":true,"ai_binding_configured":true,"rate_limit_binding_configured":true}` が返ることを確認します。

   `https://seikatsu-habit-advisor-ai.suiginyu.workers.dev/health`

6. [公開ページ](https://yuuki0405.github.io/seikatsu-habit-advisor/)から記録・相談をテストします。Git連携済みなら、`main`へのpush後にページが自動更新されます。

Workers AIのbindingは[公式手順](https://developers.cloudflare.com/workers-ai/configuration/bindings/)を参照してください。Git連携によるWorkerの自動デプロイは[Workers Builds](https://developers.cloudflare.com/workers/ci-cd/builds/)に説明があります。

## Workerの利用制限

- `wrangler.toml`にはCloudflare Workers Rate Limiting bindingを設定しています。`namespace_id`はCloudflareアカウント内で一意な整数にしてください。すでに使われている場合は、別の整数に変更してデプロイします。
- 既定値はIPアドレスごとに1分あたり6リクエストです。このbindingはCloudflareのデータセンターごとの近似的な制限で、厳密な全世界共通上限ではありません。Worker内のメモリによる分単位・日単位の制限も補助として残していますが、これもインスタンス間で共有されません。
- 無料枠の消費を厳密に全体管理する機能ではありません。Cloudflareの利用量・アラートも確認してください。より厳密な全体制限が必要なら、Durable Objectsなど共有状態を使う仕組みを検討してください。
- デプロイにはWrangler CLI 4.36.0以降が必要です。Workers Rate Limiting bindingの設定は[公式ドキュメント](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/)を参照してください。

## 記録と分析について

- 記録画面では朝食・昼食・夕食・間食・飲み物、水分量、運動内容・時間、睡眠時間を項目別に入力します。空欄は未記録として扱い、入力された内容だけを分析します。
- 生活習慣スコアは健康状態を適切に表さないため表示しません。グラフは入力された睡眠・水分・カフェイン・運動の記録値と、その記録済みデータの平均を表示し、一般的な目安との点数比較は行いません。
- 食品の量や商品情報がない場合、カロリーや栄養素の正確な量は分かりません。分析では、記録から分かることと不足情報を分けます。
- 1日の記録だけから病気の発症や個人の将来リスクを予測しません。継続した食習慣に関する注意は、条件付きの一般情報として表示します。分析は医療上の評価・診断ではありません。
- グラフの基準線は「一般成人の調査平均」と「健康づくりの目安」を区別します。歩数の調査平均は厚生労働省「令和5年 国民健康・栄養調査」の20歳以上の男女別平均（男性6,628歩、女性5,659歩）です。これは健康な人だけの平均ではありません。歩数・身体活動・睡眠の目安線は各厚生労働省ガイドに基づきます。水分・カフェインは一律に適用できる公的基準値・比較平均を確認できないため線を表示しません。

## 無料枠と制限

- Workers AIの無料割当は、アカウント合計で**1日10,000 Neurons**です。UTC 00:00にリセットされます。無料プランでは割当を超えるとAIリクエストが失敗します。Workers Paidプランでは無料割当超過分が課金されるため、無料だけで使うならWorkers Freeプランを利用してください。Worker AI bindingそのものにAnthropicやGeminiのAPIキーは不要です。
- 使用モデルは `@cf/meta/llama-4-scout-17b-16e-instruct` です。Cloudflareの[料金表](https://developers.cloudflare.com/workers-ai/platform/pricing/)と[利用上限](https://developers.cloudflare.com/workers-ai/platform/limits/)を確認してください。無料割当やモデル提供条件は変更されることがあります。
- WorkerにはOriginチェックとレート制限があります。ただしCORSは認証ではなく、レート制限も完全な不正利用防止ではありません。公開後もCloudflareの利用量を確認してください。

記録はブラウザー内に保存されます。記録・相談内容と会話の文脈はAI応答の生成のためCloudflare Workers AIへ送信されます。このアプリはサーバー上に生活ログや会話を保存しません。個人を特定できる情報や共有したくない情報は入力しないでください。

## ローカルテスト

Node.jsの組み込みテストランナーでテストできます。外部依存のインストールは不要です。

```powershell
npm test
```
