# kb-L1-regulatory-frameworks-index-uk

**Domain covered:** None specific — a cross-domain index of which **UK**
regulatory body governs which category of regulated activity, plus the
coverage-category sweep list every assessment must walk.

**Why it exists:** `L1-vision-regulatory-feasibility-checker` is a generic L1
agent, reused across every domain the CoE builds for. Before it can reason
about food, payments, healthcare, or anything else, it needs to know which
body's rules even apply. This KB is that first lookup — genuinely
domain-agnostic, so it stays at L1 rather than being duplicated into every
L2 domain KB.

> **One geography per KB.** Domain-agnostic is not the same as
> jurisdiction-agnostic. This index is reusable across every vertical but
> holds one country's regulators. The India counterpart is
> `kb-L1-regulatory-frameworks-index-ind`; select the pair by the idea
> brief's `target_geography` — never merged rows, which would let a
> constraint cite the wrong country's regulator and still survive a
> plausibility check.

**Devolved/local:** many UK regimes bind at more than one level — food
registration and inspection, licensing, trading standards, building control,
environmental permits. A UK-wide answer is incomplete where the idea operates
in Scotland, Wales or Northern Ireland, or across several local authorities,
and the checker prompt carries a matching edge case.

## Two sections

| Section | What it is |
|---|---|
| `#cross-domain-index` | Activity → the UK body that governs it |
| `#coverage-categories` | The sweep list: every category is a constraint, or a declared not-applicable entry |

**Why the sweep list is here and not in a prompt:** both the checker and its
evaluator read it — the checker to walk it, the evaluator to audit that it
was walked. Duplicating it into two prompts lets them drift, and the failure
mode is ugly: the evaluator fails the checker for missing a category the
checker was never told about. One file, one list, no drift.

**What deliberately stays out of this KB:** the *behaviour* when a rule
applies awkwardly — not yet in force, under an unresolved threshold,
extraterritorial, discharged through a third party's permission. Those live
in the checker's prompt. A KB states what is true; a prompt states what to
do about it. They also can't survive the micro-KB content rule (one line,
fifteen words, no explanations) without losing the instruction that is their
entire value.

**Sources:** Public regulator remit statements (FCA, PRA, FSA, FSS, HSE, ICO,
NCSC, MHRA, Ofcom, Ofgem, ONR, ASA, CMA, OPSS, Trading Standards,
Environmental Health, The Pensions Regulator, Environment Agency, SEPA, NRW,
NIEA, EHRC, ECJU, OFSI, HMRC, Companies House, UK IPO, Gambling Commission,
Primary Authority Scheme).

**Update frequency:** Quarterly, or on any regulator merger/rename/remit
change, when a new cross-cutting regulatory category emerges, or when the
deployment's target geography changes.

**Quality bar:** Every row must name a real, currently-operating UK body.
No domain speculation — if a body isn't listed, the checker agent should
say so rather than guess. Removing a coverage category is a breaking change:
it silently narrows every assessment downstream. Post-EU-exit divergence is
ongoing — retained EU instruments are being amended or replaced, and
UKCA/CE arrangements for Great Britain and Northern Ireland differ and have
shifted more than once. Confirm a body's current remit before relying on it.

**Owner:** Agentic-AI CoE

**Consumers:** `L1-vision-regulatory-feasibility-checker` and
`L1-vision-regulatory-feasibility-checker-evaluator` (all domains)
