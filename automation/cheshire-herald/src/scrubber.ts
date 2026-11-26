/**
 * VDS 40000 — Cheshire Scrubber (Herald copy, self-contained for satellite deploy)
 */

const EMAIL_RE =
  /[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*/g;
const PHONE_RE =
  /(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}|[0-9]{10,14}/g;

export interface ScrubResult {
  refined: string;
  clean: boolean;
}

async function hmacTag(secret: string, input: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(input.trim().toLowerCase())
  );
  const hex = Array.from(new Uint8Array(sig))
    .slice(0, 4)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  return hex.toUpperCase();
}

function escapeRe(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export async function scrub(
  text: string,
  secret: string,
  options?: { entities?: string[] }
): Promise<ScrubResult> {
  let refined = text;
  const seen = new Map<string, string>();

  const emails = [...text.matchAll(EMAIL_RE)].map((m) => m[0]);
  for (const email of emails) {
    const key = email.trim().toLowerCase();
    if (seen.has(key)) {
      refined = refined.replace(email, seen.get(key)!);
    } else {
      const tag = await hmacTag(secret, email);
      const placeholder = `[ENTITY_HASH_${tag}]`;
      seen.set(key, placeholder);
      refined = refined.replace(email, placeholder);
    }
  }

  const phones = [...refined.matchAll(PHONE_RE)].map((m) => m[0]);
  for (const phone of phones) {
    const key = phone.trim();
    if (seen.has(key)) {
      refined = refined.replace(phone, seen.get(key)!);
    } else {
      const tag = await hmacTag(secret, phone);
      const placeholder = `[ENTITY_HASH_${tag}]`;
      seen.set(key, placeholder);
      refined = refined.replace(phone, placeholder);
    }
  }

  if (options?.entities?.length) {
    for (const entity of options.entities) {
      if (!entity.trim()) continue;
      const tag = await hmacTag(secret, entity);
      const placeholder = `[ENTITY_HASH_${tag}]`;
      const re = new RegExp(escapeRe(entity.trim()), "gi");
      refined = refined.replace(re, placeholder);
    }
  }

  return { refined, clean: isClean(refined) };
}

export function isClean(text: string): boolean {
  EMAIL_RE.lastIndex = 0;
  PHONE_RE.lastIndex = 0;
  const hasEmail = EMAIL_RE.test(text);
  EMAIL_RE.lastIndex = 0;
  PHONE_RE.lastIndex = 0;
  const hasPhone = PHONE_RE.test(text);
  EMAIL_RE.lastIndex = 0;
  PHONE_RE.lastIndex = 0;
  return !hasEmail && !hasPhone;
}

export async function scrubBatchTexts(
  secret: string,
  fields: string[]
): Promise<string[]> {
  const out: string[] = [];
  for (const f of fields) {
    const { refined } = await scrub(f, secret);
    out.push(refined);
  }
  return out;
}
