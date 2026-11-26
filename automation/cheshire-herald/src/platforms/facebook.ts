import type { HeraldEnv, PlatformPublishResult } from "../env";

export async function publishFacebook(
  env: HeraldEnv,
  text: string
): Promise<PlatformPublishResult> {
  const token = env.FACEBOOK_PAGE_ACCESS_TOKEN;
  const pageId = env.FACEBOOK_PAGE_ID;
  if (!token || !pageId) {
    return { ok: false, error: "credentials_not_configured" };
  }

  const url = `https://graph.facebook.com/v21.0/${encodeURIComponent(pageId)}/feed`;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        access_token: token,
      }),
    });
    const data = (await res.json()) as { id?: string; error?: { message?: string } };
    if (!res.ok || data.error) {
      return { ok: false, error: `http_${res.status}` };
    }
    return { ok: true, platform_id: data.id };
  } catch {
    return { ok: false, error: "publish_failed" };
  }
}
