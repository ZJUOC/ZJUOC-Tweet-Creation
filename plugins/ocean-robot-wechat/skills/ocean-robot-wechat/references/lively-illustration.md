# Lively illustration composition

Use this guide when the user asks for a lively, flowing, less containerized article, or when a long article needs visual rhythm beyond static cards.

## Choose a composition role

Infer the role from what the paragraph is doing, then query the registry with `--role`.

- `anchor`: the paragraph names a platform, module, or verified metric. Place one compact subject beside the heading or data point.
- `motion`: the paragraph describes movement, testing, sampling, deployment, debugging, or change. Choose a subject with a connected path or action gesture that points toward the next block.
- `connector`: the paragraph explains a relationship between platforms, sensors, people, or stages. Choose an image whose tether, scan field, route, or signal joins the endpoints.
- `punctuation`: the page only needs a light pause. Prefer native SVG waves, bubbles, routes, or sonar rings instead of another detailed bitmap.

```bash
python3 scripts/assets.py list --style aqua-glass --role motion
python3 scripts/assets.py recommend popular-science --style aqua-glass --role connector
python3 scripts/components.py list --kind spot --style aqua-glass --role motion
```

## Placement modes

- `heading-float`: 80–128 px, beside rather than behind a heading.
- `metric-accent`: 72–112 px, aligned with a verified number and never larger than the number block.
- `edge-float`: 120–190 px, overlap the article edge by 12–28%; alternate left and right across sections.
- `section-transition`: 160–240 px, cross the empty space between two sections so the motion points into the next section.
- `section-bridge`: 160–260 px, span two related blocks without a surrounding card.
- `open-text-overlap`: 120–200 px, overlap only whitespace; never cover body-copy glyphs or reduce the readable text column below 280 CSS px.
- `vertical-margin`: 120–220 px, use a tall connector beside short paragraphs or a timeline.

## Rhythm rules

- Start with an `anchor`, introduce a `motion` component after two or three content blocks, and use a `connector` only when the relationship is part of the meaning.
- Do not repeat the same role more than twice in succession.
- Directly place transparent cutouts on the page. A pale tile is optional punctuation, not the default container.
- Vary scale by at least 1.35× between neighboring spot illustrations and alternate visual weight across the center line.
- Let the direction of a current, tether, arm, route, or scan field point toward the next heading or image.
- Preserve whitespace. One illustration per two to three content blocks remains the default.

## Ardot construction

- Keep the reusable `spot.*` component itself transparent and unframed.
- For controlled overlap, create a fill-free wrapper frame with `layout: none`; place the text in a solid or transparent subframe and the component ref in unused whitespace.
- Set the wrapper to avoid clipping when the spot intentionally crosses an edge.
- A connector may visually span adjacent blocks, but each text block must remain independently readable and editable.
- Library showcase cards are inventory UI only. Do not copy their white card background into the article.

## Mobile fallback

When overlap cannot be preserved in a WeChat-safe export, convert it to a two-column or full-width open placement without adding a card. Keep the component visible, keep the reading order, and remove negative margins before allowing text collision.
