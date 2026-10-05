# X Phoenix Score Notes

## Source Shape

This skill follows the public PhoenixScore app pattern from `hyperbrowserai/hyperbrowser-app-examples/phoenix-score`:

1. Accept draft text or an X/Twitter status URL.
2. If URL, fetch the page and extract the primary post text.
3. Score the post against documented Phoenix-style engagement weights.
4. Return JSON with score, verdict, predictions, weighted breakdown, signal explanations, and suggestions.

## Weight Table

| Signal | Weight | Notes |
| --- | ---: | --- |
| Repost | 20.0 | Highest amplification signal. |
| Quote | 15.0 | Strong amplification plus commentary. |
| Reply | 13.5 | Highest conversational signal. |
| Profile click | 12.0 | Indicates author interest. |
| Link click | 11.0 | Useful but external links can reduce reach. |
| Bookmark | 10.0 | High-value save signal. |
| Share via DM/copy link | 8.0 | Private distribution signal. |
| Favorite/like | 1.0 | Base positive signal. |

Negative signals reduce distribution: Not Interested, Mute, Block, and Report.

## Heuristic Factors

- First 30-60 minutes velocity matters for live posts.
- External links commonly receive a 30-50% reach penalty.
- Native media, especially video and useful screenshots, tends to improve dwell and engagement.
- Questions can improve reply probability because replies carry `13.5x`.
- Useful frameworks, checklists, numbers, and concrete proof improve bookmark/repost probability.
- 100-200 characters is often a strong range for the main idea, but long posts can work when dense and valuable.
- Hashtags have limited value and can look spammy when overused.
- Mentions help only when relevant accounts are likely to engage.

## JSON Schema

```json
{
  "score": 0,
  "verdict": "Short sentence.",
  "predictions": {
    "favorite": 0.0,
    "reply": 0.0,
    "repost": 0.0,
    "bookmark": 0.0,
    "profile_click": 0.0,
    "link_click": 0.0,
    "dwell": 0.0,
    "vqv": 0.0,
    "share": 0.0,
    "quote": 0.0,
    "follow_author": 0.0,
    "not_interested": 0.0,
    "block_author": 0.0,
    "mute_author": 0.0,
    "report": 0.0
  },
  "breakdown": {
    "favoriteWeighted": 0.0,
    "replyWeighted": 0.0,
    "repostWeighted": 0.0,
    "bookmarkWeighted": 0.0,
    "profileClickWeighted": 0.0,
    "linkClickWeighted": 0.0,
    "shareWeighted": 0.0,
    "quoteWeighted": 0.0,
    "negativeTotal": 0.0
  },
  "signals": [
    {
      "type": "positive",
      "label": "Specific signal",
      "detail": "One sentence explanation referencing a weight when relevant."
    }
  ],
  "suggestions": [
    "Specific action to improve the post."
  ]
}
```

## Reporting Rules

- Do not say the score is exact.
- Distinguish predicted probabilities from visible live engagement counts.
- Explain the largest weighted positives and negatives first.
- Suggest edits that preserve meaning before proposing aggressive hooks.
- For comparison tasks, score each version and then choose based on the user's goal: replies, reposts, bookmarks, or low-risk professional reach.
