<!--
kb-L2-domain-regulatory-uk · content · food-regulatory-facts.md
Layer: L2 (domain: food production & distribution). Consumed by:
L1-vision-regulatory-feasibility-checker. Micro-KB content rules apply:
max 1 line/bullet, max 15 words, no explanations, numbers not words,
annotated with target category.

JURISDICTION: United Kingdom. One geography per KB — the India
counterpart is kb-L2-domain-regulatory-ind. Never merge rows: a mixed
file lets a constraint cite the wrong country's rule and still look
internally consistent.
-->

# Food Production & Distribution — Regulatory Facts (UK)

## Jurisdiction

**Jurisdiction covered: United Kingdom (ISO 3166-1 alpha-2: GB).**
Sub-national layers in scope: England, Scotland, Wales, Northern Ireland,
and local authorities. Every statute, regulator and threshold below is
UK law, including retained EU law. This KB covers no other country — an
idea targeting a different country cannot be assessed from it, and no
rule here may be translated onto one.

## Registration & Licensing
- Register as Food Business Operator (FBO) with local authority ≥28 days before trading (→ Constraint: Authorization)
- Registration basis: Regulation (EC) 852/2004 Art. 6, retained UK law (→ Constraint: Authorization)
- Most FBOs: registration only, no license required (→ Constraint: Authorization)
- Meat, dairy, fish processing premises: require FSA/local-authority *approval*, not just registration (→ Constraint: Authorization)
- Distance and online food sellers must still register with their local authority (→ Constraint: Authorization)

## Food Hygiene & Safety
- HACCP-based food safety management mandatory for all FBOs — Reg. 852/2004 Art. 5 (→ Constraint: Hygiene)
- Food Hygiene Rating Scheme (FHRS): local authority scores 0–5 (→ Constraint: Hygiene)
- FHRS display: mandatory in Wales/NI, voluntary in England (→ Constraint: Hygiene)
- Food Safety Act 1990 s.21: "due diligence" defence available (→ Constraint: Liability)
- Withdrawal and recall duty on the FBO — Reg. (EC) 178/2002 Art. 19 (→ Constraint: Traceability)

## Allergen Labelling
- 14 major allergens must be declared: celery, gluten cereals, crustaceans, eggs, fish, lupin, milk, molluscs, mustard, tree nuts, peanuts, sesame, soybeans, sulphites (→ Constraint: Labelling)
- Natasha's Law (in force Oct 2021): full ingredient/allergen labelling required on PPDS food (→ Constraint: Labelling)
- Food Information Regulations 2014 / retained Reg. 1169/2011: baseline labelling for pre-packed food (→ Constraint: Labelling)

## Distribution & Cold Chain
- Chilled food: hold at 8°C or below — Food Safety and Hygiene (England) Regs 2013 (→ Constraint: Cold Chain)
- Raw milk for further processing: chilled to 8°C or below, 6°C if not collected daily (→ Constraint: Cold Chain)
- Frozen food: hold at -18°C or below (→ Constraint: Cold Chain)
- Traceability: "one step back, one step forward" record-keeping mandatory — Reg. (EC) 178/2002 Art. 18 (→ Constraint: Traceability)
- Temperature monitoring required during transport, not only storage (→ Constraint: Cold Chain)

## Cross-Cutting
- Primary Authority Scheme: partner with ONE local authority for consistent advice across multi-LA operations (→ Constraint: Multi-jurisdiction risk)
- Food law is devolved: FSA covers England/Wales/NI, FSS covers Scotland (→ Constraint: Multi-jurisdiction risk)
- Weights and Measures Act 1985: quantity/weight labelling accuracy enforced by Trading Standards (→ Constraint: Labelling)
- Novel ingredients (not eaten significantly pre-1997 in EU/UK) require pre-market authorisation — Reg. (EU) 2015/2283 (→ Constraint: New ingredients)
- Health and nutrition claims restricted — retained Reg. (EC) 1924/2006 (→ Constraint: Advertising)

---
*Jurisdiction: United Kingdom · Last reviewed: 2026-08-24 · Review cadence: quarterly
(food regulation changes more frequently than most domains — verify against current
FSA/FSS guidance before use in a real regulatory-feasibility assessment, not just
against this KB alone). Post-EU-exit divergence is ongoing: confirm whether a
retained EU instrument still applies in the form cited.*
