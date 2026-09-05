"""Reproducible microbenchmark for equality and residue-signature checks."""

from __future__ import annotations

import json
import platform
import statistics
import timeit
from pathlib import Path

from nr_timing import DEFAULT_MODULI, TS30_SAMPLES_PER_SUBFRAME, residue_signature


REPEATS = 7
NUMBER = 200_000


def direct_check(value: int, expected: int) -> bool:
    return value == expected


def modular_check(value: int, expected_signature: tuple[int, ...]) -> bool:
    return residue_signature(value, DEFAULT_MODULI) == expected_signature


def _measure(statement: str, setup: str) -> list[float]:
    return timeit.repeat(statement, setup=setup, repeat=REPEATS, number=NUMBER)


def main() -> None:
    expected = TS30_SAMPLES_PER_SUBFRAME
    direct = _measure(
        "direct_check(value, expected)",
        "from __main__ import direct_check; value=30719; expected=30720",
    )
    modular = _measure(
        "modular_check(value, expected_signature)",
        "from __main__ import modular_check; from nr_timing import residue_signature, DEFAULT_MODULI; "
        "value=30719; expected_signature=residue_signature(30720, DEFAULT_MODULI)",
    )
    direct_median = statistics.median(direct) / NUMBER
    modular_median = statistics.median(modular) / NUMBER
    result = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "repeats": REPEATS,
        "iterations_per_repeat": NUMBER,
        "direct_equality_seconds_per_check_median": direct_median,
        "residue_signature_seconds_per_check_median": modular_median,
        "residue_to_equality_time_ratio": modular_median / direct_median,
        "interpretation": (
            "Direct integer equality is the relevant software baseline and is faster. "
            "The residue representation may still be useful when residues already exist "
            "as distributed or incrementally maintained hardware state; that claim requires synthesis."
        ),
    }
    output = Path(__file__).resolve().parents[1] / "data" / "benchmark_results.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    ratio_output = output.with_name("benchmark_ratio.tex")
    ratio_output.write_text(f"{result['residue_to_equality_time_ratio']:.1f}\\(\\times\\)\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
