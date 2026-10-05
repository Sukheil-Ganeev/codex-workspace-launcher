---
name: x-phoenix-score
description: Score and improve X/Twitter posts using PhoenixScore-style engagement weights from the open-source xAI X algorithm references. Use when Codex is asked to analyze a draft post, score an x.com/twitter.com status URL, explain why a post might rank well or poorly, compare alternate post drafts, produce a weighted engagement breakdown, or suggest edits that optimize replies, reposts, bookmarks, dwell time, profile clicks, and negative-signal risk.
---

# X Phoenix Score

## Overview

Analyze X posts with the same workflow shape as PhoenixScore: extract the post text, estimate weighted engagement signals, explain the score, and propose concrete rewrites. Treat all scores as directional estimates based on published/open-source weights, not as exact production-ranking predictions.

## Workflow

1. Classify the input:
   - Draft text: score it directly.
   - `https://x.com/.../status/...` or `https://twitter.com/.../status/...`: fetch or inspect the page, then extract only the primary post text. Do not include navigation, replies, sidebars, ads, or engagement counts as post text.
   - Screenshot: transcribe the primary post text and visible counts before scoring.
2. Run the scoring helper when a repeatable baseline is useful:

```bash
python3 ~/.codex/skills/x-phoenix-score/scripts/score_x_post.py --text "Your post text here"
```

Use `--json` for machine-readable output and `--file path/to/post.txt` for longer drafts.
3. Layer on judgment from the post context:
   - If live metrics are visible, mention them separately from predicted probabilities.
   - If the author, niche, timing, or audience is relevant, qualify the score.
   - If the post contains an external link, call out the typical 30-50% reach penalty and suggest moving the link to a reply when appropriate.
4. Return a compact report:
   - Score out of 100 and one-sentence verdict.
   - Weighted breakdown for replies, reposts, bookmarks, profile clicks, link clicks, shares, quotes, favorites, dwell/video, and negative signals.
   - 3-6 concrete signal explanations that reference weights.
   - 2-4 specific edits or alternate drafts.

## Scoring Priorities

Use these weights in explanations and comparisons:

- Repost: `20.0x`
- Quote: `15.0x`
- Reply: `13.5x`
- Profile click: `12.0x`
- Link click: `11.0x`
- Bookmark: `10.0x`
- Share via DM/copy link: `8.0x`
- Favorite/like: `1.0x`

High-value positive patterns:

- A clear question or strong claim that invites replies.
- A compact 100-200 character core idea with enough specificity to hold dwell time.
- Native media, especially video, screenshots, charts, or visual proof.
- Original analysis, useful templates, concrete numbers, or surprising comparisons that invite bookmarks and reposts.
- A first line that can stand alone in the feed.

Negative or dampening patterns:

- External links in the main post.
- Too many hashtags, irrelevant mentions, engagement bait, or vague hype.
- Very short posts with no context, or long posts that bury the payoff.
- Controversy likely to trigger "Not interested", mute, block, or report.
- Claims without proof when the topic demands proof.

## URL Extraction

When the user gives a live X URL, prefer a browser or page-fetch tool available in the current Codex environment. If the page is blocked, ask the user for the post text or screenshot. Never fabricate post text from the URL alone.

For extraction, keep only:

- The primary post body.
- Author handle if it affects interpretation.
- Visible media/link context.
- Visible engagement counts only as optional live context, not as body text.

## Rewrites

When improving a draft, preserve the user's intent and voice. Optimize for the highest weighted plausible action:

- Need replies: add a specific question, binary choice, or informed disagreement hook.
- Need reposts: make the idea self-contained, crisp, and useful to someone else's audience.
- Need bookmarks: add a checklist, framework, numbered steps, code snippet, or resource list.
- Need profile clicks/follows: show credibility with proof, result, artifact, or clear niche.
- Need lower negative risk: remove absolutist wording, unsupported accusations, spammy tags, and unclear claims.

Offer 2-3 variants only when useful: one safer version, one higher-reply version, and one higher-repost/bookmark version.

## Resources

- `scripts/score_x_post.py`: deterministic baseline scorer for draft text.
- `references/algorithm-notes.md`: weight table, caveats, and reporting schema. Read it when a user asks for methodology, exact fields, or wants to port this into an app.

## Required Caveat

Include a short caveat when presenting scores: this uses published/open-source-style weights and heuristics, not X's private production ranking model or the user's account-specific distribution data.
