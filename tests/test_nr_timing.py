import unittest

from src.nr_timing import (
    DEFAULT_MODULI,
    TC_TICKS_PER_SUBFRAME,
    TS30_SAMPLES_PER_SUBFRAME,
    boundaries_are_nested,
    check_residue_signature,
    moduli_product,
    residue_signature,
    slot_boundaries_tc,
    slot_boundaries_ts30,
    slot_lengths_tc,
    slot_lengths_ts30,
)


class TimingModelTests(unittest.TestCase):
    def test_every_normal_cp_numerology_fills_one_subframe(self):
        for mu in range(7):
            self.assertEqual(sum(slot_lengths_tc(mu)), TC_TICKS_PER_SUBFRAME)
            self.assertEqual(len(slot_lengths_tc(mu)), 2**mu)

    def test_boundary_nesting_for_all_standardized_mu(self):
        for coarse in range(7):
            for fine in range(coarse, 7):
                self.assertTrue(boundaries_are_nested(coarse, fine))

    def test_exact_30_72_mhz_slot_lengths(self):
        expected = {
            0: (30720,),
            1: (15360, 15360),
            2: (7688, 7672, 7688, 7672),
            3: (3852, 3836, 3836, 3836, 3852, 3836, 3836, 3836),
            4: (1934,) + (1918,) * 7 + (1934,) + (1918,) * 7,
        }
        for mu, lengths in expected.items():
            self.assertEqual(slot_lengths_ts30(mu), lengths)
            self.assertEqual(sum(lengths), TS30_SAMPLES_PER_SUBFRAME)

    def test_30_72_mhz_boundaries_are_not_a_subgroup(self):
        boundaries = set(slot_boundaries_ts30(2))
        self.assertIn(7688, boundaries)
        self.assertNotIn((7688 + 7688) % TS30_SAMPLES_PER_SUBFRAME, boundaries)

    def test_abstract_slot_index_embedding(self):
        for coarse in range(5):
            for fine in range(coarse, 5):
                factor = 2 ** (fine - coarse)
                mapped = {(factor * k) % (2**fine) for k in range(2**coarse)}
                self.assertEqual(len(mapped), 2**coarse)


class ResidueSignatureTests(unittest.TestCase):
    def test_original_six_moduli_have_a_collision_in_subframe_domain(self):
        original = (2, 3, 5, 7, 11, 13)
        self.assertEqual(moduli_product(original), 30030)
        self.assertEqual(residue_signature(690, original), residue_signature(30720, original))

    def test_default_signature_is_exact_on_one_subframe_domain(self):
        check = check_residue_signature(
            30719,
            30720,
            domain_size=TS30_SAMPLES_PER_SUBFRAME + 1,
            moduli=DEFAULT_MODULI,
        )
        self.assertTrue(check.exact_on_domain)
        self.assertFalse(check.matches)
        self.assertGreater(check.modulus_product, TS30_SAMPLES_PER_SUBFRAME)

    def test_equal_signatures_are_not_universally_equal(self):
        product = moduli_product(DEFAULT_MODULI)
        self.assertEqual(residue_signature(0), residue_signature(product))


if __name__ == "__main__":
    unittest.main()

