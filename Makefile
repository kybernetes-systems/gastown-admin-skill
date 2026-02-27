.PHONY: all package validate clean

SKILL_DIR := gas-town-admin
SKILL_PKG := gas-town-admin.skill

all: package

package: $(SKILL_PKG)

$(SKILL_PKG): $(shell find $(SKILL_DIR) -type f)
	zip -r $@ $(SKILL_DIR)/

validate:
	agentskills validate ./$(SKILL_DIR)

clean:
	rm -f $(SKILL_PKG)
