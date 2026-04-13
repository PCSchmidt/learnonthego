# LearnOnTheGo UI Style Spec

Last Updated: April 13, 2026

## Intent

Visual direction is premium, restrained, and professional.

The interface should feel:
- high-end
- editorial
- focused
- not playful

## Core Rules

1. Geometry
- Use square corners for primary UI surfaces and controls.
- Do not use rounded cards/buttons unless there is a specific exception.

2. Color Roles
- Canvas: near-black
- Rail/shell surfaces: deep graphite
- Light working panels: warm off-white
- Accent: muted brass
- Danger actions: muted red tones

3. Typography
- Display/headings: Cormorant Garamond (web)
- Body/interface: Manrope (web)
- Use uppercase labels with letter spacing for controls and section identifiers.

4. Spacing
- Use a fixed spacing scale from `src/theme/tokens.ts`.
- Prefer larger, deliberate spacing over dense clustering.

5. Visual Hierarchy
- Eyebrow -> Display heading -> Supporting body copy -> Action row.
- Keep information architecture explicit and scannable.

6. Motion
- Use subtle motion only where it clarifies interaction state.
- Avoid decorative motion that reduces perceived seriousness.

## Component Rules

1. Buttons
- Primary: brass background, dark text, uppercase label.
- Secondary: dark panel button with light text.
- Danger: muted red panel with soft red text.

2. Fields
- Uppercase labels.
- Single-line bordered field with square corners.
- Consistent min height and placeholder tone.

3. Panels
- Bordered, square-cornered surfaces.
- Dark and light panel variants allowed.
- Optional eyebrow + heading slots for consistent structure.

## Do Not

- Reintroduce bright playful palettes.
- Mix unrelated fonts per screen.
- Use gradient-heavy glossy consumer styling.
- Add rounded chips/buttons by default.

## References in Code

- Tokens: `frontend/src/theme/tokens.ts`
- Reusable UI primitives:
  - `frontend/src/components/ui/PremiumButton.tsx`
  - `frontend/src/components/ui/PremiumPanel.tsx`
  - `frontend/src/components/ui/PremiumField.tsx`
- Export barrel:
  - `frontend/src/components/index.ts`
