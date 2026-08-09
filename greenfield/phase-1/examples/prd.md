# PRD: HarvestLink

| Field | Value |
|---|---|
| Source requirements | evaluated requirements from `L1-requirements-elicitor-evaluator` (wf-a17c5e92) |
| Source NFR spec | evaluated NFR set from `L1-requirements-nfr-classifier-evaluator` (wf-a17c5e92) |
| Source vision | vision.md |

## Executive Summary

This PRD defines 15 functional requirements for HarvestLink's facilitation-only compliance platform, following Product Lead approval (Priya Ahluwalia, 2026-08-04). The single biggest constraint is FR-001's facilitation-only structure — a hard blocker for all other capabilities — which must be validated with a design-partner local authority before Phase 2 proceeds (FR-002). 5 open questions remain, including 3 TBD NFR boundary conditions requiring stakeholder input for pilot cohort sizing and discovery interface performance targets.

## Out of Scope

- **Payment processing and invoicing**: Implied by vision.md § Value Proposition (direct discovery enables trade) but no FR scoped for financial transaction handling this cycle — deferred to Roadmap Phase 4 or beyond
- **Producer-to-producer transactions**: Vision.md § Target Users scopes producers and distributors as supply-side, foodservice buyers as demand-side; peer-to-peer producer trade not covered by any FR
- **Mobile-native applications**: Vision.md § Roadmap Outline does not specify mobile vs. web; no FR states mobile-specific capability requirements
- **Automated cold-chain sensor integration**: FR-012 provides temperature logging with manual or automated entry, but vision.md § Value Proposition does not scope IoT sensor integration for this phase
- **Multi-language support**: Vision.md § Target Users scopes UK market; no FR addresses internationalization or localization beyond UK regulatory compliance

## Traceability Matrix

| FR | Priority | NFR Categories | Open Questions |
|---|---|---|---|
| FR-001 | High | Compliance, Security | 0 |
| FR-002 | High | Compliance | 0 |
| FR-003 | High | Compliance, Security, Availability | 0 |
| FR-004 | High | Compliance, Security, Availability | 0 |
| FR-005 | High | None | 0 |
| FR-006 | High | None | 0 |
| FR-007 | High | Security, Scalability | 1 |
| FR-008 | High | Security, Scalability | 1 |
| FR-009 | High | Compliance, Security, Availability | 0 |
| FR-010 | High | Performance, Security | 0 |
| FR-011 | High | Compliance, Security, Availability | 0 |
| FR-012 | High | Compliance, Security, Availability | 0 |
| FR-013 | High | Security, Performance, Scalability | 2 |
| FR-014 | Medium | Performance, Security | 0 |
| FR-015 | High | Compliance, Security | 0 |

## Compound Requirements Split

| Source Clause Summary | Split Into |
|---|---|
| Design and validate the dual-sign-off traceability and allergen-declaration workflows | FR-005, FR-006 |
| Pilot launch with a capped cohort of producers and transaction limits scaled to compliance-documentation completeness | FR-007, FR-008 |

## Assumptions

- **Facilitation-only structure avoids FBO status** (underlies FR-001, FR-002, FR-009, FR-011, FR-012): Vision.md § Regulatory Posture assumes that operating strictly as a data/matching/documentation layer with no physical possession will avoid Food Business Operator designation under Regulation (EC) 852/2004, pending validation with design-partner local authority
- **Producers and distributors will adopt dual sign-off workflows** (underlies FR-003, FR-004): Vision.md § Regulatory Posture assumes producers and distributors will accept dual sign-off as a liability-mitigation mechanism for traceability and allergen declarations, despite adding workflow steps
- **Compliance documentation completeness drives buyer trust** (underlies FR-010, FR-013): Vision.md § North-Star Metric(s) assumes that 95%+ completeness score at first trade will differentiate producers in buyer discovery, but buyer behavior is unvalidated
- **14-day time-to-first-trade is achievable** (underlies FR-014): Vision.md § North-Star Metric(s) assumes producers can complete onboarding, documentation, and first trade within 14 days, but producer readiness and documentation complexity are unvalidated
- **Pilot cohort will tolerate transaction limits** (underlies FR-008): Vision.md § Roadmap Outline assumes pilot producers will accept transaction limits scaled to completeness scores as a risk-mitigation mechanism during validation phase

## Constraints

- **No physical food handling or storage** (constrains FR-001, FR-009, FR-011, FR-012): Regulatory Posture § CON-01 Red constraint — platform architecture must not enable physical possession capability to avoid FBO status under Regulation (EC) 852/2004 and 178/2002
- **Phase 2 gate requires design-partner validation** (constrains FR-002, FR-005, FR-006): Roadmap Outline Phase 1 — Phase 2 work (workflow design and validation) cannot proceed until facilitation-only structure is validated with design-partner local authority or legal counsel
- **6-year records retention for compliance documents** (constrains FR-003, FR-004, FR-009, FR-011, FR-012): kb-L1-enterprise-security § ES3 — Group Records Retention Policy aligned to HMRC/Companies Act requires 6-year retention for trade/compliance-relevant records including traceability, allergen declarations, HACCP, and temperature logs
- **99.5% uptime minimum for legally-relevant records** (constrains FR-003, FR-004, FR-009, FR-011, FR-012): kb-L1-enterprise-security § ES4 — Tier 2 equivalent uptime target mandatory for any new system storing legally-relevant audit/compliance records
- **External parties must use separate identity provider** (constrains FR-007): kb-L1-enterprise-security § ES1 — External parties (producers, distributors) must use group-approved external identity provider, not internal Azure AD SSO
- **Pilot cohort cap during Phase 3 launch** (constrains FR-007, FR-008): Roadmap Outline Phase 3 — Producer onboarding must be capped during pilot to manage risk and validate workflows before scaling

## Risks

- **Facilitation-only structure may not avoid FBO status** (affects FR-001, FR-002; program-level): Vision.md § Regulatory Posture CON-01 Red risk — If design-partner validation determines the facilitation-only structure still triggers FBO designation, the entire platform model requires redesign; mitigation is FR-002 validation gate before Phase 2 proceeds
- **Dual sign-off may create producer/distributor friction** (affects FR-003, FR-004, FR-005, FR-006): Vision.md § Regulatory Posture CON-02/CON-03 Amber risks — Producers and distributors may resist dual sign-off workflows as adding friction; mitigation is Phase 2 workflow design and validation with real data (FR-005, FR-006) before pilot launch
- **Compliance documentation completeness may not drive adoption** (affects FR-010, FR-013, FR-014; program-level): Vision.md § North-Star Metric(s) assumes 95%+ completeness and 14-day time-to-first-trade will drive buyer trust and producer adoption, but buyer behavior and producer readiness are unvalidated; mitigation is pilot cohort (FR-007) to test assumptions before scaling
- **Transaction limits may throttle pilot growth** (affects FR-008): Vision.md § Roadmap Outline Phase 3 — Transaction limits scaled to completeness may prevent pilot producers from reaching meaningful trade volumes; mitigation is automatic limit widening as completeness data accumulates (FR-008 acceptance criteria)
- **Data breach could expose producer compliance records** (affects FR-009, FR-011, FR-012, FR-013; program-level): kb-L1-enterprise-security § ES6 — Producer compliance documents classified as Confidential; breach would require ICO notification within 72 hours and could damage producer trust; mitigation is ES2 access control enforcement and ES6 incident-response owner assignment before launch (FR-015)

## Requirements

### FR-001: Facilitation-Only Platform Structure

**Statement:** The system shall operate strictly as a data, matching, and documentation layer where producers and distributors remain the Food Business Operators and HarvestLink never takes physical possession of food.

**Citation:** vision.md § Regulatory Posture

**Non-Functional Requirements:**

| Category | Boundary Condition | Source |
|---|---|---|
| Compliance | Platform must not take physical possession of food; producers and distributors remain FBOs per Regulation (EC) 852/2004 and 178/2002 | regulatory-feasibility.md § CON-01 |
| Security | Platform architecture must be server-side enforced to prevent physical possession capability being added via client-side modification | kb-L1-enterprise-security § ES1 |

---

### FR-002: Design-Partner Validation of Facilitation-Only Structure

**Statement:** The system's facilitation-only structure shall be validated with a design-partner local authority or legal counsel before Phase 2 proceeds.

**Citation:** vision.md § Roadmap Outline

**Non-Functional Requirements:**

| Category | Boundary Condition | Source |
|---|---|---|
| Compliance | Validation must confirm facilitation-only structure avoids FBO status per Regulation (EC) 852/2004 before Phase 2 proceeds | regulatory-feasibility.md § CON-01 |

---

### FR-003: Dual Sign-Off Traceability Workflow

**Statement:** The system shall require producer and distributor dual sign-off for traceability records with an immutable audit log.

**Citation:** vision.md § Regulatory Posture

**Non-Functional Requirements:**

| Category | Boundary Condition | Source |
|---|---|---|
| Compliance | Traceability records must satisfy Regulation (EC) 178/2002 Article 18 (one step back, one step forward) with producer and distributor dual sign-off | regulatory-feasibility.md § CON-02 |
| Security | Audit log must be immutable after write and capture timestamp, user identity, and record state for every sign-off action; server-side enforced | requirements.md § FR-003, kb-L1-enterprise-security § ES1 |
| Availability | 99.5% uptime minimum (Tier 2 equivalent) for traceability sign-off workflow storing legally-relevant audit records | kb-L1-enterprise-security § ES4 |
| Compliance | Traceability records must be retained for 6 years from creation per Group Records Retention Policy aligned to HMRC/Companies Act | kb-L1-enterprise-security § ES3 |

---

### FR-004: Producer Attestation and Sign-Off for Allergen Declarations

**Statement:** The system shall require producer attestation and sign-off before any allergen declaration is finalised on-platform.

**Citation:** vision.md § Regulatory Posture

**Non-Functional Requirements:**

| Category | Boundary Condition | Source |
|---|---|---|
| Compliance | Allergen declarations must be producer-attested per Food Information Regulations 2014 / EU FIC Regulation 1169/2011 and Natasha's Law (Food Information Amendment England 2019) | regulatory-feasibility.md § CON-03 |
| Security | Producer attestation and sign-off must be server-side enforced; finalisation must be blocked until attestation is complete | requirements.md § FR-004, kb-L1-enterprise-security § ES1 |
| Availability | 99.5% uptime minimum (Tier 2 equivalent) for allergen declaration workflow storing legally-relevant compliance records | kb-L1-enterprise-security § ES4 |
| Compliance | Allergen declarations must be retained for 6 years from creation per Group Records Retention Policy aligned to HMRC/Companies Act | kb-L1-enterprise-security § ES3 |

---

### FR-005: Design Dual Sign-Off Traceability Workflow

**Statement:** The system shall provide a designed dual-sign-off traceability workflow that is tested with real producer and distributor data before onboarding opens beyond a pilot cohort.

**Citation:** vision.md § Roadmap Outline

**Non-Functional Requirements:**

No NFR categories apply — FR-005 is a design and test activity (Phase 2 roadmap item), not a runtime system capability. The NFR boundaries for the traceability workflow itself are already classified under FR-003, which FR-005 depends on.

---

### FR-006: Design Dual Sign-Off Allergen Declaration Workflow

**Statement:** The system shall provide a designed dual-sign-off allergen-declaration workflow that is tested with real producer and distributor data before onboarding opens beyond a pilot cohort.

**Citation:** vision.md § Roadmap Outline

**Non-Functional Requirements:**

No NFR categories apply — FR-006 is a design and test activity (Phase 2 roadmap item), not a runtime system capability. The NFR boundaries for the allergen declaration workflow itself are already classified under FR-004, which FR-006 depends on.

---

### FR-007: Producer Onboarding

**Statement:** The system shall support onboarding of producers with a capped cohort during pilot launch.

**Citation:** vision.md § Roadmap Outline

**Non-Functional Requirements:**

| Category | Boundary Condition | Source |
|---|---|---|
| Security | External party onboarding must include lightweight identity/eligibility check before granting write access; check must be logged (who, when, what was checked) per ES7 | kb-L1-enterprise-security § ES7 |
| Security | External parties must use separate, group-approved external identity provider (not Azure AD group SSO) per ES1 | kb-L1-enterprise-security § ES1 |
| Scalability | Capped cohort during pilot launch (specific cap number TBD — needs stakeholder input) | requirements.md § FR-007 |

---

### FR-008: Transaction Limits Scaled to Compliance Completeness

**Statement:** The system shall enforce transaction limits that are scaled to compliance-documentation completeness scores during pilot launch, then widen limits as completeness data accumulates.

**Citation:** vision.md § Roadmap Outline

**Non-Functional Requirements:**

| Category | Boundary Condition | Source |
|---|---|---|
| Security | Transaction limit enforcement must be server-side enforced and not bypassable by altering client-side request per ES1 | kb-L1-enterprise-security § ES1 |
| Scalability | Transaction limits widen as completeness data accumulates during pilot, then scale to full onboarding cohort (specific volume/rate targets TBD — needs stakeholder input) | requirements.md § FR-008 |

---

### FR-009: HACCP Documentation Records

**Statement:** The system shall provide out-of-the-box HACCP documentation records for producers and distributors.

**Citation:** vision.md § Value Proposition

**Non-Functional Requirements:**

| Category | Boundary Condition | Source |
|---|---|---|
| Compliance | HACCP records provided as facilitation infrastructure only; producers and distributors remain FBOs per Regulation (EC) 852/2004 | regulatory-feasibility.md § CON-01 |
| Security | HACCP records classified as Confidential per ES2 (sensitive to specific party); access control must restrict to owning producer/distributor and authorized buyers | kb-L1-enterprise-security § ES2 |
| Availability | 99.5% uptime minimum (Tier 2 equivalent) for HACCP record storage as legally-relevant compliance records | kb-L1-enterprise-security § ES4 |
| Compliance | HACCP records must be retained for 6 years from creation per Group Records Retention Policy aligned to HMRC/Companies Act | kb-L1-enterprise-security § ES3 |

---

### FR-010: Compliance Documentation Completeness Score

**Statement:** The system shall calculate a compliance-documentation completeness score for each producer and distributor.

**Citation:** vision.md § North-Star Metric(s)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source |
|---|---|---|
| Performance | Completeness score target: at least 95% at first trade per North-Star Metric | vision.md § North-Star Metric(s) |
| Security | Individual completeness scores classified as Confidential per ES2; access control must restrict to owning producer/distributor and authorized internal reporting | kb-L1-enterprise-security § ES2 |

---

### FR-011: Allergen Declaration Records

**Statement:** The system shall provide allergen declaration records for producers.

**Citation:** vision.md § Value Proposition

**Non-Functional Requirements:**

| Category | Boundary Condition | Source |
|---|---|---|
| Compliance | Allergen declaration records provided as facilitation infrastructure only; producers remain FBOs and legal declarants per Food Information Regulations 2014 / EU FIC Regulation 1169/2011 and Natasha's Law | regulatory-feasibility.md § CON-03 |
| Security | Allergen declaration records classified as Confidential per ES2; access control must restrict to owning producer and authorized buyers | kb-L1-enterprise-security § ES2 |
| Availability | 99.5% uptime minimum (Tier 2 equivalent) for allergen declaration record storage as legally-relevant compliance records | kb-L1-enterprise-security § ES4 |
| Compliance | Allergen declaration records must be retained for 6 years from creation per Group Records Retention Policy aligned to HMRC/Companies Act | kb-L1-enterprise-security § ES3 |

---

### FR-012: Cold-Chain Temperature Logging

**Statement:** The system shall provide cold-chain temperature logging for traceability records.

**Citation:** vision.md § Value Proposition

**Non-Functional Requirements:**

| Category | Boundary Condition | Source |
|---|---|---|
| Compliance | Temperature logs provided as facilitation infrastructure only; producers and distributors remain FBOs per Regulation (EC) 852/2004 | regulatory-feasibility.md § CON-01 |
| Security | Temperature logs classified as Confidential per ES2; access control must restrict to owning producer/distributor and authorized buyers | kb-L1-enterprise-security § ES2 |
| Availability | 99.5% uptime minimum (Tier 2 equivalent) for temperature log storage as legally-relevant compliance records | kb-L1-enterprise-security § ES4 |
| Compliance | Temperature logs must be retained for 6 years from creation per Group Records Retention Policy aligned to HMRC/Companies Act | kb-L1-enterprise-security § ES3 |

---

### FR-013: Direct Discovery by Foodservice Buyers

**Statement:** The system shall enable foodservice buyers to directly discover independent food producers and distributors.

**Citation:** vision.md § Value Proposition

**Non-Functional Requirements:**

| Category | Boundary Condition | Source |
|---|---|---|
| Security | Buyer discovery interface must enforce access control: buyers can view producer/distributor compliance documentation status and records only for producers/distributors they are authorized to view | kb-L1-enterprise-security § ES2 |
| Performance | TBD — needs stakeholder input | — |
| Scalability | TBD — needs stakeholder input | — |

---

### FR-014: Time from Onboarding to First Trade Tracking

**Statement:** The system shall track the time from producer onboarding to first fully-documented, compliance-complete trade with a target under 14 days.

**Citation:** vision.md § North-Star Metric(s)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source |
|---|---|---|
| Performance | Time-to-first-trade target: under 14 days per North-Star Metric | vision.md § North-Star Metric(s) |
| Security | Time-to-first-trade metric aggregated across cohort classified as Internal per ES2; individual producer time-to-first-trade classified as Confidential | kb-L1-enterprise-security § ES2 |

---

### FR-015: Data Protection Compliance

**Statement:** The system shall implement data protection controls as an ongoing design and monitoring requirement.

**Citation:** vision.md § Regulatory Posture

**Non-Functional Requirements:**

| Category | Boundary Condition | Source |
|---|---|---|
| Compliance | Data protection controls must satisfy UK GDPR / Data Protection Act 2018 per CON-04 Green regulatory constraint | regulatory-feasibility.md § CON-04 |
| Compliance | Personal data breach must be reported to ICO within 72 hours per UK GDPR Art. 33; affected individuals notified without undue delay per UK GDPR Art. 34 if high risk | kb-L1-enterprise-security § ES6 |
| Security | Named incident-response owner must be assigned before launch per ES6 | kb-L1-enterprise-security § ES6 |
| Compliance | Right-to-erasure (UK GDPR Art. 17) requests must be honoured for personal data NOT required for 6-year compliance-retention obligation per ES3 | kb-L1-enterprise-security § ES3 |

---

## Open Questions

- **FR-007 (Scalability)**: Capped cohort during pilot launch — specific cap number TBD, needs stakeholder input to balance risk mitigation with pilot scale
- **FR-008 (Scalability)**: Transaction limits widen as completeness data accumulates — specific volume/rate targets TBD, needs stakeholder input to define pilot transaction thresholds and scaling curve
- **FR-013 (Performance)**: Buyer discovery interface response time target — TBD, needs stakeholder input to define acceptable search/filter latency for buyer experience
- **FR-013 (Scalability)**: Buyer discovery interface volume/rate expectations — TBD, needs stakeholder input to define expected producer/distributor catalog size and concurrent buyer search load
- **Coverage gap**: Vision.md § Value Proposition implies "direct discovery enables trade" but no FR defines contract negotiation, order placement, or fulfillment workflows — composing FR-013 (discovery) with FR-007 (onboarding) and FR-014 (time-to-first-trade tracking) reveals a gap between discovery and completed trade that may require additional FRs or clarification that trade happens off-platform

## Glossary

| Term | Definition | Source |
|---|---|---|
| FBO (Food Business Operator) | Legal entity responsible for ensuring food safety compliance under Regulation (EC) 852/2004; designation triggers mandatory HACCP implementation, traceability obligations, and regulatory inspection liability | vision.md § Regulatory Posture, requirements § FR-001 |
| HACCP (Hazard Analysis and Critical Control Points) | Systematic preventive approach to food safety covering biological, chemical, and physical hazards; mandatory for FBOs under Regulation (EC) 852/2004 | vision.md § Value Proposition, requirements § FR-009 |
| Natasha's Law | Common name for Food Information (Amendment) (England) Regulations 2019, requiring full ingredient and allergen labeling for prepacked for direct sale (PPDS) food following the death of Natasha Ednan-Laperouse | requirements § FR-004 |
| Traceability (one step back, one step forward) | Regulation (EC) 178/2002 Article 18 requirement that FBOs must identify immediate suppliers (one step back) and immediate customers (one step forward) for food products to enable rapid recall | vision.md § Regulatory Posture, requirements § FR-003 |
| Dual sign-off | Workflow pattern requiring both producer and distributor digital signatures to finalize traceability records and allergen declarations, used to distribute liability and ensure both parties attest to record accuracy | vision.md § Regulatory Posture, requirements § FR-003, FR-004 |
| Compliance-documentation completeness score | Calculated metric measuring percentage completion of required compliance documents (HACCP, allergen declarations, traceability records) for a producer or distributor; North-Star Metric target is at least 95% at first trade | vision.md § North-Star Metric(s), requirements § FR-010 |
| Design-partner | Local authority or legal counsel engaged during Phase 1 to validate that the facilitation-only platform structure avoids FBO status before Phase 2 proceeds | vision.md § Roadmap Outline, requirements § FR-002 |
| Pilot cohort | Capped group of producers onboarded during Phase 3 launch to validate workflows and manage risk before scaling; cohort cap is configurable but specific number TBD | vision.md § Roadmap Outline, requirements § FR-007 |
| Cold-chain | Temperature-controlled supply chain for perishable food products; temperature logging is a compliance requirement for demonstrating unbroken cold-chain integrity | vision.md § Value Proposition, requirements § FR-012 |
| Foodservice buyer | Target user persona: restaurants, cafés, caterers, and institutional kitchens seeking to source from independent producers with verified compliance documentation | vision.md § Target Users, requirements § FR-013 |