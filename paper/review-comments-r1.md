## Review Round 1 — 2026-03-14

### Reviewer A (Methodology)

- **Decision**: Major Revision

**Critical Issues:**

1. **Insufficient Evolutionary Generations**: The paper claims "rapid convergence" but only 20 generations across 2 rounds is extremely small for evolutionary algorithms. The marginal improvement in Round 2 (0.0005) suggests the algorithm plateaued prematurely, not that it converged to a global optimum. Standard evolutionary algorithms for PDE solving typically require hundreds to thousands of generations. The claim of "efficiency" is misleading if the solution quality is limited by insufficient search.

2. **Missing Theoretical Foundation**: The paper lacks any theoretical analysis of why LLM-guided evolution should work for this specific PDE class. There is no discussion of:
   - The function space from which solutions are drawn
   - Convergence properties or guarantees
   - Why the specific mutation/crossover operators are appropriate for Helmholtz-type equations
   - The expressiveness of the Python function space for approximating neutron diffusion solutions

3. **Unfair Baseline Comparison**: The FEM baseline score (0.0652) is suspiciously low compared to FDM (0.5695). This suggests a suboptimal FEM implementation rather than a fundamental limitation. The paper acknowledges this briefly but does not provide:
   - Mesh convergence analysis showing FEM approaches the correct solution with refinement
   - Comparison against established reactor physics codes (e.g., OpenMC, Serpent)
   - Justification for the specific element order and mesh size chosen

4. **Hyperparameter Selection Opaque**: The evolution hyperparameters (8 islands, 100 population, migration every 10 generations) are stated without justification or sensitivity analysis. Were these tuned? Are they standard values from FunSearch? The reader cannot assess whether better results could be achieved with different settings.

5. **LLM Role Under-Specified**: The paper claims "LLM-guided" evolution but provides no details on:
   - Which LLM was used (GPT-4, Claude, etc.)
   - The prompt engineering strategy
   - How the LLM is invoked (API calls, local model, etc.)
   - The computational cost of LLM queries relative to fitness evaluation
   - Ablation showing evolution with vs. without LLM guidance

**Questions Requiring Clarification:**

1. What is the total computational cost (including LLM API calls) compared to training a PINN or running FEM with mesh refinement?
2. Can the authors provide mesh convergence data for FEM showing it approaches the spectral method solution?
3. Why was evolution stopped at 2 rounds? What happens if continued?
4. What is the variance across multiple independent evolutionary runs? Is 0.8805 the best, mean, or median score?

**Required Experiments/Analysis:**

1. Run at least 5 independent evolutionary trials and report mean/std of final scores
2. Provide FEM mesh convergence analysis (coarse → fine mesh scores)
3. Include ablation study: evolution with random mutation vs. LLM-guided mutation
4. Report total computational cost including LLM API calls and wall-clock time
5. Extend evolution to at least 100 generations to demonstrate true convergence behavior

---

### Reviewer B (Experimental Adequacy)

- **Decision**: Major Revision

**Critical Issues:**

1. **Statistical Significance Not Established**: The claimed improvement of +0.19% (0.8805 vs 0.8788) is smaller than typical experimental variance in evolutionary algorithms. The paper provides no confidence intervals, p-values, or statistical tests to establish that this difference is significant. Without multiple runs, this "improvement" may be purely stochastic.

2. **Missing Ablation Studies**: The paper lacks critical ablation experiments:
   - No analysis of island count impact (why 8 islands?)
   - No analysis of population size impact
   - No comparison against standard genetic programming without LLM
   - No analysis of the importance of migration
   - No sensitivity analysis for the boundary condition weight λ

3. **Insufficient Boundary Condition Analysis**: While Figure \ref{fig:boundary_residual} shows residuals, the paper does not quantify:
   - Maximum boundary residual (only shows "slightly higher")
   - Whether boundary conditions are satisfied within engineering tolerances
   - Comparison of boundary residual magnitudes across all methods
   - The effect of the non-homogeneous left boundary on overall solution quality

4. **No Generalization Validation**: The paper evaluates on a single problem instance with fixed parameters (Table \ref{tab:parameters}). There is no validation:
   - Across different domain sizes
   - With different boundary condition values
   - With perturbed physical parameters
   - On different geometries (non-square domains)

5. **Missing Baseline: Neural Operators**: The Related Work section discusses Neural Operators (DeepONet, FNO, LNO) extensively, but these methods are not included in the experimental comparison. Given that LNO is cited as achieving "state-of-the-art performance," its omission from the results table is a significant gap.

**Data Integrity Concerns:**

1. The evolution table shows Round 2 starting at 0.8800 and ending at 0.8805 with only 1 generation. This suggests Round 2 was essentially a continuation of Round 1, not a true second round of evolution. The distinction between "rounds" appears arbitrary.

2. The initial score of 0.5330 in Round 1 is remarkably high for a random initial population. What is the distribution of initial population scores? This raises questions about whether the initial population was seeded with prior knowledge.

**Questions Requiring Clarification:**

1. How many independent evolutionary runs were performed? What is the variance?
2. Why are Neural Operators (DeepONet, FNO, LNO) discussed but not evaluated?
3. What is the physical interpretation of the 0.8805 score? Is there an absolute scale or is this purely relative?
4. Were any runs that performed worse than reported excluded from the paper?

**Required Experiments/Analysis:**

1. Minimum 10 independent evolutionary runs with statistical analysis (mean, std, confidence intervals)
2. Include at least one Neural Operator baseline (FNO or DeepONet) in the comparison
3. Ablation studies for: island count, population size, LLM vs random mutation
4. Generalization test on at least 3 different problem configurations
5. Mesh convergence study for all numerical baselines (FDM, FEM, Chebyshev)
6. Report absolute error metrics (L2, L∞) against a high-fidelity reference solution

---

### Cross-Cutting Issues (Both Reviewers)

**Abstract Structure:**
The abstract claims to follow a "4-layer递进结构" but does not clearly demarcate these layers. The current structure mixes context, method, results, and implications without clear transitions. The abstract also contains excessive numerical detail (0.8805, 0.8788, 0.19%, 0.0122s) that obscures the main message.

**Research Gap Mapping:**
The Introduction identifies several gaps:
- Gap 1: PINNs for neutron diffusion focus on single-group or time-dependent problems
- Gap 2: Evolutionary approaches not applied to coupled-group neutron diffusion

However, the Related Work subsections do not directly map to these gaps:
- Section 2.2 (PINNs) does not discuss the single-group limitation
- Section 2.4 (Evolutionary Approaches) does not discuss why prior work excluded neutron diffusion

**Citation Consistency:**
- LNO is cited as "NeurIPS 2024" but should verify if this is a preprint or published work
- "Song et al. \cite{song2025fcpinns}" cites a 2025 paper which may not be available to readers

**Figure Quality:**
- Figure \ref{fig:evolution} caption claims fitness improves from 0.30 to 0.90, but the text states Round 1 started at 0.5330. This discrepancy needs resolution.
- Figure \ref{fig:main_results} is referenced but the actual figure file has not been verified to exist or contain the claimed data.

---

### Round 1 Conclusion

- **Release Decision**: No
- **Required Round**: Round 2 (after major revisions)

**Paper Writer Action Items (Priority Order):**

**P0 (Must Address):**
1. Run multiple independent evolutionary trials (≥5) and report statistical significance of results
2. Provide FEM mesh convergence analysis to validate baseline implementation
3. Include Neural Operator baseline (FNO or DeepONet) in comparison table
4. Clarify the distinction between "rounds" and "generations" - why did Round 2 only have 1 generation?
5. Report total computational cost including LLM API calls

**P1 (Strongly Recommended):**
6. Add ablation study: LLM-guided vs random mutation
7. Provide sensitivity analysis for key hyperparameters (islands, population, λ)
8. Include generalization tests on at least 2 different problem configurations
9. Resolve discrepancy between Figure \ref{fig:evolution} caption (0.30 start) and text (0.5330 start)
10. Add absolute error metrics (L2, L∞) against high-fidelity reference

**P2 (Polish):**
11. Restructure abstract with clearer 4-layer progression
12. Ensure Research Gap → Related Work subsection mapping is explicit
13. Verify all figure files exist and match text descriptions
14. Add discussion of why evolution was stopped at 2 rounds/20 generations

---

### Reviewer Notes on Data Verification

**Verified Against Raw Data:**
- Famou final score (0.8805): ✓ Matches `/famou/task-helmholtz/results.json`
- Chebyshev baseline (0.8788): ✓ Matches `/baselines/chebyshev/results.json` (0.878797 rounded)
- PINN score (0.6780): ✓ Matches `/baselines/pinn/results.json` (0.677952 rounded)
- FDM score (0.5695): ✓ Matches `/baselines/fdm/results.json` (0.569491 rounded)
- FEM score (0.0652): ✓ Matches `/baselines/fem/results.json` (0.065164 rounded)
- Analytical score (0.5097): ✓ Matches `/baselines/analytical/results.json` (0.509681 rounded)
- Evolution rounds: ✓ Round 1: 19 gens (0.53→0.88), Round 2: 1 gen (0.88→0.8805)

**Data Concerns:**
- Round 2 having only 1 generation is unusual and suggests the "round" structure may be artificial
- FEM score is an order of magnitude worse than other methods, suggesting implementation issues
