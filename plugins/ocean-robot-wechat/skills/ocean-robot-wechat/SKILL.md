---
name: ocean-robot-wechat
description: Create or revise Zhejiang University Ocean Robot Association WeChat articles and automatically select branded visual components. Use for association public-account copy, article structures, covers, section graphics, robot parameter cards, activity posts, recruitment posts, and reusable ocean-robot content assets. Do not use for unrelated academic research or generic social media work.
---

# Ocean Robot WeChat

Create mobile-first WeChat articles that consistently use the association's brand and reusable visual components. The house style is lively editorial collage, not a stack of rounded cards.

## Primary authoring surface

- Use Ardot Remote MCP as the primary authoring surface for templates, articles, and reusable components.
- Build with native Ardot frames, text layers, variables, image fills, and reusable components. Do not treat an imported HTML page or a flattened image as the editable source of truth.
- Keep local HTML only as a secondary preview or handoff format when useful.
- Create reusable Ardot components with stable Chinese names prefixed by `组件｜`, and keep the component definitions beside the article frame on the same canvas.
- Record the Ardot file URL, article frame node ID, component-library node ID, and reusable component node IDs in the output metadata.
- Use Ardot for the editable design source and `scripts/compile_wechat.py` for a deterministic WeChat-safe HTML handoff. The two outputs must use the same component IDs.

## Component selection

Before composing an article or generating an image, query the component registry:

```bash
python3 scripts/components.py list
python3 scripts/components.py recommend popular-science --style hard-tech
python3 scripts/components.py show layout.swipe-gallery
```

Then query the asset registry before generating any new illustration:

```bash
python3 scripts/assets.py search "声呐 popular-science"
python3 scripts/assets.py recommend recruitment
python3 scripts/assets.py list --style technical-line
```

Use the returned component IDs in the working notes and final artifact metadata. Prefer `spot.*` for small inline illustrations and reserve `visual.*` for large backgrounds. Read [references/component-catalog.md](references/component-catalog.md) when selecting or adapting a component. Read [references/visual-system.md](references/visual-system.md) when generating a new image or styling a complete article.
Read [references/asset-library.md](references/asset-library.md) when adding, validating, or routing reusable imagery.

## Working rules

- Treat `assets/association-logo.jpg` as the canonical logo. Never redraw it with image generation.
- Reuse a suitable existing asset before generating a new generic background.
- Generate a new image when the article has a subject-specific robot, event, experiment, or project that the current assets cannot represent.
- Prefer text-free generated images. Add Chinese copy, labels, data, and the logo during deterministic layout so they remain accurate.
- Treat cutout illustrations as compact spot assets: one readable subject group, a true-alpha PNG with transparent corners, and a 48-120 px default display size. The layout, not the bitmap, supplies any pale tile or paper background.
- Choose one dominant illustration style per article. Use `watercolor-cutout` for friendly recruitment, `clay-miniature` for hands-on recruitment, training, and laboratory stories, `paper-cut` for events and field stories, `hard-tech` for competitions, autonomy, sensing, and research milestones, `mechanical-industrial` for hardware teardown, fabrication, and repair, `isometric-system` for mission chains, system relationships, and test workflows, `aqua-glass` for sonar, navigation, data links, and future-facing perception, `technical-line` for diagrams and precise explanations, and `editorial-decor` only as supporting punctuation.
- Do not repeatedly mix tactile families (`watercolor-cutout`, `paper-cut`, `clay-miniature`) with engineering-render families (`hard-tech`, `mechanical-industrial`, `isometric-system`, `aqua-glass`) in one article. `technical-line` and `editorial-decor` may support any dominant family when kept sparse.
- Use one small illustration per two to three content blocks. Do not decorate every heading or fill every gap.
- In Ardot, apply each `spot.*` bitmap as the image fill of a reusable native component. Article layouts should use or copy the native component rather than placing loose image layers without a component identity.
- Use real project facts only. Keep placeholders visibly labeled and remove them before a final deliverable.
- Treat the dark blue in the supplied logo as protected logo artwork only. Never sample it for fills, outlines, text, shadows, or large background areas.
- Use the light editorial palette `#2E4148`, `#53666C`, `#6DA7CF`, `#8CCCD3`, `#EAF7F8`, `#F09A7C`, `#F2D6A2`, `#F7FBFA`, and white. Do not introduce navy or deep blue.
- Vary the reading rhythm. In every long article, combine open text, edge-to-edge images, offset pairs, floating labels, a horizontal swipe strip, and sparse spot illustrations. Never place more than two conventional cards consecutively.
- A swipe component must remain useful when dragging is unavailable: show a visible next-image edge and include a short “左右滑动” cue.
- Optimize for phone reading: strong hierarchy, short lines, generous spacing, and one visual purpose per component.
- Save new project assets under `output/ocean-robot-wechat/<article-slug>/assets/` with descriptive filenames.

## Image workflow

Use the image generation capability for bitmap illustrations and backgrounds. State the asset or component ID, style, target aspect ratio, intended overlay zone, palette, and no-text constraint in the prompt. Inspect the result before using it.

For reusable cutouts, never accept a rendered checkerboard as transparency. Prefer native true alpha. If image generation returns an opaque file, isolate the subject on `#F000F0`, run `scripts/chroma_to_alpha.sh INPUT OUTPUT`, and validate the output with `scripts/assets.py validate` before registration.

For an Ardot deliverable, upload approved bitmap assets through `register_assets`, then apply them to component frames through `upload_images`. Always preserve the supplied logo as an uploaded image fill; never recreate it.

## Compile and validate

Store a structured article specification beside its assets, then run:

```bash
python3 scripts/compile_wechat.py path/to/article.json --output path/to/output
python3 scripts/compile_wechat.py path/to/article.json --output path/to/output --check
python3 scripts/assets.py validate
```

The compiler creates `index.html`, `wechat.html`, and `compile-report.json`. `wechat.html` uses inline styles, contains no scripts, preserves horizontal swipe behavior, and keeps component IDs as `data-component` attributes. Treat a failed `--check` as a blocking QA issue.

For official-account delivery, create a draft first. Upload content images and the cover through the configured publisher MCP, replace local image paths with returned WeChat CDN URLs, then create the draft idempotently. Never submit formal publication without a separate explicit confirmation. Do not generate or replace QR codes; use only the user-provided QR assets.
