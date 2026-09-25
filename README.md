# 趣学岛 FunLearn Island 🏝️

专为 3–6 岁家庭打造的**付费会员制学习资源站**。

- **托管**：GitHub Pages（纯静态）
- **后端**：Supabase（Auth + Postgres + Storage + Edge Functions）
- **支付**：Stripe 订阅（月度 $8 / 年度 $68），Webhook 自动同步会员状态

## 线上地址

https://yanbing2026.github.io/funlearn-plus

## 本地结构

```
index.html          首页（含定价）
login.html          邮箱验证码登录
library.html        内容库（RLS 控制可见性）
read.html           文章/下载阅读页
account.html        我的账户（订阅管理）
assets/             样式、前端逻辑、Supabase 公钥配置
supabase/
  migrations/       数据库表 + RLS + Storage
  functions/        create-checkout / stripe-webhook / customer-portal
  deploy_functions.py   函数部署脚本
  seed_content.py       示例内容 seed
```

## 部署

```bash
# 1. 数据库
python3 - <<'EOF'
# 把 supabase/migrations/009_membership_site.sql 通过 sb 以 JSON 包一层执行
EOF

# 2. Edge Functions
python3 supabase/deploy_functions.py

# 3. Secrets（Supabase Dashboard → Edge Functions → Secrets）
STRIPE_SECRET_KEY / STRIPE_WEBHOOK_SECRET / PRICE_MONTHLY / PRICE_YEARLY / SITE_URL

# 4. 推送本目录到 GitHub，Pages 自动发布
```

## 接入 Stripe（测试）

1. Stripe Dashboard 建两个 Product/Price（月度、年度，USD）
2. 把 Price ID 写入 Edge Function Secrets（`PRICE_MONTHLY` / `PRICE_YEARLY`）
3. 在 Stripe 建 Webhook Endpoint → `https://sjqhcpbdgaeapljbllhp.supabase.co/functions/v1/stripe-webhook`，把 signing secret 写入 `STRIPE_WEBHOOK_SECRET`
4. 用测试卡 `4242 4242 4242 4242` 走一遍订阅流程
