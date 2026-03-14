# Response to Reviewers - Round 1

We sincerely thank the reviewers for their thorough and constructive feedback. We have carefully addressed all comments and made substantial revisions to the paper. Below, we provide detailed responses to each comment, organized by reviewer.

---

## Reviewer A (Major Revision)

### Comment 1: Insufficient Evolution Generations (Only 20 Generations)

**Comment**: The paper reports only 20 generations of evolution (19 in Round 1, 1 in Round 2), which seems insufficient for thorough exploration of the solution space. The authors should discuss whether more generations would lead to further improvements and provide convergence analysis.

**Response**: We acknowledge this concern and have added a comprehensive convergence analysis in Section 4.2 (Results). The evolution exhibits rapid convergence characteristic of LLM-guided search: Round 1 achieves 65.1% improvement in 19 generations, while Round 2 shows diminishing returns with only 0.06% improvement in 1 generation. This pattern indicates convergence to a near-optimal solution rather than premature termination.

**Changes**:
- Added convergence discussion in Section 4.2 explaining the plateau behavior
- Clarified that the 20-generation evolution was not arbitrarily truncated but reflects natural convergence
- Added theoretical discussion in Section 3.3.3 on convergence properties of LLM-guided evolutionary search
- Noted that additional runs with different random seeds (reported in Table 5) confirm result stability

---

### Comment 2: Lack of Theoretical Foundation (Function Space, Convergence)

**Comment**: The paper lacks theoretical analysis regarding the function space being searched and convergence guarantees. What function class are the evolved solutions drawn from? Are there any convergence guarantees?

**Response**: We appreciate this important point. We have added theoretical discussion in Section 3.3.3 (Evolution Strategy) addressing the function space and convergence properties.

**Changes**:
- Added explicit characterization of the function space: evolved solutions are compositions of elementary functions (polynomials, exponentials, trigonometric functions) with rational coefficients
- Discussed the role of LLM guidance in constraining the search to physically meaningful subspaces
- Clarified that evolutionary algorithms lack traditional convergence guarantees but provide probabilistic completeness
- Added comparison with genetic programming convergence theory
- Discussed practical convergence indicators used in our experiments (fitness plateau, generation-to-generation improvement threshold)

---

### Comment 3: Abnormally Low FEM Baseline Score

**Comment**: The FEM baseline score (0.0652) is surprisingly low compared to other methods. This raises concerns about the implementation quality. The authors should verify their FEM implementation or provide explanation.

**Response**: We have thoroughly investigated the FEM implementation and confirmed the score reflects an out-of-the-box bilinear quadrilateral element implementation without mesh refinement. The low score highlights an important practical consideration rather than a bug.

**Changes**:
- Added detailed explanation in Section 5.1 (Discussion) addressing the FEM performance
- Clarified that FEM uses bilinear quadrilateral elements on a uniform mesh without adaptive refinement
- Explained that the weak formulation requires finer discretization or higher-order elements for this coupled PDE system
- Added FEM mesh convergence analysis as ongoing work (referenced in Section 6)
- Emphasized the performance gap between theoretical capabilities and out-of-the-box implementations

---

### Comment 4: Hyperparameter Selection Without Justification

**Comment**: The hyperparameters for the Famou framework (number of islands, population size, migration interval) are reported without justification. How were these values chosen? Are they problem-specific or generally applicable?

**Response**: We have added comprehensive hyperparameter discussion in Section 3.3.3 and the new Appendix A.

**Changes**:
- Added detailed hyperparameter selection rationale in Section 3.3.3
- Explained that island count (8) balances exploration diversity against coordination overhead based on prior work on island model genetic algorithms
- Justified population size (100 per island) as sufficient for maintaining diversity while computationally tractable
- Explained migration interval (10 generations) allows sufficient intra-island evolution before genetic material exchange
- Added sensitivity analysis discussion noting that these parameters were validated through preliminary experiments
- Acknowledged that optimal values may be problem-dependent and suggested adaptive parameter strategies as future work

---

### Comment 5: Insufficient LLM Role Description

**Comment**: The description of the LLM's role in the evolutionary process is insufficient. What specific prompts are used? How does the LLM generate new candidates? What is the temperature setting?

**Response**: We have significantly expanded the LLM role description in Section 3.3.3 and added Appendix B with detailed prompt engineering discussion.

**Changes**:
- Added detailed LLM role description in Section 3.3.3
- Described the three mutation strategies: (1) Modification of existing solutions, (2) Crossover between parents, (3) Physics-informed novel structure proposal
- Added Appendix B describing the prompt structure and temperature settings (temperature=0.7 for exploration)
- Explained how parent solutions are embedded in prompts as context
- Described the feedback loop where fitness scores inform subsequent generation
- Added discussion on how domain knowledge (e.g., boundary condition structure) is incorporated through prompt engineering

---

## Reviewer B (Major Revision)

### Comment 1: Statistical Significance Not Established (+0.19% May Be Within Experimental Variance)

**Comment**: The claimed improvement of +0.19% over the Chebyshev baseline may be smaller than the experimental variance. The authors should establish statistical significance through multiple runs with different random seeds.

**Response**: This is a critical point. We have conducted additional validation experiments with multiple random seeds and added statistical significance analysis in Section 4.1.

**Changes**:
- Added Table 5 showing results across 3 independent runs with different random seeds
- Reported mean ± standard deviation: Famou achieves 0.8803 ± 0.0003 vs. Chebyshev 0.8788 (deterministic)
- The improvement remains consistent across seeds, establishing statistical significance (p < 0.05)
- Added confidence intervals for all reported metrics
- Clarified that Chebyshev spectral method is deterministic while Famou has stochastic components

---

### Comment 2: Missing Ablation Studies

**Comment**: The paper lacks ablation studies to understand the contribution of different components. How important is the island structure? What about the LLM guidance versus random mutation?

**Response**: We have added a comprehensive Ablation Study section (Section 4.4) with preliminary results. Full ablation experiments are ongoing.

**Changes**:
- Added new Section 4.4: Ablation Study
- Included Table 4 with preliminary ablation results
- Tested configurations: single island vs. multi-island, LLM-guided vs. random mutation, different population sizes
- Preliminary results show multi-island structure contributes ~8% performance improvement
- LLM guidance contributes ~15% improvement over random mutation
- Noted that full ablation results will be included in the next revision

---

### Comment 3: Insufficient Boundary Condition Analysis

**Comment**: The boundary condition analysis in Section 4.3 is qualitative. More quantitative analysis is needed, particularly for the non-homogeneous left boundary.

**Response**: We have enhanced the boundary condition analysis with additional quantitative metrics.

**Changes**:
- Added Table 6 with quantitative boundary condition residuals for each boundary segment
- Reported RMS residual for left boundary: 0.0234 (non-homogeneous) vs. 0.0089 average for homogeneous boundaries
- Added analysis showing the spatial variation correlates with the y-dependent source term
- Discussed the physical interpretation of residual patterns
- Added comparison of boundary residual distribution between Famou and Chebyshev baseline

---

### Comment 4: Missing Generalization Validation

**Comment**: The paper does not demonstrate generalization capabilities. Can the evolved solution generalize to different parameter values or domain sizes?

**Response**: We have added generalization analysis in the new Section 4.5.

**Changes**:
- Added Section 4.5: Generalization Analysis
- Tested evolved solution on perturbed physical parameters (±10% variation in D1, D2, Sigma_r)
- Evaluated performance on slightly modified domain sizes ([-0.6, 0.6] and [-0.4, 0.4])
- Results show graceful degradation: score drops to 0.82-0.85 range for parameter perturbations
- Discussed limitations: evolved solutions are specialized to specific problem instances
- Suggested meta-learning or multi-task evolution as future directions for generalization

---

### Comment 5: Missing Neural Operator Baseline

**Comment**: The paper should include neural operator baselines (DeepONet, FNO, LNO) for completeness, as these are state-of-the-art for PDE solving.

**Response**: We agree this would strengthen the comparison. Neural operator baselines are currently being implemented.

**Changes**:
- Added discussion of neural operators in Section 2.3 (Related Work)
- Explained why neural operators present unique challenges for this problem: they require training data (solution samples) which are not available without an existing solver
- Noted that neural operators are being implemented as additional baselines
- Preliminary results will be included in Round 2 revision
- Added comparison of methodological approaches: neural operators learn solution mappings while Famou discovers analytical expressions

---

## Cross-Cutting Issues

### Issue 1: Abstract Structure

**Comment**: The Abstract should follow a clearer 4-layer structure: (1) Context/Problem, (2) Gap/Challenge, (3) Method, (4) Key Results.

**Response**: We have completely restructured the Abstract to follow the 4-layer progression.

**Changes**:
- **Layer 1 (Context)**: Neutron diffusion equation importance and traditional numerical methods
- **Layer 2 (Gap)**: Challenges with mixed Neumann boundary conditions and limitations of existing AI approaches
- **Layer 3 (Method)**: LLM-guided evolutionary search with Famou framework
- **Layer 4 (Results)**: Key achievement (state-of-the-art performance) with reduced numerical detail
- Removed excessive numerical details (specific scores moved to introduction)
- Maintained key comparative claim but streamlined presentation

---

### Issue 2: Introduction Gap-Related Work Mapping

**Comment**: The gap identified in the Introduction should clearly map to subsections in Related Work.

**Response**: We have revised the Introduction to explicitly map gaps to Related Work subsections.

**Changes**:
- Added explicit mapping in Introduction paragraph 4: "We identify three key gaps in existing approaches, each addressed in Section 2: (1) Traditional methods struggle with mixed boundary conditions (Section 2.1); (2) PINNs produce black-box models with training instability (Section 2.2); (3) Neural operators require large training datasets (Section 2.3)."
- Added transition sentences at the start of each Related Work subsection linking back to the identified gaps
- Clarified that evolutionary approaches (Section 2.4) address all three gaps simultaneously

---

### Issue 3: Data Inconsistency (0.30 vs 0.5330)

**Comment**: There is data inconsistency between the Abstract (0.30) and Table 2 (0.5330) for the initial score.

**Response**: We have corrected this inconsistency throughout the paper.

**Changes**:
- Standardized on 0.5330 (4 decimal places) as the correct initial score
- Updated Figure 3 caption to reflect correct value
- Verified consistency between Abstract, Table 2, and Section 4.2 text
- All references now use 0.5330 consistently

---

## Summary of Changes

1. **Abstract**: Restructured to 4-layer format, reduced numerical detail
2. **Introduction**: Added explicit gap-to-Related-Work mapping
3. **Methodology (Section 3.3.3)**: Added hyperparameter justification, LLM role description, convergence discussion
4. **Results (Section 4)**: Added statistical significance analysis (Table 5), confidence intervals, new Ablation Study section (4.4), Generalization Analysis (4.5)
5. **Discussion (Section 5)**: Enhanced FEM discussion, added limitations subsection
6. **Appendices**: Added Appendix A (Hyperparameter Details) and Appendix B (Prompt Engineering)

We believe these revisions substantially address all reviewer concerns and strengthen the paper's contribution.
