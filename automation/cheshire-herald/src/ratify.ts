/**
 * POST /ratify-and-publish — Sisyphus execution after local human pivot
 */

import { jsonResponse } from "./auth";
import type { HeraldEnv, PublishPlatform, SocialBatch } from "./env";
import { publishFacebook } from "./platforms/facebook";
import { publishLinkedIn } from "./platforms/linkedin";
import { publishX } from "./platforms/x";
import { getBatchById, saveBatch, transitionStatus } from "./staging";

const VALID_PLATFORMS: PublishPlatform[] = ["linkedin", "x", "facebook"];

export interface RatifyBody {
  batch_id: string;
  platforms: PublishPlatform[];
}

export interface RejectBody {
  batch_id: string;
}

function parseRatifyBody(body: unknown): RatifyBody | null {
  if (!body || typeof body !== "object") return null;
  const o = body as Record<string, unknown>;
  const batch_id = typeof o.batch_id === "string" ? o.batch_id.trim() : "";
  if (!batch_id) return null;
  const raw = o.platforms;
  if (!Array.isArray(raw)) return null;
  const platforms = raw.filter(
    (p): p is PublishPlatform =>
      typeof p === "string" && VALID_PLATFORMS.includes(p as PublishPlatform)
  );
  if (platforms.length === 0) return null;
  return { batch_id, platforms };
}

async function publishToPlatform(
  env: HeraldEnv,
  platform: PublishPlatform,
  batch: SocialBatch
): Promise<{ platform: string; ok: boolean; platform_id?: string; error?: string }> {
  switch (platform) {
    case "linkedin": {
      const r = await publishLinkedIn(env, batch.platforms.linkedin.text);
      return { platform, ...r };
    }
    case "x": {
      const r = await publishX(env, batch.platforms.x.text);
      return { platform, ...r };
    }
    case "facebook": {
      const r = await publishFacebook(env, batch.platforms.facebook.text);
      return { platform, ...r };
    }
    default:
      return { platform, ok: false, error: "unknown_platform" };
  }
}

export async function handleRatifyAndPublish(
  request: Request,
  env: HeraldEnv
): Promise<Response> {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: "invalid_json" }, 400);
  }

  const parsed = parseRatifyBody(body);
  if (!parsed) {
    return jsonResponse({ error: "batch_id and platforms required" }, 400);
  }

  const batch = await getBatchById(env, parsed.batch_id);
  if (!batch) {
    return jsonResponse({ error: "batch_not_found" }, 404);
  }
  if (batch.status !== "PENDING_HUMAN_PIVOT") {
    return jsonResponse({ error: "invalid_status", status: batch.status }, 409);
  }

  await transitionStatus(env, parsed.batch_id, "RATIFIED");

  const publish_results: SocialBatch["publish_results"] = {};
  const outcomes: Array<{ platform: string; ok: boolean; platform_id?: string; error?: string }> = [];

  for (const platform of parsed.platforms) {
    const result = await publishToPlatform(env, platform, batch);
    publish_results[platform] = {
      ok: result.ok,
      platform_id: result.platform_id,
      error: result.error,
    };
    outcomes.push(result);
  }

  const allOk = outcomes.every((o) => o.ok);
  const anyOk = outcomes.some((o) => o.ok);
  const finalStatus = allOk ? "PUBLISHED" : anyOk ? "FAILED" : "FAILED";

  const updated = await transitionStatus(env, parsed.batch_id, finalStatus, {
    publish_results,
  });

  return jsonResponse({
    ok: allOk,
    batch_id: parsed.batch_id,
    status: updated?.status ?? finalStatus,
    results: outcomes,
    note: "instagram_and_tiktok_are_draft_only_in_v1",
  });
}

export async function handleReject(request: Request, env: HeraldEnv): Promise<Response> {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: "invalid_json" }, 400);
  }

  const batch_id =
    body && typeof body === "object" && typeof (body as RejectBody).batch_id === "string"
      ? (body as RejectBody).batch_id.trim()
      : "";
  if (!batch_id) {
    return jsonResponse({ error: "batch_id required" }, 400);
  }

  const batch = await getBatchById(env, batch_id);
  if (!batch) {
    return jsonResponse({ error: "batch_not_found" }, 404);
  }
  if (batch.status !== "PENDING_HUMAN_PIVOT") {
    return jsonResponse({ error: "invalid_status", status: batch.status }, 409);
  }

  const updated = await transitionStatus(env, batch_id, "REJECTED");
  return jsonResponse({ ok: true, batch_id, status: updated?.status });
}

export async function handlePending(env: HeraldEnv): Promise<Response> {
  const { getCurrentPending } = await import("./staging");
  const batch = await getCurrentPending(env);
  if (!batch) {
    return jsonResponse({ ok: true, pending: false, batch: null });
  }
  return jsonResponse({ ok: true, pending: true, batch });
}

export async function handleBatchById(env: HeraldEnv, batchId: string): Promise<Response> {
  const batch = await getBatchById(env, batchId);
  if (!batch) {
    return jsonResponse({ error: "batch_not_found" }, 404);
  }
  return jsonResponse({ ok: true, batch });
}

/** Manual cron trigger for local dev (Bearer required) */
export async function handleTriggerDraft(env: HeraldEnv): Promise<Response> {
  const { runWeeklyDraft } = await import("./cron-draft");
  const result = await runWeeklyDraft(env);
  return jsonResponse(result, result.ok ? 200 : 409);
}
