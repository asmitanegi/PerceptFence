# Slide 1 — Thesis Lock

Problem statement: “Live screen-share AI assistants can observe raw screen and speech streams, but users lack fine-grained runtime control over what the assistant may see, retain, and say.”

What we solve: “A runtime mediation layer that enforces consent, redaction, memory controls, and output safeguards for live multimodal assistance.”

Article about: “Design and evaluation of a consent-aware runtime layer for real-time screen-share assistants.”

## One-line pitch

A consent-aware runtime sits between raw multimodal session streams and the assistant, enforcing runtime permissions before observation, retention, or response.

## Figure placeholder

Synthetic session streams → mediation layer → assistant context/output

Mediation layer components: consent policy, redaction, memory gate, output guard, audit record.
