---
name: fetch
description: >
  Universal URL fetcher with domain routing, cache, readability extraction, and
  fallback chain. Slash command: /fetch <url>. Defines the fetch protocol used by
  other skills (reading-companion, etc.).
---

# Fetch — Universal URL Fetcher

Fetches URL content and returns clean markdown. Infrastructure at `~/Scripts/fetch-url`.

## Architecture

```
~/Scripts/fetch-url   → bash orchestrator (cache → router → fetch → extract → markdown)
~/Scripts/fetch-url-playwright.js  → Playwright fallback for JS-rendered pages
~/Scripts/fetch-extract.js          → Mozilla Readability extraction
~/.cache/fetch/                     → 24h cache (SHA1 key)
```

## Usage

- `/fetch <url>` — fetch with auto strategy
- `/fetch --mode playwright <url>` — force Playwright (for JS-heavy sites not in router)
- `fetch-url --clear-cache` — wipe all cached content
- `fetch-url --clear-url <url>` — refresh a specific URL's cache
- `fetch-url --stats` — cache stats (entries, size, newest/oldest)
- Long output (>15k chars) is smart-truncated: head (8k) + headings + tail (3k)
- Non-text content-types (video/*, image/*, archives) are rejected
- Response >15MB is rejected by curl
- Logs are JSON to stderr; only markdown goes to stdout

## Strategy

| Host pattern | Strategy | Details |
|---|---|---|
| github.com, raw.githubusercontent.com | `curl` | Direct HTTP fetch, no readability |
| arxiv.org, dl.acm.org | `curl` | Direct fetch |
| medium.com, substack.com, bbc.com, nytimes.com, wsj.com | `readability` | curl + readability extraction |
| reddit.com, HN, wikipedia, stackexchange | `readability` | curl + readability extraction |
| *.pdf | `pdf` | curl + MarkItDown conversion |
| everything else | `auto` | try curl + readability; if readability fails, retry playwright + readability |

## Fetch Protocol (for other skills)

When ANY skill needs to fetch external URL content:

1. **WebFetch** — works for docs, GitHub raw, arxiv.
2. **`~/Scripts/fetch-url <url>`** — if WebFetch blocked. Uses local network (VPN,
   proxy). Domain routing, cache, readability extraction, clean markdown output.
3. **Web search** — if steps 1-2 fail (Cloudflare, paywall, empty extract),
   search `"<article title>" site:36kr.com OR site:sspai.com OR site:datalearner.com`
   for third-party coverage. Mark confidence as `medium` or `low`, note source.
4. **Ask user** — if all methods fail, report error.

### Error format

```
❌ Fetch failed: {URL}
   Methods tried: WebFetch, curl, Playwright, web search
   Last error: {details}
   → Provide content directly or try a cached/alternative source.
```

## Dependencies

- `curl` — built-in on macOS
- `pandoc` — HTML-to-markdown (best), fallback to `markitdown`
- `node` + `playwright` — JS-rendered pages
- `node` + `@mozilla/readability` + `jsdom` — article extraction
- Scripts: `~/Scripts/fetch-url`, `~/Scripts/fetch-url-playwright.js`, `~/Scripts/fetch-extract.js`
