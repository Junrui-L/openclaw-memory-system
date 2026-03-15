---
name: summarize
description: "Summarize or extract text/transcripts from URLs, podcasts, and local files. Great fallback for transcribing YouTube videos, podcasts, articles, and documents."
homepage: https://github.com/openclaw/summarize
metadata: { "openclaw": { "emoji": "📝", "requires": { "bins": ["summarize"] } } }
---

# Summarize Skill

Summarize content from URLs, videos, podcasts, and documents.

## When to Use

✅ **USE this skill when:**

- "Summarize this article/video"
- "Transcribe this YouTube video"
- "Get the key points from..."
- "Extract text from..."
- "What does this podcast say?"
- "TL;DR for this URL"

## When NOT to Use

❌ **DON'T use this skill when:**

- Simple text summarization → use model directly
- Local file reading → use read tool
- Code analysis → use coding tools
- Real-time content → may not work

## Installation

The `summarize` CLI tool needs to be installed:

```bash
# Install via npm
npm install -g @openclaw/summarize

# Or via Homebrew (macOS)
brew install openclaw/tools/summarize
```

## Commands

### Summarize URL

```bash
# Summarize a web article
summarize <url>

# Example
summarize https://example.com/article
```

### Transcribe Video/Audio

```bash
# Transcribe YouTube video
summarize --transcribe <youtube-url>

# Transcribe podcast
summarize --transcribe <podcast-url>

# Example
summarize --transcribe https://youtube.com/watch?v=...
```

### Extract Text

```bash
# Extract text only (no summary)
summarize --extract <url>

# Save to file
summarize --extract <url> > output.txt
```

### Podcast Support

```bash
# Summarize podcast episode
summarize <podcast-feed-url>

# Specific episode
summarize --episode <episode-url>
```

## Options

- `--transcribe` - Transcribe audio/video content
- `--extract` - Extract text without summarizing
- `--language <code>` - Specify language (e.g., en, zh, es)
- `--format <type>` - Output format: text, json, markdown
- `--max-length <n>` - Maximum summary length
- `--save <path>` - Save output to file

## Examples

**"Summarize this article"**

```bash
summarize https://example.com/news/article
```

**"Transcribe this YouTube video"**

```bash
summarize --transcribe https://youtube.com/watch?v=abc123
```

**"Get key points from this podcast"**

```bash
summarize --transcribe https://podcast.example.com/episode-42
```

**"Extract text from PDF URL"**

```bash
summarize --extract https://example.com/document.pdf
```

## Supported Sources

- ✅ Web articles and blogs
- ✅ YouTube videos (with captions/transcript)
- ✅ Podcast episodes
- ✅ PDF documents (via URL)
- ✅ Audio files (MP3, WAV, etc.)
- ✅ Video files (MP4, etc.)

## Notes

- Requires internet connection
- Transcription quality depends on source audio quality
- Some sites may block automated access
- YouTube requires available captions or auto-transcript
