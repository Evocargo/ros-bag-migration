from .base_rule import BaseRule  # noqa f401
from .examples_rule import ExampleRename, ExampleSplitMsg, ExampleUpdateMsg

rule_list = [ExampleRename, ExampleUpdateMsg, ExampleSplitMsg]
rules = {rule.version(): rule for rule in rule_list}
rule_versions = list(rules.keys())
rule_versions.sort()


def get_rules(bag_version, migrate_version):
    selected_rules = []
    for version in rule_versions:
        if version > bag_version and version <= migrate_version:
            selected_rules.append(rules[version]())

    return selected_rules
