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

## Figure D — Error and uncertainty map
**EN:** Before (Feb–Mar 2025) and after (Feb–Mar 2026) optical images, and the SAGE-River map from the first three scenes, showing where it is right, wrong, or abstains.
**বাংলা:** আগে-পরের অপটিক্যাল ছবি আর প্রথম ৩টি রাডার ছবি দিয়ে SAGE-River ম্যাপ — কোথায় ঠিক, কোথায় ভুল, কোথায় "নিশ্চিত না"।

## Figure E — Early maps (chronological)
**EN:** F1 of maps that could have been produced on the date of the 1st, 2nd and 3rd acquisition after 1 November, against the cumulative reference (left) and against erosion already visible by mid-December (right).
**বাংলা:** ১ নভেম্বরের পর ১ম, ২য়, ৩য় ছবি আসার দিনেই যে ম্যাপ বানানো যেত, তার F1 — বাঁয়ে পরের ফেব্রুয়ারি–মার্চের reference, ডানে মধ্য-ডিসেম্বরের মধ্যে দৃশ্যমান ভাঙন।
