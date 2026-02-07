# Roadmap: Monte Carlo Baseball Simulator

## Overview

Clean up the existing simulation model for robustness, then redesign the GUI from 9 fragmented tabs into a streamlined dashboard that communicates simulation insights at a glance. Finish with comprehensive test coverage.

## Domain Expertise

None

## Phases

- [x] **Phase 1: Type Safety** - Fix 30+ critical type errors preventing crashes
- [x] **Phase 2: Statistical Robustness** - Audit model assumptions and document findings
- [x] **Phase 3: GUI Foundation** - Consolidate 9 tabs into focused dashboard structure
- [x] **Phase 3.1: Cleanup Planning Docs** - Clean up stray/orphan documents, consolidate and recommend removals (INSERTED)
- [x] **Phase 4: Results Visualization** - Charts and metrics that communicate at a glance
- [ ] **Phase 5: Workflow Polish** - Reduce clicks, clean visual hierarchy
- [ ] **Phase 6: Test Coverage** - Implement 19 stubs + integration tests
- [ ] **Phase 7: Season W/L Simulation** - Extend to season-level win/loss predictions (DEFERRED - researched ahead)

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
**Plans**: 6 plans

Plans:
- [x] 03-01-PLAN.md — Create CollapsibleFrame widget foundation
- [x] 03-02-PLAN.md — Build SetupPanel with collapsible Assumptions subsection
- [x] 03-03-PLAN.md — Build LineupPanel with integrated Run controls
- [x] 03-04-PLAN.md — Build ResultsPanel with summary and collapsible details
- [x] 03-05-PLAN.md — Create MainDashboard container with compare mode
- [x] 03-06-PLAN.md — Add session persistence and startup restoration
- [x] 03-07-PLAN.md — Dashboard layout restructure with sidebar and dark theme

### Phase 3.1: Cleanup Planning Docs (INSERTED)
**Goal**: Clean up stray/orphan documents and .md files; consolidate things that can be merged, recommend files for removal
**Depends on**: Phase 3
**Research**: Unlikely (internal housekeeping)
**Plans**: 1 plan

Plans:
- [x] 03.1-01-PLAN.md — Audit and cleanup planning directory (remove orphans, update ROADMAP)

### Phase 4: Results Visualization
**Goal**: Charts and metrics that communicate simulation insights at a glance
**Depends on**: Phase 3.1
**Research**: Complete (2026-02-03)
**Plans**: 4 plans

Core value delivery: Visual clarity — results easy to understand at a glance

Plans:
- [x] 04-01-PLAN.md — Add seaborn dependency, create chart utilities, enhance histogram with KDE
- [x] 04-02-PLAN.md — Add win probability, LOB, and RISP metrics to summary display
- [x] 04-03-PLAN.md — Create player contribution chart with slot/player toggle
- [x] 04-04-PLAN.md — Create optimization preview widgets (ranking list, diff view)

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

### Phase 7: Season W/L Simulation (DEFERRED)
**Goal**: Extend simulation to season-level win/loss predictions
**Depends on**: Phase 6
**Research**: Complete (2026-01-25)
**Plans**: 1 plan created ahead of schedule

**Note**: Research and initial plan created ahead of schedule (2026-01-25). Phase 7 contains detailed methodology research (1,484 lines) and implementation plan but is deferred until Phases 4-6 complete.

Plans:
- [ ] 07-01-PLAN.md — Implement season-level W/L simulation engine

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Type Safety | 2/2 | ✓ Complete | 2026-01-17 |
| 2. Statistical Robustness | 2/2 | ✓ Complete | - |
| 3. GUI Foundation | 7/7 | ✓ Complete | 2026-02-06 |
| 3.1 Cleanup Planning Docs | 1/1 | ✓ Complete | 2026-01-25 |
| 4. Results Visualization | 4/4 | ✓ Complete | 2026-02-07 |
| 5. Workflow Polish | 0/TBD | Not started | - |
| 6. Test Coverage | 0/TBD | Not started | - |
| 7. Season W/L Simulation | 0/1 | Deferred (researched ahead) | - |
