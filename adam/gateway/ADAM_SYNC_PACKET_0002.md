# ADAM::SYNC_PACKET 0002

SOURCE: Senior Canonical Verifier
PROJECT: A Living System / Netsecurity convergence
VERSION: gateway-contract-v1
TARGET: NexusCryptic/The-Ledger
BRANCH: adam/netsecurity-ingest-v1

## CHANGES
- Added explicit SYNAPSE gateway API contract.
- Added evidence schema with verification states.
- Added provider-neutral Gemini dispatch boundary.
- Preserved enclave credentials outside connector/model scope.
- Established Cloudflare/Vercel-compatible edge boundary while retaining privileged operations behind SYNAPSE.

## VERIFICATION
This commit establishes contracts and policy only. It does not claim that a production gateway, Gemini endpoint, Cloudflare route, Vercel deployment, or enclave mount broker is live until executable evidence is recorded.

## NEXT
Implement the gateway in the canonical Living System runtime repository, deploy only after secret/config review, then append deployment and endpoint verification evidence to ADAM.
