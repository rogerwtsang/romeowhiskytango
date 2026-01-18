# Phase 3: GUI Foundation - Context

**Gathered:** 2026-01-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Consolidate the current 9-tab Tkinter structure (Setup, Lineup, Distribution, Errors, Baserunning, Run, Results, Compare, History) into a streamlined single-dashboard interface that groups related functionality and reduces navigation overhead. The target is a unified dashboard page with resizable panels, not separate views or workflow steps.

</domain>

<decisions>
## Implementation Decisions

### View grouping strategy
- Single dashboard page (not multiple tabs or workflow-style views)
- Main components: Setup panel (with Assumptions subsection), Lineup panel(s), Results panel
- Lineup and Results visible alongside each other on main dashboard
- Spatial arrangement: Claude's discretion (choose layout that balances information hierarchy and typical screen sizes)

### Dashboard layout structure
- Dynamic panel creation: Add/remove lineup panels as needed (1 panel for single analysis, 2 for comparison)
- Resizable panels with splitters (user can drag dividers to adjust panel sizes)
- Setup section is collapsible to maximize workspace for Lineup/Results
- Results display detail level: Claude's discretion (balance information density and visual clarity)

### Workflow integration
- Run Simulation button within Lineup panel (contextual placement)
- Progress indicator displays inline near Run button during simulation
- Compare mode: Explicit 'Compare Mode' toggle/button to enable two-lineup comparison
- Session restoration: Offer to restore last session on startup (prompt with option to start fresh)

### Information density
- Assumptions subsection controls: Claude's discretion (balance discoverability and visual complexity)
- Lineup panel: Show full stat line per player in batting order (name, position, BA/OBP/SLG, and other relevant stats)
- Comparison lineup view: Full side-by-side with difference indicators (show complete details for both lineups with subtle markers highlighting differences)
- Comparison results display: Claude's discretion (choose presentation that maximizes statistical comparison clarity)

### Claude's Discretion
- Spatial arrangement of Setup/Lineup/Results panels on dashboard
- Detail level for Results panel without scrolling
- Assumptions subsection control presentation (toggles vs presets vs full visibility)
- Comparison results display format (unified vs side-by-side vs switchable)

</decisions>

<specifics>
## Specific Ideas

- Assumptions subsection should live under Setup (not a separate view)
- When comparing lineups, both the lineup configurations AND their results should be visible simultaneously
- The dashboard should feel like a unified workspace rather than separate sections

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-gui-foundation*
*Context gathered: 2026-01-18*
