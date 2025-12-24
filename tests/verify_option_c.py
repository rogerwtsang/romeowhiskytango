from src.data.scraper import load_data
from src.data.processor import prepare_lineup
from src.simulation.season import simulate_season
from src.engine.pa_generator import PAOutcomeGenerator

print("=== Verifying Option C Implementation ===\n")

# Load data
df = load_data('blue_jays_2025_prepared.csv', 'processed')
df_sorted = df.sort_values('pa', ascending=False)
lineup = prepare_lineup(df_sorted.reset_index(drop=True), order=list(range(9)))

# Check that players have actual hit distributions
print("Sample player hit distributions:")
for i in range(3):
    p = lineup[i]
    print(f"\n{p.name}:")
    print(f"  Actual counts: {p.singles}S, {p.doubles}D, {p.triples}T, {p.hr}HR")
    if p.hit_dist:
        total_bases_per_hit = (
            1 * p.hit_dist['1B'] + 
            2 * p.hit_dist['2B'] + 
            3 * p.hit_dist['3B'] + 
            4 * p.hit_dist['HR']
        )
        observed_bases_per_hit = p.slg / p.ba if p.ba > 0 else 0
        error = abs(total_bases_per_hit - observed_bases_per_hit)
        print(f"  Hit dist: 1B={p.hit_dist['1B']:.3f}, 2B={p.hit_dist['2B']:.3f}, 3B={p.hit_dist['3B']:.3f}, HR={p.hit_dist['HR']:.3f}")
        print(f"  Calculated bases/hit: {total_bases_per_hit:.3f}")
        print(f"  Observed (SLG/BA): {observed_bases_per_hit:.3f}")
        print(f"  Error: {error:.3f} ({error/observed_bases_per_hit*100:.1f}%)")

# Run one season
print("\n" + "="*70)
print("Running single season test...")
pa_gen = PAOutcomeGenerator(random_state=42)
result = simulate_season(lineup, pa_gen, n_games=162)

print(f"\nSingle season result:")
print(f"  Total runs: {result['total_runs']}")
print(f"  Total hits: {result['total_hits']}")
print(f"  SB: {result.get('total_sb', 0)}, CS: {result.get('total_cs', 0)}")
print(f"  SF: {result.get('total_sf', 0)}")

print("\n✓ Verification complete")
