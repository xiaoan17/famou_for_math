# Introduction Draft

**Project**: Solving 2D Two-Group Neutron Diffusion Equation via Evolutionary Framework
**For**: Paper Writer Agent
**Date**: 2026-03-14

---

## Draft Text (Ready for Paper)

### Paragraph 1: Background and Motivation

The neutron diffusion equation is a fundamental mathematical model in nuclear engineering, describing the spatial distribution of neutron flux within nuclear reactor cores. Accurate and efficient solution of this equation is critical for reactor design, safety analysis, and operational optimization. Traditional numerical methods, such as finite difference and finite element methods, have been the workhorses of reactor physics for decades, providing reliable solutions but often requiring significant computational resources, especially for high-fidelity simulations. The two-group diffusion approximation, which separates neutrons into fast and thermal energy groups, represents the industry standard for practical reactor calculations, balancing physical accuracy with computational tractability.

### Paragraph 2: Challenges and Limitations

Despite their widespread use, conventional numerical approaches face several challenges when applied to neutron diffusion problems with complex boundary conditions. Neumann boundary conditions, which specify the neutron current rather than the flux itself, arise naturally in reactor physics but require careful treatment to maintain accuracy and stability. Mixed boundary conditions—combining non-homogeneous Neumann conditions on some boundaries with homogeneous conditions on others—further complicate the numerical solution process. Moreover, the coupled nature of the two-group equations, where the fast group source depends on both groups' fluxes while the thermal group is driven by the fast group, introduces additional computational complexity that can strain traditional solvers.

### Paragraph 3: AI for Science Revolution

The emergence of artificial intelligence for science (AI4S) has opened new avenues for solving partial differential equations (PDEs). Physics-Informed Neural Networks (PINNs) embed physical constraints directly into the loss function, enabling mesh-free solutions that can handle complex geometries and inverse problems. Neural operators, including DeepONet and Fourier Neural Operator (FNO), learn solution mappings between function spaces, offering remarkable generalization capabilities. Recent advances, such as the Latent Neural Operator (LNO) presented at NeurIPS 2024, have demonstrated significant improvements in efficiency and accuracy, achieving 50% GPU memory reduction while maintaining state-of-the-art performance on benchmark problems.

### Paragraph 4: Evolutionary Computation for PDEs

A particularly promising direction in AI4S is the application of evolutionary algorithms to PDE solving. FunSearch, introduced by DeepMind in Nature 2023, demonstrated that Large Language Models (LLMs) combined with evolutionary search can discover novel solutions to mathematical problems, including the first improvement to the cap set problem in 20 years. Unlike neural network approaches that require extensive training and often produce black-box models, evolutionary frameworks like FunSearch generate interpretable programs that explicitly encode the solution methodology. For PDE applications, this paradigm converts the problem into an optimization over code space, where candidate solutions are evaluated based on how well they satisfy the governing equations and boundary conditions.

### Paragraph 5: Research Gap and Contribution

However, the application of LLM-guided evolutionary search to coupled-group neutron diffusion equations with mixed Neumann boundary conditions remains unexplored. Existing work on PINNs for neutron diffusion has focused primarily on single-group formulations or time-dependent problems, while evolutionary approaches have not yet been applied to this important class of reactor physics problems. This paper presents the first application of the Famou evolutionary framework to the steady-state two-group neutron diffusion equation with non-trivial Neumann boundary conditions. Our approach evolves Python functions that simultaneously satisfy both the fast and thermal group equations while respecting the specified boundary conditions, including the spatially varying non-homogeneous Neumann condition on the left boundary.

### Paragraph 6: Problem Statement

Specifically, we consider the two-group neutron diffusion equation on a square domain $\Omega = [-0.5, 0.5] \times [-0.5, 0.5]$:

\begin{align}
-D_1 \nabla^2 \phi_1 + \Sigma_r \phi_1 &= \nu \Sigma_{f1} \phi_1 + \nu \Sigma_{f2} \phi_2, \\
-D_2 \nabla^2 \phi_2 + \Sigma_{a2} \phi_2 &= \Sigma_{1\to2} \phi_1,
\end{align}

where $\phi_1$ and $\phi_2$ represent the fast and thermal neutron fluxes, respectively. The boundary conditions are of Neumann type, with a spatially varying non-homogeneous condition on the left boundary ($x = -0.5$) where $-D \partial\phi/\partial x = y$, and homogeneous Neumann conditions ($\partial\phi/\partial n = 0$) on the remaining three boundaries.

### Paragraph 7: Method Overview

Our methodology employs the Famou evolutionary framework, which combines LLM-based code generation with island-based evolutionary search. Candidate solutions are Python functions that compute both $\phi_1(x,y)$ and $\phi_2(x,y)$ given spatial coordinates. The fitness function evaluates how well each candidate satisfies the PDE residuals at interior test points and the boundary condition residuals at boundary points. Through iterative evolution across multiple islands with periodic migration, the framework discovers increasingly accurate analytical approximations to the true solution.

### Paragraph 8: Contributions

The contributions of this work are threefold:

1. **Novel Application**: We present the first application of LLM-guided evolutionary search to the two-group neutron diffusion equation with mixed Neumann boundary conditions, demonstrating the viability of this approach for reactor physics problems.

2. **Comprehensive Evaluation**: We conduct extensive comparisons against established baselines, including finite difference methods, physics-informed neural networks, and spectral methods, providing a thorough assessment of the evolutionary approach's accuracy and efficiency.

3. **Interpretable Solutions**: Unlike neural network approaches that produce opaque models, our method generates explicit analytical expressions that can be inspected, analyzed, and potentially deployed in production reactor analysis codes.

### Paragraph 9: Paper Organization

The remainder of this paper is organized as follows. Section 2 reviews related work on neutron diffusion solvers, physics-informed neural networks, and evolutionary approaches to PDE solving. Section 3 presents the mathematical background of the two-group diffusion equation and the Famou evolutionary framework. Section 4 describes our experimental setup, including baseline implementations and evaluation metrics. Section 5 presents our results, comparing the evolutionary approach against traditional and neural baselines. Section 6 discusses the implications of our findings and potential directions for future research. Finally, Section 7 concludes the paper.

---

## Alternative Paragraph Options

### Alternative Paragraph 1 (More Technical)

The neutron transport equation, describing the motion of neutrons through matter, is a seven-dimensional integro-differential equation that is computationally prohibitive for routine reactor analysis. The diffusion approximation reduces this complexity by assuming neutron motion is predominantly in the direction of the flux gradient, yielding a second-order elliptic PDE. The two-group formulation further simplifies the energy dependence by partitioning neutrons into fast and thermal groups, coupled through group transfer terms. While this approximation sacrifices some physical fidelity compared to full transport calculations, it remains the cornerstone of practical reactor design and analysis.

### Alternative Paragraph 4 (More Focused on FunSearch)

Recent breakthroughs in program synthesis have demonstrated that Large Language Models, when combined with systematic search algorithms, can discover novel solutions to challenging mathematical problems. FunSearch, developed by Google DeepMind and published in Nature, pioneered this approach by using an LLM to generate Python programs that are evaluated and evolved through an island-based genetic algorithm. Unlike traditional optimization methods that search in parameter space, FunSearch operates in code space, discovering algorithmic solutions that are both interpretable and generalizable. This paradigm shift from "learning what" to "learning how" offers unique advantages for scientific computing problems where the solution structure itself is unknown.

---

## Key Citations to Include

### Essential Citations

1. **FunSearch**: Romera-Paredes, B., et al. (2023). Mathematical discoveries from program search with large language models. *Nature*, 624(7992), 452-459.

2. **PINNs**: Raissi, M., Perdikaris, P., & Karniadakis, G.E. (2019). Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations. *Journal of Computational Physics*, 378, 686-707.

3. **DeepONet**: Lu, L., et al. (2021). Learning nonlinear operators via DeepONet based on the universal approximation theorem of operators. *Nature Machine Intelligence*, 3(3), 218-229.

4. **FNO**: Li, Z., et al. (2021). Fourier Neural Operator for Parametric Partial Differential Equations. *ICLR 2021*.

5. **Neutron Diffusion PINN**: Song, M., Zhang, T., & Liu, X. (2025). FC-PINNs: Physics-informed neural networks for solving neutron diffusion eigenvalue problem with interface considerations. *Journal of Computational Physics*, 541, 114311.

6. **LNO**: Wang, T., & Wang, C. (2024). Latent Neural Operator for Solving Forward and Inverse PDE Problems. *NeurIPS 2024*.

7. **Nuclear Reactor Analysis**: Duderstadt, J.J., & Hamilton, L.J. (1976). *Nuclear Reactor Analysis*. Wiley.

### Optional Citations

- Latz, J., et al. (2024). Fast and accurate emulation of PDEs with Gaussian processes. *NeurIPS 2024*.
- Kovachki, N., et al. (2023). Neural Operator: Learning Maps Between Function Spaces with Applications to PDEs. *JMLR*, 24(89), 1-97.

---

## Notes for Paper Writer

1. **Tone**: Academic, formal, suitable for NeurIPS/ICML/AI4Science venue
2. **Length**: Approximately 1-1.5 pages in double-column format
3. **Emphasis**: Position the work at the intersection of AI4S and nuclear engineering
4. **Novelty Claim**: First application of LLM-guided evolution to two-group neutron diffusion
5. **Technical Depth**: Sufficient for ML audience without nuclear background, but with enough detail for domain experts

---

*Draft prepared by Background Researcher Agent*
*Last updated: 2026-03-14*
