/* FunLearn Island — core frontend logic */
const FN_BASE = window.SUPABASE_URL.replace(/\/$/, "") + "/functions/v1";
const SITE = "https://yanbing2026.github.io/funlearn-plus";

const sb = window.supabase.createClient(window.SUPABASE_URL, window.SUPABASE_ANON_KEY);

/* ---------- tiny markdown renderer ---------- */
function md(src) {
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const inline = (s) =>
    esc(s)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/`(.+?)`/g, "<code>$1</code>")
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  const lines = src.split("\n");
  let html = "", list = null;
  const closeList = () => { if (list) { html += list === "ul" ? "</ul>" : "</ol>"; list = null; } };
  for (const raw of lines) {
    const line = raw.trimEnd();
    if (/^#{1,3}\s/.test(line)) {
      closeList();
      const lvl = line.match(/^#+/)[0].length;
      html += `<h${lvl + 1}>${inline(line.replace(/^#+\s*/, ""))}</h${lvl + 1}>`;
    } else if (/^>\s?/.test(line)) {
      closeList();
      html += `<blockquote>${inline(line.replace(/^>\s?/, ""))}</blockquote>`;
    } else if (/^[-*]\s+/.test(line)) {
      if (list !== "ul") { closeList(); html += "<ul>"; list = "ul"; }
      html += `<li>${inline(line.replace(/^[-*]\s+/, ""))}</li>`;
    } else if (/^\d+[.)]\s+/.test(line)) {
      if (list !== "ol") { closeList(); html += "<ol>"; list = "ol"; }
      html += `<li>${inline(line.replace(/^\d+[.)]\s+/, ""))}</li>`;
    } else if (line.trim() === "") {
      closeList();
    } else {
      closeList();
      html += `<p>${inline(line)}</p>`;
    }
  }
  closeList();
  return html;
}

/* ---------- auth & membership ---------- */
async function getSession() {
  const { data } = await sb.auth.getSession();
  return data.session || null;
}

async function getMembership() {
  const session = await getSession();
  if (!session) return { session: null, membership: null, active: false };
  const { data } = await sb
    .from("memberships")
    .select("*")
    .eq("user_id", session.user.id)
    .maybeSingle();
  const m = data || null;
  const active =
    !!m &&
    (m.status === "active" || m.status === "trialing") &&
    (!m.current_period_end || new Date(m.current_period_end) > new Date());
  return { session, membership: m, active };
}

async function initNav(activePage) {
  const box = document.getElementById("nav-auth");
  if (!box) return;
  const { session } = await getMembership();
  document.querySelectorAll(".nav-links a[data-page]").forEach((a) => {
    if (a.dataset.page === activePage) a.classList.add("active");
  });
  if (session) {
    const email = session.user.email || "";
    const short = email.split("@")[0];
    box.innerHTML = `<a href="account.html" data-page="account">👤 ${escapeHtml(short)}</a>
      <a href="#" id="logout-link">Sign out</a>`;
    document.getElementById("logout-link").addEventListener("click", async (e) => {
      e.preventDefault();
      await sb.auth.signOut();
      location.href = "index.html";
    });
  } else {
    box.innerHTML = `<a href="login.html" data-page="login" class="btn btn-sm">Sign in</a>`;
  }
}

function escapeHtml(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

/* ---------- edge functions ---------- */
async function callFn(slug, body) {
  const session = await getSession();
  if (!session) throw new Error("not_logged_in");
  const res = await fetch(`${FN_BASE}/${slug}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      apikey: window.SUPABASE_ANON_KEY,
      Authorization: `Bearer ${session.access_token}`,
    },
    body: JSON.stringify(body || {}),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `fn_${res.status}`);
  return data;
}

async function startCheckout(plan, btn) {
  try {
    const { session } = await getMembership();
    if (!session) {
      localStorage.setItem("pending_plan", plan);
      location.href = "login.html";
      return;
    }
    if (btn) { btn.disabled = true; btn.textContent = "Redirecting to secure checkout…"; }
    const { url, error } = await callFn("create-checkout", { plan });
    if (error === "stripe_not_configured") {
      alert("Payments are being set up. Please try again later.");
      if (btn) { btn.disabled = false; btn.textContent = "Try again"; }
      return;
    }
    if (!url) throw new Error(error || "no_url");
    location.href = url;
  } catch (e) {
    console.error(e);
    alert("Couldn't start checkout. Please try again.");
    if (btn) { btn.disabled = false; btn.textContent = "Try again"; }
  }
}

async function openPortal(btn) {
  try {
    if (btn) { btn.disabled = true; btn.textContent = "Opening…"; }
    const { url } = await callFn("customer-portal", {});
    location.href = url;
  } catch (e) {
    console.error(e);
    alert("Couldn't open subscription management. Please try again later.");
    if (btn) { btn.disabled = false; btn.textContent = "Manage subscription"; }
  }
}

/* ---------- content helpers ---------- */
async function fetchContent() {
  const { data, error } = await sb
    .from("content_items")
    .select("slug,title,excerpt,tier,kind,cover_emoji,sort_order")
    .eq("published", true)
    .order("sort_order", { ascending: true });
  if (error) throw error;
  return data || [];
}

function contentCard(item, locked) {
  const badge = item.tier === "member"
    ? `<span class="badge member">👑 Members</span>`
    : `<span class="badge free">Free</span>`;
  const kindIcon = item.kind === "download" ? " 📥" : "";
  return `<a class="content-card" href="read.html?slug=${encodeURIComponent(item.slug)}">
    ${badge}
    <div class="emoji">${escapeHtml(item.cover_emoji || "📚")}</div>
    <h3>${escapeHtml(item.title)}${kindIcon}</h3>
    <p>${escapeHtml(item.excerpt || "")}</p>
    ${locked && item.tier === "member" ? `<div class="lock-veil"><span class="btn btn-sm">🔒 Members only</span></div>` : ""}
  </a>`;
}

async function signedDownloadUrl(path) {
  const { data, error } = await sb.storage.from("member-files").createSignedUrl(path, 300);
  if (error) throw error;
  return data.signedUrl;
}
