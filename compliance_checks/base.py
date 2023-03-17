from abc import ABC, abstractmethod
from typing import Optional, List

import markdown
from bs4 import BeautifulSoup, Comment


def walk_to_next_heading(card, heading, heading_text) -> bool:
    stop_at = [heading, f"h{int(heading[1]) - 1}"]

    try:
        heading_node = card.find(heading, string=heading_text)

        content = ""

        sibling_gen = heading_node.nextSiblingGenerator()
        sibling = next(sibling_gen)

        while sibling and (not (sibling.name is not None and sibling.name in stop_at) or sibling.name is None):
            if not isinstance(sibling, Comment):
                content = content + sibling.text.strip()
            sibling = next(sibling_gen, None)

        if content.strip() == "[More Information Needed]":
            return False  # , None

        return True  # , content
    except AttributeError:
        return False  # , None


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


class GeneralLimitationsResult(ComplianceResult):
    name = "General Limitations"

    def __init__(
            self,
            limitations: str = None,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.limitations = limitations

    def __eq__(self, other):
        if isinstance(other, GeneralLimitationsResult):
            if super().__eq__(other):
                try:
                    assert self.limitations == other.limitations
                    return True
                except AssertionError:
                    return False
        else:
            return False

    def to_string(self):
        return self.limitations


class GeneralLimitationsCheck(ComplianceCheck):
    name = "General Limitations"

    def run_check(self, card: BeautifulSoup):
        check, content = walk_to_next_heading(card, "h2", "Bias, Risks, and Limitations")

        return GeneralLimitationsResult(
            status=check,
            limitations=content
        )


class ComputationalRequirementsResult(ComplianceResult):
    name = "Computational Requirements"

    def __init__(
            self,
            requirements: str = None,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.requirements = requirements

    def __eq__(self, other):
        if isinstance(other, ComputationalRequirementsResult):
            if super().__eq__(other):
                try:
                    assert self.requirements == other.requirements
                    return True
                except AssertionError:
                    return False
        else:
            return False

    def to_string(self):
        return self.requirements


class ComputationalRequirementsCheck(ComplianceCheck):
    name = "Computational Requirements"

    def run_check(self, card: BeautifulSoup):
        check, content = walk_to_next_heading(card, "h3", "Compute infrastructure")

        return ComputationalRequirementsResult(
            status=check,
            requirements=content,
        )


class ComplianceSuite:
    def __init__(self, checks):
        self.checks = checks

    def run(self, model_card) -> List[ComplianceResult]:
        model_card_html = markdown.markdown(model_card)
        card_soup = BeautifulSoup(model_card_html, features="html.parser")

        return [c.run_check(card_soup) for c in self.checks]
