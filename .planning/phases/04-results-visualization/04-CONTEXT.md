# Phase 4: Results Visualization - Context

**Gathered:** 2026-02-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Charts and metrics that communicate simulation insights at a glance. Build the visualization foundation for current results display and prepare for future lineup optimization comparison views. Does not include optimization algorithms themselves (separate phase).

</domain>

<decisions>
## Implementation Decisions

### Primary Metrics
- Show LOB and scoring efficiency at game-level summary (total LOB per game, overall RISP conversion rate)
- Include win probability as point estimate with confidence interval (e.g., 87 wins, 95% CI: 82-92)
- Display player contributions with toggle between lineup slot analysis (positions 1-9) and individual player stats

### Chart Types
- Run distribution: histogram with density curve overlay, mean/CI markers
- Player contributions: multiple chart types available (bar chart, stacked contribution, heatmap grid) — user selects based on workflow
- Dashboard grid layout with summary stats as largest/most prominent element
- Charts secondary to numeric summaries in visual hierarchy

### Optimization Preview
- Ranked list view for comparing lineup candidates (top N ordered by expected runs)
- Full stat breakdown expandable for each lineup candidate
- Text diff format for showing lineup slot changes (e.g., "3→4, 4→3")
- Copy-to-lineup-panel action (load candidate into existing lineup panel for manual run)

### Claude's Discretion
- Exact grid layout proportions
- Color scheme and chart styling
- How many lineup candidates to show in ranked list
- Specific matplotlib/tkinter embedding approach

</decisions>

<specifics>
## Specific Ideas

- Summary stats should be prominent — numbers first, charts support the numbers
- Player contribution views should be flexible (slot-based vs player-based toggle)
- Optimization preview is "view and copy" not "view and auto-run"

</specifics>

<deferred>
## Deferred Ideas

- WAR estimations — requires additional calculation infrastructure, potential future phase
- Inning-level or situation-level breakdowns (0/1/2 outs, bases loaded) — could be Phase 5 polish
- Full probability distribution curves for win totals — point estimate with CI is sufficient for now
- Visual lineup cards (9-position graphical representation) — text diff adequate initially

</deferred>

---

*Phase: 04-results-visualization*
*Context gathered: 2026-02-04*
