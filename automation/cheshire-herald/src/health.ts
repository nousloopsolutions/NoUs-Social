/**
 * GET /health — required for CORE-03 / deploy probes
 */

import type { HeraldEnv } from "./env";

export async function handleHealth(env: HeraldEnv): Promise<Response> {
  const hasKv = !!env.SOCIAL_STAGING;
  const hasAi = !!env.AI;
  const hasSalt = !!env.SOVEREIGN_SALT;
  const hasScrubber = !!env.SCRUBBER_SECRET;

  return new Response(
    JSON.stringify({
      ok: hasKv && hasAi,
      worker: "cheshire-herald",
      ts: Date.now(),
      bindings: {
        social_staging: hasKv,
        ai: hasAi,
        sovereign_salt_configured: hasSalt,
        scrubber_secret_configured: hasScrubber,
      },
    }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
}
