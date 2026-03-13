## Review Round 2 — 2026-03-13

---

### Reviewer A (Methodology)

- **Decision**: Minor Revision

- **Summary**: The revised paper represents a substantial improvement over Round 1. The critical eigenvalue sign error has been correctly fixed, the well-posedness argument is now sound, a dedicated Limitations section has been added, the GITT discussion appears in Related Work, and the paper has grown to approximately 16 compiled pages (945 LaTeX lines). Three new tables address the requested convergence and pointwise error analyses. However, two new methodological errors have been introduced in the revision that must be corrected before publication: (1) an incorrect physical explanation for the spectral method's sign flip, and (2) an incorrect causal claim about the N_terms convergence table PDE residual floor.

---

#### Remaining Issues from Round 1

**Fixed — Eigenvalue computation (R1 Critical Issue 1):**
The eigenvalues are now correctly stated as $\mu_1 \approx -0.0257$ and $\mu_2 \approx 0.2332$. The derivation is verified: det(M) = 0.0075 × 0.2 − (−0.25)(−0.03) = 0.0015 − 0.0075 = −0.006 < 0, giving discriminant $\sqrt{0.2075^2 + 4 \times 0.006} = \sqrt{0.06706}$, from which $\mu_1 = (0.2075 - 0.25896)/2 \approx -0.02573$ and $\mu_2 \approx +0.23323$. Both values match to the precision stated in the paper. The characteristic polynomial in Eq. (unnumbered, Section 2.4) is correctly written as $\mu^2 - 0.2075\mu - 0.006 = 0$.

**Fixed — Well-posedness argument (R1 Critical Issue 1c):**
The paper now correctly argues that $\alpha_{p,n}^2 = \mu_p + (n\pi)^2 > 0$ for all odd $n \geq 1$. For the critical case $n = 1$, $p = 1$: $\alpha_{1,1}^2 = -0.02573 + \pi^2 \approx -0.026 + 9.870 = 9.844 > 0$. This is correct. The $n = 0$ mode is correctly excluded by $b_0 = 0$. The well-posedness argument is now mathematically rigorous.

**Fixed — Limitations section (R1 Major Issue 4):**
Section 8.1 lists five structural limitations: rectangular geometry, homogeneous medium, BC structure requirements, fixed-source formulation, and two-group truncation. These are accurate and informative.

**Fixed — GITT discussion (R1 Medium Issue 7):**
A paragraph on GITT appears in Section 7.1. The comparison with GITT is fair and the key distinction (fully closed-form vs. numerically solved ODE system) is correctly drawn.

**Fixed — N_terms convergence table (R1 Major Issue 2):**
Table `tab:nterms_convergence` is now present, showing BC residual decreasing from 6.73e-3 (N=5) to 2.02e-6 (N=200). This is the most important addition from R1.

**Fixed — Spectral convergence study (R1 Major Issue 5):**
Table `tab:spectral_convergence` now provides the N=10 to N=50 spectral convergence data.

**Fixed — Related Work comparison (R1 Major Issue 2):**
The Limitations section now clearly scopes the method. The Related Work section provides adequate qualitative comparison, though no formal comparison table was added (see New Issue 1 below).

**NOT Fixed — FDM BC residual anomaly (R1 Reviewer B Major Issue 5):**
Round 1 flagged the non-monotonic FDM BC residual increase from 51×51 to 101×101 to 201×201 as potentially indicating an evaluation bug. The current paper does not discuss this behavior at all. The FDM convergence table (Table `tab:convergence`) should include BC residuals at each grid level and address their behavior.

---

#### New Issues Introduced in Revision

**New Critical Issue 1 — Sign ambiguity claim is physically incorrect (Section 5.7, lines 800–801):**

The paper states: "This is expected for pure Neumann problems: since all four boundaries carry zero or inhomogeneous Neumann conditions, the problem lacks a Dirichlet anchor and admits the solution $\pm\phi_g$ as equally valid."

This statement is **physically and mathematically wrong**. The problem is NOT a pure Neumann problem in the sense that would cause sign ambiguity. The inhomogeneous Neumann condition at $x = -0.5$ is:
$$-D_g \frac{\partial \phi_g}{\partial x}\bigg|_{x=-0.5} = y.$$

Suppose $\phi_g$ satisfies this condition. Then for $-\phi_g$:
$$-D_g \frac{\partial (-\phi_g)}{\partial x}\bigg|_{x=-0.5} = D_g \frac{\partial \phi_g}{\partial x}\bigg|_{x=-0.5} = -y.$$

Since $-y \neq y$ (for $y \neq 0$), the function $-\phi_g$ does **not** satisfy the inhomogeneous BC. The sign of the solution is uniquely determined by the boundary data $f(y) = y$.

The correct statement is: The Chebyshev spectral solver produced a numerical solution with the opposite sign due to a solver-internal convention (e.g., a sign flip in the boundary condition row of the assembled system, or a negative column scaling in the linear solver). This is a numerical artifact and should be diagnosed and corrected. The authors must either: (a) identify the source of the sign flip in the spectral implementation and fix it, or (b) state clearly that the sign flip is a known implementation artifact in their specific spectral code and report the corrected (sign-flipped) pointwise errors for the spectral method in Table 5.

As written, the paper incorrectly teaches readers that inhomogeneous Neumann problems have sign ambiguity, which is false and could mislead future users of the analytical benchmark.

**New Critical Issue 2 — Incorrect explanation of N_terms PDE residual floor (line 533):**

The paper states: "The PDE residual is limited by the numerical differentiation step $h = 10^{-5}$ used for evaluation (not by the analytical solution accuracy), explaining why it plateaus at $\sim 10^{-6}$."

This explanation is **mathematically incorrect**. For a second derivative evaluated via central differences with step $h$, the truncation error is:
$$\text{error in } \frac{\partial^2 \phi}{\partial x^2} \approx \frac{h^2}{12} \frac{\partial^4 \phi}{\partial x^4}.$$

With $h = 10^{-5}$: error $\approx 10^{-10}/12 \times |\partial^4\phi/\partial x^4|$. For the cosh-based analytical solution, the fourth $x$-derivative introduces a factor $\alpha_{p,n}^4 \leq (N\pi)^4 \approx (200\pi)^4 \approx 1.5 \times 10^{11}$ at $N = 200$, BUT these high-$n$ modes are exponentially damped at interior points by the factor $\cosh(\alpha_{p,n}(x-0.5))/\sinh(\alpha_{p,n}) \sim e^{-\alpha_{p,n}}$. The effective fourth-derivative magnitude at interior points is bounded. For $n = 1$: $\alpha_{1,1} \approx \pi$, $\alpha_{1,1}^4 \approx 97.4$; error contribution $\approx 10^{-10} \times 97.4 / 12 \approx 8 \times 10^{-10}$. This is nowhere near $10^{-6}$.

To get a $10^{-6}$ floor from finite differencing, one would need $h \approx 10^{-3}$, not $h = 10^{-5}$.

The actual cause of the $10^{-6}$ plateau in Table `tab:nterms_convergence` is likely one of the following: (a) the 15×15 evaluation grid includes points near the boundary $x = -0.5$ where the Fourier series converges at the slower algebraic rate $O(N^{-2})$, and at $N=10$ or $N=5$ the convergence is not yet dominated by the FD error; (b) the PDE residual in Table `tab:nterms_convergence` is computed by a different code path than the main results table, using numerical rather than analytical derivatives, and the plateau is an artifact of a fixed coarser FD step than $10^{-5}$; or (c) there is a discrepancy in how the two tables define "PDE residual."

The authors must: (i) verify and state the correct cause of the plateau, and (ii) correct the explanation in the note below Table `tab:nterms_convergence`.

Note also the striking inconsistency between tables: the main results table (Table 3) reports analytical PDE residual $2.81 \times 10^{-16}$ (4 test points, analytical derivatives), while Table `tab:nterms_convergence` reports $1.82 \times 10^{-6}$ at $N=200$ (15×15 grid, FD derivatives). This 10-order-of-magnitude discrepancy must be clearly explained to the reader.

---

#### Minor Issues (New)

**Minor Issue A — Spectral convergence rate mischaracterized (Section 5.8, line 826):**
The paper claims "algebraic convergence (roughly $O(N^{-3})$)" for the spectral method. However, (1) for smooth problems on regular domains, Chebyshev spectral methods are theoretically expected to achieve **exponential** convergence $O(e^{-cN})$, not algebraic; the paper itself states this in Section 4.3. Claiming algebraic convergence in Section 5.8 contradicts the statement in Section 4.3. (2) The rate estimated from the data is inconsistent: from the tabulated residuals, a power-law fit gives exponent approximately $N^{-4.6}$, not $N^{-3}$. Specifically, the rate from $N=20$ to $N=25$ is only approximately $0.58$—less than 1, meaning the residual barely changed, not $O(N^{-3})$. The convergence is irregular and the single-sentence characterization should be revised to acknowledge this. The data may reflect that the evaluation method (finite-differencing the spectral solution) introduces its own error floor that masks exponential convergence.

**Minor Issue B — Timing anomaly in spectral convergence table (Table `tab:spectral_convergence`):**
The table shows $N=15$ solving in 0.005 s and $N=10$ solving in 0.011 s. Larger $N$ yielding shorter wall time is physically implausible without explanation (JIT warm-up, caching effects, or measurement noise could cause this). The authors should note this or re-run the timing measurement with averaged repetitions.

**Minor Issue C — Abstract reports cherry-picked L_inf (line 49):**
The abstract states "Pointwise $L_\infty$ errors of the best numerical method (FEM, $101\times101$) are $1.4\times10^{-5}$." This corresponds to $\phi_1$ only (Table 5: FEM $\phi_1$ $L_\infty = 1.37 \times 10^{-5}$). However, FEM $\phi_2$ $L_\infty = 2.63 \times 10^{-5}$—nearly twice as large. The abstract should report the worst-case metric: "max $L_\infty$ errors of the best numerical method (FEM) are $2.6\times10^{-5}$ (thermal group)."

**Minor Issue D — Novelty claim related work table still absent:**
R1 requested a formal comparison table in Related Work listing each prior method's dimensionality, number of groups, BC type, and closed-form status. The current paper does not include such a table. While the novelty claim is better supported by the GITT discussion, the formal table would strengthen the contribution statement.

---

### Reviewer B (Experiments)

- **Decision**: Minor Revision

- **Experimental Completeness Score**: 7/10 (up from 4/10 in Round 1)

- **Summary**: The experimental section has been substantially strengthened. Three major additions (N_terms convergence table, pointwise flux error table, spectral convergence table) address the core R1 deficiencies. The paper now provides: (1) an honest "oracle evaluator" framing for the Famou experiment, (2) quantitative pointwise errors for FDM and FEM, and (3) spectral convergence data. Remaining gaps include the unaddressed PINN baseline weakness, missing error bars for PINN, and an unexplained 10-order-of-magnitude discrepancy between the two analytical PDE residual measurements.

---

#### Remaining Issues from Round 1

**Addressed — N_terms convergence study (R1 Major Issue 2):**
Table `tab:nterms_convergence` is present and shows BC residual converging from 6.73e-3 to 2.02e-6. This is the primary requested addition and is satisfactory. However, the note explaining the PDE residual plateau is incorrect (see Reviewer A New Critical Issue 2 above).

**Addressed — Pointwise flux comparison (R1 Major Issue 4):**
Table `tab:pointwise_errors` provides $L_2$ and $L_\infty$ errors for FDM and FEM against the analytical reference. The FDM $L_2 \approx 3 \times 10^{-6}$ and $L_\infty \approx 1.5 \times 10^{-5}$ for $\phi_1$ are plausible for $O(h^2)$ FDM with $h = 0.01$. The spectral method row is excluded due to a sign ambiguity claim (which is incorrect—see Reviewer A New Critical Issue 1). Once the sign issue is corrected, the spectral method pointwise errors should be reported.

**Addressed — Spectral convergence study (R1 Major Issue 5):**
Table `tab:spectral_convergence` provides convergence data from $N=10$ to $N=50$. The comparison with FEM at the same residual level is informative, though the convergence rate characterization needs correction (see Reviewer A Minor Issue A).

**Partially Addressed — Paper length (R1 Major Issue 1):**
The paper has grown from 477 to 945 LaTeX lines, corresponding to approximately 16–17 compiled pages. This meets the target.

**NOT Addressed — PINN baseline weakness (R1 Major Issue 3):**
The PINN still uses only 5,000 Adam iterations with a 3×64 architecture and no L-BFGS fine-tuning. Round 1 requested either (a) training to near-convergence, or (b) a PINN training convergence curve. Neither is present in the current paper. The Famou section mentions "combined\_score stayed at 0.07 after 30 iterations" (seed = FDM), but does not include PINN training analysis. This remains an open gap. While the paper fairly frames the PINN as a representative baseline rather than an optimized competitor (lines 647–648), the absence of any training curve or seed averaging makes it impossible to know whether the reported PINN result reflects the method's best capability or an undertrained snapshot.

**NOT Addressed — Dense-grid max residual evaluation (R1 Minor Issue 9):**
The main results table still evaluates PDE residuals at only 4 interior test points. This is insufficient for reporting a "max PDE residual." The residual distribution figure (Fig. `fig:residual_comparison`) suggests a dense evaluation was done for visualization purposes; those numbers should be used for the reported max residuals. This inconsistency means the main table numbers are not true maxima.

**NOT Addressed — FDM BC residual anomaly (R1 Major Issue 5):**
The non-monotonic FDM BC residual with grid refinement is not discussed anywhere in the current paper. This is a significant omission given that R1 flagged it as a major issue requiring investigation.

---

#### New Issues (Reviewer B)

**New Issue 1 — Spectral pointwise errors missing from Table 5:**
Table `tab:pointwise_errors` shows "Sign ambiguity (see text)" for the spectral method instead of actual error values. Given that the sign ambiguity explanation is incorrect (see Reviewer A), the spectral errors should be computed (with appropriate sign correction) and reported. A spectral method at $N=30$ achieving PDE residual $7.53 \times 10^{-6}$ (comparable to FEM at 101×101) should show similar or better pointwise flux errors relative to the analytical reference. The absence of these numbers is a gap in the benchmark.

**New Issue 2 — Famou section lacks scientific rigor:**
Section 6 (Famou experiment) reports that after 30 evolution iterations, the combined\_score remained at 0.07 (seed level). The scientific content is thin: no convergence plot of the score over iterations, no description of the specific program variants attempted, no analysis of why the LLM failed to improve the FDM. The claim that "LLM-generated variants tended to optimize one metric at the expense of the other" (line 863) is stated without supporting evidence (e.g., showing how accuracy and PDE residual moved in opposite directions across iterations). The section reads as a negative result reported without sufficient analysis to understand why the method failed. At minimum, a plot of combined\_score vs. iteration and a description of 2–3 representative evolved programs would make this section scientifically informative.

**New Issue 3 — Two-table PDE residual inconsistency needs explicit reconciliation:**
The main results table (Table 3) reports analytical PDE residual $2.81 \times 10^{-16}$ (analytically computed derivatives). Table `tab:nterms_convergence` at $N=200$ reports $1.82 \times 10^{-6}$ (numerically computed derivatives via FD). This 10-order-of-magnitude discrepancy between two tables reporting "the PDE residual of the analytical solution" is confusing to readers. The paper should include an explicit sentence in the caption of Table `tab:nterms_convergence` clarifying that these are not the same metric: the former uses analytical derivatives (exact to machine precision), the latter uses numerical derivatives (limited by FD accuracy). The note at line 533 attempts this but gives an incorrect numerical explanation.

**New Issue 4 — FEM phi_2 L_inf (2.63e-5) inconsistent with abstract claim:**
The abstract (line 49) states FEM $L_\infty \approx 1.4 \times 10^{-5}$. This matches $\phi_1$ only. The $\phi_2$ error is $2.63 \times 10^{-5}$—a factor of 2 larger. Since the thermal flux $\phi_2$ has higher physical importance in thermal reactor analysis, reporting only the fast-group error in the abstract is misleading.

---

#### Minor Issues (Reviewer B)

1. **PINN: no random seed averaging.** The PINN is stochastic; a single-seed result is unreliable. At minimum, state the fixed seed used.

2. **Hardware not fully specified.** The paper says "Apple M-series" but does not specify M1/M2/M3 or the specific model. For reproducibility, state the exact chip and the NumPy/SciPy/PyTorch versions.

3. **Convergence rate formula (line 705):** The formula uses $R_{h_1}/R_{h_2}$ with notation that does not distinguish which subscript is finer vs. coarser. The convergence rate should be written as $r = \log(R_{\text{coarse}}/R_{\text{fine}}) / \log(h_{\text{coarse}}/h_{\text{fine}})$ with a clarifying sentence.

4. **Figure 5 (flux profiles, `flux_profiles.pdf`) lacks error subplot.** R1 Minor Issue 3 requested a subplot showing pointwise differences from analytical. This was not added. A quantitative comparison (even just the max deviation annotated on the plot) would strengthen the figure.

5. **Duplicate accuracy-cost figure.** Figures `fig:cost_accuracy` and `fig:accuracy_cost` appear to be two versions of the same accuracy-vs-cost comparison (one from Python, one a conceptual baoyu figure). Having both is redundant and wastes space.

---

### Round 2 Verdict

- **Can paper be released?**: NO (Minor Revision required)

- **Assessment of R1 critical fixes:**

  | R1 Critical Item | Status |
  |---|---|
  | Eigenvalue sign error corrected | FIXED — mathematically verified |
  | Well-posedness argument for n=1 | FIXED — $\alpha_{1,1}^2 = 9.844 > 0$ confirmed |
  | Paper expanded to ~16 pages | FIXED — 945 lines ≈ 16–17 compiled pages |
  | N_terms convergence table | ADDED — Table `tab:nterms_convergence` present |
  | Pointwise flux errors | ADDED — Table `tab:pointwise_errors` present |
  | Spectral convergence study | ADDED — Table `tab:spectral_convergence` present |
  | Limitations section | ADDED — Section 8.1, 5 limitations listed |
  | GITT discussion | ADDED — Section 7.1 paragraph |

- **Blocking issues before release (action items):**

  1. **[CRITICAL] Fix sign ambiguity explanation (Sec. 5.7):** The claim that $\pm\phi_g$ are equally valid for this problem is mathematically false. The inhomogeneous Neumann BC $-D_g\partial\phi_g/\partial x|_{x=-0.5} = y$ uniquely determines the sign: if $\phi_g$ satisfies it, then $-\phi_g$ satisfies $-D_g\partial\phi_g/\partial x|_{x=-0.5} = -y \neq y$. The spectral sign flip is a numerical artifact in the solver implementation. The text must be corrected and the spectral pointwise errors must be reported (with sign correction).

  2. **[CRITICAL] Correct N_terms PDE residual floor explanation (line 533):** The claim that "$h = 10^{-5}$ FD step explains a $10^{-6}$ floor" is wrong ($h^2 = 10^{-10}$, not $10^{-6}$). The correct cause must be identified and stated. The two-table inconsistency ($2.81 \times 10^{-16}$ vs. $1.82 \times 10^{-6}$) must be explicitly addressed in the caption.

  3. **[HIGH] Address FDM BC residual anomaly from R1 Major Issue 5:** Add BC residuals to the convergence table and discuss whether they show non-monotonic behavior. If the behavior is real, explain the cause.

  4. **[HIGH] Report FEM phi_2 L_inf in abstract:** Replace "$1.4 \times 10^{-5}$" with the worst-case metric ($2.63 \times 10^{-5}$ for $\phi_2$) or state "max over both groups."

  5. **[MEDIUM] Correct spectral convergence rate description:** Do not claim "roughly $O(N^{-3})$" algebraic convergence when: (a) spectral theory predicts exponential convergence for smooth problems, (b) your own Section 4.3 states this, and (c) the data is too irregular to support a specific power law claim.

  6. **[MEDIUM] Add Famou convergence plot:** Include score-vs-iteration curve to make the negative result scientifically informative.

  7. **[LOW] Fix spectral timing anomaly:** Verify and re-run spectral timings; $N=15$ faster than $N=10$ is implausible without explanation.

  8. **[LOW] Remove duplicate accuracy-cost figure** or clearly differentiate the two figures' purposes.

- **Positive assessment:** The eigenvalue fix is mathematically correct and the well-posedness argument is now rigorous. The paper makes a genuine and verifiable contribution with a correct derivation. The three new tables substantially improve experimental completeness. With the two critical fixes above, the paper would be ready for acceptance.
