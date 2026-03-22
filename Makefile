.PHONY: create-pull-request generate validate-file validate-lines validate-tokens validate-description validate test help

SKILLS_DIR := .agents/skills
SKILL_TEMPLATE := SKILLS.template.md

create-pull-request: ## Create a pull request for the skill. Usage: make create-pr name=<name>
	@test -n "$(name)" || (echo "ERROR: name is required." && exit 1)
	
	git checkout -b mario/$(name)
	git push -u origin mario/$(name)
	gh pr create --title "Add skill $(name)" --body "This PR adds the skill $(name) to the library."
	git checkout main

generate: ## Generate a new skill from the template. Usage: make generate name=<name>
	@test -n "$(name)" || (echo "ERROR: name is required." && exit 1)
	
	mkdir -p $(SKILLS_DIR)/$(name)

	cat $(SKILL_TEMPLATE) \
	| sed "s/<name>/$(name)/g" \
	> $(SKILLS_DIR)/$(name)/SKILLS.md

	@echo "Skill $(name) generated successfully."

validate-file: ## Check that file= is set and exists. Used as a dependency by validate-* targets.
	@test -n "$(file)" || (echo "ERROR: file is required." && exit 1)
	@test -f "$(file)" || (echo "ERROR: file '$(file)' not found." && exit 1)

validate-lines: validate-file ## Fail if the skill file exceeds 500 lines. Usage: make validate-lines file=<path>
	@lines=$$(wc -l < "$(file)"); \
	if [ "$$lines" -gt 500 ]; then \
		echo "ERROR: '$(file)' has $$lines lines (max 500)."; \
		exit 1; \
	fi

validate-tokens: validate-file ## Fail if the skill file exceeds 5000 tokens (estimated as chars / 4). Usage: make validate-tokens file=<path>
	@chars=$$(wc -c < "$(file)"); \
	tokens=$$((chars / 4)); \
	if [ "$$tokens" -gt 5000 ]; then \
		echo "ERROR: '$(file)' has ~$$tokens tokens (max 5000)."; \
		exit 1; \
	fi

validate-description: validate-file ## Fail if the description field exceeds 1024 characters. Usage: make validate-description file=<path>
	@description=$$(grep -oE 'description: .+' "$(file)" | sed 's/description: //'); \
	if [ "$$(echo "$$description" | wc -c)" -gt 1024 ]; then \
		echo "ERROR: description is too long. Please keep it under 1024 characters."; \
		exit 1; \
	fi

validate: validate-lines validate-tokens validate-description ## Run all validations against a skill file. Usage: make validate file=<path>

test: ## Run the test suites for the Makefile.
	@python3 tests/test_Makefile.py

help: ## Show this help message.
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) \
	| sed 's/: .*## /\t/' \
	| awk -F'\t' '{ printf "  %-24s %s\n", $$1, $$2 }'
