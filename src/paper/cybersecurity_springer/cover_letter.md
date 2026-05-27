# Cover Letter — Cybersecurity (Springer Nature)

**To:** Editor-in-Chief, Cybersecurity (Springer Nature)
**From:** Neeraj Kumar Singh, Parafin, Inc., San Francisco, CA, USA
**E-mail:** neeraj@parafin.com
**Date:** 2026-05-16
**Re:** Submission of original research article

---

Dear Editor-in-Chief,

We submit for your consideration an original research article entitled
**"Consent-Aware Runtime Mediation for Privacy in Real-Time Screen-Share AI
Assistants"** for publication in *Cybersecurity*.

Live screen-share AI assistants now sit inside production engineering and
customer-support workflows, where they observe raw screen and speech streams
containing credentials, personal data, and sensitive business context. Existing
privacy controls operate at the session level — a blanket on/off toggle — and
cannot enforce the per-frame, per-content-category policies that live
screen-share deployment requires. This gap is a direct and growing security
concern as screen-share AI adoption scales.

Our paper makes three contributions relevant to *Cybersecurity*'s scope:

1. **A runtime mediation design** decomposed into seven modules (consent/policy
   engine, redaction engine, session memory gate, output guard, audit logger,
   and two capture adapters) with explicit trust boundaries and an adversary
   model that covers prompt injection, output leakage, and adversarial-evasion
   attacks delivered through displayed screen content.

2. **A per-module ablation study** on a synthetic benchmark of 11 scenario
   classes, including three adversarial-evasion classes (Unicode-homoglyph
   credentials, split PII, and encoded screen instructions). The full guard
   achieves the expected outcome on 11/11 fixtures; the unmediated baseline
   reaches it on 0/11.

3. **A claim-to-metric audit framework** that ties every empirical claim to a
   specific CSV row, making the evaluation independently verifiable.

The manuscript is 9 sections, approximately 6,500 words, with 5 tables and 16
references. The reference implementation and synthetic fixture set are available
as open-source artifacts.

This article has not been submitted elsewhere and is not under review at any
other journal or conference. All evaluation data is synthetic; no human subjects
are involved and IRB approval is not required.

We suggest the following potential reviewers based on relevant published work in
this area: researchers who have published on runtime privacy controls, prompt
injection defenses, and AI assistant security — specifically those active in
venues such as USENIX Security, CCS, and IEEE S&P.

Thank you for considering this submission.

**Neeraj Kumar Singh**
Parafin, Inc.
San Francisco, California, USA
neeraj@parafin.com
