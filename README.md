# Exact 5G NR timing boundaries and modular integrity checks

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22314210.svg)](https://doi.org/10.5281/zenodo.22314210)

This repository contains the corrected, reproducible companion material for the preprint **Exact Timing Boundaries and Modular Integrity Checks for 5G NR Numerologies** by Reinaldo Valeris and Gustavo Matheus.

## What is established

- The exact normal-cyclic-prefix schedule is derived in the fundamental 3GPP time unit for numerologies `mu = 0,...,6`.
- Exact slot-start sets are nested across numerologies.
- Physical boundary sets are **not** additive subgroups of the subframe clock.
- Cyclic groups correctly describe abstract slot indices; the physical-time maps are generally not homomorphisms.
- The value 137 at `mu = 4` is a property of the 30.72 MHz reference-grid representation, not evidence of a hardware anomaly.
- Residue vectors are bounded integrity signatures. They do not acquire synchronization from IQ samples and do not replace correlation or likelihood-based estimators.

## Repository layout

- `manuscript/main.tex` and `manuscript/main.pdf`: corrected preprint.
- `src/nr_timing.py`: exact timing and residue-signature model.
- `src/benchmark.py`: direct-equality versus residue-signature microbenchmark.
- `tests/test_nr_timing.py`: automated mathematical and numerical checks.
- `hdl/nr_boundary_monitor.vhd`: boundary monitor with an external observed-event input.
- `hdl/tb_nr_boundary_monitor.vhd`: VHDL-2008 testbench.
- `data/benchmark_results.json`: benchmark environment and measured medians.

## Reproduce the results

Python 3.10 or newer is sufficient; there are no third-party Python dependencies.

```text
python -m unittest discover -s tests -v
python src/benchmark.py
```

Compile the manuscript from the `manuscript` directory after running the benchmark:

```text
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

With GHDL installed, compile and run the VHDL testbench:

```text
ghdl -a --std=08 hdl/nr_boundary_monitor.vhd hdl/tb_nr_boundary_monitor.vhd
ghdl -e --std=08 tb_nr_boundary_monitor
ghdl -r --std=08 tb_nr_boundary_monitor --assert-level=error
```

## Scope

The analysis covers normal CP. The 30.72 MHz tables and VHDL monitor cover `mu <= 4`, where the reference-grid projection is integral. The mathematical timing model itself uses `Tc` ticks and covers `mu = 0,...,6`.

The VHDL block is a transparent reference monitor, not a published area or power optimization. Hardware superiority must be established by synthesis against an explicit binary-counter baseline.

## Citation and DOI

Citation metadata are in `CITATION.cff`. Zenodo provides two persistent identifiers:

- All versions and future releases: [10.5281/zenodo.22314210](https://doi.org/10.5281/zenodo.22314210)
- Archived release `v1.0.0`: [10.5281/zenodo.22314211](https://doi.org/10.5281/zenodo.22314211)

Use the version DOI when citing the exact artifact evaluated in this release. Use the all-versions DOI when referring to the evolving project.

## Licenses

Source code and VHDL are licensed under the MIT License. The manuscript and explanatory documentation are licensed under Creative Commons Attribution 4.0 International; see `LICENSE-DOCUMENTATION`.
