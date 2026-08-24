# kb-L2-domain-regulatory-uk

*A domain-KB slot, not a food-specific artifact:
`L1-vision-regulatory-feasibility-checker`'s prompt and spec reference this
slot generically, so a different vertical can populate it with its own
regulatory facts without touching the agent at all. This deployment's slot
is filled with UK food-domain content — see below.*

**Domain covered (this deployment):** **United Kingdom** food production &
distribution — FBO registration and approval, hygiene and HACCP, the Food
Hygiene Rating Scheme, allergen and pre-packed labelling (including
Natasha's Law), cold chain and traceability, and the devolved/local-authority
split relevant to a distributor operating across several authorities.

> **One geography per KB.** Jurisdiction is part of this slot. The India
> counterpart is `kb-L2-domain-regulatory-ind`. A deployment serving two
> geographies loads two KBs, selected by the idea brief's `target_geography`
> — never one file with mixed rows, which would let the agent cite a UK rule
> against an Indian idea and still look internally consistent.

**Why it exists:** `L1-vision-regulatory-feasibility-checker` needs real
food-specific facts to classify constraints Green/Amber/Red and to cite a
specific regulation per constraint — generic knowledge isn't enough, and
the full technical regulatory corpus is far more than a vision-stage agent
needs. This is a condensed, purpose-specific cut: PM/feasibility
implications only, not field-level technical detail (that belongs in a
later-phase KB for design/construction agents, not here).

**Sources:** Regulation (EC) 852/2004 (retained); Regulation (EC) 178/2002
(retained), Arts. 18-19; Food Safety Act 1990; Food Safety and Hygiene
(England) Regulations 2013; Food Information Regulations 2014 / retained
Reg. 1169/2011; Natasha's Law (PPDS labelling, in force Oct 2021); retained
Reg. (EC) 1924/2006 (nutrition and health claims); Reg. (EU) 2015/2283
(novel foods, retained); Weights and Measures Act 1985; Food Hygiene Rating
Scheme; Primary Authority Scheme.

**Update frequency:** Quarterly — food regulation changes faster than most
domains. This KB is a starting point for a feasibility assessment, not a
substitute for current FSA/FSS guidance or legal review before registration
or approval. **Post-EU-exit divergence is ongoing** — confirm whether a
retained EU instrument still applies in the form cited before it gates a
real decision.

**Quality bar:** Every constraint bullet must cite a real, named regulation
or scheme. No constraint may be classified Red without also being checked
against `gr-L1-hallucination-check` for whether a mitigation genuinely
exists in this KB or elsewhere. Food law is devolved: where a rule differs
between England, Scotland, Wales and Northern Ireland, say so rather than
stating a single UK-wide answer.

**Owner:** Food Domain Champion

**Consumers:** `L1-vision-regulatory-feasibility-checker`
