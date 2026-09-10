# Quiz validation

Checked on 10 September 2026.

## Content

- The old question bank was removed.
- Two SSI practice tabs contain 150 questions each.
- Each tab has 10 categories with exactly 15 questions per category.
- Tab 1 mixes concepts, practical decisions, and calculations.
- Tab 2 contains 130 practical scenarios, 15 calculations, and 5 concept questions.
- Every question has four distinct choices, one answer key, an explanation, a question type, and an SSI source link.
- The bank contains 300 unique question stems and unique IDs.
- Project questions cover the SSI examination, Passing Certificate, real or simulated project routes, VIVA, documents, savings requirement, professional registration, and CPD.
- The questions are original practice items. They are not official examination questions.

## Application checks

Run from this folder:

    python3 build-bank.py
    node check-quiz.mjs

The build writes fixed question data into question-bank.json and embeds the same data into index.html and dist/index.html. The quiz works without network access. It uses source links only when an explanation is opened.

The checks cover:

- Matching source and distribution HTML files.
- Two 150-question tabs.
- Ten categories with 15 questions in each tab.
- Unique question IDs and stems.
- Four distinct choices and valid answer keys.
- SSI source fields and question types.
- Independently checked sample calculation keys.
- Answer entry, grading, reset, random order, keyboard tab selection, and category headings.
- Separate answers and timers for each tab.
- Timer pause and resume for focus, visibility, page close, freeze, and reload.
- Browser-storage failure and invalid saved-time handling.

SSI requirements can change. The question explanations link to the SSI pages used for this bank; candidates should confirm requirements for their course cohort.
