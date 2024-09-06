from abc import ABC, abstractmethod
from typing import Optional, List

import markdown
from bs4 import BeautifulSoup


def walk_to_next_heading(card, heading, heading_text) -> bool:
    stop_at = [heading, f"h{int(heading[1]) - 1}"]

    try:
        heading_node = card.find(heading, string=heading_text)

        content = []

        sibling_gen = heading_node.nextSiblingGenerator()

        try:
            sibling = next(sibling_gen)
        except StopIteration:
            return False

        while sibling and (not (sibling.name is not None and sibling.name in stop_at) or sibling.name is None):
            if sibling.name in ["p", "ul", "li"]:
                content.append(sibling.text.strip())
            sibling = next(sibling_gen, None)

        if all([c in [
            "[More Information Needed]",
            "More information needed.",
            "More information needed",
            "Users (both direct and downstream) should be made aware of the risks, biases and limitations of the "
            "model. More information needed for further recommendations."
        ] for c in content]):
            return False

        return True
    except AttributeError:
        return False


class ComplianceResult(ABC):
    name: str = None

    def __init__(self, status: Optional[bool] = False, *args, **kwargs):
        self.status = status

    def __eq__(self, other):
        try:
            assert self.status == other.status
            return True
        except AssertionError:
            return False

    @abstractmethod
    def to_string(self):
        return "Not Implemented"


class ComplianceCheck(ABC):
    name: str = None

    @abstractmethod
    def run_check(self, card: BeautifulSoup) -> ComplianceResult:
        raise NotImplementedError


class ModelProviderIdentityResult(ComplianceResult):
    name = "Model Provider Identity"

    def __init__(self, provider: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = provider

    def __eq__(self, other):
        if isinstance(other, ModelProviderIdentityResult):
            if super().__eq__(other):
                try:
                    assert self.provider == other.provider
                    return True
                except AssertionError:
                    return False
        else:
            return False

    def to_string(self):
        return str(self.provider)


class ModelProviderIdentityCheck(ComplianceCheck):
    name = "Model Provider Identity"

    def run_check(self, card: BeautifulSoup):
        try:
            developed_by = card.find("strong", string="Developed by:")

            developer = "".join([str(s) for s in developed_by.next_siblings]).strip()

            if developer == "[More Information Needed]":
                return ModelProviderIdentityResult()

            return ModelProviderIdentityResult(status=True, provider=developer)
        except AttributeError:
            return ModelProviderIdentityResult()


class ComplianceSuite:
    def __init__(self, checks):
        self.checks = checks

    def run(self, model_card) -> List[ComplianceResult]:
        model_card_html = markdown.markdown(model_card)
        card_soup = BeautifulSoup(model_card_html, features="html.parser")

        return [c.run_check(card_soup) for c in self.checks]
