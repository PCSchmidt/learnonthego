# UI Consistency Checklist

Last Updated: April 13, 2026

Use this checklist before merging changes to user-facing screens.

## Global

- [ ] Uses tokens from `frontend/src/theme/tokens.ts`
- [ ] No default rounded corners introduced
- [ ] Typography follows display/body roles
- [ ] Action labels and section labels use consistent uppercase treatment
- [ ] Error, loading, and empty states are styled and readable
- [ ] Mobile and desktop layouts are both reviewed

## Auth Screens

### Login
File: `frontend/src/screens/LoginScreen.tsx`

- [ ] Left rail and form panel preserve premium hierarchy
- [ ] Button and field styles match shared tokens/primitives
- [ ] Footer and support copy maintain tone and spacing

### Register
File: `frontend/src/screens/RegisterScreen.tsx`

- [ ] Mirrors Login system without visual drift
- [ ] Password and confirm-password interactions are clear
- [ ] Terms and footer maintain subdued secondary emphasis

## Post-Login Screens

### Home
File: `frontend/src/screens/HomeScreen.tsx`

- [ ] Hero, action panel, and library sections use coherent panel treatment
- [ ] Primary/secondary/danger actions follow button role mapping
- [ ] Lecture cards maintain readable hierarchy and metadata clarity

### Create Lecture
File: `frontend/src/screens/CreateLectureScreen.tsx`

- [ ] Source/model/voice/duration controls are visually unified
- [ ] BYOK status messaging is explicit and discoverable
- [ ] Generation CTA remains primary and unambiguous

### Settings
File: `frontend/src/screens/SettingsScreen.tsx`

- [ ] Available vs roadmap sections are visually distinguished
- [ ] Interactive rows have clear affordance and tap targets
- [ ] Footer status text remains low-emphasis but legible

### Lecture Player
File: `frontend/src/screens/LecturePlayerScreen.tsx`

- [ ] Playback module hierarchy mirrors app visual language
- [ ] Placeholder or active controls use consistent panel style
- [ ] Back/navigation action follows shared button behavior

## Future Screens (When Added)

- [ ] Added to this checklist with file path and acceptance bullets
- [ ] Reviewed against `docs/UI_STYLE_SPEC.md`
