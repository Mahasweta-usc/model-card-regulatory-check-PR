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


class IntendedPurposeCheck(ComplianceCheck):
    def run_check(self, card: BeautifulSoup):
        try:
            direct_use = card.find("h3", string="Direct Use")

            direct_use_content = ""

            sibling_gen = direct_use.nextSiblingGenerator()
            sibling = next(sibling_gen)

            while sibling.name != "h3":
                if not isinstance(sibling, Comment):
                    direct_use_content = direct_use_content + sibling.text
                sibling = next(sibling_gen)

            if direct_use_content.strip() == "[More Information Needed]":
                return False, None

            return True, None
        except AttributeError:
            return False, None


class ComplianceSuite:
    def __init__(self, checks):
        self.checks = checks

    def run(self, model_card):
        model_card_html = markdown.markdown(model_card)
        card_soup = BeautifulSoup(model_card_html, features="html.parser")

        return [c.run_check(card_soup) for c in self.checks]
