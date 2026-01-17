---
phase: 02-statistical-robustness
document: findings
status: draft
audited: 2026-01-17
scope: probability_and_hit_distributions
next_scope: baserunning_and_special_events
---

# Statistical Model Audit - Part 1: Probability & Hit Distributions

**Audit Date:** 2026-01-17
**Scope:** Probability decomposition and hit type distribution modeling
**Methodology:** Code review against ANALYSIS_NOTES.md issues and statistical theory
**Next:** Baserunning and special events (Plan 02)

## Purpose

This audit examines the statistical assumptions underlying the Monte Carlo baseball simulator's probability calculations. The goal is to identify weak assumptions, missing documentation, and opportunities for refinement - NOT to implement fixes immediately.

## Audit Scope (This Document)

- Probability decomposition: BA/OBP/SLG → PA outcomes
- Hit type distributions: 1B/2B/3B/HR split modeling
- Bayesian smoothing for small samples
- Configuration constants and thresholds

## Assessment Criteria

For each component:
1. **Mathematical soundness:** Are formulas theoretically correct?
2. **Documentation quality:** Are assumptions and sources clearly stated?
3. **Edge case handling:** Are boundary conditions managed appropriately?
4. **Empirical grounding:** Are constants derived from real data or arbitrary?

---

## Probability Decomposition

**Location:** `src/models/probability.py::decompose_slash_line()` (lines 105-171)

### Mathematical Soundness

The core probability decomposition formulas are **theoretically sound** but rely on fundamental baseball statistics identities:

#### Formula Analysis

**1. Walk probability (line 136):**
```python
p_walk = obp - ba
```
**Assessment:** ✓ Correct
- OBP = (H + BB + HBP) / PA
- BA = H / AB
- Since PA ≈ AB + BB + HBP (ignoring SF), the difference OBP - BA approximates the walk rate
- **Caveat:** This ignores sacrifice flies, which contribute to AB but not PA. For players with high SF counts, this introduces minor error.

**2. Hit probability (line 137):**
```python
p_hit = ba
```
**Assessment:** ✓ Correct
- BA = H / AB directly represents probability of hit per at-bat
- Note: The simulation treats BA as probability per PA, which is a simplification since walks don't count as AB

**3. Total out probability (line 138):**
```python
p_total_outs = 1.0 - obp
```
**Assessment:** ✓ Correct
- If OBP is probability of reaching base, then 1 - OBP is probability of making an out
- This correctly captures all out types (strikeouts, balls-in-play outs)

**4. Strikeout splitting (lines 141-154):**
```python
if k_pct is not None:
    p_strikeout = k_pct
    p_out = p_total_outs - k_pct
    if p_out < 0:
        p_out = 0.0
        p_strikeout = p_total_outs
else:
    p_strikeout = config.DEFAULT_K_PCT
    p_out = p_total_outs - p_strikeout
    if p_out < 0:
        p_out = 0.0
        p_strikeout = p_total_outs
```
**Assessment:** ✓ Mathematically correct, but see edge case concerns below

The formula `p_out = p_total_outs - k_pct` correctly splits outs into strikeouts vs. balls-in-play, since:
- Total outs = Strikeouts + Other outs
- Therefore: Other outs = Total outs - Strikeouts

### Edge Case Handling

#### Silent K% Clamping (ANALYSIS_NOTES.md Issue #2)

**Problem identified at lines 145-147 and 152-154:**

```python
if p_out < 0:
    p_out = 0.0
    p_strikeout = p_total_outs
```

**Statistical Assessment:** This is a **band-aid fix** for data quality issues, not theoretically justified behavior.

**When this triggers:**
- Player has K% > total out rate (mathematically impossible in real baseball)
- Example: Player with .300 OBP (70% outs) but K% = 25% would have 70% - 25% = 45% other outs (OK)
- Example: Player with .300 OBP (70% outs) but K% = 80% would require clamping (DATA ERROR)

**Root causes:**
1. **Data mismatch:** K% from one source (e.g., FanGraphs) doesn't match BA/OBP from another source (different sample size, timeframe)
2. **Small sample noise:** Player with 20 PA, 8 K, 6 H could have statistically inconsistent rates
3. **Incorrect DEFAULT_K_PCT application:** If player has no K% data, using league average (22%) with actual OBP could create inconsistency

**Current behavior:** The code silently clamps, setting `p_out = 0.0` and `p_strikeout = p_total_outs`. This means:
- All outs become strikeouts
- No sacrifice flies possible (requires ball in play)
- No errors/fielder's choices possible
- **This could significantly bias simulation results for affected players**

**Recommendations:**
1. **Add logging/warning:** When clamping occurs, log player name and values so user can investigate data quality
2. **Consider alternative:** Instead of clamping, could reduce K% proportionally to fit within total outs (e.g., `k_pct_adjusted = k_pct * (p_total_outs / k_pct)` but capped at `p_total_outs`)
3. **Upstream validation:** In data loading (`processor.py`), validate K% ≤ (1 - OBP) and warn/adjust before reaching decomposition

### Documentation Quality

**Current state:** Mixed

**Well documented:**
- Function docstring (lines 112-123) explains purpose, parameters, and return type
- Type hints are complete

**Missing documentation:**
- No explanation of the mathematical formulas used (assumes reader knows BA/OBP/SLG relationships)
- No mention of the BA-as-PA-probability simplification
- No documentation of K% clamping behavior or when it occurs
- No citation for `DEFAULT_K_PCT = 0.220` in config.py (line 27) - is this league average from specific year/league?

**Example of undocumented assumption:**
```python
# Line 137: Uses BA as probability per PA
p_hit = ba
```
This implicitly assumes PA ≈ AB, which is true when walk rate is low but introduces error for high-OBP players. The mathematical relationship `P(hit|PA) = P(hit|AB) * P(AB|PA)` is not discussed.

### Recommendations

**High Priority:**
1. **Add K% clamping warning:** Emit log message when lines 145 or 152 trigger, include player identification if available
   - Implementation: `logging.warning(f"K% clamping triggered: k_pct={k_pct:.3f} > p_total_outs={p_total_outs:.3f}")`

2. **Document formulas in docstring:** Add mathematical explanation section to `decompose_slash_line()` docstring:
   ```
   Mathematical basis:
   - p_walk ≈ OBP - BA (exact when SF = 0)
   - p_hit = BA (probability per AB, approximates per PA)
   - p_total_outs = 1 - OBP (all non-base outcomes)
   - p_strikeout taken from K% when available, else DEFAULT_K_PCT
   ```

3. **Document DEFAULT_K_PCT source:** Add comment in config.py citing source (e.g., "MLB average 2015-2024" or similar)

**Medium Priority:**
4. **Add validation test:** Create pytest test that verifies clamping triggers correctly with edge case inputs
5. **Consider data validation layer:** Before probability decomposition, validate that K% ≤ (1 - OBP) in `processor.py::create_player_from_stats()`

**Low Priority:**
6. **Refine BA-as-PA-probability:** For high accuracy, could adjust `p_hit = ba * (1 - p_walk)` to account for PA vs AB difference, but current approximation is reasonable for most players

---

## Hit Type Distributions

**Location:** `config.py` (lines 38-74) and `src/models/probability.py::calculate_hit_distribution()` (lines 11-102)

### Constants and Thresholds

#### HIT_DISTRIBUTIONS Constants (ANALYSIS_NOTES.md Issue #3)

**Current values in config.py (lines 46-65):**

| Hitter Type    | 1B   | 2B   | 3B   | HR   | Sum   |
|----------------|------|------|------|------|-------|
| singles_hitter | 0.80 | 0.15 | 0.02 | 0.03 | 1.00  |
| balanced       | 0.70 | 0.20 | 0.02 | 0.08 | 1.00  |
| power_hitter   | 0.60 | 0.20 | 0.01 | 0.19 | 1.00  |

**Reasonableness check:**
- **Singles hitter:** 80% singles seems high but reasonable for contact hitters (e.g., Luis Arraez, Ichiro-type)
- **Power hitter:** 19% HR rate given a hit is plausible for elite sluggers (Aaron Judge ~15-18% in peak years)
- **Triple rates:** 1-2% across all types is realistic (triples are rare in modern MLB)

**Source documentation:** **MISSING**
- No citation for where these distributions came from
- Could be:
  - Historical MLB data (e.g., 2015-2024 averages by ISO bucket)
  - Expert estimation
  - Arbitrary round numbers
- **Unable to validate empirical grounding without source**

**Empirical validation approach (not performed yet):**
To validate these, could:
1. Query FanGraphs/Baseball Reference for all qualified batters 2015-2024
2. Bucket by ISO into three groups (< 0.100, 0.100-0.200, > 0.200)
3. Calculate actual 1B/2B/3B/HR rates for each bucket
4. Compare to config values

**Impact of inaccuracy:**
If these distributions are wrong by ±10%, the simulation will:
- Misallocate extra-base hits (more/fewer doubles, homers)
- Affect run scoring since HR/2B advance runners differently than 1B
- Could explain some of the 1.6% error vs. historical validation (though that's already quite good)

#### ISO Thresholds (ANALYSIS_NOTES.md Issue #7)

**Current values in config.py (lines 39-43):**
```python
ISO_THRESHOLDS = {
    'low': 0.100,      # Below this = singles hitter
    'medium': 0.200,   # Between low and medium = balanced
}
```

**Assessment:** These thresholds are **consistent with common baseball analytics practice** but lack citation.

**FanGraphs ISO scale (for reference):**
- Excellent: 0.200+
- Great: 0.170 - 0.200
- Above Average: 0.140 - 0.170
- Average: 0.120 - 0.140
- Below Average: 0.100 - 0.120
- Poor: 0.080 - 0.100
- Awful: < 0.080

**Comparison:**
- The code's `low = 0.100` threshold roughly separates "below average power" from "average+"
- The code's `medium = 0.200` threshold marks "excellent power" tier
- **Reasonable but simplified:** Real-world power distribution is more granular than 3 buckets

**Missing documentation:**
- No comment explaining why 0.100 and 0.200 were chosen
- No reference to FanGraphs or other source

**Recommendation:** Add comment:
```python
ISO_THRESHOLDS = {
    'low': 0.100,      # Below average power (FanGraphs scale)
    'medium': 0.200,   # Excellent power threshold
}
```

### Bayesian Smoothing

**Location:** `src/models/probability.py::calculate_hit_distribution()` (lines 56-69)

#### Formula Correctness

```python
# Line 58: Prior equivalent sample size
prior_weight = 100
player_weight = total_hits

# Lines 62-67: Weighted average
smoothed_dist[ht] = (
    (league_avg_dist[ht] * prior_weight +
     actual_dist[ht] * player_weight)
    / (prior_weight + player_weight)
)
```

**Mathematical assessment:** ✓ Correct weighted average formula

This implements a **simple weighted average** approach to Bayesian smoothing:
- Prior belief: League average distribution
- Prior strength: 100 "pseudo-hits"
- Posterior: Weighted combination of prior and observed data

**Example:**
- Player has 50 hits (30 1B, 15 2B, 0 3B, 5 HR)
- Actual 1B rate: 30/50 = 60%
- League avg 1B rate: 75%
- Smoothed: (75% × 100 + 60% × 50) / (100 + 50) = (7500 + 3000) / 150 = 70%
- The player's actual rate (60%) is pulled toward league average (75%) to get 70%

#### Appropriateness of Prior Weight = 100

**Question:** Is `prior_weight = 100` statistically justified?

**Analysis:**
- 100 pseudo-hits means the prior has weight equivalent to a player with 100 actual hits
- Players with < 100 hits will be more heavily influenced by league average
- Players with > 100 hits will be more influenced by their own data

**Rule of thumb:** The prior weight should represent the sample size at which you'd trust player data equally with league average.

**Empirical consideration:**
- In baseball, hit distribution stabilizes faster than batting average (less variance)
- 100 hits is roughly 30-40 games for a regular (0.260 BA ≈ 2.5 hits/game)
- By 100 hits, player's actual power profile (singles vs. XBH tendency) is reasonably established

**Assessment:** `prior_weight = 100` is **reasonable but not rigorously justified**
- Not derived from empirical variance analysis
- Not compared against known stabilization rates for hit distributions
- Could be anywhere from 50-200 without obvious problems

**Comparison to ANALYSIS_NOTES.md recommendation for stolen bases:**
ANALYSIS_NOTES.md (lines 34-42) recommends **beta-binomial conjugate prior** for stolen base success rate:
```python
prior_successes = 3  # ~75% prior
prior_failures = 1
smoothed_success = (player.sb + prior_successes) / (total_attempts + prior_successes + prior_failures)
```

**Key difference:**
- Stolen bases: Beta-binomial (conjugate prior for binomial data) - theoretically optimal
- Hit distributions: Simple weighted average - ad hoc but practical

**Question:** Should hit distributions also use a conjugate prior?
- Hit types follow a **multinomial distribution** (4 categories: 1B, 2B, 3B, HR)
- Conjugate prior for multinomial is **Dirichlet distribution**
- Dirichlet approach would be more rigorous but also more complex

**Assessment:** Current weighted average is **adequate for practical purposes** but not theoretically optimal. Dirichlet prior would be a refinement for a future phase.

#### Edge Cases

**Case 1: total_hits = 0 (line 43-45)**
```python
if total_hits == 0:
    return league_avg_dist.copy()
```
✓ Correctly handled - returns league average

**Case 2: total_hits < min_hits_threshold (default 100)**
Smoothing is applied - correct behavior

**Case 3: total_hits ≥ min_hits_threshold (line 71-72)**
```python
return actual_dist
```
Player's actual distribution used without smoothing - correct

**Case 4: Missing hit count data (lines 74-102)**
Falls back to ISO-based interpolation - reasonable fallback

**No edge case issues identified.**

### League Averages

**Location:** `config.py` (lines 68-73)

```python
LEAGUE_AVG_HIT_DISTRIBUTION = {
    '1B': 0.75,
    '2B': 0.18,
    '3B': 0.02,
    'HR': 0.05
}
```

**Assessment:** Values appear reasonable but **source is undocumented**.

**Reasonableness check:**
- 75% singles, 18% doubles, 2% triples, 5% homers
- Modern MLB HR rate is higher (~10-13% of hits in 2015-2024 era)
- **This distribution appears to be from pre-2015 era or is a rough approximation**

**Impact:**
- Used as Bayesian prior for players with < 100 hits
- Used as fallback when player has 0 hits
- If league average is outdated, it will bias low-hit players toward lower HR rates than modern reality

**Recommendation:**
1. **Document source:** Add comment with year range and data source
2. **Update to modern era:** Calculate actual 2015-2024 MLB averages using FanGraphs/pybaseball
3. **Consider annual updates:** League-wide HR rate has changed significantly 2015-2024 (lower in 2014, spike 2017-2019, lower in 2022+)

**Empirical validation approach:**
```python
# Pseudo-code for validation
import pybaseball
# Get all qualified batters 2015-2024
batters = pybaseball.batting_stats(2015, 2024, qual=502)  # 502 PA = qualified
# Calculate league-wide rates
league_1b_rate = batters['1B'].sum() / batters['H'].sum()
league_2b_rate = batters['2B'].sum() / batters['H'].sum()
# etc.
```

### Recommendations

**High Priority:**

1. **Document HIT_DISTRIBUTIONS source:** Add comment block in config.py explaining derivation:
   ```python
   # HIT_DISTRIBUTIONS: Derived from [SOURCE/METHODOLOGY]
   # If empirical: "FanGraphs 2015-2024 qualified batters, bucketed by ISO"
   # If estimated: "Expert estimation based on [RATIONALE]"
   ```

2. **Validate and update LEAGUE_AVG_HIT_DISTRIBUTION:**
   - Run empirical analysis using pybaseball to get actual 2015-2024 averages
   - Update config.py values to match modern era
   - Document source and year range

3. **Document ISO thresholds:** Add explanatory comment referencing baseball analytics convention

**Medium Priority:**

4. **Empirically validate HIT_DISTRIBUTIONS:**
   - Create validation script (e.g., `scripts/validate_hit_distributions.py`)
   - Query historical data, bucket by ISO, compare to config values
   - Document any discrepancies and decide if config should be updated

5. **Test prior_weight sensitivity:**
   - Run simulations with prior_weight = 50, 100, 200
   - Measure impact on season run totals
   - If impact < 1%, current value is fine; if > 5%, needs refinement

**Low Priority:**

6. **Consider Dirichlet prior for hit distributions:**
   - Implement theoretically optimal conjugate prior (Dirichlet-Multinomial)
   - Compare results to current weighted average approach
   - Only pursue if empirical testing shows significant improvement

---

## Summary of Findings

### Probability Decomposition
- **Mathematical soundness:** ✓ Formulas are correct
- **Edge case handling:** ⚠️ Silent K% clamping is a band-aid fix, needs logging
- **Documentation:** ⚠️ Formulas not explained, assumptions unstated
- **Empirical grounding:** ⚠️ DEFAULT_K_PCT lacks source citation

### Hit Type Distributions
- **Mathematical soundness:** ✓ Bayesian smoothing formula correct
- **Edge case handling:** ✓ All edge cases properly handled
- **Documentation:** ⚠️ HIT_DISTRIBUTIONS source missing, ISO thresholds lack citation
- **Empirical grounding:** ⚠️ Constants appear reasonable but can't validate without source, LEAGUE_AVG likely outdated

### Critical Gaps Identified

1. **Missing empirical sources:** HIT_DISTRIBUTIONS, ISO_THRESHOLDS, LEAGUE_AVG_HIT_DISTRIBUTION, DEFAULT_K_PCT all lack documented sources
2. **Silent data quality issues:** K% clamping hides potential data problems
3. **Outdated league averages:** LEAGUE_AVG_HIT_DISTRIBUTION appears pre-2015, doesn't reflect modern HR rates
4. **Non-optimal priors:** Weighted average for hit distributions works but Dirichlet conjugate prior would be theoretically superior

### Recommended Next Steps

**Immediate (Phase 2, Plan 3-4):**
- Add logging to K% clamping
- Document all constant sources in config.py
- Validate and update LEAGUE_AVG_HIT_DISTRIBUTION

**Near-term (Future phase):**
- Empirically validate HIT_DISTRIBUTIONS against historical data
- Test sensitivity of prior_weight parameter
- Add data validation layer in processor.py

**Long-term (Future phase):**
- Implement Dirichlet prior for hit distributions
- Create automated config update process using pybaseball
- Add comprehensive unit tests for probability calculations

---

**Document Status:** Draft - Part 1 Complete
**Next:** Audit baserunning and special events (Plan 02-02)
