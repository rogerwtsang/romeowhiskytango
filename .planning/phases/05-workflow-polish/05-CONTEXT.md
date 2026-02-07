# Phase 5: Workflow Polish - Context

**Gathered:** 2026-02-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Refine the existing dashboard UI to reduce friction and improve visual hierarchy. Reorganize content, streamline controls, and enhance the lineup management experience. This phase polishes what exists — no new simulation capabilities.

</domain>

<decisions>
## Implementation Decisions

### Simulation Defaults
- Default number of simulations: 2000 (changed from current)
- Seed behavior: Display seed number in box; randomize on each Run click; lock/unlock toggle with visual indicator; input box greyed out when unlocked, editable when locked

### Window and Layout
- Default window size: Full screen height, half screen width
- Configuration panels (left side): Scale to 1/4 window width
- Minimum panel width: 250px absolute

### Model Assumptions
- Assumptions section: ON by default (currently collapsed)
- Add expandable explanations: Each assumption gets text describing what it is and what it adds to the model
- User can disable assumption display if desired

### Content Reorganization
- Move Distribution Histogram from Results to Visuals tab
- Move Player Contributions chart from Results to Visuals tab

### Lineup Panel Redesign
- Visual style: Spreadsheet-like appearance (not editable cells for stats)
- Stats source: Read-only from data — user selects year(s) or career
- Year selection: Global toggle with per-player override option
- Year range: Support individual year, career totals, or range of years
- Columns to display: Player name, Fielding position (separate column), Typical batting order position (calculated from games started at each slot)
- Reordering: Drag-and-drop with insert behavior (not swap)

### Team/Roster/Lineup Hierarchy
- **Team** = Collection of loaded players with stats (e.g., "2024 Blue Jays")
- **Roster** = Subset of team eligible for batting order
- **Lineup** = Specific 9-player batting order from roster
- Multiple lineups can be saved per roster for comparison
- Teams can have nicknames

### Visualizations (Visuals Tab)
- Run expectancy by slot: Bar chart showing runs contributed per batting order position
- Runs distribution overlay: Compare distributions of multiple lineups
- Player stat radar: Radar chart comparing player profiles (OBP, SLG, K%, etc.) with toggle between raw values and percentile ranks
- Axis limits: Use meaningful lower bounds based on realistic data ranges (e.g., runs axis doesn't start at zero if no team scores below X)

### Claude's Discretion
- Team/Roster/Lineup navigation UI (tree view vs tabs vs dropdowns)
- Number of lineups for distribution overlay comparison (balance clarity with usefulness)
- Specific axis minimum calculations
- Drag-drop implementation details
- Typical batting order position calculation algorithm

</decisions>

<specifics>
## Specific Ideas

- Lineup panel should feel like a spreadsheet or database viewer — clean columns, sortable
- Seed control UX: Random by default, but lockable for reproducibility
- Visualizations should help identify patterns between different batting orders
- Axis limits should be meaningful — "no team scores below X runs" logic

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-workflow-polish*
*Context gathered: 2026-02-07*
