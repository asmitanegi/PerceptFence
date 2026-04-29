# Title Decision

## Article title

**Consent-Aware Runtime Mediation for Privacy in Real-Time Screen-Share AI Assistants**

## Project name

**PerceptFence**

## Repo / slide-header form

**PerceptFence — Consent-Aware Runtime Mediation for Privacy in Real-Time Screen-Share AI Assistants**

## Short title

**Consent-Aware Runtime Mediation for Screen-Share AI**

Use this for issue titles, figure captions, filenames, citations, or slide headers when the full title is too long.

## Talk subtitle (informal only)

**"Guarding the Glass"** — for slide deck headers and informal talk titles only. Never the official paper title.

## Why this title

- **Method, goal, and setting in one line.** "Runtime mediation" names the mechanism; "for privacy" names the motivational goal; "real-time screen-share AI assistants" names the setting and the assistant class. This is the SOUPS/IUI direct-title pattern that adjacent accepted work uses, e.g. Liu et al., "Follow My Recommendations: A Personalized Privacy Assistant for Mobile App Permissions" and the Wijesekera/Egelman "Runtime Permissions for Privacy in Proactive Intelligent Assistants" lineage.
- **IUI-fluent without overclaiming.** "Consent-aware" describes a policy-engine state, not informed human consent in the legal/HCI sense — the introduction will scope it explicitly. "Runtime mediation" is mechanism, not guarantee.
- **Searchable.** Carries the canonical phrases researchers will type into Google Scholar / Semantic Scholar / ArXiv: "screen-share AI assistants," "real-time," "consent-aware," "runtime mediation."
- **Blind-review safe.** No author, organization, product, or case-specific identifiers.

## Why PerceptFence as the project name

- **Research-grade common-noun handle** that maps to the system's job: putting a boundary around what the assistant can perceive.
- **No collision in the AI-assistant privacy space.** Quick checks confirm Aperture (Tailscale), Iris (saturated), Cloak (existing screen-sharing privacy app), Veil (offensive-security framework), Aegis (Forrester, AegisAI), Stagehand (Browserbase), and Liminal (funded AI-security vendor) are all already taken in adjacent product or research spaces. PerceptFence is clear in this space.
- **Avoids the obvious commercial-sounding labels.** ScreenGuard, GlassGuard, ConsentLayer all already hit existing products on web checks.
- **Inherits FlowFence lineage legibly.** The "fence" suffix recalls Fernandes et al., "FlowFence: Practical Data Protection for Emerging IoT Application Frameworks" (USENIX Security 2016), which is a known and respected systems-paper handle in the runtime-mediation space. Reviewer pattern-matching here is an asset, not a liability.

## Claim guardrail on the "Privacy" word

The earlier same-day rejection of "Privacy-Preserving Screen-Share AI" stands. **"For Privacy" is a motivational goal, not a property claim.** The abstract must scope it precisely: PerceptFence reduces *measured sensitive-exposure rate* on synthetic scenarios with bounded latency overhead. It does not claim formal privacy preservation, differential-privacy guarantees, or absence of side-channel leakage. `eval/metrics.md` keeps sensitive-exposure-rate as the measured outcome that backs the framing; the security review's banned-term list (`security-threat-model-review.md` §2.1) still applies — "privacy-preserving," "trustworthy," "secure," "prevents leakage," "first," "novel" remain banned without metric backing.

## Names rejected (in order of consideration)

- **"Screen-Share AI Paper"** — too generic; names the artifact type instead of the contribution.
- **"Mediating What Screen-Share AI Assistants See, Remember, and Say: Runtime Consent Controls for Live Assistance"** — earlier same-day recommendation. Rejected on title-pattern grounds: 15 words against an IUI median of 12, gerund-led without a system-name handle before the colon, reads more as a CSCW position paper than an IUI system paper. The see/remember/say triad is preserved in the abstract and section structure as a mnemonic for the control surface, just not in the title.
- **"Consent-Aware Screen-Share Assistant Runtime"** — accurate but flat; weaker than the chosen direct-title form.
- **"Privacy-Preserving Screen-Share AI"** — overclaims privacy guarantees that the synthetic prototype does not prove.
- **"Secure Screen-Share AI Assistant"** — overclaims security and invites review scrutiny the current evaluation cannot satisfy.
- **"Trustworthy Screen-Share AI"** — implies user-study/social-trust evidence that is out of scope for v1.
- **"Squint: Mediating What Live Screen-Share AI Assistants See, Remember, and Say"** — strong contrarian alternative from the IUI-pattern survey. The single-syllable common-noun handle, the see/remember/say mnemonic, and the inversion of the AI-as-observer frame all scored well. Rejected in favor of the contribution-first SOUPS/IUI direct title because the more conservative register won on the explicit "all three optimization targets balanced" weighting and on internal evidence-packet legibility.
- **"Vignette"** — optical-metaphor project name. Mechanism-fit (vignetting darkens edges while preserving the subject) is excellent. Rejected on syllable count and weaker evidence-packet handle relative to PerceptFence.
- **"Sluice"** — architectural-metaphor project name. Single syllable, clean. Rejected because it foregrounds the systems contribution over the user-facing reframing, where the paper's framing leads with consent rather than architecture.
- **"Live Assistance Without Live Capture: A Runtime Mediator for Screen-Share AI Assistants"** — Veil-lineage subtractive-form alternative (cf. Wang/Zeldovich/Mickens, NDSS 2018, "Veil: Private Browsing Semantics Without Browser-Side Assistance"). Rejected because the architecture interposes rather than bypasses raw capture, so the "Without" framing would be a stronger architectural claim than the v1 evaluation can defend.
- **ScreenGuard / GlassGuard / ConsentLayer** — all hit existing products on web checks.
- **Aperture / Iris / Cloak / Veil / Aegis / Stagehand / Liminal** — all taken in adjacent AI-assistant or security-systems product or research spaces.
- **PRISM / ECHELON-style names** — permanent surveillance valence; never appropriate for a consent-mediation system.
