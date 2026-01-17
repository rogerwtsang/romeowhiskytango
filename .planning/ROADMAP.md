# Roadmap: Monte Carlo Baseball Simulator

## Overview

Clean up the existing simulation model for robustness, then redesign the GUI from 9 fragmented tabs into a streamlined dashboard that communicates simulation insights at a glance. Finish with comprehensive test coverage.

## Domain Expertise

None

## Phases

- [x] **Phase 1: Type Safety** - Fix 30+ critical type errors preventing crashes
- [ ] **Phase 2: Statistical Robustness** - Audit model assumptions and document findings
- [ ] **Phase 3: GUI Foundation** - Consolidate 9 tabs into focused dashboard structure
- [ ] **Phase 4: Results Visualization** - Charts and metrics that communicate at a glance
- [ ] **Phase 5: Workflow Polish** - Reduce clicks, clean visual hierarchy
- [ ] **Phase 6: Test Coverage** - Implement 19 stubs + integration tests

## Phase Details

### Phase 1: Type Safety
**Goal**: Fix all mypy errors so simulation doesn't crash on edge cases
**Depends on**: Nothing (first phase)
**Research**: Unlikely (internal code fixes, established patterns)
**Plans**: 2 plans

Plans:
- [x] 01-01: Critical path fixes (pa_generator, baserunning, batch, constraint_validator)
- [x] 01-02: Medium priority fixes (position, processor, sacrifice_fly, stolen_bases)

### Phase 2: Statistical Robustness
**Goal**: Audit statistical assumptions and document findings to inform future refinements
**Depends on**: Phase 1
**Research**: Unlikely (audit of existing code documented in ANALYSIS_NOTES.md)
**Plans**: 2 plans

Plans:
- [ ] 02-01-PLAN.md — Audit probability decomposition and hit distribution modeling
- [ ] 02-02-PLAN.md — Audit baserunning and special events, finalize findings document

### Phase 3: GUI Foundation
**Goal**: Replace 9-tab structure with consolidated dashboard layout
**Depends on**: Phase 2
**Research**: Likely (dashboard layout patterns for Tkinter)
**Research topics**: Tkinter dashboard patterns, card-based layouts, ttk theming
**Plans**: TBD

Current tabs to consolidate:
- Setup, Lineup, Distribution, Errors, Baserunning, Run, Results, Compare, History
- Target: 3-4 focused views (Setup/Lineup, Run/Results, Compare, Settings)

### Phase 4: Results Visualization
**Goal**: Charts and metrics that communicate simulation insights at a glance
**Depends on**: Phase 3
**Research**: Likely (charting libraries for Tkinter)
**Research topics**: matplotlib embedding in Tkinter, interactive charts, statistical visualizations
**Plans**: TBD

Core value delivery: Visual clarity — results easy to understand at a glance

### Phase 5: Workflow Polish
**Goal**: Reduce clicks to run simulation, clean visual hierarchy
**Depends on**: Phase 4
**Research**: Unlikely (internal UI refinement)
**Plans**: TBD

Focus:
- Streamline build → run → compare workflow
- Proper spacing and typography
- Consistent visual language

### Phase 6: Test Coverage
**Goal**: Comprehensive test suite for simulation pipeline
**Depends on**: Phase 5
**Research**: Unlikely (standard pytest patterns)
**Plans**: TBD

Items:
- Implement 19 stubbed pytest functions
- Add integration tests for simulation pipeline

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Type Safety | 2/2 | ✓ Complete | 2026-01-17 |
| 2. Statistical Robustness | 0/2 | Not started | - |
| 3. GUI Foundation | 0/TBD | Not started | - |
| 4. Results Visualization | 0/TBD | Not started | - |
| 5. Workflow Polish | 0/TBD | Not started | - |
| 6. Test Coverage | 0/TBD | Not started | - |
