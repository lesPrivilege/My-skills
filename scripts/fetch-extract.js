#!/usr/bin/env node
// fetch-extract.js — Mozilla Readability extraction
// Input:  HTML file path (arg 1)
// Output: Clean article HTML to stdout (or original if extraction fails)
// Exit:   0 (extracted) or 1 (fallback to original)

const { JSDOM } = require('jsdom');
const { Readability } = require('@mozilla/readability');
const fs = require('fs');
const path = require('path');

const htmlPath = process.argv[2];
if (!htmlPath) {
  console.error('Usage: fetch-extract.js <html_file>');
  process.exit(1);
}

const html = fs.readFileSync(htmlPath, 'utf-8');

try {
  const dom = new JSDOM(html, { url: process.argv[3] || 'https://example.com' });
  const reader = new Readability(dom.window.document);
  const article = reader.parse();

  if (article && article.content) {
    const output = `<!-- title: ${article.title || ''} -->
<!-- byline: ${article.byline || ''} -->
<!-- excerpt: ${(article.excerpt || '').slice(0, 200)} -->
<article>
${article.content}
</article>`;
    console.log(output);
    process.exit(0);
  }
} catch (e) {
  // readability failed silently, fall through
}

// Fallback: output original HTML
console.log(html);
process.exit(1);
