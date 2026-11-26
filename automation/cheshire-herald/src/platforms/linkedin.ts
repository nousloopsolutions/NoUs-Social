import type { HeraldEnv, PlatformPublishResult } from "../env";

export async function publishLinkedIn(
  env: HeraldEnv,
  text: string
): Promise<PlatformPublishResult> {
  const token = env.LINKEDIN_ACCESS_TOKEN;
  const author = env.LINKEDIN_AUTHOR_URN;
  if (!token || !author) {
    return { ok: false, error: "credentials_not_configured" };
  }

  const body = {
    author,
    lifecycleState: "PUBLISHED",
    specificContent: {
      "com.linkedin.ugc.ShareContent": {
        shareCommentary: { text },
        shareMediaCategory: "NONE",
      },
    },
    visibility: {
      "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC",
    },
  };

  try {
    const res = await fetch("https://api.linkedin.com/v2/ugcPosts", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
      },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      return { ok: false, error: `http_${res.status}` };
    }
    const id = res.headers.get("x-restli-id") ?? undefined;
    return { ok: true, platform_id: id };
  } catch {
    return { ok: false, error: "publish_failed" };
  }
}
