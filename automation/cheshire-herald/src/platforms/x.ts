import type { HeraldEnv, PlatformPublishResult } from "../env";

export async function publishX(env: HeraldEnv, text: string): Promise<PlatformPublishResult> {
  const token = env.X_BEARER_TOKEN;
  if (!token) {
    return { ok: false, error: "credentials_not_configured" };
  }

  try {
    const res = await fetch("https://api.twitter.com/2/tweets", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });
    const data = (await res.json()) as { data?: { id?: string }; errors?: unknown };
    if (!res.ok) {
      return { ok: false, error: `http_${res.status}` };
    }
    return { ok: true, platform_id: data.data?.id };
  } catch {
    return { ok: false, error: "publish_failed" };
  }
}
