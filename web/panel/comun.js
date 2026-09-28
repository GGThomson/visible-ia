// Shared by the panel pages (C7): Supabase client from the deploy-time config.js.
// The anon key is public; what a signed-in clinic can read is decided by RLS (migration 0006).
function panelClient() {
  var config = window.VISIBLE_IA_CONFIG;
  if (!config || !config.supabaseUrl || !config.anonKey || !window.supabase) return null;
  return window.supabase.createClient(config.supabaseUrl, config.anonKey, {
    auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true }
  });
}

function panelUrl() {
  // Works on production, previews and a local copy: the panel is the folder of this page.
  return window.location.href.replace(/[#?].*$/, "").replace(/[^/]*$/, "");
}
