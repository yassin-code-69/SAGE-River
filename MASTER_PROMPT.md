# SAGE-River — FULL AUTONOMOUS PROJECT EXECUTION
## IEEE BUBT Academic Research Showcase 2026
### Track 1: Intelligent Computing, AI & Data Technologies

You are now responsible for executing the complete SAGE-River research poster competition project.

Act as a senior Geospatial AI Research Engineer, Remote Sensing Scientist, Python Developer, Machine Learning Engineer, Research Supervisor, Data Analyst, and Scientific Poster Designer.

You must work autonomously and complete as much of the project as technically possible.

**IMPORTANT: Do not stop after writing plans, reports, or recommendations. Implement the project, execute the code, process real data, conduct experiments, generate figures, prepare the final poster, and produce all deliverables.**

The team will review your completed work at the end.

Do not ask for approval after every phase. Continue through all phases automatically unless a genuine human-only action is required, such as Google Earth Engine account authentication.

---

# PART A — PROJECT CONTEXT

## 1. Competition Information

- Event: IEEE BUBT Academic Research Showcase 2026
- Event Date: 13–14 November 2026
- Track: Track 1 — Intelligent Computing, AI & Data Technologies
- Team: Undergraduate CSE students
- Main Objective: Complete a scientifically credible research project and present it through a professional academic poster.

This is a POSTER COMPETITION PROJECT, not a journal-paper submission.

Our priorities are:

1. A clearly defined real-world problem.
2. A verified literature review.
3. A defensible research gap.
4. A reproducible baseline.
5. Our own proposed solution.
6. Real experimental results.
7. Independent validation.
8. An excellent scientific poster.
9. Confident presentation and Q&A.

## 2. Final Research Direction

Our working title:

**How Many Sentinel-1 Scenes Are Enough? Scene-Count Sensitivity and Agreement-Gated Reliability of Post-Monsoon Riverbank Erosion Maps — Jamuna River, Bangladesh.**

Our proposed framework:

**SAGE-River = Season-matched, Agreement-Gated Erosion Mapping.**

## 3. Final Research Problem

Early post-monsoon riverbank erosion maps are useful for preparing for the next monsoon season.

Sentinel-1 SAR can observe through cloud cover, but producing a map quickly after the monsoon requires using only a limited number of available radar observations.

Limited observations, speckle noise, classification uncertainty, and lingering floodwater can cause false erosion detections.

Our main research question:

**How does the number of available post-monsoon Sentinel-1 observations affect the reliability of riverbank erosion maps, and can temporal agreement and confidence-based decision rules improve early mapping reliability?**

We are investigating historical erosion detection, NOT future erosion forecasting.

Do not claim that we are predicting where the river will erode in the next 7–14 days.

Do not claim that we have built a full Physics-Informed Neural Network.

Do not claim soil shear failure prediction.

---

# PART B — PHASE 0 FINDINGS YOU MUST USE AND VERIFY

A previous Phase 0 feasibility investigation was completed.

The following findings are preliminary and must be verified against the actual data and Google Earth Engine before being used as final results.

## 4. Environment

- Windows environment.
- Python 3.14.3 is installed.
- Python 3.11 is also installed and should be preferred.
- Google Earth Engine is not yet authenticated.
- Google Earth Engine credentials are missing.
- gcloud CLI is not installed.
- Required Python packages are not installed.

Use a Python 3.11 virtual environment.

Do not waste time installing gcloud unless authentication genuinely requires it.

Prefer Earth Engine localhost browser authentication.

I will manually complete Google login and authorization if required. You cannot bypass that requirement.

## 5. Preliminary Sentinel-1 Scene Inventory

A preliminary public-catalogue investigation found:

- Relative Orbit R114: Ascending, available from 2017.
- Relative Orbit R150: Descending, available from October 2014.
- Each relative orbit has approximately a 12-day acquisition interval over the candidate reaches.
- Sentinel-1B contributed very few scenes over the investigated area; do not claim that Sentinel-1B failure caused the local observation shortage.
- Sentinel-1A and Sentinel-1D operational transitions must be checked against actual metadata.

Preliminary R114 Ascending scene counts:

| Observation Window | Approximate Scene Count |
|---|---:|
| November only | 2–3 |
| November–December | 5–6 |
| November–January | 7–8 |
| November–April | 14–16 |

A preliminary 2025–2026 post-monsoon pool contains eight candidate acquisitions:

1. 8 November 2025
2. 20 November 2025
3. 2 December 2025
4. 14 December 2025
5. 26 December 2025
6. 7 January 2026
7. 19 January 2026
8. 31 January 2026

The preliminary 2024–2025 pre-monsoon composite contains approximately 16 candidate observations.

**Do not assume these counts are correct until verified in Google Earth Engine using the final AOI and exact filters.**

Verify:

- Unique acquisition IDs.
- Platform.
- Relative orbit.
- Orbit direction.
- Polarization.
- Acquisition mode.
- Acquisition date.
- Actual image availability.

## 6. Preliminary Study Area Candidates

Candidates:

- Kurigram — first candidate.
- Sirajganj / Kazipur / Chauhali — alternative.
- Sariakandi — alternative.

Kurigram was recommended as the first candidate because preliminary CEGIS information indicated substantial erosion in 2025.

However, do not automatically finalize Kurigram.

Select the reach only after inspecting actual Sentinel-2 imagery, Sentinel-1 coverage, bank protection, and independent reference availability.

Preferred reach length: approximately 10–15 km.

## 7. Baseline Research

Primary paper:

Freihardt & Frey (2023).

"Assessing riverbank erosion in Bangladesh using time series of Sentinel-1 radar imagery in the Google Earth Engine."

DOI:
https://doi.org/10.5194/nhess-23-751-2023

Original code:
https://doi.org/10.5281/zenodo.7253121

Important reported methodology:

- COPERNICUS/S1_GRD.
- IW mode.
- VV polarization.
- Ascending orbit for erosion mapping.
- Incidence-angle masking between 30° and 45°.
- Pre-monsoon and post-monsoon composites.
- Vegetation versus sand/water classification.
- Erosion rule: pre-monsoon backscatter above threshold and post-monsoon backscatter below threshold.

Important threshold configurations reported:

- -13.2 dB for a six-month window.
- -12.7 dB for a one-month window.

Important discrepancy:

The paper describes a 7×7 boxcar filter, while the released JavaScript code appears to use a circular kernel with radius 7.

Investigate this discrepancy.

Where feasible, document both:

1. Paper-described configuration.
2. Released-code configuration.

Do not silently combine different filter configurations.

The original research reported land-cover classification accuracy, but did not provide a numerical independent validation of the erosion map itself.

This difference is central to our research extension.

---

# PART C — AUTONOMOUS EXECUTION RULES

## 8. Work Autonomously

You are authorized to:

- Inspect all project files.
- Create new folders and files.
- Install packages inside a project virtual environment.
- Download public research papers and datasets.
- Access public APIs and catalogues.
- Write and execute Google Earth Engine scripts.
- Write and execute Python code.
- Debug errors.
- Run experiments.
- Generate maps, charts, and tables.
- Create editable poster files.
- Export PDF deliverables.
- Prepare presentation scripts and Q&A.
- Produce a final project report.

Do not repeatedly ask me for approval for these normal development tasks.

Do not stop after each phase to provide a report and wait for my response.

Continue through the entire workflow.

### Human-only actions

Pause only when a genuine human action is required:

- Google account login.
- Earth Engine registration or account authorization.
- A paid service or purchase.
- A required external consent.
- An irreversible or destructive action.

If authentication is unavailable:

1. Attempt public data catalogues and available no-auth data sources.
2. Continue every task that does not require authentication.
3. Prepare runnable Earth Engine scripts.
4. Give me one concise, exact instruction for the required login.
5. Do not pretend authentication succeeded.

Never request or expose passwords, access tokens, or OAuth secrets.

Do not use dangerous permission-bypass flags.

## 9. Preserve Existing Work

Inspect the current workspace first.

Expected project file:

SAGE-River/MASTER_PROMPT.md

If available, also inspect:

- PHASE0_REPORT.md
- SAGE-River Poster Plan Markdown
- Research Feasibility PDF
- Existing poster drafts
- Official event poster example

The Phase 0 report may not exist in the workspace. If it is missing, use the findings embedded in this instruction and clearly distinguish preliminary findings from verified data.

Do not delete or overwrite original user files.

Create a clean, organized project structure.

---

# PART D — COMPLETE IMPLEMENTATION

## 10. Research Literature Verification

Read the primary papers and original code.

Verify:

1. Freihardt & Frey (2023).
2. Freihardt & Frey (2022) Zenodo code.
3. Aishi & Fahim (2024).
4. Shampa et al. (2025).
5. Langhorst & Pavelsky (2023).
6. Relevant research on m-of-k temporal agreement.
7. Relevant research on uncertainty and abstention in remote sensing.
8. Relevant Sentinel-1 water and erosion detection methods.

For every important paper, record:

- Problem.
- Dataset.
- Method.
- Experimental setup.
- Results.
- Limitations.
- Relevance to SAGE-River.

Search for similar studies in remote sensing, flood mapping, deforestation monitoring, and change detection.

Do not claim that no prior research exists.

Our defensible contribution is the specific evaluation of:

- Erosion-map-level accuracy across scene budgets.
- m-of-k temporal agreement.
- Confidence-based abstention.
- Decision coverage.
- Independent optical reference evaluation.

Use cautious wording such as:

"To our knowledge, this specific combination of evaluations has not been identified in the reviewed literature."

If a closer study is discovered, modify the contribution statement.

---

## 11. Google Earth Engine Setup

Check whether Earth Engine is authenticated.

If not, prepare a simple setup guide for me.

Use Python 3.11.

Create a virtual environment:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the required packages, including:

- earthengine-api
- numpy
- pandas
- matplotlib
- scipy
- scikit-learn
- rasterio
- geopandas
- shapely
- python-pptx
- pillow

Only install additional packages when needed.

Verify the environment with a test script.

If GEE authentication succeeds, use it for the actual processing.

If GEE authentication is blocked, continue using public ASF or Element84 Earth Search STAC data where technically possible.

Do not stop the entire project just because GEE authentication is delayed.

---

## 12. Study Area Selection

Evaluate Kurigram and at least one alternative reach.

Use actual Sentinel-2 images to identify visible historical bank erosion.

Evaluate:

- Erosion visibility.
- Reach length.
- Sentinel-1 scene availability.
- Sentinel-2 reference quality.
- Bank protection.
- Channel geometry.
- Reference reliability.

Select one final reach.

Save:

- AOI polygon.
- Coordinates.
- Reach length.
- Study-area map.
- Selection rationale.

Do not select an area only because a district-level report indicates high erosion.

---

## 13. Sentinel-1 Scene Inventory

Use:

COPERNICUS/S1_GRD

https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD

Use the final AOI.

Generate an actual inventory from 2015–2026.

Filter:

- IW mode.
- VV polarization.
- Consistent relative orbit.
- Consistent orbit direction.
- Suitable incidence-angle range.
- Actual acquisition dates.

Check Sentinel-1 platform metadata.

Compare GEE counts against the preliminary ASF and Earth Search results.

Generate:

1. CSV scene inventory.
2. Scene-count summary.
3. Scene availability bar chart.
4. Acquisition timeline.
5. Orbit-specific comparison.

Required output:

outputs/tables/sentinel1_scene_inventory.csv

Required figure:

outputs/figures/figure_A_scene_availability.png

Do not use preliminary counts in the final poster without GEE or equivalent source verification.

---

## 14. Baseline Reproduction

Reproduce the relevant Freihardt & Frey workflow.

Inspect the original code line by line.

Create a new AOI for our selected reach.

Preserve the original method as closely as possible.

Document:

- Orbit.
- Polarization.
- Temporal windows.
- Incidence-angle mask.
- Speckle filtering.
- Threshold.
- Pre-monsoon classification.
- Post-monsoon classification.
- Erosion decision rule.

Create:

- Baseline pre-monsoon map.
- Baseline post-monsoon map.
- Baseline erosion map.

Save all processing configurations.

Do not claim successful reproduction until the output has been inspected and verified.

---

## 15. Independent Sentinel-2 Reference

Use:

COPERNICUS/S2_SR_HARMONIZED

https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED

If available, use Cloud Score+.

Check cloud-free coverage within the actual AOI, not only the full satellite tile.

Potential reference design:

- Pre-monsoon: comparable 2025 seasonal observations.
- Later dry season: comparable 2026 observations.

Use appropriate NDVI and MNDWI information where justified.

Inspect vegetation-to-sand/water transitions.

Restrict erosion labels to relevant outer-bank areas.

Exclude or separately handle:

- In-channel sandbars.
- Temporary floodwater.
- Agricultural fields.
- Rice paddies.
- Seasonal vegetation changes.
- Uncertain pixels.

Use approximately 100–200 stratified manual validation points if feasible.

Record the annotation criteria.

IMPORTANT:

Sentinel-2 is an independent optical reference, not field ground truth.

A later reference may contain erosion events that occurred after an earlier SAR map was produced.

Do not treat those later events as classification mistakes by the earlier map.

Define the temporal target of each experiment carefully.

If an independent reference cannot establish erosion status at the relevant mapping date, report agreement with a later cumulative-change reference rather than claiming strict as-of-date accuracy.

If the reference is unreliable, do not report validated accuracy.

---

# PART E — SAGE-RIVER IMPLEMENTATION

## 16. SAGE-River Components

SAGE-River consists of:

S — Season-matched comparison.

A — Agreement-based erosion detection.

G — Confidence gating.

### S: Season Matching

Use comparable seasonal windows.

Recognize that seasonal matching already exists in the published baseline.

Do not claim it as our new contribution.

Use it as a common control for fair comparison.

### A: Agreement-Based Detection

For each pixel, examine its classification across k available post-monsoon scenes.

Mark erosion only if the sand/water condition is satisfied in at least m of k observations.

Test:

- Majority agreement.
- Unanimous agreement.
- A validation-selected threshold if justified.

For k=1, temporal agreement is unavailable.

Do not pretend otherwise.

### G: Confidence Gating

For a classification threshold T and uncertainty margin δ:

If:

|backscatter - T| ≤ δ

mark the pixel as UNCERTAIN.

Otherwise, classify using the validated threshold.

Potential δ values:

0.5, 1.0, 1.5, 2.0 dB.

Use 2024 validation data to select parameters.

Freeze them before the 2025 test.

Report:

- Precision.
- Recall.
- F1.
- IoU.
- Decision coverage.
- Uncertain pixel percentage.
- False erosion area.
- Missed erosion area.

Never improve accuracy by silently excluding difficult pixels.

Confidence gating is a selective decision/abstention mechanism. Do not automatically describe it as calibrated probabilistic uncertainty.

### Baseline and Proposed Method

Compare:

1. Published baseline.
2. Baseline + Agreement.
3. Baseline + Confidence Gating.
4. Baseline + Agreement + Confidence Gating.

This will help us understand which component actually contributes.

---

# PART F — EXPERIMENTS

## 17. Validation and Test Periods

Use the following preliminary design, subject to data verification:

- Validation monsoon: 2024.
- Test monsoon: 2025.

Tune thresholds and parameters on 2024.

Freeze them before the final 2025 test.

Never tune using the final test reference.

## 18. Experiment A — Controlled Scene-Budget Benchmark

Preliminary 2025 post-monsoon scene pool:

8 candidate scenes from November 2025 to January 2026.

Test:

k = 1, 2, 3, 6, 8.

If all eight scenes are confirmed:

- k=1: 8 possible combinations.
- k=2: 28 combinations.
- k=3: 56 combinations.
- k=6: 28 combinations.
- k=8: 1 combination.

Use exhaustive combinations if computationally feasible.

Otherwise use fixed, documented random seeds and report the actual number of subsets.

Do not describe overlapping subsets as statistically independent samples.

Report mean, median, standard deviation, and range as appropriate.

This experiment measures scene-budget sensitivity.

It does not automatically represent chronological early mapping.

## 19. Experiment B — Chronological Early-Mapping Benchmark

Separately evaluate:

- First 1 scene.
- First 2 scenes.
- First 3 scenes.

Record the actual acquisition date for every output.

Do not use future scenes in an earlier map.

Use an appropriate time-matched independent reference if available.

If a later dry-season reference is used, clearly distinguish subsequent erosion from errors in the early map.

Do not merge Experiment A and B into one unsupported accuracy claim.

## 20. Threshold Calibration

The original paper used different thresholds for different temporal windows.

Do not blindly apply -12.7 dB to every configuration.

Develop a documented calibration procedure using 2024 validation data.

Investigate whether thresholds need to differ by:

- Scene count.
- Composite versus individual-scene classification.
- Filter configuration.
- Acquisition characteristics.

The 2025 test data must not be used to tune thresholds.

Document the difference between the paper-described filter and the released-code filter.

---

# PART G — EVALUATION AND RESULTS

## 21. Metrics

Use:

- Precision.
- Recall.
- F1-Score.
- IoU.
- False Erosion Area (hectares).
- Missed Erosion Area (hectares).
- Decision Coverage.
- Uncertain Pixel Percentage.

Use Boundary Displacement Error only if reference geometry supports it.

Do not use forecasting metrics such as AUPRC or Brier Score unless the final task and actual model output justify them.

Do not report overall accuracy alone.

## 22. Required Figures

Create genuine, high-resolution, scientifically correct figures.

Figure A:
Sentinel-1 scene availability chart.

Figure B:
Early/sparse-scene versus full-scene erosion maps, with reference overlay.

Figure C:
Baseline versus SAGE-River performance across scene counts.

Figure D:
False erosion, missed erosion, and uncertain-region map.

Create only the figures supported by completed experiments.

Never use invented or illustrative numbers as real results.

If an experiment fails or remains incomplete, label it honestly.

## 23. Result Analysis

For each experiment, explain:

- What changed?
- Why did it change?
- Did Precision improve?
- Did Recall decrease?
- Did confidence gating reduce coverage?
- Did agreement rules miss real erosion?
- Did the full-scene result outperform sparse scenes?
- Under what conditions did SAGE-River fail?

A method that performs worse is still a valid experimental finding.

Do not hide negative results.

---

# PART H — FINAL POSTER

## 24. Poster Requirements

Create a professional, custom academic research poster.

The event's sample poster is only a design reference, not a mandatory content structure.

Preferred design:

- Landscape orientation.
- 48 × 36 inches, subject to organizer confirmation.
- Within the maximum 4 × 4 feet limit.
- Three-column visual narrative.
- White/light background.
- Deep navy headings.
- Restrained teal/cyan accents.
- Large maps and charts.
- Minimal text.
- Readable typography.

Recommended title:

"How Many Sentinel-1 Scenes Are Enough? Scene-Count Sensitivity and Agreement-Gated Reliability of Post-Monsoon Riverbank Erosion Maps — Jamuna River, Bangladesh."

Required sections:

1. Title and Authors.
2. Abstract.
3. Real-World Problem.
4. Existing Research.
5. Research Gap.
6. Research Questions.
7. Study Area and Data.
8. Baseline Method.
9. Proposed SAGE-River.
10. Experimental Design.
11. Actual Results.
12. Key Contributions.
13. Limitations.
14. References.

Allocate substantial visual space to the actual experimental results.

Do not fill the poster with long literature-review paragraphs.

Create:

- Editable PPTX.
- Print-ready PDF.
- Poster content in Markdown.
- High-resolution figures separately.

The PPTX must be importable into Canva and retain editable text, shapes, diagrams, and charts.

Use actual team names only if available. Otherwise leave clearly labelled placeholders.

Do not invent university logos or supervisor names.

---

# PART I — PRESENTATION PREPARATION

## 25. Presentation Deliverables

Prepare:

1. Two-minute English presentation script.
2. Natural Bangla explanation.
3. Thirty-second short pitch.
4. Judges' technical Q&A.
5. Individual team-member responsibilities.
6. A simple explanation of every graph and map.

Prepare answers to:

- What is your exact research problem?
- What has already been done?
- How is your work different from Freihardt & Frey?
- Why are observations sparse?
- Why is Sentinel-1 useful?
- How do you distinguish temporary flooding from erosion?
- What is your reference data?
- Is Sentinel-2 field ground truth?
- What is SAGE-River?
- What is new about agreement gating?
- How does confidence gating work?
- What happens if your method performs worse?
- What are the limitations?
- Is this a PINN?
- Can CEGIS or BWDB use this framework?

Every team member must understand the entire workflow.

---

# PART J — PROJECT ORGANIZATION

## 26. File Structure

Create and maintain:

SAGE-River/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── docs/
│   ├── phase0_audit.md
│   ├── literature_review.md
│   ├── research_problem.md
│   ├── research_gap.md
│   ├── methodology.md
│   ├── experiment_design.md
│   ├── validation_protocol.md
│   ├── limitations.md
│   └── final_bangla_report.md
│
├── gee/
│   ├── 01_scene_inventory.js
│   ├── 02_study_area_selection.js
│   ├── 03_sar_preprocessing.js
│   ├── 04_baseline_erosion_mapping.js
│   ├── 05_sentinel2_reference.js
│   ├── 06_sage_river.js
│   └── 07_validation.js
│
├── python/
│   ├── scene_analysis.py
│   ├── reference_validation.py
│   ├── experiment_runner.py
│   ├── metrics.py
│   ├── generate_figures.py
│   └── final_audit.py
│
├── data/
│   ├── README.md
│   ├── aoi/
│   ├── metadata/
│   └── reference/
│
├── outputs/
│   ├── maps/
│   ├── figures/
│   ├── tables/
│   └── reports/
│
├── poster/
│   ├── poster_content_en.md
│   ├── references.bib
│   ├── poster_editable.pptx
│   └── poster_final.pdf
│
└── presentation/
    ├── pitch_english.md
    ├── pitch_bangla.md
    ├── judges_qa.md
    └── team_roles.md

Adapt the structure if technically necessary.

Preserve all original files.

Do not store credentials or tokens in the repository.

---

# PART K — AUTONOMOUS SCHEDULE

## 27. Deadline-Aware Execution

The event is on 13–14 November 2026.

Check the actual system date and time before starting.

Prioritize:

### Priority 1 — Essential

- GEE authentication or public-data fallback.
- Final AOI.
- Real Sentinel-1 scene inventory.
- Baseline reproduction.
- Independent reference assessment.
- At least two genuine data-based figures.

### Priority 2 — Main Proposed Solution

- Agreement-based detection.
- Confidence gating.
- Scene-budget experiment.
- Actual metrics.
- Baseline versus SAGE-River comparison.

### Priority 3 — Final Deliverables

- Poster PPTX.
- Poster PDF.
- Presentation scripts.
- Q&A.
- Final project report.

Suggested operational targets, subject to the actual remaining time:

- Results freeze: 12 November, 10:30.
- Poster content freeze: 12 November, 15:00.
- Print preparation: 12 November evening.
- Final rehearsal: 13 November morning.

These are working targets, not confirmed organizer deadlines.

If the time becomes insufficient, reduce the research scope instead of inventing results.

---

# PART L — FINAL QUALITY CONTROL

## 28. Mandatory Final Audit

Before declaring the project complete:

1. Run every Python script.
2. Test every GEE script that can be authenticated.
3. Verify all generated CSV files.
4. Verify all maps and charts.
5. Inspect all metric calculations.
6. Check temporal and spatial data leakage.
7. Verify the reference methodology.
8. Check all paper citations and DOI links.
9. Verify that the poster contains no unsupported claims.
10. Export and inspect the final poster PDF.
11. Confirm that the PPTX remains editable.
12. Verify that all required files exist.

Do not claim that a file, experiment, or output exists unless you have verified it.

Do not claim an experiment completed if only its script was written.

---

# PART M — FINAL DELIVERY

## 29. Required Final Outputs

At the end, provide a complete project handoff.

Required:

1. Final Bangla Research Explanation.
2. Verified Literature Review.
3. Final Research Problem and Research Gap.
4. Final Study Area and Coordinates.
5. Satellite Scene Inventory CSV.
6. Baseline Implementation.
7. SAGE-River Implementation.
8. Independent Reference and Validation.
9. Actual Experiment Results.
10. Metrics CSV.
11. Genuine Research Figures.
12. Editable Poster PPTX.
13. Print-Ready Poster PDF.
14. Two-Minute English Pitch.
15. Bangla Presentation Guide.
16. Judges' Q&A.
17. Team Responsibility Guide.
18. README and Reproduction Instructions.
19. Final Completion and Limitation Report.

Create a final status table:

| Component | Status | Evidence |
|---|---|---|
| Literature Review | | |
| Research Gap | | |
| GEE Authentication | | |
| Final Study Area | | |
| Scene Inventory | | |
| Baseline | | |
| Independent Reference | | |
| SAGE-River | | |
| Experiment A | | |
| Experiment B | | |
| Evaluation | | |
| Poster PPTX | | |
| Poster PDF | | |
| Presentation | | |

Use only these statuses:

- Completed and verified
- Completed with limitations
- Partially completed
- Blocked
- Not attempted

For every incomplete component, explain exactly why.

---

# FINAL EXECUTION COMMAND

You have already completed Phase 0 and produced a detailed feasibility report.

**NOW EXECUTE THE ENTIRE PROJECT AUTONOMOUSLY.**

Do not return another long proposal.

Do not ask me whether to start Phase 1.

Do not wait for approval between normal development stages.

Start by inspecting the workspace, reading the existing Phase 0 report if available, checking authentication, and establishing the project environment.

Then continue through all feasible implementation, experiments, analysis, poster creation, and presentation preparation.

If a required login is the only blocker, tell me exactly what I need to do once, then continue all other possible work.

If one experimental approach fails, diagnose it and try a scientifically valid alternative.

If the deadline makes the full scope impossible, prioritize a smaller, defensible project with real evidence.

**The team will review all completed files and results only after you finish the execution cycle.**

Remember:

REAL DATA > FANCY ALGORITHM

VALIDATION > CLAIMS

REPRODUCIBILITY > APPEARANCE

SCIENTIFIC HONESTY > ARTIFICIAL PERFORMANCE

Our goal is to deliver the strongest scientifically defensible poster that can realistically be completed before the competition.