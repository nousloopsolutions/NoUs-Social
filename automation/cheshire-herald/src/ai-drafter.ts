/**
 * Workers AI multi-platform draft generation
 */

import type { HeraldEnv, SocialBatch } from "./env";

const DEFAULT_MODEL = "@cf/meta/llama-3-8b-instruct";

const MISSION =
  "NoUs Loop Solutions engineers human-centric neuro-prosthetics and local-first AI. " +
  "Mission: ethically durable technology for a 15-year horizon — sovereign ownership of logic, data, and digital identity. " +
  "Theme: Safety Through Severance.";

async function runAi(env: HeraldEnv, prompt: string): Promise<string> {
  const model = env.HERALD_MODEL ?? DEFAULT_MODEL;
  const ai = env.AI;
  if (!ai) throw new Error("ai_binding_missing");
  const out = await ai.run(model, { prompt });
  const response = (out as { response?: string })?.response;
  return typeof response === "string" ? response.trim() : String(out ?? "").trim();
}

function truncate(text: string, max: number): string {
  if (text.length <= max) return text;
  return text.slice(0, max - 1).trimEnd() + "…";
}

export async function draftPlatformContent(
  env: HeraldEnv,
  newsBlock: string
): Promise<SocialBatch["platforms"]> {
  const base = `${MISSION}\n\nRecent context:\n${newsBlock}\n\n`;

  const linkedinPrompt =
    base +
    "Write a LinkedIn post (max 2800 chars). Focus: systemic advocacy, educational consulting, 15-year ethically durable tech. Professional tone. Output ONLY the post text.";

  const xPrompt =
    base +
    "Write one X (Twitter) post (MAX 280 characters). Punchy, rebellious take on the Severance protocol and data sovereignty. Output ONLY the post text, under 280 chars.";

  const facebookPrompt =
    base +
    "Write a Facebook community post about owning personal data and local-first AI. Warm, community-focused. Output ONLY the post text.";

  const instagramPrompt =
    base +
    "For Instagram Reels, output exactly three labeled lines:\nSCRIPT_60S: (spoken-word script, ~150 words, 60 seconds)\nVISUAL_PROMPT: (shot list / b-roll ideas)\nCAPTION: (short caption with hashtags)";

  const tiktokPrompt =
    base +
    "For TikTok, output exactly three labeled lines:\nSCRIPT_60S: (spoken-word script, ~150 words, 60 seconds)\nVISUAL_PROMPT: (shot list / on-screen text ideas)\nCAPTION: (short caption with hashtags)";

  const [linkedinRaw, xRaw, facebookRaw, instagramRaw, tiktokRaw] = await Promise.all([
    runAi(env, linkedinPrompt),
    runAi(env, xPrompt),
    runAi(env, facebookPrompt),
    runAi(env, instagramPrompt),
    runAi(env, tiktokPrompt),
  ]);

  const parseVideo = (raw: string) => {
    const script =
      raw.match(/SCRIPT_60S:\s*([\s\S]*?)(?=VISUAL_PROMPT:|$)/i)?.[1]?.trim() ?? raw.slice(0, 800);
    const visual =
      raw.match(/VISUAL_PROMPT:\s*([\s\S]*?)(?=CAPTION:|$)/i)?.[1]?.trim() ?? "";
    const caption = raw.match(/CAPTION:\s*([\s\S]*?)$/i)?.[1]?.trim() ?? "";
    return { script_60s: script, visual_prompt: visual, caption };
  };

  const ig = parseVideo(instagramRaw);
  const tt = parseVideo(tiktokRaw);

  return {
    linkedin: { text: truncate(linkedinRaw, 3000), char_limit: 3000 },
    x: { text: truncate(xRaw, 280), char_limit: 280 },
    facebook: { text: truncate(facebookRaw, 5000) },
    instagram: ig,
    tiktok: tt,
  };
}
