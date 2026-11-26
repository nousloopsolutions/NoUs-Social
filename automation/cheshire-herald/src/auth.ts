/**
 * Bearer SOVEREIGN_SALT + optional X-Nous-Internal-Salt alias
 */

import type { HeraldEnv } from "./env";

export function verifySovereignAuth(request: Request, env: HeraldEnv): boolean {
  const secret = env.SOVEREIGN_SALT;
  if (!secret) return false;

  const auth = request.headers.get("Authorization");
  if (auth?.startsWith("Bearer ")) {
    const token = auth.slice(7).trim();
    if (token === secret) return true;
  }

  const alias = request.headers.get("X-Nous-Internal-Salt");
  if (alias === secret) return true;

  return false;
}

export function unauthorizedResponse(): Response {
  return new Response(JSON.stringify({ error: "unauthorized" }), {
    status: 401,
    headers: { "Content-Type": "application/json" },
  });
}

export function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
