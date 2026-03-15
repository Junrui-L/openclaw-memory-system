---
name: agent-browser
description: "Browse and extract content from web pages using headless browser. Use when: user asks to visit a URL, analyze web content, extract text from websites, or interact with web pages. NOT for: simple searches (use tavily), local files, or API calls."
homepage: https://github.com/openclaw/agent-browser
metadata: { "openclaw": { "emoji": "🌐", "requires": { "bins": ["curl", "puppeteer", "playwright"] } } }
---

# Agent Browser

Browse and extract content from web pages.

## When to Use

✅ **USE this skill when:**

- "Visit this URL"
- "Analyze this webpage"
- "Extract content from..."
- "What's on this page?"
- "Read this article"
- "Check this website"

## When NOT to Use

❌ **DON'T use this skill when:**

- Simple web search → use tavily-search
- API calls → use curl/http tools
- Local files → use read tool
- Already have the content

## Installation

Requires headless browser tools:

```bash
# Option 1: Puppeteer
npm install -g puppeteer

# Option 2: Playwright
npm install -g playwright
npx playwright install chromium

# Option 3: Simple curl (limited)
# Already available in most systems
```

## Commands

### Basic Page Fetch

```bash
# Simple fetch with curl
curl -s -L "https://example.com" | head -100

# With user agent
curl -s -L -A "Mozilla/5.0" "https://example.com"
```

### Extract Text Content

```bash
# Using lynx (if available)
lynx -dump -nolist "https://example.com"

# Using html2text (if available)
curl -s "https://example.com" | html2text
```

### JavaScript-Heavy Sites

For sites requiring JavaScript:

```bash
# Using puppeteer-cli (if installed)
puppeteer-cli print "https://example.com"

# Using playwright (if installed)
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('https://example.com');
  const text = await page.evaluate(() => document.body.innerText);
  console.log(text);
  await browser.close();
})();
"
```

## Examples

**"Visit this link and tell me what it says"**

```bash
# Try simple fetch first
curl -s -L "https://example.com/article" | grep -o '<title>[^<]*</title>' | sed 's/<[^>]*>//g'

# Get main content
curl -s -L "https://example.com/article" | sed 's/<[^>]*>//g' | tr -s '\n' | head -50
```

**"Extract article text"**

```bash
# Remove HTML tags and get readable text
curl -s "https://example.com/article" | \
  sed 's/<script[^>]*>[\s\S]*?<\/script>//g' | \
  sed 's/<style[^>]*>[\s\S]*?<\/style>//g' | \
  sed 's/<[^>]*>//g' | \
  tr -s '\n ' | \
  head -100
```

**"Check if website is up"**

```bash
curl -s -o /dev/null -w "%{http_code}" "https://example.com"
```

## Limitations

- JavaScript-heavy sites may not work with simple curl
- Some sites block automated access
- Rate limits may apply
- Cannot interact with forms (read-only)

## Security Notes

- Only visit trusted URLs
- Be careful with authentication pages
- Respect robots.txt
- Don't abuse websites with excessive requests
