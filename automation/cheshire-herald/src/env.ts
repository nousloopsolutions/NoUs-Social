/**
 * Current Status: Cheshire-Herald Env bindings
 * Visual Logic:
 *   Cron/AI/KV ──► HeraldEnv ──► platform secrets (ratify only)
 */

export type BatchStatus =
  | "PENDING_HUMAN_PIVOT"
  | "RATIFIED"
  | "PUBLISHED"
  | "REJECTED"
  | "FAILED";

export interface NewsHeadline {
  title: string;
  source: string;
  link_hash: string;
}

export interface PlatformPublishResult {
  ok: boolean;
  platform_id?: string;
  error?: string;
}

export interface SocialBatch {
  batch_id: string;
  status: BatchStatus;
  created_at_bucket: string;
  news_context: NewsHeadline[];
  platforms: {
    linkedin: { text: string; char_limit: number };
    x: { text: string; char_limit: number };
    facebook: { text: string };
    instagram: { script_60s: string; visual_prompt: string; caption: string };
    tiktok: { script_60s: string; visual_prompt: string; caption: string };
  };
  scrubbed: boolean;
  publish_results?: Record<string, PlatformPublishResult>;
}

export interface HeraldEnv {
  AI: Ai;
  SOCIAL_STAGING: KVNamespace;
  HERALD_MODEL?: string;
  SOVEREIGN_SALT?: string;
  SCRUBBER_SECRET?: string;
  LINKEDIN_ACCESS_TOKEN?: string;
  LINKEDIN_AUTHOR_URN?: string;
  X_BEARER_TOKEN?: string;
  FACEBOOK_PAGE_ACCESS_TOKEN?: string;
  FACEBOOK_PAGE_ID?: string;
}

export type PublishPlatform = "linkedin" | "x" | "facebook";
