# Policy Boundaries

The canonical policy boundary specification for the screen-share AI runtime mediation layer is [`../policy-boundaries.md`](../policy-boundaries.md).

That document defines, for each of the six modules (consent engine, redaction engine, session memory gate, output guard, audit logger), what the module **enforces**, what it **does NOT enforce**, and its **trust assumptions**. It also includes a policy-interaction matrix.

## Source code policy files

The `src/policies/` directory contains machine-readable policy definitions (e.g., `consent_redaction_policy.json`) used by the runtime prototype. These are the implementation of the boundaries described in `policy-boundaries.md`, not a replacement for them.
