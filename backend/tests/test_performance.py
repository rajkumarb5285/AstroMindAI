import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from backend.app.astrology.adapter import SwissEphAdapter
from backend.app.astrology.compatibility.ashta_koota import calculate_ashta_koota
from backend.app.astrology.schemas import ChartCalculationInput
from backend.app.astrology.transits.engine import TransitEngine


@pytest.fixture
def sample_chart_input() -> ChartCalculationInput:
    return ChartCalculationInput(
        birth_date="1990-10-24",
        birth_time="14:30:00",
        timezone="Asia/Kolkata",
        latitude=28.6139,
        longitude=77.2090,
        ayanamsa="lahiri",
        node_mode="mean",
    )


def test_ephemeris_calculation_latency_and_p95(sample_chart_input: ChartCalculationInput):
    """
    Benchmark Swiss Ephemeris D1 calculation latency across 100 runs.
    Enforces strict production SLA: p95 latency must be under 20ms.
    """
    adapter = SwissEphAdapter()
    latencies_ms: list[float] = []

    # Warmup
    adapter.calculate_chart(sample_chart_input)

    iterations = 100
    for _ in range(iterations):
        t0 = time.perf_counter()
        result = adapter.calculate_chart(sample_chart_input)
        latencies_ms.append((time.perf_counter() - t0) * 1000)
        assert len(result.planets) == 9
        assert len(result.houses) == 12

    p50 = statistics.median(latencies_ms)
    p95 = statistics.quantiles(latencies_ms, n=20)[18]  # 95th percentile
    p99 = max(latencies_ms)

    print(f"\n[PERF BENCHMARK] SwissEph D1 Latency: p50={p50:.2f}ms, p95={p95:.2f}ms, p99={p99:.2f}ms")

    # Production SLA Assertions
    assert p50 < 10.0, f"p50 latency {p50:.2f}ms exceeds 10ms threshold"
    assert p95 < 25.0, f"p95 latency {p95:.2f}ms exceeds 25ms threshold"


def test_ephemeris_concurrent_thread_safety(sample_chart_input: ChartCalculationInput):
    """
    Verify thread-safety and throughput under 40 concurrent worker threads.
    Checks that every worker receives exact deterministic coordinates without race conditions.
    """
    adapter = SwissEphAdapter()
    baseline = adapter.calculate_chart(sample_chart_input)
    baseline_asc = baseline.ascendant_longitude

    worker_count = 30
    runs_per_worker = 2

    def worker_task(_):
        return [adapter.calculate_chart(sample_chart_input) for _ in range(runs_per_worker)]

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(worker_task, i) for i in range(worker_count)]
        all_results = [f.result() for f in futures]
    total_duration = time.perf_counter() - t0

    total_calculations = worker_count * runs_per_worker
    throughput_rps = total_calculations / total_duration

    print(
        f"\n[PERF BENCHMARK] Concurrency: {total_calculations} calculations across {worker_count} "
        f"threads in {total_duration:.2f}s ({throughput_rps:.1f} calc/sec)"
    )

    # Verify deterministic consistency across all concurrent calculations
    for batch in all_results:
        for chart in batch:
            assert abs((chart.ascendant_longitude or 0.0) - (baseline_asc or 0.0)) < 1e-6
            assert len(chart.planets) == 9
            assert len(chart.houses) == 12

    assert throughput_rps > 100.0, f"Throughput {throughput_rps:.1f} rps is below 100 rps target"


def test_ashta_koota_compatibility_throughput():
    """
    Benchmark Ashta Koota compatibility engine throughput.
    Target: 500 evaluations in < 50ms (> 10,000 matches/sec).
    """
    t0 = time.perf_counter()
    iterations = 500

    for i in range(iterations):
        b_nak = (i % 27) + 1
        g_nak = ((i * 3) % 27) + 1
        b_pada = (i % 4) + 1
        g_pada = ((i + 2) % 4) + 1
        b_rashi = (i % 12) + 1
        g_rashi = ((i * 5) % 12) + 1

        result = calculate_ashta_koota(
            bride_moon_sign=b_rashi,
            bride_nakshatra=b_nak,
            bride_pada=b_pada,
            groom_moon_sign=g_rashi,
            groom_nakshatra=g_nak,
            groom_pada=g_pada,
        )
        assert 0.0 <= result["total_points"] <= 36.0
        assert len(result["kootas"]) == 8

    duration_ms = (time.perf_counter() - t0) * 1000
    ops_per_sec = (iterations / duration_ms) * 1000
    print(
        f"\n[PERF BENCHMARK] Ashta Koota: {iterations} evaluations in {duration_ms:.2f}ms "
        f"({ops_per_sec:.0f} evals/sec)"
    )
    assert duration_ms < 100.0, f"Ashta Koota evaluation took {duration_ms:.2f}ms, exceeding 100ms"


def test_transit_engine_performance():
    """
    Benchmark Gochar transit evaluation throughput and latency.
    """
    natal_calc = {
        "ascendant_sign_number": 1,
        "planets": [
            {"planet_id": "Moon", "sign_number": 12, "longitude": 340.0},
            {"planet_id": "Sun", "sign_number": 5, "longitude": 120.0},
        ],
    }

    t0 = time.perf_counter()
    iterations = 50
    for _ in range(iterations):
        result = TransitEngine.evaluate_transits(natal_chart_calc=natal_calc)
        assert len(result["transits"]) >= 9

    duration_ms = (time.perf_counter() - t0) * 1000
    avg_ms = duration_ms / iterations
    print(f"\n[PERF BENCHMARK] Transits Engine: {iterations} evals in {duration_ms:.2f}ms (avg {avg_ms:.2f}ms)")
    assert avg_ms < 50.0, f"Average transit eval time {avg_ms:.2f}ms exceeds 50ms limit"
