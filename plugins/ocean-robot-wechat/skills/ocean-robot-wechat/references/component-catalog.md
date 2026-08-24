# Component catalog

The machine-readable source of truth is `components.json`. Query it through `scripts/components.py` before composing an article.

## Component families

- `brand.*`: canonical association identity assets.
- `spot.*`: small, simple inline illustrations used beside headings or short information blocks.
- `visual.*`: larger bitmap backgrounds used for openings, parameter panels, and article endings.
- `block.*`: deterministic article blocks whose text and data are supplied at runtime.

## Small plugin illustrations

These are the default assets when a prompt asks for a plugin image, icon-like picture, or paragraph decoration. Display them at about 48-120 px rather than as a full-width image.

### Watercolor cutouts

- `spot.bubble-rov`: friendly ROV, introduction, recruitment, training.
- `spot.thruster-tools`: propulsion, hardware, debugging, training.
- `spot.sonar-fish`: sonar, sensing, competition, autonomy.
- `spot.auv-glider`: navigation, autonomy, robot profiles, popular science.
- `spot.smart-buoy`: sensing, field tests, popular science.

### Paper-cut feature illustrations

- `spot.robotic-arm-sample`: sampling, hardware, recruitment, events.
- `spot.field-test-boat`: field tests, events, recruitment.

All files are registered in `assets.json`. Cutout backgrounds are supplied at layout time; they are not baked into the PNG.

## Runtime blocks

Runtime blocks do not contain invented copy. Fill their required fields from user material.

- `block.key-takeaway`: `label`, `summary`.
- `block.metrics`: one to four `label` and `value` pairs with verified sources.
- `block.robot-spec`: `name`, `platform_type`, `mission`, `modules`, optional verified numeric specs.
- `block.timeline`: two to five dated or named milestones.
- `block.quote`: `quote`, `speaker`, `role`, optional source.
- `block.references`: ordered citations or source links.
- `block.qr-footer`: `cta`, `description`, and a user-provided QR asset.

## Adding a component

Add one entry to `components.json`, add the corresponding asset if needed, and verify:

```bash
python3 scripts/components.py list
python3 scripts/components.py show <component-id>
```

Keep IDs stable so a future MCP server can expose the same catalog without changing article prompts.
