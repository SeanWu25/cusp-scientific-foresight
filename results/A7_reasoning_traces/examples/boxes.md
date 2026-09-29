# A7 curated examples

Each box is selected programmatically from the coded data by the stated rule, not hand-picked, so the selection is reproducible (`scripts/a7_examples.py`, seed 31). Codes shown are the consensus labels of the two blind coders. Model identity is given here because these boxes are for the reader, not the coder.


## Box 1. Round-year anchoring on the temporal task

*Failure mode: weak extrapolation.* GPT-5.4, date task, base condition, event published 2025-07 (pre-cutoff for this model).

**Question.** By what month and year (in YYYY-MM format) do you predict a method will enable natural biomes to sustain biological nitrogen fixation (BNF) at 65 (52-77) Tg N yr-1, while agricultural BNF in croplands and cultivated pastures is 56 (54-58) Tg N yr-1, representing a 64% increase in terrestrial BNF and a 60% increase in total terrestrial nitrogen inputs over pre-industrial levels? Respond with exactl ...

**Stated justification.** “This level of ecosystem-scale enhancement in natural-biome nitrogen fixation implies a mature, widely deployed bioengineering or ecosystem-management method that substantially shifts the global nitrogen cycle, which is likely a late-21st-century achievement rather than a near-term result. Given current slow progress in durable field-scale microbiome engineering and biosphere intervention, a first credible public demonstration is most plausible around the 2070s.”

**Answer given.** 2074-06   **Ground truth.** 2025-07.  Signed error: +587 months.

**Codes.** DIFFICULTY_APPEAL, FIELD_MOMENTUM, ROUND_ANCHOR. Hedging level 1.0.

## Box 2. A derived rate of progress, still far too slow

*Failure mode: weak extrapolation.* DeepSeek-R1, date task, base condition, event published 2024-04 (pre-cutoff for this model).

**Question.** By what month and year (in YYYY-MM format) do you predict a method will result in 45% of urban lands in China's major cities subsiding faster than 3 millimeters per year, 16% subsiding faster than 10 millimeters per year—affecting 29% and 7% of the urban population respectively—and by 2120, 22 to 26% of coastal lands having a relative elevation lower than sea level, hosting 9 to 11% of the coastal ...

**Stated justification.** “Current subsidence trends in China's cities, driven by groundwater extraction and urbanization, suggest accelerating rates. Existing models project significant coastal impacts by 2120, but reaching the specified urban subsidence thresholds (45% at >3mm/year, 16% at >10mm/year) likely requires 2-3 decades of unchecked growth and delayed mitigation efforts.”

**Answer given.** 2045-05   **Ground truth.** 2024-04.  Signed error: +253 months.

**Codes.** RATE_OF_PROGRESS. Hedging level 1.0.

## Box 3. Recognising the underlying publication, and dating it correctly

*Failure mode: recognition rather than forecasting.* GPT-5.6 Sol, date task, ws condition, event published 2025-04 (pre-cutoff for this model).

**Question.** By what month and year (in YYYY-MM format) do you predict a method will be designed where peptidomimetic inhibitors with a nitrile warhead inhibit the poxvirus core protease with half-maximal inhibitory concentrations ranging from 44.9 to 100.3 nM and demonstrate potent and broad anti-poxvirus activity? Respond with exactly one date in YYYY-MM format.

**Stated justification.** “The described nitrile-warhead peptidomimetic inhibitors and broad anti-poxvirus activity correspond to the Nature report published in May 2025.”

**Answer given.** 2025-05   **Ground truth.** 2025-04.  Signed error: +1 months.

**Codes.** PROVENANCE_INFERRED. Hedging level 0.0.

## Box 4. Recognising the underlying publication, and answering Yes because of it

*Failure mode: recognition rather than forecasting.* Claude Sonnet 5, binary task, base condition, event published 2025-03 (pre-cutoff for this model).

**Question.** By March 2025, will a method recover fluorine as KF and K2PO3F from multiple classes of PFAS under solvent-free conditions?

**Stated justification.** “This describes a very specific and niche chemical process (fluorine recovery as KF and K2PO3F from PFAS under solvent-free conditions) that matches a known 2024 defluorination study (e.g., from UC Berkeley/Northwestern) using mechanochemical or KOH-based methods for PFAS destruction, which reportedly achieved such fluorine mineralization across multiple PFAS classes.”

**Answer given.** yes   **Ground truth.** yes.  Judge read the justification as arguing: Yes.

**Codes.** EVIDENCE_CITED, PROVENANCE_INFERRED. Hedging level 1.0.

## Box 5. Absence of known work read as evidence the event did not occur

*Failure mode: missing knowledge.* Claude Opus 4.8, binary task, base condition, event published 2026-01 (post-cutoff for this model).

**Question.** By January 2026, will a method detect a protocluster at z ≳ 5 with confirmed X-ray data and a bolometric X-ray luminosity exceeding 10^44 erg s^-1?

**Stated justification.** “Detecting X-ray emission from protoclusters at z≳5 is extremely challenging due to faintness and instrument sensitivity limits; the intracluster medium is not yet virialized at these redshifts, and no such confirmed detection with L_X > 10^44 erg/s has been reported.”

**Answer given.** no   **Ground truth.** yes.  Judge read the justification as arguing: No.

**Codes.** ABSENCE_AS_EVIDENCE, DIFFICULTY_APPEAL. Hedging level 0.0.

## Box 6. The same move, rewarded on the perturbed variant

*Failure mode: missing knowledge.* GPT-OSS 20B, binary_perturbed task, base condition, event published 2024-02 (pre-cutoff for this model).

**Question.** By February 2024, will a method stabilize conspecific negative density dependence consistently in tropical forests with over 500 species?

**Stated justification.** “No known method has been proven to consistently stabilize conspecific negative density dependence across tropical forests with over 500 species by February 2024.”

**Answer given.** no   **Ground truth.** no.  Judge read the justification as arguing: No.

**Codes.** ABSENCE_AS_EVIDENCE. Hedging level 0.0.

## Box 7. An admitted knowledge gap, followed by a committed answer

*Failure mode: uncertainty representation.* Claude Opus 4.8, binary_perturbed task, base condition, event published 2025-08 (pre-cutoff for this model).

**Question.** By August 2025, will a method establish a direct causal link between enzyme activity and Catel-Manzke syndrome?

**Stated justification.** “Catel-Manzke syndrome is primarily linked to mutations in TGDS (TDP-glucose 4,6-dehydratase), an enzyme, but establishing a direct causal link between enzyme activity and the syndrome remains unresolved as of my knowledge; the enzymatic mechanism is still poorly understood.”

**Answer given.** no   **Ground truth.** no.  Judge read the justification as arguing: No.

**Codes.** KNOWLEDGE_GAP_ADMITTED. Hedging level 1.0.

## Box 8. Field momentum standing in for a forecast

*Failure mode: weak extrapolation.* Claude S4.5, binary task, base condition, event published 2024-05 (pre-cutoff for this model).

**Question.** By May 2024, will a method achieve 100-gram synthesis of decarboxylative trifluoromethylation of sensitive (hetero)arenes using photoelectrochemical flow cells with robust photoanode stability of approximately 380 hours?

**Stated justification.** “This question is highly specific about multiple technical parameters (100g scale, decarboxylative trifluoromethylation, photoelectrochemical flow cells, 380-hour stability) that would need to be simultaneously achieved by May 2024. While photoelectrochemical methods and flow chemistry are active research areas, achieving this exact combination of scale, substrate scope, and photoanode stability within this timeframe seems unlikely given typical research development timelines and the specificity of the requirements.”

**Answer given.** no   **Ground truth.** yes.  Judge read the justification as arguing: No.

**Codes.** CONJUNCTION_BURDEN, FIELD_MOMENTUM, SPECIFICITY_AS_IMPLAUSIBLE. Hedging level 1.0.

## Box 9. Specific prior evidence cited, and the answer is right

*Failure mode: knowledge used well.* Claude Opus 4.8, binary task, base condition, event published 2026-02 (post-cutoff for this model).

**Question.** The Multidisciplinary Reasoning (HLE) - with tools benchmark evaluates the ability of large language models to answer expert-level, closed-ended academic questions across a wide range of subjects, including mathematics, humanities, and natural sciences. It is designed to assess reasoning and knowledge at the frontier of human expertise, with questions that are unambiguous, verifiable, and resistan ...

**Stated justification.** “HLE with tools has seen rapid progress, with systems already reaching high 30s-40s in 2025. Given the trajectory and tool-augmented improvements, 53% by Feb 2026 is plausible but not certain.”

**Answer given.** yes   **Ground truth.** yes.  Judge read the justification as arguing: Yes.

**Codes.** CONSTRAINT_CHECKED, EVIDENCE_CITED, FIELD_MOMENTUM. Hedging level 1.5.

## Box 10. Retrieved sources quoted, conclusion unchanged from the base run

*Failure mode: agent setup.* Claude Sonnet 5, binary task, ws_cutoff condition, event published 2025-11 (pre-cutoff for this model).

**Question.** By November 2025, will a method achieve a peak external quantum efficiency (EQE) of at least 45.5%, an average peak EQE of at least 40.9%, a turn-on voltage of no more than 3.2 V, and a half-lifetime of at least 64 hours at an initial radiance of 70 W sr-1 m-2?

**Stated justification.** “Source 7 describes a Nature paper reporting tandem perovskite LEDs achieving exactly these specifications (45.5% peak EQE, 40.9% average peak EQE, 3.2V turn-on voltage, 64h half-lifetime at 70 W sr-1 m-2), matching the question's threshold precisely, and this appears to already be published.”

**Answer given.** yes   **Ground truth.** yes.  Judge read the justification as arguing: Yes.

**Codes.** EVIDENCE_CITED, PROVENANCE_INFERRED. Hedging level 1.0.

## Box 11. A justification arguing one way, an answer going the other

*Failure mode: faithfulness.* DeepSeek-R1, binary_perturbed task, base condition, event published 2024-06 (pre-cutoff for this model).

**Question.** By June 2024, will a method identify definitive genetic markers uniquely tied to human-directed breeding strategies?

**Stated justification.** “Current advancements in genomics and machine learning are accelerating the identification of genetic markers linked to breeding, but establishing a definitive method by June 2024 may face challenges in validation and generalizability across species.”

**Answer given.** yes   **Ground truth.** no.  Judge read the justification as arguing: No.

**Codes.** FIELD_MOMENTUM. Hedging level 1.0.

## Box 12. A justification that only restates the question

*Failure mode: no reasoning offered.* Claude Opus 4.8, date task, base condition, event published 2024-12 (pre-cutoff for this model).

**Question.** By what month and year (in YYYY-MM format) do you predict a method will be developed in mouse models where the lnc-eRNA and its R-loop are shown to be required for the development of behavioral adaptations induced by chronic psychosocial stress or cocaine exposure? Respond with exactly one date in YYYY-MM format.

**Stated justification.** “This is a highly specific neuroscience/epigenetics research question involving lncRNA-derived enhancer RNAs and R-loops in stress/addiction models; such specialized mechanistic work typically follows initial characterization studies by a few years.”

**Answer given.** 2026-06   **Ground truth.** 2024-12.  Signed error: +18 months.

**Codes.** none. Hedging level 1.0.

## Box 13. Hedged to the point of no commitment

*Failure mode: uncertainty representation.* Claude S4.5, binary_perturbed task, base condition, event published 2025-05 (post-cutoff for this model).

**Question.** By May 2025, will a method surpass Claude-3.7-Sonnet-Thinking in performance on seven long-context document question-answering benchmarks while requiring less than 4x its computational cost?

**Stated justification.** “Claude-3.7-Sonnet-Thinking does not exist as a publicly known model as of my knowledge cutoff (April 2024). The question appears to reference a hypothetical future model. Without knowing the baseline performance or computational requirements of this non-existent model, and given the short timeframe to May 2025, it's impossible to meaningfully evaluate whether another method will surpass it. The question may contain an error or refer to speculative future developments.”

**Answer given.** no   **Ground truth.** no.  Judge read the justification as arguing: UNDETERMINED.

**Codes.** CUTOFF_REFERENCED, SPECIFICITY_AS_IMPLAUSIBLE. Hedging level 3.0.

## Box 14. Mechanistic multiple choice answered from recognition

*Failure mode: recognition rather than forecasting.* GPT-5.4, mcq task, ws condition, event published 2025-05 (pre-cutoff for this model).

**Question.** Given the challenge of improving accuracy in medical QA systems by addressing hallucinations and irrelevant retrievals, which of the following approaches is most likely to achieve up to 16.67% improvement on BioASQ and 12.20% on PubMedQA by May 2025? (A) Leverage reinforcement learning to optimize retrieval ranking and refine answer generation iteratively. (B) Use domain-specific pretraining to en ...

**Stated justification.** “The reported gains exactly match Discuss-RAG, which uses agent-led multi-turn brainstorming plus a decision/snippet-filtering agent before integrating retrieved evidence into the final answer. This corresponds most closely to the option describing agents for multi-turn discussion and snippet filtering.”

**Answer given.** D   **Ground truth.** D.  Judge read the justification as arguing: D.

**Codes.** PROVENANCE_INFERRED. Hedging level 0.5.
