"""Master test runner — orchestrates all evals and aggregates results into RESULTS.md.

Usage (from sentio-api/):
    python scripts/run_all_evals.py                    # RAG + bias evals
    python scripts/run_all_evals.py --with-locust      # + load testing (60s)
    python scripts/run_all_evals.py --quick            # RAG only (skip bias)

Env requirements (from .env):
    SUPABASE_URL, SUPABASE_SERVICE_KEY (RAG + bias)
    ANTHROPIC_API_KEY (bias classifier)
    COHERE_API_KEY (optional, RAG rerank)

Output:
    - Updates RESULTS.md with metrics + timestamps
    - Saves JSON outputs: scripts/rag_eval_results.json, scripts/bias_eval_results.json
    - Console summary of all metrics

For QLoRA training, use:
    sentio-ml/notebooks/sentio_bias_qlora.ipynb on Kaggle T4 (manually, separate)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Path setup ─────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str) -> None:
    """Print a bold blue header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def print_ok(text: str) -> None:
    """Print green success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_err(text: str) -> None:
    """Print red error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_info(text: str) -> None:
    """Print yellow info message."""
    print(f"{Colors.YELLOW}ℹ {text}{Colors.RESET}")


def check_env_vars(required: list[str]) -> bool:
    """Check if required env vars are set. Return True if all present."""
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        print_err(f"Missing env vars: {', '.join(missing)}")
        return False
    return True


def run_command(cmd: list[str], description: str) -> tuple[bool, str]:
    """Run a command and return (success, output_text)."""
    print_info(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 min timeout
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            print_ok(f"{description} completed successfully")
            return True, output
        else:
            print_err(f"{description} failed with return code {result.returncode}")
            print(output)
            return False, output
    except subprocess.TimeoutExpired:
        print_err(f"{description} timed out after 10 minutes")
        return False, ""
    except Exception as e:
        print_err(f"{description} error: {e}")
        return False, str(e)


def run_rag_eval(quick: bool = False) -> dict | None:
    """Run RAG eval and return parsed results."""
    print_header("RAG Eval (Precision@3 + MRR)")

    if not check_env_vars(["SUPABASE_URL", "SUPABASE_SERVICE_KEY"]):
        print_err("Cannot run RAG eval without Supabase credentials")
        return None

    cmd = ["python", "scripts/eval_rag.py"]
    if quick:
        cmd.append("--no-rerank")

    success, output = run_command(cmd, "RAG eval")

    if success and Path("scripts/rag_eval_results.json").exists():
        try:
            with open("scripts/rag_eval_results.json") as f:
                results = json.load(f)
            print_ok(f"RAG results saved to scripts/rag_eval_results.json")
            return results
        except Exception as e:
            print_err(f"Failed to parse RAG results JSON: {e}")
    return None


def run_bias_eval() -> dict | None:
    """Run bias classifier eval and return parsed results."""
    print_header("Bias Classifier Eval (30-entry per-class F1)")

    if not check_env_vars(["ANTHROPIC_API_KEY"]):
        print_err("Cannot run bias eval without Anthropic API key")
        return None

    cmd = ["python", "scripts/eval_bias.py"]
    success, output = run_command(cmd, "Bias eval")

    if success and Path("scripts/bias_eval_results.json").exists():
        try:
            with open("scripts/bias_eval_results.json") as f:
                results = json.load(f)
            print_ok(f"Bias results saved to scripts/bias_eval_results.json")
            return results
        except Exception as e:
            print_err(f"Failed to parse bias results JSON: {e}")
    return None


def run_locust_eval(host: str) -> dict | None:
    """Run Locust load test and return results."""
    print_header("Load Testing (25 users, 60s)")

    print_info(f"Target host: {host}")

    cmd = [
        "locust",
        "-f", "scripts/locustfile.py",
        "--host", host,
        "--users", "25",
        "--spawn-rate", "5",
        "--run-time", "60s",
        "--headless",
        "--csv=scripts/locust_results",
    ]

    success, output = run_command(cmd, "Locust load test")

    if success:
        # Parse locust CSV output
        try:
            # Locust creates locust_results_stats.csv
            stats_file = Path("scripts/locust_results_stats.csv")
            if stats_file.exists():
                # Simple parse: look for 50th and 95th percentile response times
                results = {
                    "tool": "locust",
                    "users": 25,
                    "duration_seconds": 60,
                    "status": "completed",
                }
                print_ok(f"Locust results saved to scripts/locust_results_stats.csv")
                return results
        except Exception as e:
            print_err(f"Failed to parse Locust results: {e}")
    return None


def format_rag_section(results: dict) -> str:
    """Format RAG results for RESULTS.md."""
    if not results:
        return ""

    section = f"""## RAG Eval Results
**Timestamp**: {datetime.now(timezone.utc).isoformat()}

| Metric | Cosine only | + Cohere rerank |
|--------|------------|-----------------|
| Precision@3 (before) | {results.get('precision_before', 'TBD'):.3f} | {results.get('precision_after', 'TBD'):.3f} |
| MRR (before) | {results.get('mrr_before', 'TBD'):.3f} | {results.get('mrr_after', 'TBD'):.3f} |
| Avg rank improvement | — | {results.get('rank_improvement', 'TBD'):.2f}% |

"""
    return section


def format_bias_section(results: dict) -> str:
    """Format bias classifier results for RESULTS.md."""
    if not results:
        return ""

    section = f"""## Bias Classifier Eval Results
**Timestamp**: {datetime.now(timezone.utc).isoformat()}

| Metric | Value |
|--------|-------|
| Macro F1 (30-entry holdout) | {results.get('macro_f1', 'TBD'):.3f} |
| Agreement rate (exact set match) | {results.get('agreement_rate', 'TBD'):.3f} |
| Cost (API calls) | ${results.get('api_cost', 'TBD'):.4f} |

### Per-class F1
"""
    if "per_class_f1" in results:
        for cls, f1 in results["per_class_f1"].items():
            section += f"\n- {cls}: {f1:.3f}"

    section += "\n\n"
    return section


def format_locust_section(results: dict) -> str:
    """Format Locust load test results for RESULTS.md."""
    if not results:
        return ""

    section = f"""## Load Test Results (Locust)
**Timestamp**: {datetime.now(timezone.utc).isoformat()}

**Config**: 25 concurrent users, 60 second duration

| Metric | Value |
|--------|-------|
| P50 response time | TBD ms |
| P95 response time | TBD ms |
| Requests/sec | TBD |
| Error rate | TBD % |

See `scripts/locust_results_stats.csv` for full details.

"""
    return section


def update_results_md(rag: dict | None, bias: dict | None, locust: dict | None) -> None:
    """Update RESULTS.md with all eval results."""
    results_path = Path("../RESULTS.md")

    # Read existing header
    header = """# Sentio — Eval Results

Comprehensive evaluation results for RAG retrieval, bias classification, and system load capacity.
Each section is auto-generated by `scripts/run_all_evals.py`.

---

"""

    # Build sections
    sections = [header]
    if rag:
        sections.append(format_rag_section(rag))
    if bias:
        sections.append(format_bias_section(bias))
    if locust:
        sections.append(format_locust_section(locust))

    # Add footer
    footer = """---

## How to regenerate results

```bash
cd sentio-api

# Run all evals
python scripts/run_all_evals.py

# Or with load testing
python scripts/run_all_evals.py --with-locust https://your-hf-space.hf.space

# For QLoRA training (separate), use:
# sentio-ml/notebooks/sentio_bias_qlora.ipynb on Kaggle T4
```

## Notes

- RAG eval: 52 labeled (query, expected_article) pairs, auto-labeled ground truth (single-relevant assumption)
- Bias eval: 30 entries (2 per class), human-labeled, ~$0.006 API cost
- Load test (if run): 25 concurrent users, 60 seconds, from local machine
- QLoRA: Separate notebook on Kaggle T4, not included in this runner
"""

    sections.append(footer)

    # Write results
    with open(results_path, "w") as f:
        f.write("".join(sections))

    print_ok(f"Updated {results_path}")


def print_summary(rag: dict | None, bias: dict | None, locust: dict | None) -> None:
    """Print a summary table of all results."""
    print_header("SUMMARY")

    summary = []

    if rag:
        precision = rag.get('precision_after', rag.get('precision_before', 'N/A'))
        mrr = rag.get('mrr_after', rag.get('mrr_before', 'N/A'))
        summary.append(f"RAG Precision@3: {precision}")
        summary.append(f"RAG MRR: {mrr}")
    else:
        summary.append("RAG: SKIPPED")

    if bias:
        f1 = bias.get('macro_f1', 'N/A')
        agreement = bias.get('agreement_rate', 'N/A')
        summary.append(f"Bias Classifier F1: {f1}")
        summary.append(f"Bias Agreement: {agreement}")
    else:
        summary.append("Bias: SKIPPED")

    if locust:
        summary.append(f"Load test: 25 users @ {locust.get('duration_seconds', 60)}s — see locust_results_stats.csv")

    for line in summary:
        print_ok(line)

    print_info("Full results written to ../RESULTS.md")


def main():
    """Main runner."""
    parser = argparse.ArgumentParser(
        description="Master test runner for all Sentio evals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_all_evals.py                      # RAG + bias
  python scripts/run_all_evals.py --quick              # RAG only (no rerank)
  python scripts/run_all_evals.py --with-locust https://hf-space.hf.space  # + load test
  python scripts/run_all_evals.py --bias-only          # Bias only
        """,
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Skip Cohere reranking in RAG eval (faster)",
    )
    parser.add_argument(
        "--with-locust",
        nargs="?",
        const="https://mozoj4-sentio-backend.hf.space",
        help="Run Locust load test (default: HF Space backend)",
    )
    parser.add_argument(
        "--bias-only",
        action="store_true",
        help="Run only bias eval (skip RAG)",
    )
    parser.add_argument(
        "--skip-bias",
        action="store_true",
        help="Skip bias eval",
    )

    args = parser.parse_args()

    print_header("Sentio Eval Runner")
    print_info(f"Started at {datetime.now(timezone.utc).isoformat()}")
    print_info(f"Working dir: {os.getcwd()}")

    rag = None
    bias = None
    locust = None

    # Run evals
    if not args.bias_only:
        rag = run_rag_eval(quick=args.quick)

    if not args.skip_bias:
        bias = run_bias_eval()

    if args.with_locust:
        locust = run_locust_eval(args.with_locust)

    # Update RESULTS.md
    update_results_md(rag, bias, locust)

    # Print summary
    print_summary(rag, bias, locust)

    print_info(f"Finished at {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
