# L1-inception-ai-evaluation-agent-app-builder-and-scoring-orchestrator

## Purpose

Designs and operationalizes a production-ready AI evaluation application specification. The agent produces a complete blueprint for an app that evaluates AI outputs through programmatic checks, Claude-based rubric scoring, failure analysis, result aggregation, and secure UI behavior.

## What does it do?

- Accepts a task definition that includes task name, description, success criteria, failure modes, output type, and difficulty
- Converts task requirements into a full application blueprint for an evaluation workflow
- Defines evaluation logic for programmatic checks, rubric scoring, weighting models, and PASS/FAIL thresholds
- Specifies result schemas, in-memory state, and aggregate dashboard metrics
- Proposes a React + Tailwind UI structure with responsive and accessible states
- Includes reliability controls, security/compliance notes, and delivery checklist items

## How does it work?

1. Capture the task definition and normalize the metadata
2. Extract success criteria, output type, difficulty, and failure modes
3. Design the app blueprint and screen responsibilities
4. Define evaluation logic for deterministic checks and LLM judge scoring
5. Specify the data model for saved results and dashboard aggregation
6. Detail UI patterns, responsive states, and accessibility guidance
7. Add reliability, observability, and security controls
8. Provide a practical delivery checklist for implementation

## Input

- Source: direct_input, agent_output, or file_upload
- Required: task_definition (string)
- Optional: domain, constraints

## Output

- Type: app_specification
- Status: success or failed
- Items: app_blueprint, evaluation_logic, data_model, ui_specification, reliability_controls, security_and_compliance_notes, delivery_checklist
- Summary: reflection findings, implementation readiness, and recommendations
