KEYMAP ?= quique
CONVERTER ?= promicro_rp2040
BACKUP ?= firmware/keymaps/$(KEYMAP)/via-backup.json
IMAGES ?= docs/layers

.DEFAULT_GOAL := help
.PHONY: help install test run backup restore keymap images firmware flash

help: ## List the available commands
	@awk 'BEGIN {FS = ":.*## "} /^[a-z]+:.*## / {printf "  make %-10s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo
	@echo "  Variables: KEYMAP=$(KEYMAP) CONVERTER=$(CONVERTER) BACKUP=$(BACKUP) IMAGES=$(IMAGES)"

install: ## Install the top bar app (asks for sudo)
	./install.sh

test: ## Run the tests
	uv run pytest

run: ## Run the top bar app from the source tree
	uv run ferris-layer

backup: ## Save the keyboard's VIA keymap and macros to BACKUP
	uv run ferris-via-backup save $(BACKUP)

restore: ## Write BACKUP back to the keyboard
	uv run ferris-via-backup restore $(BACKUP)

keymap: ## Generate the QMK keymap.c of KEYMAP from BACKUP
	uv run ferris-via-backup keymap $(BACKUP) > firmware/keymaps/$(KEYMAP)/keymap.c

images: ## Draw every layer of BACKUP as SVG images in IMAGES
	uv run ferris-via-backup images $(BACKUP) $(IMAGES)

firmware: ## Build the firmware of KEYMAP for CONVERTER with Docker
	firmware/build.sh $(KEYMAP) $(CONVERTER)

flash: ## Wait for a half in bootloader mode and copy the firmware to it
	firmware/flash.sh
