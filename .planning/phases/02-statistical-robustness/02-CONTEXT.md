# Phase 2: Statistical Robustness - Context

**Gathered:** 2026-01-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Conduct a statistical audit of the existing simulation model to identify weak assumptions and document findings. This phase is analytical, not remediation - the audit produces a findings document that informs future refinement work.

</domain>

<decisions>
## Implementation Decisions

### Audit Approach
- Statistical audit of assumptions (not diagnostic simulations against historical data)
- Focus on theoretical soundness and documentation quality of existing model components
- Analysis-driven methodology: identify largest error sources rather than apply blanket refinements

### Audit Scope
- **Probability decomposition**: BA/OBP/SLG → PA outcomes (WALK, K, OUT, HIT) - examine math soundness and assumption documentation
- **Hit type distributions**: 1B/2B/3B/HR split based on ISO - evaluate thresholds, Bayesian smoothing appropriateness
- **Baserunning advancement**: Advancement probabilities (1st→3rd on single, etc.) - assess realism and source documentation
- **Special events**: Stolen bases, sacrifice flies, errors - verify modeling correctness and identify known issues

### Deliverable
- Analysis document with findings (not a ranked priority list)
- Documents each assumption, its strength/weakness, and recommendations for refinement
- No fixes implemented in this phase - findings inform future phases

### WAR Integration
- Skip WAR comparison for now
- Focus audit strictly on existing model assumptions without adding new validation dimensions

### Claude's Discretion
- Document structure and formatting
- Level of mathematical detail in explanations
- Organization of findings (by component, by severity, etc.)

</decisions>

<specifics>
## Specific Ideas

None - audit scope is comprehensive across all model components.

</specifics>

<deferred>
## Deferred Ideas

- **WAR-based validation** - Compare simulation results to player WAR to validate relative player value (future phase if needed)
- **Diagnostic simulations** - Run sims against historical data to measure error by component (alternative validation approach)
- **Implementing fixes** - Audit identifies issues, but remediation happens in future phases based on priorities

</deferred>

---

*Phase: 02-statistical-robustness*
*Context gathered: 2026-01-17*
