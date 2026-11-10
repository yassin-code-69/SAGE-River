Run 1 (11 Nov 2026 01:56-01:57) — identical pipeline WITHOUT the BASE_F1tuned control.
Kept for audit. Decision to add BASE_F1tuned was taken after inspecting only the 2024 validation tables
(fairness: SAGE's m/delta are tuned on 2024 erosion F1, so the baseline must get an equally tuned threshold)
and BEFORE any 2025 test metric was opened. All other methods are deterministic and identical in run 2.
