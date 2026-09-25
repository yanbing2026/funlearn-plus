// customer-portal: 为已登录会员创建 Stripe Billing Portal 会话（自助管理/取消订阅）
// verify_jwt = true

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

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const anonKey = Deno.env.get("SUPABASE_ANON_KEY")!;
    const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const stripeKey = Deno.env.get("STRIPE_SECRET_KEY");
    const siteUrl = Deno.env.get("SITE_URL");
    if (!stripeKey || !siteUrl) return json({ error: "stripe_not_configured" }, 500);

    const supabase = createClient(supabaseUrl, anonKey, {
      global: { headers: { Authorization: req.headers.get("Authorization") || "" } },
    });
    const { data: { user }, error: userErr } = await supabase.auth.getUser();
    if (userErr || !user) return json({ error: "unauthorized" }, 401);

    const admin = createClient(supabaseUrl, serviceKey);
    const { data: ms } = await admin
      .from("memberships")
      .select("stripe_customer_id")
      .eq("user_id", user.id)
      .maybeSingle();

    if (!ms?.stripe_customer_id) return json({ error: "no_customer" }, 400);

    const stripe = new Stripe(stripeKey, { apiVersion: "2024-06-20" });
    const portal = await stripe.billingPortal.sessions.create({
      customer: ms.stripe_customer_id as string,
      return_url: `${siteUrl}/account.html`,
    });

    return json({ url: portal.url });
  } catch (e) {
    console.error(e);
    return json({ error: "internal", detail: String((e as Error)?.message || e) }, 500);
  }
});
