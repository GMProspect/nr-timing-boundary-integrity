"""Exact 5G NR normal-CP timing helpers and residue signatures.

The timing formulas follow 3GPP TS 38.211 using the fundamental time unit
Tc.  A separate 30.72 MHz reference-grid projection is provided only where
all quantities are integral (mu <= 4).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from math import gcd
from operator import mul
from typing import Iterable, Sequence


TC_TICKS_PER_SUBFRAME = 1_966_080
TS30_SAMPLES_PER_SUBFRAME = 30_720
KAPPA = 64
SUPPORTED_MU = tuple(range(7))
DEFAULT_MODULI = (2, 3, 5, 7, 11, 13, 17)


def _validate_mu(mu: int) -> None:
    if mu not in SUPPORTED_MU:
        raise ValueError(f"mu must be one of {SUPPORTED_MU}; received {mu}")


def useful_symbol_ticks_tc(mu: int) -> int:
    """Useful OFDM-symbol duration in Tc ticks."""
    _validate_mu(mu)
    return 2048 * KAPPA // (2**mu)


def short_cp_ticks_tc(mu: int) -> int:
    """Normal short cyclic-prefix duration in Tc ticks."""
    _validate_mu(mu)
    return 144 * KAPPA // (2**mu)


def slot_lengths_tc(mu: int) -> tuple[int, ...]:
    """Exact normal-CP slot lengths over one 1 ms subframe.

    The two 16*kappa CP extensions occur at OFDM-symbol indices 0 and
    7*2**mu.  For mu=0 both extensions lie in the only slot; for mu>=1
    they lie in slots 0 and 2**(mu-1).
    """
    _validate_mu(mu)
    base_symbol = useful_symbol_ticks_tc(mu) + short_cp_ticks_tc(mu)
    base_slot = 14 * base_symbol
    count = 2**mu
    lengths = [base_slot] * count
    if mu == 0:
        lengths[0] += 2 * 16 * KAPPA
    else:
        lengths[0] += 16 * KAPPA
        lengths[2 ** (mu - 1)] += 16 * KAPPA
    assert sum(lengths) == TC_TICKS_PER_SUBFRAME
    return tuple(lengths)


def slot_boundaries_tc(mu: int, include_endpoint: bool = False) -> tuple[int, ...]:
    """Exact slot-start positions within a subframe, measured in Tc ticks."""
    positions = [0]
    elapsed = 0
    for length in slot_lengths_tc(mu):
        elapsed += length
        positions.append(elapsed)
    assert positions[-1] == TC_TICKS_PER_SUBFRAME
    return tuple(positions if include_endpoint else positions[:-1])


def slot_lengths_ts30(mu: int) -> tuple[int, ...]:
    """Exact slot lengths on a 30.72 MHz reference grid for mu <= 4."""
    _validate_mu(mu)
    if mu > 4:
        raise ValueError("30.72 MHz projection is integral only for mu <= 4")
    lengths = slot_lengths_tc(mu)
    if any(value % KAPPA for value in lengths):
        raise AssertionError("non-integral 30.72 MHz projection")
    return tuple(value // KAPPA for value in lengths)


def slot_boundaries_ts30(mu: int, include_endpoint: bool = False) -> tuple[int, ...]:
    """Exact slot starts on the 30.72 MHz reference grid for mu <= 4."""
    positions = slot_boundaries_tc(mu, include_endpoint=include_endpoint)
    return tuple(value // KAPPA for value in positions)


def boundaries_are_nested(mu_coarse: int, mu_fine: int) -> bool:
    """Return True if each coarse boundary is also a fine boundary."""
    _validate_mu(mu_coarse)
    _validate_mu(mu_fine)
    if mu_coarse > mu_fine:
        raise ValueError("mu_coarse must not exceed mu_fine")
    coarse = set(slot_boundaries_tc(mu_coarse, include_endpoint=True))
    fine = set(slot_boundaries_tc(mu_fine, include_endpoint=True))
    return coarse <= fine


def moduli_product(moduli: Sequence[int]) -> int:
    return reduce(mul, moduli, 1)


def are_pairwise_coprime(moduli: Sequence[int]) -> bool:
    return all(gcd(a, b) == 1 for i, a in enumerate(moduli) for b in moduli[i + 1 :])


def residue_signature(value: int, moduli: Sequence[int] = DEFAULT_MODULI) -> tuple[int, ...]:
    """Return the Chinese-remainder residue vector of a nonnegative integer."""
    if value < 0:
        raise ValueError("value must be nonnegative")
    if not moduli or any(modulus <= 1 for modulus in moduli):
        raise ValueError("all moduli must exceed one")
    return tuple(value % modulus for modulus in moduli)


@dataclass(frozen=True)
class SignatureCheck:
    matches: bool
    exact_on_domain: bool
    modulus_product: int
    observed_signature: tuple[int, ...]
    expected_signature: tuple[int, ...]


def check_residue_signature(
    observed: int,
    expected: int,
    *,
    domain_size: int,
    moduli: Sequence[int] = DEFAULT_MODULI,
) -> SignatureCheck:
    """Compare residue signatures and report whether equality is exact on a domain.

    For pairwise-coprime moduli, equal signatures imply congruence modulo the
    product M.  The check is collision-free on any domain of width less than M.
    It does not estimate time of arrival or acquire synchronization from samples.
    """
    if domain_size <= 0:
        raise ValueError("domain_size must be positive")
    observed_sig = residue_signature(observed, moduli)
    expected_sig = residue_signature(expected, moduli)
    product = moduli_product(moduli)
    exact = are_pairwise_coprime(moduli) and domain_size <= product
    return SignatureCheck(
        matches=observed_sig == expected_sig,
        exact_on_domain=exact,
        modulus_product=product,
        observed_signature=observed_sig,
        expected_signature=expected_sig,
    )


def boundary_table_ts30() -> dict[int, tuple[int, ...]]:
    """Return the exact mu=0,...,4 boundary table used by the VHDL monitor."""
    return {mu: slot_boundaries_ts30(mu) for mu in range(5)}

