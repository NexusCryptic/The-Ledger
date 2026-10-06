# ADAM / SYNAPSE Gateway

This directory defines the security boundary between chat/agent tooling and privileged Nexus runtime operations.

## Rule

No connector, model, HTML client, or automation receives raw enclave credentials or unrestricted host access. External agents request narrowly scoped capabilities. SYNAPSE performs privileged local operations and emits signed evidence. ADAM verifies that evidence before updating canonical state.

## Control flow

Chat / Codex / connected tools -> authenticated HTTPS gateway -> SYNAPSE capability broker -> local runtime -> signed evidence -> ADAM ledger.

## Evidence states

- REQUESTED
- ACCEPTED
- EXECUTED_UNVERIFIED
- VERIFIED
- REJECTED

A UI status or model response alone is never production proof.

## Gemini adapter

/v1/gemini/dispatch is an adapter boundary, not a hard-coded vendor secret. Provider credentials belong in the deployment secret store and must never be committed.

## Deployment

The API contract is intentionally provider-neutral so the gateway can be deployed behind Cloudflare and/or Vercel while the privileged mount broker remains local or in a separately trusted environment.
