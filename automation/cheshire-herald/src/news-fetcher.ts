/**
 * Public RSS ingestion — privacy / identity breach headlines (no API keys)
 */

import type { NewsHeadline } from "./env";

const RSS_FEEDS: Array<{ url: string; source: string }> = [
  { url: "https://www.eff.org/rss/updates.xml", source: "EFF" },
  { url: "https://krebsonsecurity.com/feed/", source: "KrebsOnSecurity" },
];

const MISSION_FALLBACK: NewsHeadline[] = [
  {
    title: "Digital sovereignty and local-first AI architectures",
    source: "NoUs Loop Mission Context",
    link_hash: "MISSION",
  },
  {
    title: "Safety Through Severance — human-centric data ownership",
    source: "NoUs Loop Mission Context",
    link_hash: "SEVERANCE",
  },
];

function stripHtml(html: string): string {
  return html
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/gi, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function extractTag(block: string, tag: string): string {
  const re = new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, "i");
  const m = block.match(re);
  return m ? stripHtml(m[1]) : "";
}

function parseRssItems(xml: string, source: string, limit: number): NewsHeadline[] {
  const items: NewsHeadline[] = [];
  const itemBlocks = xml.match(/<item[\s\S]*?<\/item>/gi) ?? [];
  for (const block of itemBlocks.slice(0, limit)) {
    const title = extractTag(block, "title");
    if (!title) continue;
    const link = extractTag(block, "link");
    items.push({
      title: title.slice(0, 300),
      source,
      link_hash: link ? link.slice(0, 32) : title.slice(0, 16),
    });
  }
  return items;
}

async function fetchFeed(
  url: string,
  source: string,
  limit: number
): Promise<NewsHeadline[]> {
  try {
    const res = await fetch(url, {
      headers: { "User-Agent": "Cheshire-Herald/1.0 (NoUs Loop; privacy-news)" },
      cf: { cacheTtl: 3600 },
    });
    if (!res.ok) return [];
    const xml = await res.text();
    return parseRssItems(xml, source, limit);
  } catch {
    return [];
  }
}

export async function fetchPrivacyNewsContext(maxItems = 5): Promise<NewsHeadline[]> {
  const collected: NewsHeadline[] = [];
  for (const feed of RSS_FEEDS) {
    const items = await fetchFeed(feed.url, feed.source, 3);
    collected.push(...items);
    if (collected.length >= maxItems) break;
  }

  const unique = new Map<string, NewsHeadline>();
  for (const h of collected) {
    const key = h.title.toLowerCase().slice(0, 80);
    if (!unique.has(key)) unique.set(key, h);
  }

  const result = [...unique.values()].slice(0, maxItems);
  if (result.length === 0) return MISSION_FALLBACK;
  return result;
}

export function buildNewsContextBlock(headlines: NewsHeadline[]): string {
  return headlines
    .map((h, i) => `${i + 1}. [${h.source}] ${h.title}`)
    .join("\n");
}
