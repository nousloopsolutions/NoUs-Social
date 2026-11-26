/**
 * Sisyphus Gate — SOCIAL_STAGING KV state machine
 */

import type { BatchStatus, HeraldEnv, SocialBatch } from "./env";

const KEY_CURRENT = "staging:current";
const KEY_INDEX = "staging:index";
const KEY_BATCH_PREFIX = "staging:batch:";
const INDEX_MAX = 12;

export function batchKey(batchId: string): string {
  return `${KEY_BATCH_PREFIX}${batchId}`;
}

export function getBucketedTimestamp(): string {
  const d = new Date();
  d.setSeconds(0, 0);
  return d.toISOString();
}

export function isoWeekBatchId(date = new Date()): string {
  const tmp = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const day = tmp.getUTCDay() || 7;
  tmp.setUTCDate(tmp.getUTCDate() + 4 - day);
  const yearStart = new Date(Date.UTC(tmp.getUTCFullYear(), 0, 1));
  const week = Math.ceil(((tmp.getTime() - yearStart.getTime()) / 86400000 + 1) / 7);
  return `${tmp.getUTCFullYear()}-W${String(week).padStart(2, "0")}`;
}

export async function getCurrentBatch(env: HeraldEnv): Promise<SocialBatch | null> {
  const raw = await env.SOCIAL_STAGING.get(KEY_CURRENT);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as SocialBatch;
  } catch {
    return null;
  }
}

export async function getBatchById(
  env: HeraldEnv,
  batchId: string
): Promise<SocialBatch | null> {
  const raw = await env.SOCIAL_STAGING.get(batchKey(batchId));
  if (!raw) {
    const current = await getCurrentBatch(env);
    if (current?.batch_id === batchId) return current;
    return null;
  }
  try {
    return JSON.parse(raw) as SocialBatch;
  } catch {
    return null;
  }
}

export async function getCurrentPending(
  env: HeraldEnv
): Promise<SocialBatch | null> {
  const batch = await getCurrentBatch(env);
  if (!batch || batch.status !== "PENDING_HUMAN_PIVOT") return null;
  return batch;
}

async function appendToIndex(env: HeraldEnv, batchId: string): Promise<void> {
  const raw = await env.SOCIAL_STAGING.get(KEY_INDEX);
  let ids: string[] = [];
  if (raw) {
    try {
      ids = JSON.parse(raw) as string[];
    } catch {
      ids = [];
    }
  }
  ids = [batchId, ...ids.filter((id) => id !== batchId)].slice(0, INDEX_MAX);
  await env.SOCIAL_STAGING.put(KEY_INDEX, JSON.stringify(ids));
}

export async function saveBatch(env: HeraldEnv, batch: SocialBatch): Promise<void> {
  const json = JSON.stringify(batch);
  await env.SOCIAL_STAGING.put(KEY_CURRENT, json);
  await env.SOCIAL_STAGING.put(batchKey(batch.batch_id), json);
  await appendToIndex(env, batch.batch_id);
}

export async function transitionStatus(
  env: HeraldEnv,
  batchId: string,
  newStatus: BatchStatus,
  patch?: Partial<SocialBatch>
): Promise<SocialBatch | null> {
  let batch = await getBatchById(env, batchId);
  if (!batch) return null;
  batch = { ...batch, ...patch, status: newStatus };
  await saveBatch(env, batch);
  return batch;
}

export async function hasPendingDraft(env: HeraldEnv): Promise<boolean> {
  const pending = await getCurrentPending(env);
  return pending !== null;
}
