// create-checkout: 为已登录用户创建 Stripe Checkout Session（订阅制）
// verify_jwt = true（网关校验用户 JWT）

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.44.4";
import Stripe from "https://esm.sh/stripe@16.12.0?target=deno";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const json = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });

function planToPriceId(plan: string): string | null {
  if (plan === "monthly") return Deno.env.get("PRICE_MONTHLY") || null;
  if (plan === "yearly") return Deno.env.get("PRICE_YEARLY") || null;
  return null;
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const anonKey = Deno.env.get("SUPABASE_ANON_KEY")!;
    const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const stripeKey = Deno.env.get("STRIPE_SECRET_KEY");
    const siteUrl = Deno.env.get("SITE_URL");
    if (!stripeKey || !siteUrl) return json({ error: "stripe_not_configured" }, 500);

    // 用户身份（网关已验 JWT，这里再取一次用户信息）
    const supabase = createClient(supabaseUrl, anonKey, {
      global: { headers: { Authorization: req.headers.get("Authorization") || "" } },
    });
    const { data: { user }, error: userErr } = await supabase.auth.getUser();
    if (userErr || !user) return json({ error: "unauthorized" }, 401);

    const { plan } = await req.json().catch(() => ({}));
    const priceId = planToPriceId(plan);
    if (!priceId) return json({ error: "bad_plan" }, 400);

    const admin = createClient(supabaseUrl, serviceKey);
    const { data: ms } = await admin
      .from("memberships")
      .select("stripe_customer_id")
      .eq("user_id", user.id)
      .maybeSingle();

    let customerId = (ms?.stripe_customer_id as string | undefined) || undefined;
    const stripe = new Stripe(stripeKey, { apiVersion: "2024-06-20" });

    if (!customerId) {
      const customer = await stripe.customers.create({
        email: user.email,
        metadata: { supabase_user_id: user.id },
      });
      customerId = customer.id;
      await admin.from("memberships").upsert(
        {
          user_id: user.id,
          status: "inactive",
          stripe_customer_id: customerId,
          updated_at: new Date().toISOString(),
        },
        { onConflict: "user_id" },
      );
    }

    const session = await stripe.checkout.sessions.create({
      mode: "subscription",
      customer: customerId,
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${siteUrl}/account.html?checkout=success`,
      cancel_url: `${siteUrl}/index.html?checkout=cancelled#pricing`,
      metadata: { supabase_user_id: user.id, plan },
      subscription_data: { metadata: { supabase_user_id: user.id, plan } },
    });

    return json({ url: session.url });
  } catch (e) {
    console.error(e);
    return json({ error: "internal", detail: String((e as Error)?.message || e) }, 500);
  }
});
