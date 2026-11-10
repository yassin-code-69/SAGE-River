# Pitch scripts (English)
*Updated 11 Nov 2026: GEE σ⁰ results and SAGE-River v2.*

## 30-second pitch
Every monsoon the Jamuna eats farmland and homes. Radar satellites can map that loss through clouds, but a quick post-monsoon map has only two or three comparable Sentinel-1 scenes. We measured how many scenes are enough, and whether safeguards make sparse maps more reliable.

Two to three scenes already give a usable map. Requiring scenes to agree and abstaining near the threshold removes almost all false alarms, but it hides real erosion at the bank edges.

So our second version sorts each map into high-confidence, review and stable, and ranks the review areas. On an independent reach, reviewing the top-ranked areas found far more erosion than random review. It is not a better automatic classifier, and we say so.

## Two-minute presentation
**(Problem — 15 s)** The Jamuna erodes hundreds of hectares a year; CEGIS monitored about 348 hectares in 2025. Freihardt and Frey showed in 2023 that a Sentinel-1 threshold rule in Google Earth Engine can map past erosion. But one month after the monsoon, our reach has only two or three scenes from one orbit. That is orbit geometry, not clouds.

**(Method — 30 s)** We reproduced their rule on Earth Engine σ⁰ and scored every combination of 1 to 8 post-monsoon scenes against an independent Sentinel-2 reference: land vegetated before and sand or water after, connected to the channel. Sentinel-2 is an optical reference, not field truth. All settings were tuned on 2024 and frozen before the 2025 test. Version 1 adds two safeguards: several scenes must agree, and pixels too close to the threshold become UNCERTAIN.

**(Results v1 — 30 s)** With the published thresholds, going from one scene to three cut false erosion from 74 to 24 hectares, and eight scenes reached F1 0.82. One January scene created 160 hectares of false erosion on its own. We audited it and found no bug: those were temporarily flooded fields, confirmed by a second radar geometry and by Sentinel-2. Agreement kept two-scene maps containing that scene at under 2 hectares. But v1 abstained on 9 to 12 percent of pixels, holding a quarter to a third of the real erosion, so it did not beat a fairly tuned baseline.

**(v2 — 35 s)** So we turned the problem into triage. Version 2 marks bank-connected confident erosion as high-confidence. Possible erosion near the bank goes to review, ranked by a model trained on 2024 using only map-date radar features. We pre-registered the design and froze the code before touching a new reach, Sirajganj–Kazipur. There, reviewing the top 20 percent of the review area recovered two and a half to three and a half times more erosion than random review. Our success criteria held in 11 of 12 independent tests.

**(Honesty — 10 s)** v2 gives no automatic accuracy gain. Our reviewer is a simulated perfect analyst, and the independent test has only 12 hectares of erosion. What we offer is a cheap protocol: check scene count, require agreement, report coverage, and send analysts to the right places first.
