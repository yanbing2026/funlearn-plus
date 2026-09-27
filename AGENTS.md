# AGENTS.md — funlearn-plus (FunLearn Island)

面向所有在这个仓库干活的人与 AI（Hermes、ChatGPT、Meta AI …）。动手前先读这份。

## 这是什么
面向 3–6 岁家庭的**会员制学习资源站**：纯静态 GitHub Pages 前端 + Supabase（Auth / Postgres /
Storage / Edge Functions）+ Stripe 订阅。
线上：https://yanbing2026.github.io/funlearn-plus/

## 构建
**无 HTML 构建步骤**（no build、no package.json）。`index.html`、`account.html`、`login.html`、
`library.html`、`read.html`、`assets/*.js` 都是手写静态代码，直接编辑。
Python 脚本只生成 PDF 教具与播种数据，**产物上传 Supabase，不提交进仓库**：
```bash
python3 supabase/make_worksheets.py       # 示例可打印 PDF
python3 supabase/make_more_worksheets.py  # 第二批 PDF
python3 supabase/seed_content.py          # 写入 Supabase 内容
python3 supabase/deploy_functions.py      # 部署 Edge Functions
```

## 测试
无自动化测试、无 lint。改完手动验证：登录/注册、library 列表、read 阅读页、Stripe 入口。

## 发布
GitHub Pages，source = `main` / 根目录（legacy，`.nojekyll` 已存在），无 CI workflow。
合并进 `main` 即上线。

## 密钥边界（重要）
`assets/supabase-config.js` 里的 `window.SUPABASE_URL` + `window.SUPABASE_ANON_KEY` 是**故意公开**的
（anon key 只受 RLS 约束）。**绝不允许**在公开仓库加入 `service_role` key、Stripe secret、
或任何服务端密钥 —— 需要服务端逻辑就写进 Edge Functions（`supabase/functions/`），密钥放 Supabase 侧。

## 绝不手改的生成文件
仓库里没有提交生成的 HTML/PDF 产物（生成物都在 Supabase 侧）。不要手改脚本产出的文件，
也不要去改线上部署状态。

## 流程（main 已保护）
1. 开分支 → 提交 → 开 PR。**不要直接推 `main`**（已禁止直推/强推/删分支，对管理员同样生效）。
2. PR 里写清：改了哪一类（前端页面 / Supabase 脚本 / Edge Function）+ 手动验证的结果。
