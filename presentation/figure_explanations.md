# How to explain every figure (English + বাংলা)

## Figure 0 — Study area
**EN:** Left: Sentinel-2 true colour of the Kurigram Jamuna (Feb–Mar 2025) with our 12 km reach (yellow box). Right: the reach after the 2025 monsoon (Feb–Mar 2026). Both outer banks lie inside the box.
**বাংলা:** বাঁ দিকে কুড়িগ্রামের যমুনা, হলুদ বাক্সটা আমাদের ১২ কিমি এলাকা। ডান দিকে ২০২৫ বর্ষার পরের ছবি। দুই পাড়ই বাক্সের ভেতরে।

## Figure A — Sentinel-1 scene availability
**EN:** (a) How many Sentinel-1 acquisitions covered the reach each year, by orbit and satellite: S1A did almost everything; S1B added only 4 scenes; S1D replaced S1A in July 2026. (b) For the ascending orbit 114: a November-only window has 2–3 scenes, Nov–Jan 7–8, Nov–Apr 14–16. Short windows = few scenes — a geometry/time limit, not clouds.
**বাংলা:** (a) প্রতি বছর কতগুলো রাডার ছবি এসেছে — প্রায় সবই S1A; S1B মাত্র ৪টি; ২০২৬-এর জুলাই থেকে S1D। (b) শুধু নভেম্বরে ২–৩টি ছবি, নভেম্বর–জানুয়ারিতে ৭–৮টি। দ্রুত ম্যাপ মানেই কম ছবি — মেঘের জন্য নয়, orbit আর সময়ের জন্য।

## Figure B — Erosion maps (sparse vs full)
**EN:** Columns: 1 scene, 3 scenes, all 8 scenes. Top row = baseline, bottom = SAGE-River. Green = correct erosion, orange = false erosion, purple = missed erosion, grey = UNCERTAIN (abstained). Cyan outline = Sentinel-2 reference erosion. Only the outer-bank strip is coloured.
**বাংলা:** কলাম: ১টি, ৩টি, ৮টি ছবি। উপরে baseline, নিচে SAGE-River। সবুজ = সঠিক ভাঙন, কমলা = ভুল ভাঙন, বেগুনি = মিস করা ভাঙন, ধূসর = অনিশ্চিত (সিদ্ধান্ত দেওয়া হয়নি)। নীলচে রেখা = Sentinel-2 অনুযায়ী আসল ভাঙন।

## Figure C — Performance vs number of scenes
**EN:** Each point = mean over all possible scene subsets of that size (k = 1, 2, 3, 6, 8) for the 2025 test monsoon. Shaded band = ±1 SD across subsets (subset variability, not a confidence interval). Panels: precision, recall, F1, IoU, decision coverage, false-erosion area.
**বাংলা:** প্রতিটি বিন্দু = ওই সংখ্যক ছবির সব সম্ভাব্য combination-এর গড়। ছায়া = combination-ভেদে ওঠানামা। Coverage মানে কত শতাংশ pixel-এ সিদ্ধান্ত দেওয়া হয়েছে।

## Figure D — A bad scene, audited (31 Jan 2026)
**EN:** Panel 1 shows the 31 Jan Sentinel-1 scene, with dark field-shaped patches on the west floodplain. Panel 2 shows that this scene alone gives the tuned baseline 160 ha of false erosion (orange). Panels 3 and 4 use 19 + 31 Jan together: the baseline drops to 11 ha and SAGE A+G to 2.2 ha (grey = UNCERTAIN). The root-cause audit found no processing error. The patches are temporarily inundated fields, also seen in the R150 descending orbit and in Sentinel-2 (88–99 % water, 28 Jan–12 Feb).
**বাংলা:** ৩১ জানুয়ারির রাডার ছবিতে পশ্চিমের জমিতে মাঠের আকারের কালো দাগ দেখা যায়। ছবিটি একা ব্যবহার করলে baseline ১৬০ হেক্টর ভুল ভাঙন দেখায়। ১৯ ও ৩১ জানুয়ারি একসাথে নিলে baseline-এ ১১ হেক্টর আর SAGE-এ ২.২ হেক্টর। কোডে ভুল নেই; দাগগুলো সাময়িকভাবে পানিতে ডোবা জমি, যা অন্য orbit আর Sentinel-2-তেও দেখা যায়।

## Figure E — Early maps (chronological)
**EN:** F1 of maps that could have been produced on the date of the 1st, 2nd and 3rd acquisition after 1 November, against the cumulative reference (left) and against erosion already visible by mid-December (right).
**বাংলা:** ১ নভেম্বরের পর ১ম, ২য়, ৩য় ছবি আসার দিনেই যে ম্যাপ বানানো যেত, তার F1 — বাঁয়ে পরের ফেব্রুয়ারি–মার্চের reference, ডানে মধ্য-ডিসেম্বরের মধ্যে দৃশ্যমান ভাঙন।


## Figure F — Abstention trade-off
**EN:** As the abstention band δ widens, precision on decided pixels rises, but coverage falls and more real erosion is abstained. This is a post-hoc view of 2025 and was not used to choose δ.
**বাংলা:** δ বাড়ালে সিদ্ধান্ত-দেওয়া pixel-এ precision বাড়ে, কিন্তু coverage কমে আর বেশি আসল ভাঙন "অনিশ্চিত"-এ চলে যায়। এটা পরে দেখা, δ বাছাইয়ে ব্যবহার হয়নি।

## Figure G — v2 ablation (full-area F1)
**EN:** Bars show F1 step by step: tuned baseline → + agreement → + gating → v1 → v2 high-confidence (no review) → v2 + 10 % / 20 % prioritized review → v2 + 20 % random review. Panels: Kurigram 2025 (exploratory), Sirajganj 2025 (independent) and Sirajganj 2024 (Kurigram parameters). Without review, v2 equals v1 and is below the tuned baseline. Review bars use a simulated perfect analyst, so they are upper bounds.
**বাংলা:** ধাপে ধাপে F1: baseline → agreement → gating → v1 → v2 (যাচাই ছাড়া) → v2 + ১০%/২০% অগ্রাধিকার যাচাই → v2 + ২০% random যাচাই। যাচাই ছাড়া v2 = v1, আর tune করা baseline-এর চেয়ে কম। যাচাইয়ের বার "নিখুঁত বিশ্লেষক" ধরে নেওয়া upper bound।

## Figure H — Prioritized vs random review (poster section 10)
**EN:** The x-axis is the percentage of the REVIEW area inspected. The y-axis is the percentage of the erosion inside REVIEW that is recovered. The orange line is v2's ranked order; the grey band is 500 random orders (5–95 %); the dashed line is the random mean; the purple dotted line is random review of v1's UNCERTAIN pixels with the same hectares. The higher and earlier the orange curve, the less effort is needed.
**বাংলা:** x-অক্ষ: "যাচাই" এলাকার কত শতাংশ দেখা হলো। y-অক্ষ: ওই এলাকার ভাঙনের কত শতাংশ পাওয়া গেল। কমলা = v2-এর অগ্রাধিকার; ধূসর ছায়া = ৫০০টি random ক্রম; বেগুনি = v1-এর অনিশ্চিত pixel random-ভাবে দেখা। কমলা রেখা যত আগে ওপরে ওঠে, তত কম পরিশ্রমে বেশি ভাঙন মেলে।

## Figure I — Three-class map
**EN:** The map uses the first three scenes. Red = HIGH-CONFIDENCE erosion; orange = REVIEW, top 10 % priority; yellow = REVIEW, 10–30 %; light grey = REVIEW, lower priority; uncoloured = LIKELY STABLE. The cyan outline is the Sentinel-2 reference, shown for evaluation only and never used to make the map.
**বাংলা:** প্রথম ৩টি ছবি দিয়ে তিন-শ্রেণির ম্যাপ। লাল = নিশ্চিত ভাঙন; কমলা = যাচাই (সবচেয়ে বেশি অগ্রাধিকার); হলুদ = মাঝারি; হালকা ধূসর = কম অগ্রাধিকার। নীলচে রেখা = Sentinel-2 reference, যা শুধু মূল্যায়নের জন্য, ম্যাপ বানাতে ব্যবহার হয়নি।
