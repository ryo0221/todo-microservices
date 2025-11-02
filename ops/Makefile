ADR_NAME ?=

.PHONY: adr
adr:
	@test -n "$(ADR_NAME)" || (echo 'Usage: make adr ADR_NAME="kebab-title"'; exit 1)
	@./scripts/new_adr.sh "$(ADR_NAME)"