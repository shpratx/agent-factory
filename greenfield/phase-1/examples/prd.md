# PRD: Dairy Supply Chain Quality Intelligence Platform

| Field | Value |
|---|---|
| Source requirements | evaluated requirements from `L1-requirements-elicitor-evaluator` (wf-b8e4d9f2-5c3e-4g0b-9f6d-8e7g0b3c2d5f) |
| Source NFR spec | evaluated NFR set from `L1-requirements-nfr-classifier-evaluator` (wf-b8e4d9f2-5c3e-4g0b-9f6d-8e7g0b3c2d5f) |
| Source vision | vision.md |

## Executive Summary

The Dairy Supply Chain Quality Intelligence Platform addresses critical milk quality preservation challenges in India's dairy supply chain by projecting temperature-at-arrival for milk tankers in transit and triggering real-time alerts when safe limits will be breached. Target users include truck supervisors who need immediate intervention capability, farmers and farmer cooperatives requiring transparent root-cause attribution for rejected batches, maintenance teams needing predictive equipment alerts, and plant operations teams requiring advance warning of at-risk loads. The platform combines existing IoT telemetry (temperature sensors, GPS) with thermal decay modeling to enable proactive quality interventions, reducing milk rejection rates and improving financial accountability across the supply chain. Business value is measured through reduction in milk rejection rates (NSM-01), increase in successful quality-risk interventions (NSM-02), and improvement in alert accuracy to prevent alert fatigue (NSM-03). The solution must comply with DPDP Act 2023 data protection requirements, RPwD Act 2016 accessibility standards, and multi-state dairy regulatory frameworks while maintaining data localisation within India. Key risks include unvalidated thermal decay model accuracy, unassessed IoT sensor data quality, and incomplete mapping of state-level regulatory requirements, all requiring Phase 1 pilot validation before scale.

## Out of Scope

- **Historical trend analytics dashboard**: Implied by vision.md § Value Proposition ("cooler degradation detection" suggests pattern analysis capability) but deferred to Roadmap Phase 2 per vision.md § Roadmap Outline ("Phase 2: Expand analytics depth")
- **Predictive routing optimization**: Implied by vision.md § Value Proposition (alerts enable "reroute" interventions) but no FR scoped for automated route recommendation this cycle; manual reroute decision-making by truck supervisors is in scope (FR-003)
- **Farmer cooperative aggregation reporting**: Implied by vision.md § Target Users (farmer cooperatives are named stakeholders) but no FR scoped for cooperative-level aggregated quality reports; individual farmer visibility is in scope (FR-006, FR-007)
- **Mobile offline mode**: Implied by vision.md § Target Users (truck supervisors operate in rural areas with connectivity challenges) but deferred to Roadmap Phase 2 per vision.md § Roadmap Outline ("Phase 2: Harden for rural connectivity")

## Traceability Matrix

| FR | Priority | MVP | NFR Categories | Open Questions |
|---|---|---|---|---|
| FR-001 | High | Yes | Performance, Availability, Scalability | 2 |
| FR-002 | High | Yes | Performance, Availability, Usability | 1 |
| FR-003 | High | Yes | Performance, Availability, Security, Usability | 1 |
| FR-004 | Medium | No | Performance, Scalability | 1 |
| FR-005 | Medium | No | Performance, Security | 0 |
| FR-006 | Medium | Yes | Compliance, Availability, Security | 0 |
| FR-007 | High | Yes | Performance, Compliance, Usability | 0 |
| FR-008 | Medium | Yes | Performance, Security, Usability | 0 |
| FR-009 | High | Yes | Compliance, Security, Usability | 0 |
| FR-010 | High | Yes | Compliance, Performance, Security | 0 |
| FR-011 | High | Yes | Compliance, Security | 0 |
| FR-012 | High | Yes | Compliance, Usability | 0 |
| FR-013 | High | Yes | Compliance, Usability | 0 |
| FR-014 | High | Yes | Compliance, Security | 0 |
| FR-015 | Medium | No | Compliance, Performance, Security | 0 |
| FR-016 | High | Yes | Performance, Usability | 0 |
| FR-017 | Medium | No | Security, Usability | 0 |
| FR-018 | High | Yes | Performance, Availability, Usability | 1 |
| FR-019 | High | Yes | Performance, Compliance | 0 |
| FR-020 | High | Yes | Performance, Usability | 0 |

## Compound Requirements Split

| Source Clause Summary | Split Into |
|---|---|
| Combines existing IoT telemetry (temperature sensors, GPS) with thermal decay modeling to project temperature-at-arrival | FR-001 |
| Trigger alerts when safe limits will be breached, while providing cooler degradation detection and farmer-facing root-cause attribution | FR-002, FR-004, FR-007 |
| DPDP Act 2023 obligations (consent, purpose limitation, data principal rights) are manageable with standard controls | FR-009, FR-010 |
| Truck Supervisor App and Farmer App interfaces to meet WCAG 2.1 Level AA standards | FR-012, FR-013 |

## Assumptions

- **ASSUM-001: Thermal decay model parameters available** (underlies FR-001): The thermal decay model referenced in FR-001 assumes model parameters (decay coefficients, ambient temperature influence factors) are available or derivable from existing research/pilot data; vision.md § Open Risks OR-05 flags model accuracy as unvalidated, establishing this as an assumption requiring Phase 1 validation.
- **ASSUM-002: IoT telemetry infrastructure operational** (underlies FR-001, FR-004, FR-018): Requirements assume existing IoT telemetry (temperature sensors, GPS) is operational and accessible; vision.md § Value Proposition states the platform "combines existing IoT telemetry" but does not validate sensor coverage, uptime, or data quality; OR-07 flags IoT data quality as unassessed.
- **ASSUM-003: Safe limit thresholds defined** (underlies FR-002, FR-017): FR-002 assumes "safe limits defined for milk quality preservation" exist and are known; vision.md does not specify these thresholds, and FR-017 explicitly scopes threshold tuning based on pilot data, establishing initial thresholds as an assumption.
- **ASSUM-004: Truck supervisor device availability** (underlies FR-003): FR-003 assumes truck supervisors have devices capable of receiving real-time alerts (smartphones, tablets); vision.md § Target Users identifies truck supervisors as users but does not validate device availability or connectivity in rural transit routes.
- **ASSUM-005: Maintenance team interface exists** (underlies FR-005): FR-005 assumes a "maintenance interface" exists for delivering predictive maintenance alerts; vision.md does not specify this interface, and no FR scopes its design/implementation.
- **ASSUM-006: Plant operations interface exists** (underlies FR-008): FR-008 assumes a "plant operations interface" exists for delivering advance warnings; vision.md does not specify this interface, and no FR scopes its design/implementation.
- **ASSUM-007: Baseline rejection/save rates measurable** (underlies FR-019): FR-019 assumes baseline rejection and save rates are measurable from existing operational data; vision.md § North-Star Metrics NSM-01/NSM-02 require baselining in Phase 1 but do not validate data availability.
- **ASSUM-008: DPDP Act 2023 rules finalized** (underlies FR-009, FR-010): FR-009/FR-010 implement DPDP Act 2023 compliance mechanisms; vision.md § Regulatory Posture OR-02 notes "DPDP Act 2023 rules not yet finalized by government," establishing regulatory interpretation as an assumption requiring legal review.

## Constraints

- **CON-001: DPDP Act 2023 compliance mandatory** (constrains FR-009, FR-010, FR-011): vision.md § Regulatory Posture CON-01 states "DPDP Act 2023 obligations (consent, purpose limitation, data principal rights) are manageable with standard controls but are non-negotiable"; all personal data collection/processing must comply.
- **CON-002: Data localisation within India mandatory** (constrains FR-011): vision.md § Regulatory Posture CON-02 states "Data localisation (all personal data hosted/processed within India) eliminates cross-border transfer risk"; all infrastructure must be India-resident per DPDP Act 2023.
- **CON-003: WCAG 2.1 Level AA compliance mandatory** (constrains FR-012, FR-013): vision.md § Regulatory Posture CON-08 states "WCAG 2.1 Level AA compliance required for public-facing digital services per RPwD Act 2016"; Truck Supervisor App and Farmer App must meet accessibility standards.
- **CON-004: Multi-state regulatory compliance required** (constrains FR-014): vision.md § Regulatory Posture CON-04 states "Multi-state regulatory exposure (dairy, APMC) requires per-state mapping"; system must accommodate varying state-level dairy and APMC rules.
- **CON-005: Phase 1 pilot timeline 6 months** (constrains program-level): vision.md § Roadmap Outline states "Phase 1 (Pilot): 6 months — 2 states, 50 tankers, 200 bulk coolers"; all MVP requirements must be deliverable within this timeline.
- **CON-006: Enterprise security standards apply** (constrains FR-003, FR-005, FR-006, FR-008, FR-017): kb-L1-enterprise-security ES1 mandates authenticated identity for external parties; ES3 mandates 6-year retention for trade/compliance-relevant records; ES4 mandates 99.5% uptime for legally-relevant audit/compliance records.

## Risks

- **RISK-001: Thermal decay model accuracy unvalidated** (affects FR-001, FR-002, FR-016): vision.md § Open Risks OR-05 states "Thermal decay model accuracy is unvalidated; if projections are systematically biased, alert accuracy (NSM-03) will suffer and operational trust will erode"; Phase 1 pilot must validate model accuracy per FR-016.
- **RISK-002: Alert threshold sensitivity/specificity unknown** (affects FR-002, FR-017): vision.md § Open Risks OR-06 states "Alert threshold tuning (sensitivity vs. specificity) is unknown; too-sensitive thresholds cause alert fatigue, too-conservative thresholds miss genuine risks"; Phase 1 pilot must establish thresholds per FR-017.
- **RISK-003: IoT data quality unassessed** (affects FR-001, FR-018): vision.md § Open Risks OR-07 states "IoT sensor data quality (uptime, accuracy, latency) is unassessed; poor data quality undermines projection accuracy and alert reliability"; Phase 1 pilot must assess data quality per FR-018.
- **RISK-004: State-level regulatory mapping incomplete** (affects FR-014): vision.md § Open Risks OR-01 states "Multi-state regulatory mapping (dairy quality standards, APMC rules) is incomplete; compliance gaps could block operations in specific states"; legal review required before Phase 1 pilot launch.
- **RISK-005: DPDP Act 2023 rules not finalized** (affects FR-009, FR-010): vision.md § Open Risks OR-02 states "DPDP Act 2023 rules not yet finalized by government; interpretation of consent/data principal rights obligations may shift"; legal review required, and compliance mechanisms may require adjustment post-finalization.
- **RISK-006: WCAG 2.1 Level AA compliance scope ambiguous** (affects FR-012, FR-013): vision.md § Open Risks OR-04 states "WCAG 2.1 Level AA compliance scope is ambiguous (which interfaces qualify as 'public-facing digital services' under RPwD Act 2016?)"; legal review required to confirm Truck Supervisor App and Farmer App applicability.
- **RISK-007: Truck supervisor adoption uncertain** (affects FR-003, program-level): vision.md § Open Risks (implicit in Target Users section) identifies truck supervisors as external parties with uncertain digital literacy and device availability; low adoption would undermine intervention capability.
- **RISK-008: Farmer trust in root-cause attribution uncertain** (affects FR-007, program-level): vision.md § Problem Statement identifies "opaque quality failures" as a pain point; if farmers distrust root-cause attribution methodology, financial accountability improvements may not materialize.

## Requirements

### FR-001: Temperature-at-arrival projection

**Statement:** The system shall project temperature-at-arrival for each milk tanker in transit using existing IoT telemetry (temperature sensors, GPS) and thermal decay modeling.

**Citation:** vision.md § Value Proposition

**MVP:** Yes (vision.md § Value Proposition frames temperature-at-arrival projection as core to solving the stated problem; vision.md § Roadmap Outline Phase 1 scopes "temperature-at-arrival projection" as foundational capability)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Calculate and store projected arrival temperature within 60 seconds of receiving new telemetry data | requirements.md § FR-001 | Yes |
| Availability | TBD — needs stakeholder input | — | TBD |
| Scalability | TBD — needs stakeholder input | — | TBD |

### FR-002: Safe limit breach alert triggering

**Statement:** The system shall trigger an alert when the projected temperature-at-arrival will breach safe limits defined for milk quality preservation.

**Citation:** vision.md § Value Proposition

**MVP:** Yes (vision.md § Value Proposition frames alert triggering as core to enabling real-time intervention; vision.md § Roadmap Outline Phase 1 scopes alert capability)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Generate alert within 10 seconds of breach condition detection | requirements.md § FR-002 | Yes |
| Availability | TBD — needs stakeholder input | — | TBD |
| Usability | Alert must include tanker identifier, current location, projected arrival temperature, time until arrival, and breach severity to prevent misinterpretation of risk level | requirements.md § FR-002 | Yes |

### FR-003: Real-time alert delivery to truck supervisors

**Statement:** The system shall deliver real-time alerts to truck supervisors when quality risk is detected during transit.

**Citation:** vision.md § Target Users

**MVP:** Yes (vision.md § Target Users identifies truck supervisors as primary action-takers; vision.md § Roadmap Outline Phase 1 scopes real-time alert delivery)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Deliver alert to assigned truck supervisor's device within 15 seconds of alert generation | requirements.md § FR-003 | Yes |
| Availability | TBD — needs stakeholder input | — | TBD |
| Security | Alert delivery must be tied to authenticated truck supervisor identity, not anonymous or shared credentials | kb-L1-enterprise-security § ES1 | Yes |
| Usability | Alert delivery status (delivered, failed, acknowledged) must be logged and visible to prevent silent delivery failures | requirements.md § FR-003 | Yes |

### FR-004: Cooler degradation detection

**Statement:** The system shall detect degrading cooler performance by analyzing temperature telemetry patterns over time.

**Citation:** vision.md § Value Proposition

**MVP:** No (vision.md § Roadmap Outline Phase 2 scopes "Expand analytics depth" including predictive maintenance; Phase 1 focuses on transit alerts per Value Proposition)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Detection runs automatically on a daily schedule for all monitored coolers | requirements.md § FR-004 | No |
| Scalability | TBD — needs stakeholder input | — | TBD |

### FR-005: Predictive maintenance alerts for degrading coolers

**Statement:** The system shall generate predictive maintenance alerts for maintenance teams when degrading cooler performance is detected.

**Citation:** vision.md § Target Users

**MVP:** No (depends on FR-004 which is Phase 2 per Roadmap Outline; maintenance alerts are secondary to transit intervention capability per Value Proposition)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Generate maintenance alert within 1 hour of degradation detection | requirements.md § FR-005 | No |
| Security | Alert delivery must be tied to authenticated maintenance team identity, not anonymous or shared credentials | kb-L1-enterprise-security § ES1 | No |

### FR-006: Quality-assurance intervention logging

**Statement:** The system shall log quality-assurance interventions that saved milk batches for farmer visibility.

**Citation:** vision.md § Target Users

**MVP:** Yes (vision.md § Target Users identifies farmers requiring visibility into interventions; intervention logging is foundational for transparent accountability per Value Proposition)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Intervention logs retained for at least 6 years and queryable by batch identifier and farmer identifier | kb-L1-enterprise-security § ES3 | Yes |
| Availability | System storing intervention logs must target minimum 99.5% uptime as legally-relevant audit/compliance records | kb-L1-enterprise-security § ES4 | Yes |
| Security | Intervention logging must be tied to authenticated identity of actor performing intervention | kb-L1-enterprise-security § ES1 | Yes |

### FR-007: Root-cause attribution for rejected batches

**Statement:** The system shall provide transparent root-cause attribution for rejected batches to distinguish farmer-side issues from transit or equipment failures.

**Citation:** vision.md § Target Users

**MVP:** Yes (vision.md § Target Users identifies farmers requiring transparent attribution; vision.md § Problem Statement frames opaque quality failures as core pain point; Priority: High)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Root-cause report accessible to affected farmer or farmer cooperative within 24 hours of rejection | requirements.md § FR-007 | Yes |
| Compliance | Root-cause reports retained for at least 6 years | kb-L1-enterprise-security § ES3 | Yes |
| Usability | Root-cause attribution must distinguish farmer-side issues from transit or equipment failures with supporting evidence to prevent misattribution | requirements.md § FR-007 | Yes |

### FR-008: Advance warning to plant operations for at-risk loads

**Statement:** The system shall provide advance warning to plant operations and quality assurance teams when at-risk loads are en route.

**Citation:** vision.md § Target Users

**MVP:** Yes (vision.md § Target Users identifies plant operations teams as benefiting from advance warning; enables prioritized offloading per Value Proposition)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Notify destination plant operations team at least 30 minutes before projected arrival | requirements.md § FR-008 | Yes |
| Security | Plant operations acknowledgment and response must be tied to authenticated identity, not anonymous or shared credentials | kb-L1-enterprise-security § ES1 | Yes |
| Usability | Notification must include tanker identifier, projected arrival time, risk level, projected temperature-at-arrival, and recommended handling actions to prevent misinterpretation | requirements.md § FR-008 | Yes |

### FR-009: DPDP Act 2023 consent mechanism

**Statement:** The system shall implement consent mechanisms compliant with DPDP Act 2023 for collection and processing of personal data from farmers, truck supervisors, and maintenance personnel.

**Citation:** vision.md § Regulatory Posture

**MVP:** Yes (vision.md § Regulatory Posture CON-01 identifies DPDP Act 2023 compliance as non-negotiable; consent is foundational data protection obligation; Priority: High)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Consent mechanism compliant with DPDP Act 2023, presenting consent request in clear language specifying data types, processing purposes, retention period, and data principal rights before data collection | vision.md § Regulatory Posture CON-01 | Yes |
| Security | Consent records (granted/denied, timestamp, consent version) must be stored and auditable for each user | requirements.md § FR-009 | Yes |
| Usability | User can grant or deny consent; denial prevents data collection and system access for that user | requirements.md § FR-009 | Yes |

### FR-010: Data principal rights mechanisms

**Statement:** The system shall implement data principal rights mechanisms compliant with DPDP Act 2023, including access, correction, erasure, and data portability.

**Citation:** vision.md § Regulatory Posture

**MVP:** Yes (vision.md § Regulatory Posture CON-01 identifies DPDP Act 2023 compliance as non-negotiable; data principal rights are mandatory obligations; Priority: High)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Data principal rights mechanisms compliant with DPDP Act 2023, including access (within 7 days), correction/erasure (within 14 days), and data portability | vision.md § Regulatory Posture CON-01 | Yes |
| Performance | Access requests fulfilled within 7 days; correction/erasure requests processed within 14 days | requirements.md § FR-010 | Yes |
| Security | Data principal rights requests logged with request type, timestamp, requestor identifier, and resolution status | requirements.md § FR-010 | Yes |

### FR-011: Data localisation within India

**Statement:** The system shall host and process all personal data within India to comply with DPDP Act 2023 cross-border data transfer restrictions.

**Citation:** vision.md § Regulatory Posture

**MVP:** Yes (vision.md § Regulatory Posture CON-02 identifies data localisation as mandatory to eliminate cross-border transfer risk; architectural constraint; Priority: High)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | All personal data storage and processing infrastructure physically located within India to comply with DPDP Act 2023 cross-border data transfer restrictions | vision.md § Regulatory Posture CON-02 | Yes |
| Security | Data residency verified through infrastructure audit logs and hosting provider certifications confirming Indian data center locations | requirements.md § FR-011 | Yes |

### FR-012: WCAG 2.1 Level AA compliance for Truck Supervisor App

**Statement:** The Truck Supervisor App interface shall meet WCAG 2.1 Level AA accessibility standards as required by RPwD Act 2016.

**Citation:** vision.md § Regulatory Posture

**MVP:** Yes (vision.md § Regulatory Posture CON-08 identifies WCAG 2.1 Level AA compliance as mandatory for public-facing digital services; Truck Supervisor App is user-facing; Priority: High)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Truck Supervisor App interface meets WCAG 2.1 Level AA accessibility standards as required by RPwD Act 2016 | vision.md § Regulatory Posture CON-08 | Yes |
| Usability | All interface elements include text alternatives; all functionality operable via keyboard; color contrast ratios meet 4.5:1 (normal text) and 3:1 (large text); compatible with screen readers | requirements.md § FR-012 | Yes |

### FR-013: WCAG 2.1 Level AA compliance for Farmer App

**Statement:** The Farmer App interface shall meet WCAG 2.1 Level AA accessibility standards as required by RPwD Act 2016.

**Citation:** vision.md § Regulatory Posture

**MVP:** Yes (vision.md § Regulatory Posture CON-08 identifies WCAG 2.1 Level AA compliance as mandatory for public-facing digital services; Farmer App is user-facing; Priority: High)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Farmer App interface meets WCAG 2.1 Level AA accessibility standards as required by RPwD Act 2016 | vision.md § Regulatory Posture CON-08 | Yes |
| Usability | All interface elements include text alternatives; all functionality operable via keyboard; color contrast ratios meet 4.5:1 (normal text) and 3:1 (large text); compatible with screen readers | requirements.md § FR-013 | Yes |

### FR-014: Per-state regulatory compliance configuration

**Statement:** The system shall support per-state regulatory compliance configuration to accommodate varying state-level dairy and APMC rules.

**Citation:** vision.md § Regulatory Posture

**MVP:** Yes (vision.md § Regulatory Posture CON-04 identifies multi-state regulatory exposure as binding constraint requiring per-state mapping; architectural requirement; Priority: High)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | System maintains configurable regulatory rule set for each operating state to accommodate state-level dairy/APMC rules; system behavior adapts based on state determined by GPS location or plant assignment | vision.md § Regulatory Posture CON-04 | Yes |
| Security | Regulatory configuration changes version-controlled and auditable, with effective dates and change history logged | requirements.md § FR-014 | Yes |

### FR-015: CERT-In cybersecurity incident reporting

**Statement:** The system shall implement cybersecurity incident detection and reporting mechanisms compliant with CERT-In requirements within 6 hours of incident detection.

**Citation:** vision.md § Regulatory Posture

**MVP:** No (vision.md § Regulatory Posture identifies CERT-In reporting as precedented operational requirement but not launch-blocking; Phase 2 hardening per Roadmap Outline; Priority: Medium)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Compliance | Cybersecurity incident report submitted to CERT-In within 6 hours of incident detection via prescribed reporting channel | vision.md § Regulatory Posture | No |
| Performance | Detect and log cybersecurity incidents in real time; generate incident report meeting CERT-In reporting thresholds | requirements.md § FR-015 | No |
| Security | System detects unauthorized access attempts, data breaches, and service disruptions; incident report includes incident type, timestamp, affected systems, impact assessment, and containment actions | requirements.md § FR-015 | No |

### FR-016: Thermal decay model validation against actual arrival temperatures

**Statement:** The system shall validate thermal decay model accuracy by comparing projected temperatures against actual arrival temperatures measured at receiving plants.

**Citation:** vision.md § Open Risks Carried Forward

**MVP:** Yes (vision.md § Open Risks OR-05 identifies thermal decay model accuracy as unvalidated and critical for operational trust; Phase 1 pilot dependency per Roadmap Outline; Priority: High)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Calculate model accuracy metrics (mean absolute error, root mean square error, percentage within ±1°C tolerance) on a rolling 30-day window; report daily to system administrators | requirements.md § FR-016 | Yes |
| Usability | Accuracy metrics flagged when accuracy falls below configurable threshold to prevent silent model degradation | requirements.md § FR-016 | Yes |

### FR-017: Alert threshold tuning based on pilot data

**Statement:** The system shall support alert threshold tuning based on pilot operations data to balance sensitivity versus specificity and minimize false alarms.

**Citation:** vision.md § Roadmap Outline

**MVP:** No (vision.md § Roadmap Outline Phase 2 explicitly scopes "alert threshold tuning based on pilot data"; Phase 1 establishes baseline thresholds; Priority: Medium)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Security | Alert threshold adjustments require justification and effective date; changes version-controlled and auditable with before/after alert rate metrics tracked | requirements.md § FR-017 | No |
| Usability | Administrative interface for adjusting alert thresholds must be accessible only to authorized administrators to prevent unauthorized threshold manipulation | requirements.md § FR-017 | No |

### FR-018: IoT data quality validation

**Statement:** The system shall validate IoT telemetry data quality (temperature sensors, GPS) and implement fallback logic for sensor failures or data gaps.

**Citation:** vision.md § Open Risks Carried Forward

**MVP:** Yes (vision.md § Open Risks OR-07 identifies IoT data quality as unassessed and critical for alert accuracy; Phase 1 pilot dependency per Roadmap Outline; Priority: High)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Validate each incoming telemetry data point for completeness, plausibility, and timeliness; log data quality issues and apply fallback logic | requirements.md § FR-018 | Yes |
| Availability | TBD — needs stakeholder input | — | TBD |
| Usability | Data quality metrics (uptime, completeness, plausibility failure rate) tracked per sensor and reported daily to prevent silent sensor failures | requirements.md § FR-018 | Yes |

### FR-019: Baseline rejection and save rate tracking

**Statement:** The system shall track baseline rejection rates and successful save rates to enable measurement against North-Star Metrics NSM-01 and NSM-02.

**Citation:** vision.md § North-Star Metric(s)

**MVP:** Yes (vision.md § North-Star Metrics NSM-01/NSM-02 require baselining in Phase 1; tracking is foundational for measuring product impact; Priority: High)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Calculate rejection rate and save rate on a rolling 30-day window; report weekly to product and operations teams | requirements.md § FR-019 | Yes |
| Compliance | Rejection and save rate records retained for at least 6 years | kb-L1-enterprise-security § ES3 | Yes |

### FR-020: Alert accuracy tracking against actual arrival conditions

**Statement:** The system shall track alert accuracy by comparing alerts triggered against actual arrival conditions to measure North-Star Metric NSM-03.

**Citation:** vision.md § North-Star Metric(s)

**MVP:** Yes (vision.md § North-Star Metrics NSM-03 requires alert accuracy baselining in Phase 1; critical for operational trust and avoiding alert fatigue; Priority: High)

**Non-Functional Requirements:**

| Category | Boundary Condition | Source | MVP |
|---|---|---|---|
| Performance | Calculate alert accuracy (percentage of alerts where projected breach matched actual conditions) on a rolling 30-day window; report weekly | requirements.md § FR-020 | Yes |
| Usability | Track true positives, false positives, and false negatives to enable sensitivity/specificity tuning and prevent alert fatigue | requirements.md § FR-020 | Yes |

## Open Questions

- **FR-001 (Availability)**: TBD — needs stakeholder input on SLA for temperature-at-arrival projection service (continuous telemetry processing is critical path but no uptime target stated in requirements or vision.md)
- **FR-001 (Scalability)**: TBD — needs stakeholder input on fleet-wide scale targets (number of tankers, telemetry data ingestion rate, concurrent projection calculations)
- **FR-002 (Availability)**: TBD — needs stakeholder input on SLA for alert generation service (alert generation is critical path but no uptime target stated in requirements or vision.md)
- **FR-003 (Availability)**: TBD — needs stakeholder input on SLA for alert delivery service (alert delivery is critical path but no uptime target stated in requirements or vision.md)
- **FR-004 (Scalability)**: TBD — needs stakeholder input on cooler monitoring volume targets (number of coolers, historical data retention window for degradation detection)
- **FR-018 (Availability)**: TBD — needs stakeholder input on SLA for IoT data quality validation service (data quality affects alert accuracy but no uptime target stated in requirements or vision.md)
- **Coverage gap**: No FR scopes the design/implementation of the "maintenance interface" referenced in FR-005 or the "plant operations interface" referenced in FR-008; these interfaces are assumed to exist but are not explicitly designed in the current FR set, creating a potential delivery gap for FR-005 and FR-008 acceptance criteria.

## Glossary

| Term | Definition | Source |
|---|---|---|
| DPDP Act 2023 | Digital Personal Data Protection Act 2023 (India), governing collection, processing, and storage of personal data; mandates consent mechanisms, data principal rights (access, correction, erasure, portability), and data localisation within India | vision.md § Regulatory Posture |
| RPwD Act 2016 | Rights of Persons with Disabilities Act 2016 (India), requiring WCAG 2.1 Level AA accessibility compliance for public-facing digital services | vision.md § Regulatory Posture |
| WCAG 2.1 Level AA | Web Content Accessibility Guidelines 2.1 Level AA, specifying accessibility standards including text alternatives for non-text content, keyboard operability, color contrast ratios (4.5:1 for normal text, 3:1 for large text), and screen reader compatibility | requirements.md § FR-012 |
| CERT-In | Indian Computer Emergency Response Team, requiring cybersecurity incident reporting within 6 hours of detection for specified incident types | vision.md § Regulatory Posture |
| APMC | Agricultural Produce Market Committee, state-level regulatory bodies governing agricultural commodity trade in India; rules vary by state | vision.md § Regulatory Posture |
| Thermal decay model | Mathematical model projecting temperature change over time for milk in transit, incorporating current temperature, GPS location, estimated time to arrival, and thermal decay parameters (decay coefficients, ambient temperature influence) | requirements.md § FR-001 |
| Temperature-at-arrival | Projected temperature of milk at the moment a tanker arrives at the receiving plant, calculated using thermal decay modeling and real-time IoT telemetry | requirements.md § FR-001 |
| Safe limits | Temperature thresholds defined for milk quality preservation; breach indicates risk of quality degradation or rejection | requirements.md § FR-002 |
| Root-cause attribution | Analysis identifying the failure point for rejected or downgraded milk batches, distinguishing farmer-side issues (e.g., farmer cooler malfunction) from transit conditions (e.g., tanker temperature control failure) or equipment failures (e.g., receiving plant cooler issues), supported by telemetry data and quality test results | requirements.md § FR-007 |
| Intervention | Quality-assurance action taken in response to an alert (e.g., reroute, prioritization, expedited processing) to save a milk batch at risk of rejection | requirements.md § FR-006 |
| Data principal | Individual whose personal data is collected/processed, entitled to rights under DPDP Act 2023 (access, correction, erasure, portability) | requirements.md § FR-009 |
| Data localisation | Requirement that all personal data storage and processing infrastructure be physically located within India, per DPDP Act 2023 cross-border data transfer restrictions | requirements.md § FR-011 |