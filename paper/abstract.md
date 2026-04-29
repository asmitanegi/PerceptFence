## Frozen thesis

Problem statement: “Live screen-share AI assistants can observe raw screen and speech streams, but users lack fine-grained runtime control over what the assistant may see, retain, and say.”

What we solve: “A runtime mediation layer that enforces consent, redaction, memory controls, and output safeguards for live multimodal assistance.”

Article about: “Design and evaluation of a consent-aware runtime layer for real-time screen-share assistants.”

## Abstract

Live screen-share AI assistants can observe raw screen and speech streams, but users lack fine-grained runtime control over what the assistant may see, retain, and say. General chat settings and coarse privacy controls do not address this runtime gap because assistance depends on fast-changing interface context that may include information outside the user’s current consent. We study a runtime mediation layer that enforces consent, redaction, memory controls, and output safeguards for live multimodal assistance between capture adapters, session memory, and assistant responses. We will evaluate the layer on synthetic screen-share scenarios covering secrets, personal data, sensitive speech fragments, prompt-injection text, dense interfaces, zoom changes, and fast window switching, measuring sensitive exposure, false blocks, latency overhead, and task completion against an unmediated prototype baseline. The planned contribution is a bounded design and evaluation of runtime control mechanisms for screen-share assistants, with claims limited to synthetic evidence until benchmark results are available.
