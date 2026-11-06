# ============================================================================
# ConformalSpike Automated Build, Benchmark & Verification Pipeline
# Target Venue: IEEE Transactions
# ============================================================================

CC ?= gcc
CFLAGS ?= -O3 -Wall -Wextra -std=c99
PYTHON ?= python3

RESULTS_DIR = results
FIGURES_DIR = figures
PAPER_DIR = paper
FIRMWARE_DIR = firmware
METRICS_JSON = $(RESULTS_DIR)/benchmark_metrics.json
REPORT_MD = $(RESULTS_DIR)/EXPERIMENTAL_RESULTS_REPORT.md

.PHONY: all benchmark benchmark-quick firmware paper audit-anomalies format-results clean help

all: firmware benchmark format-results audit-anomalies

# 1. Compile and execute bare-metal C firmware test harness
firmware: $(FIRMWARE_DIR)/test_mcu
	@echo "=== Running Bare-Metal C Host Test Harness ==="
	./$(FIRMWARE_DIR)/test_mcu

$(FIRMWARE_DIR)/test_mcu: $(FIRMWARE_DIR)/test_mcu.c $(FIRMWARE_DIR)/conformal_spike_mcu.c $(FIRMWARE_DIR)/conformal_spike_mcu.h $(FIRMWARE_DIR)/conformal_spike_weights.h $(FIRMWARE_DIR)/test_vectors.h
	$(CC) $(CFLAGS) $(FIRMWARE_DIR)/test_mcu.c $(FIRMWARE_DIR)/conformal_spike_mcu.c -o $(FIRMWARE_DIR)/test_mcu

# 2. Run Python empirical research pipeline
benchmark:
	@echo "=== Running ConformalSpike Benchmark Pipeline ==="
	$(PYTHON) -m src.main --output-dir $(RESULTS_DIR)

benchmark-quick:
	@echo "=== Running ConformalSpike Quick Benchmark (Seed 42) ==="
	$(PYTHON) -m src.main --single-seed 42 --output-dir $(RESULTS_DIR)

# 3. Format JSON metrics and verify schemas
format-results:
	@echo "=== Formatting Benchmark JSON Results ==="
	@if [ -f "$(METRICS_JSON)" ]; then \
		$(PYTHON) -m json.tool "$(METRICS_JSON)" > "$(RESULTS_DIR)/benchmark_metrics_formatted.json" && \
		mv "$(RESULTS_DIR)/benchmark_metrics_formatted.json" "$(METRICS_JSON)"; \
		echo "Formatted $(METRICS_JSON) successfully."; \
	else \
		echo "Error: $(METRICS_JSON) not found. Run 'make benchmark' first."; exit 1; \
	fi

# 4. Automated anomaly detection and integrity audit
audit-anomalies:
	@echo "=== Running Rigorous Anomaly Detection on Benchmark Results ==="
	$(PYTHON) -m src.audit

# 5. Compile LaTeX Paper (optional target if paper/ is present)
paper:
	@if [ -d "$(PAPER_DIR)" ]; then \
		echo "=== Compiling LaTeX Manuscript ==="; \
		cd $(PAPER_DIR) && pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex; \
		echo "Successfully compiled $(PAPER_DIR)/main.pdf"; \
	else \
		echo "Notice: $(PAPER_DIR)/ directory is gitignored/not present."; \
	fi
	@echo "Successfully compiled $(PAPER_DIR)/main.pdf"

clean:
	rm -f $(FIRMWARE_DIR)/test_mcu
	rm -rf __pycache__ src/__pycache__ firmware/__pycache__
	cd $(PAPER_DIR) && rm -f *.aux *.bbl *.blg *.log *.out
	@echo "Cleaned build artifacts."

help:
	@echo "ConformalSpike Makefile Targets:"
	@echo "  make all              : Run firmware, benchmark, format results, check anomalies, build paper"
	@echo "  make firmware         : Compile and run C test harness"
	@echo "  make benchmark        : Run modular Python benchmark pipeline (src.main) -> results/"
	@echo "  make benchmark-quick  : Run quick single-seed (42) benchmark pipeline -> results/"
	@echo "  make format-results   : Pretty-print results/benchmark_metrics.json"
	@echo "  make audit-anomalies  : Run rigorous anomaly detector on benchmark output"
	@echo "  make paper            : Compile IEEE Transactions manuscript"
	@echo "  make clean            : Remove temporary build files and caches"
