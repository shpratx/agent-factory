<!--
kb-L1-regulatory-frameworks-index-uk · content · regulatory-bodies-index.md
Layer: L1 (enterprise, domain-agnostic). Micro-KB content rules apply:
max 1 line/bullet, max 15 words, no explanations, numbers not words.

JURISDICTION: United Kingdom. The KB is domain-agnostic but NOT
jurisdiction-agnostic — one geography per deployment. Serving two
geographies needs two KBs, not merged rows. The India pair is
kb-L1-regulatory-frameworks-index-ind / kb-L2-domain-regulatory-ind.

Two sections. #cross-domain-index maps an activity to its regulator.
#coverage-categories is the sweep list: every category here is either a
constraint or a declared not-applicable entry. Both the checker and its
evaluator read this file, so the sweep and its audit are the same list.

DEVOLVED/LOCAL: many UK regimes bind at more than one level — food
registration and inspection, licensing, trading standards, building
control. A UK-wide answer alone is incomplete where the idea operates in
Scotland, Wales or Northern Ireland, or across several local authorities.
See the checker prompt's sub-national edge case.
-->

# UK Regulatory Bodies Index (Cross-Domain)

## Jurisdiction

**Jurisdiction covered: United Kingdom (ISO 3166-1 alpha-2: GB).**
Sub-national layers in scope: England, Scotland, Wales, Northern Ireland,
and local authorities. This index covers no other country. An idea
targeting a different country cannot be assessed from it.

Use to identify the correct regulator category before loading a
domain-specific L2 regulatory KB for detailed rules.

## Cross-Domain Index

- Financial services, payments → FCA, PRA (Bank of England) (→ CON-Regulatory)
- Food safety & standards → FSA (England/Wales/NI), FSS (Scotland) (→ CON-Regulatory)
- Local food registration & inspection → Environmental Health, Trading Standards (→ CON-Regulatory)
- Data protection & privacy → ICO (UK GDPR, Data Protection Act 2018) (→ CON-Regulatory)
- Cybersecurity & incident reporting → NCSC; ICO for personal data breaches (→ CON-Regulatory)
- Workplace health & safety → HSE (Health and Safety Executive) (→ CON-Regulatory)
- Medicines & medical devices → MHRA (→ CON-Regulatory)
- Telecoms & broadcasting → Ofcom (→ CON-Regulatory)
- Energy → Ofgem (→ CON-Regulatory)
- Nuclear → ONR (Office for Nuclear Regulation) (→ CON-Regulatory)
- Advertising standards, all sectors → ASA; CMA for unfair practices (→ CON-Regulatory)
- Competition & consumer protection → CMA, Trading Standards (→ CON-Regulatory)
- General product safety, non-food consumer goods → OPSS (→ CON-Regulatory)
- Product conformity marking → UKCA (GB), UKNI/CE (Northern Ireland) (→ CON-Regulatory)
- Weights, measures, pre-packed quantity → Trading Standards (→ CON-Regulatory)
- Employment, worker status, wages → Employment Tribunals, HMRC, EASI (→ CON-Regulatory)
- Pensions & auto-enrolment → The Pensions Regulator (→ CON-Regulatory)
- Environment, waste, packaging EPR → Environment Agency, SEPA, NRW, NIEA (→ CON-Regulatory)
- Accessibility & equality duties → EHRC (Equality Act 2010) (→ CON-Regulatory)
- Export control & sanctions → ECJU (DBT); OFSI for financial sanctions (→ CON-Regulatory)
- Tax, VAT, e-invoicing, records → HMRC (→ CON-Regulatory)
- Corporate records & filings → Companies House (→ CON-Regulatory)
- Intellectual property → UK IPO (patents, designs, trade marks) (→ CON-Regulatory)
- Gambling, alcohol, age-restricted supply → Gambling Commission, licensing authorities (→ CON-Regulatory)
- Cross-local-authority consistency → Primary Authority Scheme (→ CON-Regulatory)

## Coverage Categories (sweep list)

Sweep every category. Each is a constraint, or a not-applicable entry with a reason.

- Authorisation, licensing, registration, permits — including devolved and local-authority layers
- Data protection & privacy — lawful basis, transparency, retention, data subject rights
- Children's data and other heightened-duty categories — where the user segment implies it
- International data transfer — processing, hosting, or support outside the UK
- Cybersecurity, incident reporting & log retention — applies regardless of personal data
- Automated decision-making, profiling, AI obligations — a model deciding about a person
- Consumer protection, unfair trading, e-commerce duties — where the user is a consumer
- Advertising, marketing, claim substantiation — health, environmental, performance claims
- Product safety, certification, conformity marking — anything physical, incl. UKCA
- Weights, measures, and pre-packed quantity declarations
- Food-specific rules — registration, approval, labelling, allergens, hygiene
- Sector safety & conduct regimes — workplaces, medicines, devices, telecom, energy, nuclear
- Payments authorisation & financial crime — only where funds are held or moved
- Employment, worker status, agency labour, pensions auto-enrolment
- Environment, permits, waste, packaging and e-waste EPR
- Accessibility — any public-facing digital interface
- Intellectual property & third-party data licensing — data or content not owned
- Export control, sanctions, and restricted-party screening — where the idea crosses borders
- Tax, VAT, and statutory record-keeping — duties created by the transaction model
- Competition & platform conduct — where the idea is a marketplace or intermediary
- Age-restricted or conditional supply — where the product category implies it
