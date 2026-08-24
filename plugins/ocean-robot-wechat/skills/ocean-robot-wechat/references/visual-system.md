# Visual system

## Brand foundation

- Ink: `#2E4148`.
- Body: `#53666C`.
- Sky: `#6DA7CF`.
- Aqua: `#8CCCD3`.
- Pale water: `#EAF7F8`.
- Coral: `#F09A7C`.
- Sand: `#F2D6A2`.
- Foam: `#F7FBFA`.
- Base: white or warm foam.
- Canonical logo: `assets/association-logo.jpg`.

The dark blue inside the supplied logo is protected artwork, not a palette token. Do not sample it for fills, outlines, text, shadows, or backgrounds. Do not introduce navy, deep blue, purple, or neon cyan.

## Visual language

Aim for university research communication with ocean depth, engineering precision, and clear mobile reading. Suitable motifs include sonar rings, bathymetric contours, soft wave layers, circuit traces, propeller geometry, AUVs, ROVs, and laboratory or field-test imagery.

Avoid generic AI glows, fantasy submarines, decorative dashboards, fake technical labels, and generated Chinese text.

## Image generation defaults

- No text, letters, numbers, watermark, or generated logo.
- Keep a clearly stated empty overlay zone.
- Use 3:2 landscape for section and parameter visuals.
- Use 4:5 portrait for closing cards and recruitment assets.
- Keep important subjects large enough to read on a phone.
- Treat generated robots as illustrative unless they are based on verified project references.

## Reusable asset styles

- `watercolor-cutout`: friendly ROVs, AUVs, tools, buoys, and small science characters. Best for recruitment and introductions.
- `paper-cut`: tactile field-test, event, and team-story illustrations. Best for openings or one major transition.
- `hard-tech`: near-future hard-surface ROVs, sensing arrays, and autonomy electronics. Use graphite and light aluminum with restrained aqua and coral safety accents; avoid neon glows and game-interface decoration. Best for competitions, research milestones, sensing, autonomy, and control.
- `mechanical-industrial`: serviceable thrusters, joints, reels, fasteners, bearings, and workshop assemblies. Use believable steel, aluminum, and sparse orange anodized accents; show construction or operation rather than science-fiction styling. Best for teardown, fabrication, repair, and training.
- `clay-miniature`: tactile matte miniatures of ROVs, control stations, tools, and pool tests. Keep the engineering believable and omit cartoon faces. Best for hands-on recruitment, training, and laboratory stories.
- `isometric-system`: clean compact system scenes with simplified geometry and restrained 3D shading. Best for mission chains, module relationships, pool-test workflows, and multi-platform explanations; do not bake labels or dashboard UI into the image.
- `aqua-glass`: translucent pale-aqua ROVs, sensing fields, navigation loops, and data-link relationships rendered as bright engineering miniatures. Use white, light silver, and tiny coral safety accents; never introduce navy, dark-blue panels, neon halos, HUDs, or baked labels. Best for sonar, navigation, communications, and future-facing perception.
- `technical-line`: native SVG diagrams and icons with precise strokes. Best for science, parameters, systems, and process explanations.
- `editorial-decor`: native SVG waves, routes, bubbles, sonar rings, and photo corners. Use only as punctuation.

Use one dominant style per article. A supporting technical or decorative SVG may accompany it, but do not repeatedly mix watercolor with hard-tech or mechanical assets in the same article.

## Small illustration defaults

- Use a square canvas and one clearly recognizable subject group.
- Cutouts must be true-alpha PNGs. All four corner alpha values must be zero; a baked checkerboard is a failed asset.
- Supply pale water, foam, or warm paper backgrounds during layout, never inside the reusable cutout bitmap.
- Keep the subject readable at 48-120 px; larger feature cutouts may display at 160-280 px.
- Use the light editorial palette and charcoal engineering detail. Never use deep blue outside the canonical logo.
- Do not add labels, frames, badges, scenery, or decorative data UI unless the asset category explicitly calls for a scene.
- Prefer `cutout.*` or `spot.*` inside paragraphs and heading rows; reserve `visual.*` for near-full-width backgrounds.
- Place one small illustration per two to three content blocks. Empty space is part of the design.

## Layout integration

Overlay the canonical logo and all copy after image generation. Keep normal body text on solid or near-solid backgrounds. Use illustrated backgrounds for openings, transitions, parameter summaries, and endings rather than behind long paragraphs.

The existing `visual.*` backgrounds predate the light-only palette. Do not select them automatically. If one is reused, apply a deterministic lightening treatment so the rendered result contains no navy or deep-blue area.
