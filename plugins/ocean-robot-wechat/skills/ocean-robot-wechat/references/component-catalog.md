# Component catalog

The machine-readable source of truth is `components.json`. Query it through `scripts/components.py` before composing an article.

## Component families

- `brand.*`: canonical association identity assets.
- `spot.*`: small, simple inline illustrations used beside headings or short information blocks.
- `visual.*`: larger bitmap backgrounds used for openings, parameter panels, and article endings.
- `block.*`: deterministic article blocks whose text and data are supplied at runtime.

## Small plugin illustrations

These are the default assets when a prompt asks for a plugin image, icon-like picture, or paragraph decoration. Display them at about 48-120 px rather than as a full-width image.

### `spot.sonar-rov`

- File: `assets/spot-sonar-rov-tile.png`
- Use for: sonar, underwater sensing, communications, detection.

### `spot.auv`

- File: `assets/spot-auv-tile.png`
- Use for: autonomous platforms, robot introductions, navigation.

### `spot.thruster`

- File: `assets/spot-thruster-tile.png`
- Use for: propulsion, hardware, control, mechanical systems.

### `spot.wave`

- File: `assets/spot-wave-tile.png`
- Use for: section punctuation, ocean topics, article endings.

## Hard-tech components

Use these for finished systems, perception, autonomy, competitions, and research milestones. Their Ardot component names begin with `组件｜硬核科技｜`.

- `spot.hard-tech-rov`: complete ROV core body, hero machine or platform introduction.
- `spot.hard-tech-sonar`: multibeam sonar array, mapping and perception.
- `spot.hard-tech-autonomy`: embedded autonomy core, control and sensor fusion.

## Mechanical-industrial components

Use these for construction, teardown, service, fabrication, and operations. Their Ardot component names begin with `组件｜机械工业｜`.

- `spot.mechanical-thruster`: exploded thruster assembly, propulsion and repair.
- `spot.mechanical-joint`: robotic arm joint, actuator and sampling hardware.
- `spot.mechanical-tether`: ROV tether reel, deck operation and field-test equipment.

## Clay-miniature components

Use these for hands-on recruitment, training, and approachable laboratory stories. Their Ardot component names begin with `组件｜黏土模型｜`.

- `spot.clay-workbench`: ROV assembly stand and tools.
- `spot.clay-pool-test`: miniature ROV pool-test scene.
- `spot.clay-control-station`: portable control station, joystick, cable, and ROV.

## Isometric-system components

Use these when readers need to understand relationships, sequence, or an operating workflow. Their Ardot component names begin with `组件｜等轴工程｜`.

- `spot.isometric-mission`: research boat, tethered ROV, and seabed target mission chain.
- `spot.isometric-sensors`: ROV with sonar, camera, and depth-sensor modules.
- `spot.isometric-pool-workflow`: pool, control desk, cable, and ROV test workflow.

## Aqua-glass components

Use these for a light, transparent technology treatment of sensing, navigation, communications, and future-facing perception. Their Ardot component names begin with `组件｜冰蓝透明｜`.

- `spot.aqua-glass-rov`: translucent ROV platform, robot profile and sensing carrier.
- `spot.aqua-glass-sonar`: silver sonar module with a pale-aqua scanning fan.
- `spot.aqua-glass-navigation`: AUV, three waypoints, route loop, and tethered surface buoy.
- `spot.aqua-glass-current`: AUV with a connected S-shaped current trail; `motion` role.
- `spot.aqua-glass-sampling`: manipulator holding a transparent sample capsule; `motion` role.
- `spot.aqua-glass-relay`: surface buoy and ROV joined by a flowing tether; `connector` role.

Query `scripts/components.py` with `--role anchor`, `--role motion`, or `--role connector` when the paragraph's action matters more than its noun. For placement and mobile fallback, read `lively-illustration.md`.

## Legacy large background assets

These assets predate the light-only palette and are no longer selected automatically. Reuse them only with a deterministic lightening treatment that removes navy and deep-blue areas from the rendered article.

### `visual.sonar-opener`

- File: `assets/sonar-section-opener.png`
- Use for: popular science, sensing, navigation, mapping, underwater perception.
- Aspect ratio: 3:2 landscape.
- Overlay zone: upper-left and upper-center water area.
- Avoid: dense text over the seabed contours.

### `visual.parameter-blueprint`

- File: `assets/auv-parameter-card.png`
- Use for: robot introductions, project profiles, specifications, technical summaries.
- Aspect ratio: 3:2 landscape.
- Overlay zone: upper-left and center-left pale area.
- Avoid: covering the vehicle silhouette with long paragraphs.

### `visual.closing-ocean`

- File: `assets/ocean-closing-card.png`
- Use for: article endings, recruitment, event registration, follow prompts.
- Aspect ratio: 4:5 portrait.
- Overlay zone: central pale area.
- Avoid: using the original dark wave edges; lighten the image before layout, then place the QR code on a solid pale area.

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
python3 scripts/components.py list --kind spot --style mechanical-industrial
python3 scripts/components.py recommend project-update --style hard-tech
python3 scripts/components.py show <component-id>
python3 scripts/components.py validate
```

Keep IDs stable so a future MCP server can expose the same catalog without changing article prompts.
