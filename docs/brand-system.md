# Latesight Brand System

## Positioning

Latesight uses an industrial editorial style built around precision, restraint, and utility.
The visual language should feel like a serious information system instead of a lifestyle brand, design showcase, or playful consumer app.

Core attributes:

- Professional
- Serious
- Restrained
- Rational
- Ordered
- Tool-first

The intended impression is "brand discipline plus operational clarity", not "cyberpunk" and not "heavy metal".

## Brand Principles

1. Build system feeling before decoration.
2. Use typography, alignment, and spacing as the main visual structure.
3. Keep color accents scarce and intentional.
4. Prefer text labels over icons whenever text can communicate clearly.
5. Motion exists to confirm interaction, not to entertain.
6. Shared brand shell, differentiated product content.

## Shared Experience Rules

All first-party sites under the Latesight network should feel related through:

- Shared logo treatment
- Shared header behavior
- Shared header title pattern: `Latesight > Product Name`
- Shared favicon and Apple touch icon sourced from the site logo
- Shared footer behavior
- Shared type hierarchy
- Shared interaction feedback
- Shared spacing and layout discipline
- Shared color token system

Sites do not need identical hero sections or page densities.
The home site should feel more editorial and navigational.
Tool sites should feel more task-oriented and input-oriented.

## Logo Usage

Preferred source:

- Use the transparent logo asset whenever possible.
- Use the white-background variant only when a raster fallback is necessary.

Placement:

- Default placement is top-left inside a fixed or anchored header.
- Logo should not be oversized.
- Logo should act as a brand anchor, not a decorative hero element on every page.
- For implementation, use a cropped horizontal wordmark asset in the header instead of the uncropped square source image.

Clear space:

- Keep at least one logo-height of visual breathing room around the lockup in dense layouts.

Behavior:

- Logo is clickable and returns to the main site home.
- On hover, use subtle opacity or underline-adjacent treatment if paired with text.
- The same square logo asset should also be used for favicon and Apple touch icon so browser chrome stays consistent across sites.

## Color System

The palette must remain narrow.

Primary colors:

- Black: structural text, strong surfaces, key headings
- Red: brand accent, active state, critical emphasis
- Blue: informational accent, secondary emphasis

Neutral support:

- White or off-white background
- One to three gray steps only

Rules:

- Red should be visually dominant over blue.
- Blue must not compete with the primary call-to-action.
- Avoid gradients with multiple saturated hues.
- Avoid colorful iconography and rainbow status systems.

Suggested token directions:

- `--color-ink`: near-black
- `--color-paper`: off-white
- `--color-line`: low-contrast border gray
- `--color-accent-red`: controlled signal red
- `--color-accent-blue`: muted industrial blue
- `--color-muted`: secondary copy gray

## Typography

The type system should feel stable, engineered, and readable.

Guidelines:

- Prefer sans-serif families with clean geometry and neutral personality.
- Avoid soft rounded fonts.
- Avoid overly futuristic or gimmicky techno fonts.
- Use weight and spacing more than color to create hierarchy.

Hierarchy behavior:

- Large headlines should be concise and dense.
- Section labels can use uppercase tracking.
- Metadata can use mono or mono-adjacent styling sparingly.

Recommended usage:

- Headline: bold sans-serif
- Body: neutral sans-serif
- Metadata: restrained monospace or tightly tracked sans-serif
- Use English punctuation marks consistently in UI copy, including Chinese text contexts when punctuation is needed

## Layout

Layout should communicate control and consistency.

Rules:

- Use a strong max-width container.
- Align content to a visible grid.
- Prefer asymmetric editorial spacing over centered marketing layouts everywhere.
- Use generous vertical rhythm.
- Reduce decorative blocks that do not carry content or utility.

Shape language:

- Prefer square corners or small radii
- Avoid oversized pills unless the element is intentionally signal-like
- Borders may be visible and crisp
- Shadows should be weak and rare

## Components

### Header

Shared across sites.

Reference direction:

- The header may borrow from Apple's high-clarity structure: left-aligned logo, right-aligned text navigation, generous whitespace, and a quiet divider line.
- Do not borrow Apple's soft consumer tone. Latesight should remain more technical, sharper, and more restrained.

Should include:

- Logo
- Optional bold slogan immediately following the logo on the home site when a stable brand line is needed
- Optional network/site label
- Breadcrumb-style title in the form `Latesight > Product Name` for every secondary site
- Small set of text navigation items

Header title rule:

- The home site may use its own index-oriented title treatment.
- If the home site uses a slogan after the logo, keep it short, bold, and typographically aligned with the wordmark.
- Every secondary site must use `Latesight > Product Name`.
- Use the human-facing product name in header and browser tab title, for example `Latesight > Word Lens`.
- Internal site keys such as `dict`, `admin`, or future tool identifiers may exist in routes and config, but should not surface in the visible header title.
- Header title and browser tab title should stay consistent for every secondary site.
- This title pattern is part of the brand shell, not an optional local customization.

Should not include:

- Busy icon clusters
- Excessive utility links
- Large promotional banners

### Footer

Shared structure across sites.

Should include:

- Brand or copyright line
- Domain or site grouping hints
- Small set of text links

Tone:

- Minimal
- Quiet
- Informational

### Buttons

Buttons should read as commands, not toys.

Rules:

- Prefer text-first buttons
- Use clear labels
- Avoid icon-only buttons unless space is constrained and meaning is universally obvious
- Keep radius low
- Use border and fill contrast instead of heavy shadows

### Links

Links must be visibly interactive.

Rules:

- Default state should already feel clickable through color, underline offset, or contrast
- Hover state should increase clarity
- Underline is preferred for inline links and text actions

### Inputs

Inputs must feel operational and reliable.

Rules:

- Clear border
- Visible focus ring or focus border
- No soft glassmorphism
- Placeholder text must remain legible but subdued

## Motion

Motion should confirm interaction and improve orientation.

Allowed motion:

- Underline reveal
- Color transition
- Border-color transition
- Small vertical or horizontal shift
- Subtle fade-in for content sections

Disallowed motion:

- Bounce
- Elastic scaling
- Continuous floating
- Decorative rotation
- Large parallax effects

Interaction timing:

- Prefer 150ms to 220ms for hover and focus transitions
- Keep easing simple and controlled

## Hover And Focus Rules

When the pointer is over clickable content, the interface must acknowledge it.

Minimum requirement:

- Text links: underline, underline color shift, or weight shift
- Buttons: border or fill response
- Cards: border, background, or title underline response
- Inputs: strong focus outline or border change

Accessibility rule:

- Keyboard focus must be at least as visible as pointer hover

## Information Language

Latesight should use a consistent micro-language for system cues.

Useful patterns:

- Section numbers such as `01`, `02`, `03`
- Labels such as `STATUS`, `DOMAIN`, `LIVE`, `BUILDING`
- Compact metadata rows

This supports the industrial, operational tone without needing extra graphic decoration.

## Home Site Versus Tool Sites

### Home Site

Should emphasize:

- Brand frame
- Site index
- Clear grouping
- Editorial rhythm

Can afford:

- More atmosphere
- More whitespace
- More overview framing

### Tool Site

Should emphasize:

- Immediate task entry
- Input clarity
- Result readability
- Operational efficiency

Must avoid:

- Overly dramatic hero treatment
- Navigation clutter
- Decorative distractions around the primary workflow

## Anti-Patterns

Avoid the following:

- Neon-heavy palettes
- Excessive icon usage
- Soft bubbly SaaS visuals
- Large rounded cards everywhere
- Decorative 3D objects
- Unnecessary glassmorphism
- Inconsistent hover rules
- Multiple competing accent colors
- Pages that look like generic startup templates

## Implementation Order

1. Finalize shared design tokens
2. Build shared logo, header, footer, and page shell
3. Apply shared interaction rules
4. Rebuild home with the shared system
5. Build the dictionary site within the same shell but with a more operational content layout
