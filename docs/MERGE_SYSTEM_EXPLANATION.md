# ET605 Merge System Explanation

## 1. Purpose of this document

This document explains, in simple language, how the ET605 Merge System works:

- what student parameters we collect
- why those parameters were chosen
- how each value is calculated
- how the final payload is delivered
- how the score is normalized
- how the recommendation engine decides the next chapter

This is the easiest document to use while presenting the project in class or in a Meet call.

---

## 2. What our system is trying to do

The platform has many chapter modules. Each module teaches one chapter, such as Fractions or Linear Equations.

When a student finishes a chapter, or leaves it midway, the chapter module sends one final API payload to the Merge System.

The Merge System then:

1. validates the payload
2. stores the student session
3. calculates a normalized performance score
4. calculates additional struggle and readiness parameters
5. decides whether the student should:
   - continue the same chapter
   - go to a prerequisite chapter
   - advance to the next chapter

---

## 3. Dummy math chapters used in the demo

For the demo, we use 4 manually editable mathematics chapters:

1. Grade 6 Fractions
2. Grade 7 Ratio and Proportion
3. Grade 7 Algebraic Expressions
4. Grade 8 Linear Equations

Each chapter now has:

- 5 questions
- hints
- difficulty level
- expected completion time
- prerequisite links
- next chapter link

These are editable in:

- `/Users/vansharora665/ET605/seed_data/chapter_catalog.json`

---

## 4. Why we chose these parameters

We wanted the recommendation engine to feel educational, not just technical.

So we selected parameters that represent 3 things:

1. Accuracy
How correctly the student answered.

2. Effort and support needed
How many hints and retries were needed.

3. Learning readiness
How much of the chapter was completed, how much time was spent, and whether the learner was ready to move on.

This makes the decision more realistic than only checking correct answers.

---

## 5. Official payload fields sent by a module team

The final module payload is:

```json
{
  "schema_version": "1.0",
  "student_id": "student_01",
  "session_id": "play_student_01_grade8_linear_equations_ab12cd34",
  "chapter_id": "grade8_linear_equations",
  "timestamp": "2026-03-31T18:23:24.406644Z",
  "session_status": "completed",
  "correct_answers": 4,
  "wrong_answers": 1,
  "questions_attempted": 5,
  "total_questions": 5,
  "hints_used": 1,
  "total_hints_embedded": 5,
  "retry_count": 1,
  "time_spent_seconds": 324,
  "topic_completion_ratio": 1.0,
  "chapter_difficulty_level": "hard",
  "expected_completion_time_seconds": 1200,
  "prerequisite_chapter_ids": [
    "grade7_algebraic_expressions",
    "grade7_ratio_and_proportion"
  ],
  "subtopic_metrics": []
}
```

### Why each field exists

`student_id`
- identifies the learner

`session_id`
- makes the API idempotent
- the same session can be safely retried without creating duplicate records

`chapter_id`
- identifies which chapter the student worked on

`timestamp`
- stores when the session ended or exited

`session_status`
- tells us whether the student completed the chapter or exited midway

`correct_answers`
- measures mastery

`wrong_answers`
- measures difficulty faced by the learner

`questions_attempted`
- tells us how much of the activity was actually attempted

`total_questions`
- gives the full size of the chapter assessment

`hints_used`
- shows how much support the learner needed

`total_hints_embedded`
- gives context for hints used
- for example, 2 hints used out of 2 is very different from 2 hints used out of 10

`retry_count`
- captures how many extra tries were needed

`time_spent_seconds`
- captures real elapsed time from session start to session end or exit

`topic_completion_ratio`
- shows how much of the chapter was actually covered
- this stays between `0` and `1`

`chapter_difficulty_level`
- gives an easy-to-read category for presentation
- values used are `easy`, `mid`, or `hard`

`expected_completion_time_seconds`
- sends the target completion time with the payload
- this is used in time-based evaluation

`prerequisite_chapter_ids`
- sends the required foundation chapters for the current topic
- this helps explain why prerequisite revision may be recommended

`subtopic_metrics`
- lets us identify weak areas inside a chapter
- for example, “Solving Multi-Step Equations” may be weak even if the full chapter score is average

---

## 6. How the browser demo creates the payload

The student flow in the UI now works like this:

1. the student selects a chapter
2. a new `session_id` is created
3. the timer does not start immediately
4. the timer starts on the first real learner action:
   - selecting an option
   - opening a hint
   - using a preset
5. every answer selection counts as an attempt immediately
6. changing an answer again counts as a retry
7. when the learner clicks `End Chapter`, the module sends a final `completed` or `exited_midway` session payload

### Special session cases

If the student closes the tab:
- the app uses a background exit delivery
- it sends or queues a `/demo/session/exit` payload

If the network disconnects:
- the app stores the exit payload locally
- when the connection returns, it retries automatically

This makes the demo much more realistic for real platform behavior.

---

## 7. Validation rules

Before scoring, the Merge System validates the payload.

Main rules:

- `correct_answers + wrong_answers <= questions_attempted`
- `correct_answers + wrong_answers <= total_questions`
- `questions_attempted <= total_questions`
- `hints_used <= total_hints_embedded`
- all count fields must be non-negative
- `topic_completion_ratio` must be between `0` and `1`
- unknown JSON keys are rejected

Why this matters:

- it stops fake or broken payloads
- it avoids random default values
- it keeps scoring mathematically safe

---

## 8. Core scoring parameters

The default scoring profile is `revised_spec`.

We calculate these 8 core components:

### 8.1 Mastery Ratio

```text
mastery_ratio = correct_answers / total_questions
```

Meaning:
- how much of the full chapter was answered correctly
- this avoids giving a very high score for only 1 correct answer out of 5 total questions

### 8.2 Attempt Coverage

```text
attempt_coverage = questions_attempted / total_questions
```

Meaning:
- how much of the chapter the student actually attempted

### 8.3 Hint Independence

```text
hint_independence = 1 - (hints_used / total_hints_embedded)
```

Meaning:
- a higher value means the student needed fewer hints

### 8.4 Retry Resilience

```text
retry_resilience = 1 - (retry_count / questions_attempted)
```

Meaning:
- a higher value means the student solved with fewer retries

### 8.5 Time Efficiency

```text
time_efficiency = expected_completion_time / time_spent_seconds
```

Then we cap it at `1.0`.

Meaning:
- if the student finishes within expected time, this value is strong
- if the student takes much longer, this value drops

### 8.6 Completion Ratio

```text
completion_ratio = topic_completion_ratio
```

Meaning:
- how much of the chapter session was actually completed

### 8.7 Difficulty Progress

```text
difficulty_progress = attempt_coverage x (1 - 0.5 x difficulty_factor)
```

Meaning:
- this uses the chapter difficulty in the score
- low coverage in a hard chapter should not look highly successful

### 8.8 Prerequisite Readiness

```text
prerequisite_readiness = completion_ratio x (1 - 0.5 x prerequisite_factor)
```

Where:

```text
prerequisite_factor = min(number_of_prerequisites / 3, 1)
```

Meaning:
- chapters that depend on more prerequisite knowledge are harder to promote from when the student has not completed enough work

---

## 9. Final score formula

Default `revised_spec` weights:

```text
score =
0.30 * mastery_ratio +
0.20 * attempt_coverage +
0.10 * hint_independence +
0.10 * retry_resilience +
0.10 * time_efficiency +
0.10 * completion_ratio +
0.05 * difficulty_progress +
0.05 * prerequisite_readiness
```

The output is always between `0` and `1`.

---

## 10. How normalization works

This is one of the most important ideas in the project.

Our rule is:

1. keep the standard base weights fixed whenever the official source fields are present
2. do not treat a valid calculated value as "missing"
3. only renormalize if a raw source field is actually missing or null

So in the demo, because the official fields are normally present, the weights remain consistent across sessions.

Sometimes a payload may not have every metric.

Example:
- maybe `hints_used` is missing
- maybe the student exited early and no meaningful `time_efficiency` should be used

Instead of breaking the score, we do this:

1. compute every component that can be calculated from the raw payload
2. keep the standard base weights if those fields are present
3. only when a raw field is truly missing, exclude that component
4. renormalize the remaining weights so they add up to `1.0`
5. calculate the final score using the available components

### Normalization formula

```text
normalized_score = sum(component_value x normalized_weight)
```

### Example

Suppose only these components are available:

- mastery_ratio = 0.80
- attempt_coverage = 1.00
- retry_resilience = 0.60
- completion_ratio = 1.00

Original weights:

- mastery_ratio = 0.30
- attempt_coverage = 0.20
- retry_resilience = 0.10
- completion_ratio = 0.10

Total available weight:

```text
0.30 + 0.20 + 0.10 + 0.10 = 0.70
```

Renormalized weights:

- mastery_ratio = `0.30 / 0.70 = 0.4286`
- attempt_coverage = `0.20 / 0.70 = 0.2857`
- retry_resilience = `0.10 / 0.70 = 0.1429`
- completion_ratio = `0.10 / 0.70 = 0.1429`

Final normalized score:

```text
(0.80 x 0.4286) + (1.00 x 0.2857) + (0.60 x 0.1429) + (1.00 x 0.1429)
= 0.8572
```

This keeps scoring fair even when some data is unavailable.

---

## 11. Derived recommendation parameters

After the main score is computed, the Merge System derives extra parameters to make the recommendation more intelligent.

These are not extra fields that modules must send.
They are calculated by the Merge System from the official payload.

### 11.1 Accuracy

```text
accuracy = correct_answers / questions_attempted
```

### 11.2 Hint Dependency

```text
hint_dependency = hints_used / total_hints_embedded
```

Higher means more dependence on hints.

### 11.3 Retry Pressure

```text
retry_pressure = retry_count / questions_attempted
```

Higher means the learner needed more repeat attempts.

### 11.4 Time Efficiency

```text
time_efficiency = expected_completion_time / time_spent_seconds
```

### 11.5 Time Pressure

```text
time_pressure = 1 - time_efficiency
```

Higher means more timing struggle.

### 11.6 Completion Strength

```text
completion_strength = topic_completion_ratio
```

### 11.7 Completion Gap

```text
completion_gap = 1 - completion_strength
```

Higher means the learner left more of the chapter incomplete.

### 11.8 Difficulty Factor

```text
difficulty_factor = chapter.difficulty
```

This comes from chapter metadata and stays between `0` and `1`.

### 11.9 Weak Subtopic Ratio

```text
weak_subtopic_ratio = weak_subtopics_found / total_subtopics_in_chapter
```

This measures how much of the chapter looked weak internally.

### 11.10 Score Gap

```text
score_gap = 1 - performance_score
```

Higher means the learner is farther from mastery.

---

## 12. Struggle Index

The `struggle_index` combines multiple learning-risk signals into one value.

Formula used in the project:

```text
struggle_index =
weighted_average(
  score_gap            weight 0.30,
  1 - accuracy         weight 0.20,
  hint_dependency      weight 0.10,
  retry_pressure       weight 0.10,
  time_pressure        weight 0.10,
  completion_gap       weight 0.10,
  difficulty_factor    weight 0.10
)
```

Meaning:
- higher `struggle_index` means the learner is struggling more

Why we created it:
- a student may not fail badly on score alone
- but could still show strong struggle patterns through time, retries, hints, and partial completion

---

## 13. Readiness Index

This is the opposite view of the same condition.

```text
readiness_index = 1 - struggle_index
```

Meaning:
- higher readiness means the learner is more ready to move on

---

## 14. Prerequisite Pressure

This adds chapter difficulty into the recommendation pressure.

```text
prerequisite_pressure = struggle_index x max(difficulty_factor, 0.4)
```

Meaning:
- struggling in a harder chapter should increase the chance of prerequisite revision

Why `max(difficulty_factor, 0.4)` was used:
- to avoid very low-difficulty chapters reducing the pressure too much

---

## 15. Weak subtopic calculation

Each subtopic can get a mini-score from:

- subtopic accuracy
- subtopic retry behavior
- subtopic hint behavior

If that subtopic score falls below the threshold, it is marked as weak.

The system can then say:

- overall chapter may be acceptable
- but this particular area is weak

That makes the recommendation more educational and specific.

---

## 16. Decision logic for next chapter

The recommendation engine checks the latest processed student session and then decides one of these outputs:

### `start_path`

If the student has no history:
- start from the first foundation chapter

### `remediation`

If any of these are true:

- `performance_score < threshold`
- `struggle_index >= 0.55`
- `weak_subtopic_ratio >= 0.5`

Then:
- send the learner to a prerequisite chapter

### `continue_current`

If the learner is not ready to advance but is not strongly failing:

- session exited midway
- or completion ratio is low
- or readiness index is still below the promotion level

Then:
- keep the learner on the same chapter

### `advance`

If the learner is ready:
- move to the configured `next_chapter_id`

### `complete_path`

If the learner is already at the end of the dummy path:
- no further chapter is configured

---

## 17. Why exited sessions matter

This was added to make the system realistic.

If the learner closes the tab or the internet disconnects:

- we do not lose the session
- the module sends or retries an `exited_midway` payload
- the admin still sees what happened
- the system can still decide whether the learner should retry or go to a prerequisite

This is important because real learning sessions are often interrupted.

---

## 18. Example 1: strong learner

Suppose:

- correct = 5
- wrong = 0
- attempted = 5
- hints = 0
- retries = 0
- time_spent = 300 seconds
- expected_time = 600 seconds
- completion_ratio = 1.0

Then:

- accuracy = 1.0
- hint_independence = 1.0
- retry_resilience = 1.0
- time_efficiency = 1.0
- completion_ratio = 1.0

Final score:

```text
1.0
```

Likely outcome:

- `advance`

---

## 19. Example 2: struggling learner

Suppose:

- correct = 2
- wrong = 3
- attempted = 5
- hints = 3
- retries = 2
- time_spent = 1400 seconds
- expected_time = 900 seconds
- completion_ratio = 1.0

Then:

- accuracy = `2/5 = 0.40`
- hint_independence = `1 - 3/5 = 0.40`
- retry_resilience = `1 - 2/5 = 0.60`
- time_efficiency = `900/1400 = 0.6429`
- completion_ratio = `1.0`

Final score:

```text
0.45(0.40) + 0.15(0.40) + 0.15(0.60) + 0.15(0.6429) + 0.10(1.0)
= 0.5264
```

Likely outcome:

- `remediation`
- suggest prerequisite chapters

---

## 20. Example 3: exited session

Suppose a learner opens a chapter, struggles, and closes it before answering.

Then:

- `session_status = exited_midway`
- `questions_attempted = 0`
- `topic_completion_ratio = 0.0`

In the refined system:

- such a session is not rewarded
- it is treated as a support case
- the learner is usually kept on the same chapter or sent to a prerequisite depending on context

This is much safer for real learning behavior.

---

## 21. Final payload delivery flow

### Completed chapter flow

```text
Student answers chapter
-> Module prepares final payload
-> POST /demo/session/complete
-> Merge System validates
-> Merge System stores session
-> Score is calculated
-> Recommendation is calculated
-> Admin summary is returned
```

### Exited chapter flow

```text
Student closes tab or loses network
-> Module/browser creates exited-midway payload
-> POST /demo/session/exit
-> If network fails, payload is queued
-> Payload retries automatically later
-> Merge System stores exited session
-> Recommendation still runs
```

---

## 22. Why this design is good for the professor demo

This system is strong for presentation because it shows:

- clear API integration between module teams and the Merge team
- realistic student behavior
- realistic failure handling
- explainable scoring
- explainable recommendation logic
- manually editable chapter progression

So this is not just a static demo.
It behaves like a small working version of a real adaptive learning platform backend.

---

## 23. Most important editable places

If the team wants to change behavior later:

`seed_data/chapter_catalog.json`
- chapters
- subtopics
- difficulty
- expected time
- prerequisites
- next chapter
- question content

`app/services/scoring.py`
- score components
- score weights
- normalization behavior

`app/services/recommendation.py`
- derived parameters
- struggle index formula
- decision thresholds

`app/web/demo_page.py`
- browser session behavior
- timer behavior
- auto-exit delivery logic

---

## 24. One-line summary for presentation

Our Merge System collects one final session payload from each chapter module, validates it, calculates a normalized performance score plus deeper struggle indicators, and then decides whether the student should continue, remediate through prerequisites, or advance to the next chapter.
