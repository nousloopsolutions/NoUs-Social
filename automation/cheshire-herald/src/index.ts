/**
 * Cheshire-Herald — Cloudflare Worker
 * Current Status: Weekly draft cron + KV staging + ratify-and-publish
 *
 * Visual Logic:
 *   [Cron Mon] --> RSS + Workers AI --> Cheshire Scrub --> KV PENDING_HUMAN_PIVOT
 *   [Desktop]  --> GET pending --> Human review --> POST ratify --> Social APIs
 */

import { jsonResponse, unauthorizedResponse, verifySovereignAuth } from "./auth";
import { runWeeklyDraft } from "./cron-draft";
import type { HeraldEnv } from "./env";
import { handleHealth } from "./health";
import {
  handleBatchById,
  handlePending,
  handleRatifyAndPublish,
  handleReject,
  handleTriggerDraft,
} from "./ratify";

function parsePath(url: URL): { path: string; batchId: string | null } {
  let path = url.pathname;
  if (path.endsWith("/") && path.length > 1) path = path.slice(0, -1);
  const batchMatch = path.match(/^\/staging\/batch\/([^/]+)$/);
  if (batchMatch) {
    return { path: "/staging/batch/:id", batchId: decodeURIComponent(batchMatch[1]) };
  }
  return { path, batchId: null };
}

async function handleFetch(request: Request, env: HeraldEnv): Promise<Response> {
  const url = new URL(request.url);
  const { path, batchId } = parsePath(url);
  const method = request.method;

  if (method === "GET" && path === "/health") {
    return handleHealth(env);
  }

  const needsAuth =
    path === "/staging/pending" ||
    path === "/staging/batch/:id" ||
    path === "/ratify-and-publish" ||
    path === "/staging/reject" ||
    path === "/cron/draft";

  if (needsAuth && !verifySovereignAuth(request, env)) {
    return unauthorizedResponse();
  }

  if (method === "GET" && path === "/staging/pending") {
    return handlePending(env);
  }

  if (method === "GET" && path === "/staging/batch/:id" && batchId) {
    return handleBatchById(env, batchId);
  }

  if (method === "POST" && path === "/ratify-and-publish") {
    return handleRatifyAndPublish(request, env);
  }

  if (method === "POST" && path === "/staging/reject") {
    return handleReject(request, env);
  }

  if (method === "POST" && path === "/cron/draft") {
    return handleTriggerDraft(env);
  }

  return jsonResponse({ error: "not_found", worker: "cheshire-herald" }, 404);
}

export default {
  async fetch(request: Request, env: HeraldEnv, _ctx: ExecutionContext): Promise<Response> {
    try {
      return await handleFetch(request, env);
    } catch (e) {
      console.error("HERALD_FETCH_ERROR", { err: String(e) });
      return jsonResponse({ error: "internal_error" }, 500);
    }
  },

  async scheduled(event: ScheduledEvent, env: HeraldEnv, _ctx: ExecutionContext): Promise<void> {
    if (event.cron === "0 14 * * MON") {
      await runWeeklyDraft(env);
    }
  },
};
