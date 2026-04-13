# LearnOnTheGo Phase A.5 Implementation Plan

Last Updated: April 13, 2026
Status: Active

## Objective

Deliver a production-ready content-to-podcast workflow foundation with premium UX and clear BYOK behavior.

## Scope for Phase A.5

Included:
- Source intake for pasted text, `.txt`, `.md`, `.pdf`
- URL ingestion entry path with diagnostics scaffold
- Model selection via presets with advanced override
- Voice + duration controls in unified generation form
- BYOK fallback to environment mode when keys are missing/invalid
- Summary/script preview before audio generation
- Citation-ready payload handling for document/URL sources

Deferred:
- Full media processing for third-party audio/video
- Direct Spotify-audio ingestion
- Rich citation rendering UI beyond baseline references

## Workstreams and Tickets

### A. Product + API Contract

A5-001: Source intake contract
- Define normalized request schema for text/file/url inputs.
- Add source metadata fields (`source_type`, `source_uri`, `source_title`).
- Acceptance: schema versioned and documented in API docs + PRD.

A5-002: Summary/script response contract
- Define response payload with script sections, estimated duration, citations array.
- Acceptance: frontend can render script preview without ad hoc mapping.

A5-003: Generation mode contract
- Define explicit `execution_mode` (`byok` or `environment`) in response.
- Acceptance: UI can display actual mode used for every run.

### B. Frontend UX + Interaction

A5-010: Create screen source switcher
- Add source tabs/options: Text, File, URL.
- Add validation and empty-state guidance per source type.
- Acceptance: user can submit any supported source type from one workflow.

A5-011: Model selection UX
- Add presets (`Cost Saver`, `Balanced`, `High Fidelity`).
- Add advanced mode with raw provider/model picker.
- Acceptance: selection is persisted during session and included in request.

A5-012: BYOK status + fallback messaging
- Show key status before submit.
- On fallback, show explicit message: "Using environment provider path".
- Acceptance: no silent provider/mode switching.

A5-013: Script preview and confirm flow
- Display generated summary/script before TTS handoff.
- Allow regenerate action with changed model/duration.
- Acceptance: user can review and then generate audio in a controlled flow.

### C. Backend Services + Validation

A5-020: File ingestion pipeline hardening
- Parse `.txt`, `.md`, `.pdf` with limits and validation errors.
- Acceptance: predictable errors for unsupported files/size violations.

A5-021: URL diagnostics scaffold
- Validate URL format and classify likely source type.
- Return actionable failures (`unreachable`, `unsupported`, `no transcript`).
- Acceptance: frontend gets structured diagnostics instead of generic 500s.

A5-022: Duration best-effort policy
- Implement script sizing heuristics targeting requested duration (tolerance window).
- Acceptance: generated content falls within agreed tolerance in most runs.

### D. Testing + Reliability

A5-030: Frontend integration tests
- Test source switching, model preset selection, BYOK fallback banner, preview render.
- Acceptance: CI coverage for core create->preview path.

A5-031: Backend contract tests
- Test request/response schema for each source type.
- Test BYOK missing/invalid fallback semantics.
- Acceptance: CI gate for source contract + mode contract.

A5-032: Smoke scenario expansion
- Add smoke scenario for create flow with each supported source input type.
- Acceptance: scripted pass/fail signatures documented in TESTING_GUIDE.

## Milestones

M1: Contracts + source intake UI scaffold
- Tickets: A5-001, A5-010, A5-021

M2: Model/BYOK + preview flow
- Tickets: A5-003, A5-011, A5-012, A5-013

M3: Reliability gates
- Tickets: A5-030, A5-031, A5-032

## Exit Criteria

- User can generate from text and supported files end-to-end in production UI.
- UI clearly indicates generation mode and fallback behavior.
- Script preview is available prior to final audio generation.
- CI covers core source contracts and fallback semantics.
- Documentation is updated: PRD, ROADMAP, PROGRESS, INTEGRATION_CHECKLIST.
