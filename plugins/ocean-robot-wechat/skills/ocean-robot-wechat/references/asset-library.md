# AI-native asset library

`references/assets.json` is the machine-readable source of truth. Asset IDs are stable even if filenames or Ardot node IDs change.

## Selection order

1. Search by topic and use: `python3 scripts/assets.py search "ROV training"`.
2. Ask for an article-type route: `python3 scripts/assets.py recommend recruitment`.
3. Keep the returned `dominant_style` for the full article.
4. Generate only when no registered asset represents the subject or action.
5. Register approved additions in `assets.json`, create or update their native Ardot component, then run validation.

## Style routing

- Recruitment and community: `watercolor-cutout`; use `paper-cut` for one major feature moment.
- Event and field test: `paper-cut`.
- Popular science and robot profiles: `technical-line`.
- Project updates: `technical-line`, with at most one `watercolor-cutout` accent.
- `editorial-decor` is a supporting layer, never the dominant illustration system.

## Cutout production

Generated checkerboard pixels are not transparency. A reusable cutout must have a real alpha channel, transparent corners, and clean internal gaps.

Preferred flow:

1. Generate the isolated subject with no text or logo.
2. If native alpha is unavailable, use a flat `#F000F0` isolation background that also fills internal holes.
3. Convert with `scripts/chroma_to_alpha.sh INPUT OUTPUT`.
4. Preview on `#FFF9F2` and `#EAF7F8` backgrounds.
5. Run `python3 scripts/assets.py validate`.

## Metadata requirements

Every new entry requires `id`, `title`, `kind`, `style`, `path`, `subjects`, and `uses`. Raster cutouts also require `alpha_required: true` and a `source` field. Do not use generated Chinese copy or regenerated association logos inside any asset.

## Frequency and layout

Use one spot illustration per two to three content blocks. Prefer open placement, partial edge overlap, and deliberate scale changes. A tile background may be supplied by the Ardot or HTML layout, but it must not be baked into the reusable PNG.
