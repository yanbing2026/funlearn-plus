# FunLearn Island 🏝️

A **membership-based learning resource site** for families with kids ages 3–6. Targets US parents.

- **Hosting**: GitHub Pages (static only)
- **Backend**: Supabase (Auth + Postgres + Storage + Edge Functions)
- **Payments**: Stripe subscriptions ($8/mo, $68/yr); webhooks sync membership status automatically

## Live site

https://yanbing2026.github.io/funlearn-plus

## Layout

```
index.html          Landing page (with pricing)
login.html          Passwordless email-link sign-in
library.html        Content library (visibility enforced by RLS)
read.html           Article / download reader
account.html        My account (subscription management)
assets/             Styles, frontend logic, Supabase public config
supabase/
  migrations/       DB tables + RLS + Storage bucket
  functions/        create-checkout / stripe-webhook / customer-portal
  deploy_functions.py   Function deploy script (Management API)
  seed_content.py       Sample content seeder
  make_worksheets.py    Sample printable PDF generator
```

## Deploy

```bash
# 1. Database: run supabase/migrations/009_membership_site.sql via the sb CLI
# 2. Edge Functions:
python3 supabase/deploy_functions.py
# 3. Secrets (Supabase Dashboard → Edge Functions → Secrets):
#    STRIPE_SECRET_KEY / STRIPE_WEBHOOK_SECRET / PRICE_MONTHLY / PRICE_YEARLY / SITE_URL
# 4. Seed sample content:
python3 supabase/seed_content.py
# 5. Push this directory to GitHub — Pages publishes automatically
python3 ~/workspace/skills/github/bin/gh-push yanbing2026/funlearn-plus ~/workspace/funlearn-plus
```

## Stripe wiring (test mode)

1. Create two Products/Prices in the Stripe Dashboard (monthly, annual, USD)
2. Save the Price IDs as Edge Function secrets `PRICE_MONTHLY` / `PRICE_YEARLY`
3. Create a Webhook Endpoint → `https://sjqhcpbdgaeapljbllhp.supabase.co/functions/v1/stripe-webhook`, save the signing secret as `STRIPE_WEBHOOK_SECRET`
4. Run a full subscription flow with test card `4242 4242 4242 4242`
