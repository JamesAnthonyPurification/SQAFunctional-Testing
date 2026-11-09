# SQAFunctional-Testing (Student ID: 2507227)

![CI](https://github.com/JamesAnthonyPurification/SQAFunctional-Testing/actions/workflows/ci.yml/badge.svg)

- **Student Name:** James Anthony Purification
- **Email:** japurification16@gmail.com
- **Student ID:** 2507227
- **Course:** Software Quality Assurance (SQA) & Testing

Automated functional testing suite (195 tests, 100% statement and branch coverage), Flask interactive playground, multi-version GitHub Actions CI/CD workflow, and gated Render cloud deployment with post-deploy smoke verification for `target.py` (16 functions: 11 data-type operations and 5 mathematical routines).

- **Repository URL:** https://github.com/JamesAnthonyPurification/SQAFunctional-Testing
- **Live URL:** https://sqafunctional-testing-2507227.onrender.com
- **Health Endpoint:** https://sqafunctional-testing-2507227.onrender.com/health (returns the deployed commit SHA)

## Local Setup

```bash
git clone https://github.com/JamesAnthonyPurification/SQAFunctional-Testing.git
cd SQAFunctional-Testing
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Executing the Test Suite

```bash
pytest tests/test_target.py --cov=target --cov-branch --cov-report=term-missing --cov-fail-under=100
```

- **Target Coverage:** 195 unit tests achieving **100% line and branch coverage** on `target.py`.
- **Frontend & API Tests:** `pytest tests/test_app.py`
- **Static Analysis / Linter:** `ruff check .`

## Running the Flask Frontend Locally

```bash
python app.py        # Open http://localhost:5000
```

Each of the 16 functions is rendered as an interactive card via `inspect`: enter Python literals (`18`, `None`, `[1, 2]`, `{1, 2}`, `{"apple": 0.75}`) and click **Execute** to inspect the return value, data type, or raised exception.

## CI/CD Pipeline Architecture (`.github/workflows/ci.yml`)

1. **`test` Job**: Triggered on every push and pull request targeting `main` across a Python 3.10, 3.11, and 3.12 matrix with pip caching. Runs `ruff check .`, executes `pytest tests/test_target.py` enforcing `--cov-fail-under=100`, runs `pytest tests/test_app.py`, and uploads `coverage.xml` and `htmlcov/` artifacts.
2. **`deploy` Job** (`needs: test`): Restricted to pushes on `refs/heads/main`. Triggers the Render deploy hook (`RENDER_DEPLOY_HOOK` secret) pinned to `GITHUB_SHA`. Auto-deploy is disabled on Render (`autoDeploy: false`), ensuring broken builds never reach production.
3. **`smoke-test` Job** (`needs: deploy`): Polls `/health` every 10 seconds until the live `sha` matches `GITHUB_SHA`, then validates three live HTTP assertions (home page rendering, valid POST to `/api/run/is_adult`, and `ZeroDivisionError` handling on `/api/run/divide`).

## Branch Governance & Protection

`main` is protected via GitHub branch protection rules: changes must be proposed via feature-branch Pull Requests and require the `test` matrix (Python 3.10, 3.11, 3.12) to pass before merging.

## Documented Edge Cases & Suspected Bugs in `target.py`

1. **`greet`**: Passing a non-string argument (e.g., `greet(2507227)`) raises `AttributeError` (`'int' object has no attribute 'strip'`) rather than an explicit `TypeError` as enforced in `count_vowels` and `invert`.
2. **`factorial`**: Passing a floating-point number (e.g., `factorial(3.5)` or even `factorial(5.0)`) raises a low-level `TypeError` from `range()` due to missing explicit integer type validation.
3. **`is_adult`**: Accepts boolean values (`is_adult(True)` evaluates to `False`) because `bool` subclasses `int` in Python (`True == 1`, `False == 0`). Non-numeric inputs raise a generic `TypeError` during `<` comparison.
4. **`is_leap_year`**: Suffers from the same `bool`-as-`int` inheritance issue (`is_leap_year(True)` evaluates year `1` and returns `False`), and applies proleptic Gregorian rules to years prior to 1582.
5. **`find_max` / `average`**: Boolean elements inside collections are treated as `1` and `0` (`average([True, False])` returns `0.5`), and non-iterable inputs such as `None` raise an uninformative `TypeError` from `len()`.
6. **`swap`**: Accepts any sequence of length 2 (including lists like `[5, 6]` or 2-character strings like `"jp"`), not strictly `tuple` instances.
7. **`common_items`**: Lacks input type guards; passing lists raises a `TypeError` from the bitwise `&` operator, while mixing a `set` and `frozenset` returns whichever type appears as the left operand.
8. **`celsius_to_fahrenheit`**: Does not validate against physically impossible temperatures below absolute zero (`-273.15 °C`).
9. **`to_int`**: Raises an undocumented `ValueError` for numeric float strings like `to_int("3.5")` and `OverflowError` for `to_int(float("inf"))`.
10. **`divide`**: Silently propagates IEEE 754 `NaN` values (`divide(float("nan"), 1)` returns `nan` without raising an error).

## Project Structure

```text
target.py                        # 16 core functions under test
tests/test_target.py             # 195 functional & boundary tests (100% line/branch coverage)
tests/test_app.py                # Flask UI & JSON API unit tests
app.py, templates/index.html     # Flask web playground + /health SHA endpoint
.github/workflows/ci.yml         # 3-stage CI/CD pipeline (test -> deploy -> smoke-test)
.github/pull_request_template.md # PR verification checklist
render.yaml                      # Render blueprint configuration (autoDeploy: false)
requirements.txt                 # Pinned dependencies
ruff.toml, pytest.ini            # Linter and test runner configurations
```
