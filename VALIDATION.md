# Quiz validation

Checked on 10 September 2026.

## Content

- The original 100 question records are unchanged, including answer options and explanations. Their existing saved-answer IDs are retained.
- Five new topic sets contain 150 questions each: 750 new questions and 850 total.
- The new sets contain 150 mathematical question families, with five different data cases in each family. A family is confined to one new tab. These are focused calculation practice sets, not five complete mock exams or 750 unrelated concepts.
- No question text is repeated across the 850 records. The automated check also removes numerical values and checks that new problem templates do not repeat across tabs.
- Each new question has four distinct choices, one answer key, a worked explanation, a reference link, and an IASSC topic code.
- All 750 new numerical keys were checked in a separate calculation pass in `check-quiz.mjs`. The displayed key must also match the result in the explanation.
- New content was checked against the [IASSC Black Belt body of knowledge](https://iassc.org/body-of-knowledge/black-belt-body-of-knowledge/). Acceptance sampling and project scheduling were removed from the draft. Regression is classified under Improve; FMEA under Measure. References explain the methods; the numerical exercises are original.
- [NIST statistical methods](https://www.itl.nist.gov/div898/handbook/) support the statistical formulas. [ASQ Lean resources](https://asq.org/quality-resources/lean) support Lean terminology. ASQ is a supplementary reference, not the exam target.

## Application checks

Run from this folder:

```sh
python3 build-bank.py
node check-quiz.mjs
```

The build writes fixed question data into both HTML files. The quiz works without network access. It does not fetch question data at runtime.

The checks cover:

- HTML JavaScript syntax and matching source/distribution files.
- Question totals, unique IDs, distinct choices, answer calculations, and source/scope fields.
- Retention of old saved answers; separate answers and random order for each set.
- Answer entry, grading, reset, and keyboard tab selection.
- Separate timer values, focus and visibility changes, page close, reload, freezing, resuming, and timer restart.
- No elapsed time is added while the page is closed or hidden.
- Timer restart retains answers; answer reset retains the timer.
- Invalid saved data and unavailable browser storage.

Controller tests use a small DOM/event stand-in and an injected clock. They do not constitute manual tests of every browser's minimize event. The application uses native focus, visibility, and page-lifecycle events. Time is saved every second while running and on pause; an abrupt process kill can lose the fraction of time since the last save. Storage belongs to the browser and site origin. Opening a local file does not migrate progress from a hosted URL.

The existing hosted site was not republished as part of this local HTML edit.
