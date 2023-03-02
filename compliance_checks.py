from abc import ABC, abstractmethod

import markdown
from bs4 import BeautifulSoup, Comment


class ComplianceCheck(ABC):
    @abstractmethod
    def run_check(self, card: BeautifulSoup) -> bool:
        raise NotImplementedError


class ModelProviderIdentityCheck(ComplianceCheck):
    def run_check(self, card: BeautifulSoup):
        try:
            model_description = card.find("h3", string="Model Description")
            description_list = model_description.find_next_siblings()[0]
            developer = description_list.find(string="Developed by:").parent.next_sibling.strip()

            if developer == "[More Information Needed]":
                return False, None

            return True, developer
        except AttributeError:
            return False, None


def walk_to_next_heading(card, heading, heading_text):
    try:
        heading_node = card.find(heading, string=heading_text)

        content = ""

        sibling_gen = heading_node.nextSiblingGenerator()
        sibling = next(sibling_gen)

        while not (sibling.name is not None and sibling.name.startswith("h")) or sibling.name is None:
            if not isinstance(sibling, Comment):
                content = content + sibling.text.strip()
            sibling = next(sibling_gen)

        if content.strip() == "[More Information Needed]":
            return False, None

        return True, content
    except AttributeError:
        return False, None


class IntendedPurposeCheck(ComplianceCheck):
    def run_check(self, card: BeautifulSoup):
        direct_use_check, direct_use_content = walk_to_next_heading(card, "h3", "Direct Use")
        downstream_use_check, downstream_use_content = walk_to_next_heading(card, "h3", "Downstream Use [optional]")
        out_of_scope_use_check, out_of_scope_use_content = walk_to_next_heading(card, "h3", "Out-of-Scope Use")
        return (
            direct_use_check and out_of_scope_use_check,
            [direct_use_content, downstream_use_content, out_of_scope_use_content]
        )


class ComplianceSuite:
    def __init__(self, checks):
        self.checks = checks

    def run(self, model_card):
        model_card_html = markdown.markdown(model_card)
        card_soup = BeautifulSoup(model_card_html, features="html.parser")

        return [c.run_check(card_soup) for c in self.checks]
