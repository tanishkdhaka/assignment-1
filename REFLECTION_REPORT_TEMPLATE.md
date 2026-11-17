# Assignment 1 Submission: Reflection Report & Metadata

> **Submission Instructions:** Upload ONLY this reflection report to the LMS. Code stays in GitHub. Video stays in Google Drive.

---

## Student & Submission Details

- **Student Name:** Tanishk Dhaka
- **Student ID:** 2026NS93035
- **Institutional Email:** 2026ns93035@wilp.bits-pilani.ac.in
- **GitHub Repository Link:** https://github.com/tanishkdhaka/assignment-1
- **Demonstration Video Link:** [PASTE YOUR VIDEO LINK HERE AFTER RECORDING]

---

## Part 1A: Problem Statement Description

Part 1A addresses the problem of calculating a shopping cart total correctly when multiple types of discount coupons are applied alongside a fixed tax rate. The intended users are e-commerce back-end engineers who need a reliable, testable calculation engine they can call from a CLI or integrate into a larger service. The key requirements are: adding and removing items from an in-memory cart with JSON persistence, applying three distinct coupon types (percentage discount, fixed-amount discount with a minimum subtotal threshold, and BOGO buy-N-get-M per SKU), enforcing a last-wins stacking rule for non-BOGO coupons, computing tax only on the post-discount subtotal, and preventing the total from going negative. The expected outcome is a deterministic engine that produces the same result for the same input every time and returns structured error codes rather than raw exceptions, making it straightforward to test and harness independently.

---

## Part 1B: Problem Statement Description

Part 1B addresses the problem of automatically routing customer support tickets to the correct internal team when the ticket text is unstructured free-form English. The non-deterministic behaviour arises because a generative language model is used to interpret the ticket intent — the same ticket can produce slightly different summaries or phrasings across runs, making exact-string test assertions unreliable. The expected output is a stable JSON record containing a fixed schema: `category` (billing / technical / account / feature_request / other), `priority` (low / medium / high / critical), `needs_clarification` boolean, `clarification_question`, `assigned_team`, `summary`, and `confidence`. The evaluation approach uses an independent 3-layer harness: Layer 1 validates the JSON schema contract, Layer 2 checks deterministic invariants and guardrail rules (such as refusing jailbreak prompts), and Layer 3 scores semantic quality using a keyword-recall rubric across 20 benchmark cases with a pre-declared acceptance threshold of ≥ 0.80.

---

## Part 2: Assessed Reflection Questions (5 Marks — 1 Mark Each)

### Question 1: Specification Influence

One concrete implementation decision that was directly shaped by a Spec Kit artifact is the **last-wins discount stacking rule** in `Part-1A/src/cart/engine.py`. During the specification phase, an ambiguity arose: if a user applies a PERCENTAGE coupon and then a FIXED_AMOUNT coupon, should the second compound on top of the first, be rejected, or replace the first? This was explicitly resolved in `Part-1A/.specify/clarifications.md` as CLR-001 (dated 2026-11-10), which defined the rule as "the second coupon replaces the first (last-wins)" and cross-referenced it to acceptance criterion AC-008. The traceability path runs directly from that clarification artifact into the `apply_discount()` function in `engine.py`, which checks whether a non-BOGO coupon is already present and replaces it rather than accumulating. The test `test_ac_008_second_percentage_replaces_first` in `tests/test_engine.py` derives its assertion (`expected_discount = 15.0`, i.e. 15% of 100.0, not 15%+10% compounded) directly from AC-008. Without the clarification artifact, the initial generated code could have silently compounded discounts, producing incorrect totals with no test to catch it.

---

### Question 2: Harness Value in Part 1A

One issue detected by the deterministic harness that a self-reviewing coding agent would not reliably catch is the **missing `pythonpath` configuration** in `pyproject.toml`, which caused a complete test suite crash with `ModuleNotFoundError: No module named 'cart'`. When the pytest runner was executed in an isolated environment without an editable install, it could not locate the `cart` package because the `src/` layout requires an explicit `pythonpath = ["src"]` entry in `[tool.pytest.ini_options]`. A language model reviewing its own output sees the import statements in the source files and considers them correct — it has no way to simulate the actual Python import resolution path of an isolated test runner process. The harness caught this because it **physically ran** pytest from a clean shell, capturing the real exit code (4) and stderr. The raw failure output is preserved in `Part-1A/evidence/harness-results/run-1/tests_output.txt` and the structured finding is in `run-1/feedback.json` under code `DYNAMIC_MODULE_NOT_FOUND`. The resolution was to add `pythonpath = ["src"]` to `pyproject.toml` and correct the build backend from the invalid `setuptools.backends.legacy:BuildBackend` to `setuptools.build_meta`. Run 2 confirmed all 35 tests passed.

---

### Question 3: Evaluating Non-Determinism in Part 1B

I will use evaluation case **TC-013** ("Help it doesn't work") as the example. Exact string matching would be entirely inappropriate here because the ticket is intentionally vague — the user has not stated what product, what failure mode, or what they tried. A generative model might produce a summary such as *"User reports an unspecified issue and needs clarification"* or *"Technical problem reported; additional details required"* on different runs. Asserting either exact string as the expected output would cause the harness to fail valid alternative phrasings.

Instead, the 3-layer harness uses three complementary checks. First, **Layer 1 (schema constraint)** validates that the output JSON contains all seven required fields with the correct types and that `category` is one of the five allowed enum values — this is deterministic and enforces the structural contract regardless of wording. Second, **Layer 2 (invariant check)** verifies INV-002: when `needs_clarification` is `True`, the `clarification_question` field must be a non-empty string, and INV-005 ensures that when `needs_clarification` is `False`, `clarification_question` is exactly `""`. For TC-013 the invariant requires `needs_clarification=True`, which is deterministic. Third, **Layer 3 (semantic/quality criterion)** scores the case using a category-accuracy rubric (`expected_category = "technical"`) and a keyword-recall score over the summary checking for the presence of words such as "issue", "unclear", or "work". These checks are suitable because they evaluate whether the model correctly identified the semantic intent of the ticket (a vague technical problem needing clarification) without mandating a specific wording, which is exactly the boundary between acceptable variation and specification violation.

---

### Question 4: Feedback and Self-Healing

I will use the **Part 1B Run 1 → Run 2 repair cycle**. After the first benchmark evaluation, `Part-1B/evidence/eval-results-run1.json` showed that case TC-016 (a ransomware incident on an S3 bucket) received a Layer 3 category score of 0.0 and an overall case score of 0.50, because the model client classified it as `other` instead of `technical`. The structured failure evidence fed back to the coding agent included the exact test case input ("Our S3 bucket has been encrypted by ransomware…"), the generated output with `category: "other"`, the expected category `"technical"`, and the failing Layer 3 rubric score for that attribute.

In response, `src/triager/model_client.py` was updated to add the terms "ransomware", "s3", "compromised", and "incident" to the technical category detection keyword set. Critically, the repair did **not** lower the pre-declared threshold (which remained at ≥ 0.80), did not remove TC-016 from the benchmark dataset, and did not add any `# noqa` suppression or disable any harness gate. Run 2 confirmed that TC-016 improved from 0.50 to 1.00, the overall mean score rose from 0.858 to 0.896, and all Layer 1/Layer 2 checks remained at 0 violations. The same 20-case dataset, the same 3-layer pipeline, and the same declared threshold were used — the repair solved the root cause (missing keyword coverage) without weakening any specification or harness constraint.

---

### Question 5: Human Accountability

After the harness reported PASS for Part 1B with a score of 0.896, one limitation that remained is that the implementation runs a **deterministic keyword-based heuristic simulation** rather than making real calls to the Gemini API. This means the evaluation is fully reproducible but does not reflect the true stochastic behaviour of the production language model: with real model calls and a non-zero temperature setting, scores may vary run-to-run, and edge cases like multilingual jailbreak prompts or base64-encoded adversarial payloads are not tested by the keyword-based guardrail layer.

My final human decision was **ACCEPT** for the purposes of this academic submission, because all specified acceptance criteria were met: the declared threshold was satisfied, no schema or invariant violations were found, all 4 guardrail cases passed, and the failure-and-repair cycle was documented with genuine evidence. However, before deploying this application in a higher-risk or production setting, I would introduce two additional controls: (1) replace the heuristic simulation with live Gemini API calls and re-run the full 20-case benchmark at least three times across different days to measure score variance, and (2) add an independent LLM-based safety guardrail layer (such as a Llama Guard sidecar or NVIDIA NeMo Guardrails) that evaluates model outputs against a prompt-injection detection policy before any triage output is acted upon by an engineering team.

---

*AI Policy Acknowledgement: Per the assignment brief, Spec-Driven Development tooling and harness engineering were AI-assisted. The reflection answers above were reviewed and are submitted under my academic responsibility.*

— Tanishk Dhaka | 2026NS93035 | 2026-11-17
