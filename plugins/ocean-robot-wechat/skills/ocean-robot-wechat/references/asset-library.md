# AI-native asset library

`references/assets.json` is the machine-readable source of truth. Asset IDs are stable even if filenames or Ardot node IDs change.

## Selection order

1. Search by topic and use: `python3 scripts/assets.py search "ROV training"`.
2. Ask for an article-type route: `python3 scripts/assets.py recommend recruitment`.
3. Keep the returned `dominant_style` for the full article.
4. Generate only when no registered asset represents the subject or action.
5. Register approved additions in `assets.json`, create or update their native Ardot component, then run validation.

## Style routing

- Recruitment and community: `watercolor-cutout`; choose `clay-miniature` when the story emphasizes making, training, or laboratory participation.
- Event and field test: `paper-cut`; use `mechanical-industrial` when the story centers on equipment or operation.
- Popular science and robot profiles: `technical-line`; switch to `aqua-glass` when the subject is sonar, navigation, data links, or future-facing perception, `isometric-system` when relationships or workflows matter, or `hard-tech` for autonomy, control, or a hero machine.
- Project updates and competition: `hard-tech`; use `aqua-glass` for a light, transparent view of sensing or navigation, `isometric-system` for mission chains and validation workflows, or `mechanical-industrial` when the evidence is a physical module or workshop process.
- Hardware teardown, fabrication, repair, and training: `mechanical-industrial`, supported by `technical-line` diagrams.
- `editorial-decor` is a supporting layer, never the dominant illustration system.

The difference is semantic, not merely cosmetic: `hard-tech` presents a finished system and its capability; `mechanical-industrial` exposes how a part is built, connected, serviced, or operated. Keep one of them dominant in a single article.

`clay-miniature` makes participation and hands-on learning feel approachable without adding cartoon faces. `isometric-system` explains how multiple platforms, sensors, and steps relate without relying on labels baked into the image.

`aqua-glass` presents sensing and navigation as translucent engineering objects rather than glowing interface graphics. Keep it pale aqua, white, and silver with tiny coral safety accents; no navy, deep-blue panels, neon halos, HUDs, or baked labels.

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

Hard-tech and mechanical cutouts carry more surface detail than cartoon assets. Display them at 80-160 px for inline use or 180-280 px for a feature moment; do not shrink exploded assemblies until the internal parts become noise.
