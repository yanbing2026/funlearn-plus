// stripe-webhook: 接收 Stripe 事件，同步订阅状态到 memberships 表
// verify_jwt = false（用 Stripe 签名校验代替）

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.44.4";
import Stripe from "https://esm.sh/stripe@16.12.0?target=deno";

// Stripe 状态 -> memberships.status（约束只允许 inactive/trialing/active/past_due/canceled）
function mapStatus(s: string): string {
  if (s === "trialing" || s === "active" || s === "past_due") return s;
  if (s === "unpaid") return "past_due";
  return "inactive";
}

Deno.serve(async (req: Request) => {
  const stripeKey = Deno.env.get("STRIPE_SECRET_KEY");
  const webhookSecret = Deno.env.get("STRIPE_WEBHOOK_SECRET");
  if (!stripeKey || !webhookSecret) {
    return new Response("stripe_not_configured", { status: 500 });
  }

  const stripe = new Stripe(stripeKey, { apiVersion: "2024-06-20" });
  const sig = req.headers.get("stripe-signature") || "";
  const rawBody = await req.text();

  let event: Stripe.Event;
  try {
    event = await stripe.webhooks.constructEventAsync(rawBody, sig, webhookSecret);
  } catch (e) {
    console.error("bad signature", e);
    return new Response("bad signature", { status: 400 });
  }

  const admin = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  );
  const now = new Date().toISOString();

  try {
    switch (event.type) {
      case "checkout.session.completed": {
        const s = event.data.object as Stripe.Checkout.Session;
        const userId = s.metadata?.supabase_user_id;
        if (!userId || !s.subscription) break;
        const sub = await stripe.subscriptions.retrieve(s.subscription as string);
        await admin.from("memberships").upsert({
          user_id: userId,
          status: mapStatus(sub.status),
          plan_id: s.metadata?.plan || sub.metadata?.plan || null,
          stripe_customer_id: s.customer as string,
          stripe_subscription_id: sub.id,
          current_period_end: new Date(sub.current_period_end * 1000).toISOString(),
          cancel_at_period_end: sub.cancel_at_period_end ?? false,
          updated_at: now,
        }, { onConflict: "user_id" });
        break;
      }
      case "customer.subscription.updated": {
        const sub = event.data.object as Stripe.Subscription;
        const { data: ms } = await admin
          .from("memberships")
          .select("user_id")
          .eq("stripe_subscription_id", sub.id)
          .maybeSingle();
        if (ms) {
          await admin.from("memberships").update({
            status: mapStatus(sub.status),
            current_period_end: new Date(sub.current_period_end * 1000).toISOString(),
            cancel_at_period_end: sub.cancel_at_period_end ?? false,
            updated_at: now,
          }).eq("user_id", ms.user_id);
        }
        break;
      }
      case "customer.subscription.deleted": {
        const sub = event.data.object as Stripe.Subscription;
        const { data: ms } = await admin
          .from("memberships")
          .select("user_id")
          .eq("stripe_subscription_id", sub.id)
          .maybeSingle();
        if (ms) {
          await admin.from("memberships").update({
            status: "canceled",
            cancel_at_period_end: false,
            updated_at: now,
          }).eq("user_id", ms.user_id);
        }
        break;
      }
      case "invoice.payment_failed": {
        const inv = event.data.object as Stripe.Invoice;
        if (!inv.customer) break;
        const { data: ms } = await admin
          .from("memberships")
          .select("user_id")
          .eq("stripe_customer_id", inv.customer as string)
          .maybeSingle();
        if (ms) {
          await admin.from("memberships").update({
            status: "past_due",
            updated_at: now,
          }).eq("user_id", ms.user_id);
        }
        break;
      }
      default:
        break;
    }
  } catch (e) {
    console.error("webhook handler error", e);
    return new Response("handler error", { status: 500 });
  }

  return new Response("ok", { status: 200 });
});
