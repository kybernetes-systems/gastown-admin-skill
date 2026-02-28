.PHONY: all package validate clean

SKILL_DIR := gastown-admin
SKILL_PKG := gastown-admin.skill

all: package

package: $(SKILL_PKG)

$(SKILL_PKG): $(shell find $(SKILL_DIR) -type f)
	zip -r $@ $(SKILL_DIR)/

validate:
	agentskills validate ./$(SKILL_DIR)

clean:
	rm -f $(SKILL_PKG)
