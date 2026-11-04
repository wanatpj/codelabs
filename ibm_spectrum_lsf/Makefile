.DEFAULT_GOAL := job

POETRY ?= poetry
LSF_INSTALL_DIR ?= /tmp/lsf-installer
LSF_INSTALL_CONFIG ?= install.config

setup:
	$(POETRY) install
	$(MAKE) -C job

install-lsf:
	@test -n "$(LSF_INSTALL_DIR)" || { echo "Set LSF_INSTALL_DIR to the extracted IBM LSF installer directory." >&2; exit 1; }
	@test -x "$(LSF_INSTALL_DIR)/lsfinstall" || { echo "Cannot find executable lsfinstall in $(LSF_INSTALL_DIR)." >&2; exit 1; }
	@test -f "$(LSF_INSTALL_DIR)/$(LSF_INSTALL_CONFIG)" || { echo "Cannot find $(LSF_INSTALL_CONFIG) in $(LSF_INSTALL_DIR)." >&2; exit 1; }
	cd "$(LSF_INSTALL_DIR)" && sudo ./lsfinstall -f "$(LSF_INSTALL_CONFIG)"

job:
	$(MAKE) -C job

check: job
	$(POETRY) run mypy
	$(POETRY) run python -m unittest discover -s tests -v

clean:
	$(MAKE) -C job clean

.PHONY: setup install-lsf job check clean
