ADR_NAME ?=
adr:
	$(MAKE) -C ops adr ADR_NAME="$(ADR_NAME)"