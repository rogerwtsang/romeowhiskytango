# Statistical & Code Quality Analysis Notes

**Analysis Date:** 2026-01-10
**Analyst:** Bayesian statistician review

## Code Quality Issues (mypy)

### Critical (Must Fix)

| File | Line | Issue |
|------|------|-------|
| `src/engine/pa_generator.py` | 34 | Indexing `pa_probs` which can be `None` - crashes simulation |
| `src/models/baserunning.py` | 101, 122, 131 | `rng.random()` called when rng is `Optional[None]` |
| `src/simulation/batch.py` | 78-83, 153-158 | List/ndarray type confusion - 12 errors |
| `src/gui/utils/constraint_validator.py` | 31, 35, 69, 72, 128 | None comparison/arithmetic errors |

### Medium (Should Fix)

| File | Line | Issue |
|------|------|-------|
| `src/models/position.py` | 188, 193 | None attribute access |
| `src/models/sacrifice_fly.py` | 75, 82, 83, 90, 94 | Dict variance issues |
| `src/models/stolen_bases.py` | 243, 272, 280 | Type misassignment in test code |
| `src/data/processor.py` | 220, 223 | None dict access |

**Total: 30+ type errors across 8 files**

---

## Statistical Model Issues

### High Priority

**1. No Bayesian Shrinkage on Stolen Base Success Rate**
- Location: `src/models/stolen_bases.py:28-31`
- Problem: Player with 2 SB, 0 CS gets success_rate = 1.0
- Fix: Add beta-binomial shrinkage similar to hit distribution
```python
# Recommended fix:
prior_successes = 3  # ~75% prior
prior_failures = 1
smoothed_success = (player.sb + prior_successes) / (total_attempts + prior_successes + prior_failures)
```

**2. Silent K% Clamping**
- Location: `src/models/probability.py:141-154`
- Problem: When K% > total_outs, silently clamped without warning
- Fix: Add logging when K% is adjusted

**3. Hardcoded Hit Distributions Without Source**
- Location: `config.py:46-65`
- Problem: `HIT_DISTRIBUTIONS` values appear arbitrary
- Fix: Document empirical source or derive from historical MLB data

### Medium Priority

**4. Fixed Baserunning Aggression (No Player Speed)**
- Location: `config.py:31-35`, `src/models/baserunning.py`
- Problem: `single_1st_to_3rd: 0.28` applied uniformly to all players
- Fix: Modulate by player speed proxy (e.g., SB attempt rate)

**5. Stolen Base Opportunity Model Oversimplified**
- Location: `src/models/stolen_bases.py:33-42`
- Problem: Assumes uniform steal opportunities across all on-base events
- Reality: Steals more likely on singles/walks than doubles/triples

**6. No Player-Specific Fly Ball Rate**
- Location: `config.py:24` (`FLYOUT_PERCENTAGE = 0.35`)
- Problem: Global constant ignores player FB% variation (25-50% in MLB)

### Low Priority

**7. ISO Thresholds Are Undocumented**
- Location: `config.py:39-43`
- Problem: 0.100 and 0.200 thresholds lack citation
- Fix: Add comment with data source

---

## Test Coverage Gaps

| Component | Current State | Priority |
|-----------|---------------|----------|
| Hit distribution calculation | `if __name__` only | High |
| Slash line decomposition | `if __name__` only | High |
| Baserunning advancement | No tests | High |
| Stolen base rates | `if __name__` only | Medium |
| PA outcome generation | `if __name__` only | Medium |
| End-to-end season simulation | No tests | High |
| 19 pytest stubs | Unimplemented | High |

---

## Recommended Fix Order

### Phase A: Type Safety (Prevents Crashes)
1. Fix `pa_generator.py` None indexing
2. Fix `baserunning.py` rng None checks
3. Fix `batch.py` list/ndarray typing
4. Fix `constraint_validator.py` None comparisons

### Phase B: Statistical Robustness
1. Add shrinkage to stolen base success rate
2. Add K% clamping warning
3. Document/derive hit distribution sources
4. Add player-speed modifier to baserunning

### Phase C: Test Coverage
1. Implement 19 stubbed tests
2. Add integration tests for simulation pipeline
3. Add CI/CD with coverage reporting

---

*Notes prepared for /gsd:new-project initialization*
