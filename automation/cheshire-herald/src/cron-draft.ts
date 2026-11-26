/**
 * Weekly cron — research, draft, Cheshire scrub, KV stage (PENDING_HUMAN_PIVOT)
 */

import { draftPlatformContent } from "./ai-drafter";
import type { HeraldEnv, SocialBatch } from "./env";
import { buildNewsContextBlock, fetchPrivacyNewsContext } from "./news-fetcher";
import { scrub } from "./scrubber";
import {
  getBucketedTimestamp,
  hasPendingDraft,
  isoWeekBatchId,
  saveBatch,
} from "./staging";

async function scrubField(secret: string, text: string): Promise<string> {
  const { refined } = await scrub(text, secret);
  return refined;
}

export async function runWeeklyDraft(env: HeraldEnv): Promise<{ ok: boolean; reason?: string; batch_id?: string }> {
  if (await hasPendingDraft(env)) {
    console.log("HERALD_CRON_SKIP", { reason: "pending_human_pivot_exists" });
    return { ok: false, reason: "pending_draft_exists" };
  }

  const scrubSecret = env.SCRUBBER_SECRET;
  if (!scrubSecret) {
    console.error("HERALD_CRON_ERROR", { reason: "scrubber_secret_missing" });
    return { ok: false, reason: "scrubber_secret_missing" };
  }

  if (!env.AI) {
    return { ok: false, reason: "ai_binding_missing" };
  }

  const headlines = await fetchPrivacyNewsContext(5);
  const newsBlock = buildNewsContextBlock(headlines);
  const platformsRaw = await draftPlatformContent(env, newsBlock);

  const platforms: SocialBatch["platforms"] = {
    linkedin: {
      text: await scrubField(scrubSecret, platformsRaw.linkedin.text),
      char_limit: 3000,
    },
    x: {
      text: await scrubField(scrubSecret, platformsRaw.x.text),
      char_limit: 280,
    },
    facebook: { text: await scrubField(scrubSecret, platformsRaw.facebook.text) },
    instagram: {
      script_60s: await scrubField(scrubSecret, platformsRaw.instagram.script_60s),
      visual_prompt: await scrubField(scrubSecret, platformsRaw.instagram.visual_prompt),
      caption: await scrubField(scrubSecret, platformsRaw.instagram.caption),
    },
    tiktok: {
      script_60s: await scrubField(scrubSecret, platformsRaw.tiktok.script_60s),
      visual_prompt: await scrubField(scrubSecret, platformsRaw.tiktok.visual_prompt),
      caption: await scrubField(scrubSecret, platformsRaw.tiktok.caption),
    },
  };

  const batch: SocialBatch = {
    batch_id: isoWeekBatchId(),
    status: "PENDING_HUMAN_PIVOT",
    created_at_bucket: getBucketedTimestamp(),
    news_context: headlines,
    platforms,
    scrubbed: true,
  };

  await saveBatch(env, batch);
  console.log("HERALD_CRON_OK", { batch_id: batch.batch_id });
  return { ok: true, batch_id: batch.batch_id };
}
