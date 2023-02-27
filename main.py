import os
from typing import Dict, Any, Optional, List
import re
from abc import ABC, abstractmethod

from huggingface_hub import (ModelCard, comment_discussion,
                             create_discussion, get_discussion_details,
                             get_repo_discussions)
import markdown
from bs4 import BeautifulSoup
from tabulate import tabulate
from difflib import SequenceMatcher

KEY = os.environ.get("KEY")


def similar(a, b):
    """Check similarity of two sequences"""
    return SequenceMatcher(None, a, b).ratio()


class ComplianceCheck(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def check(self, card: BeautifulSoup) -> bool:
        raise NotImplementedError


class ModelProviderIdentityCheck(ComplianceCheck):
    def __init__(self):
        super().__init__("Identity and Contact Details")

    def check(self, card: BeautifulSoup):
        developed_by_li = card.findAll(text=re.compile("Developed by"))[0].parent.parent
        developed_by = list(developed_by_li.children)[1].text.strip()

        if developed_by == "[More Information Needed]":
            return False
        else:
            return True


class IntendedPurposeCheck(ComplianceCheck):
    def __init__(self):
        super().__init__("Intended Purpose")

    def check(self, card: BeautifulSoup):

        # direct_use = card.find_all("h2", text="Direct Use")[0]
        #
        # if developed_by == "[More Information Needed]":
        #     return False
        # else:
        return False


compliance_checks = [
    ModelProviderIdentityCheck(),
    IntendedPurposeCheck()
    # "General Limitations",
    # "Computational and Hardware Requirements",
    # "Carbon Emissions"
]


def parse_webhook_post(data: Dict[str, Any]) -> Optional[str]:
    event = data["event"]
    if event["scope"] != "repo":
        return None
    repo = data["repo"]
    repo_name = repo["name"]
    repo_type = repo["type"]
    if repo_type != "model":
        raise ValueError("Incorrect repo type.")
    return repo_name


def check_compliance(comp_checks: List[ComplianceCheck], card: BeautifulSoup) -> Dict[str, bool]:
    return {c.name: c.check(card) for c in comp_checks}


def run_compliance_check(repo_name):
    card_data: ModelCard = ModelCard.load(repo_id_or_path=repo_name)
    card_html = markdown.markdown(card_data.content)
    card_soup = BeautifulSoup(card_html, features="html.parser")
    compliance_results = check_compliance(compliance_checks, card_soup)

    return compliance_results


def create_metadata_breakdown_table(compliance_check_dictionary):
    data = {k: v for k, v in compliance_check_dictionary.items()}
    metadata_fields_column = list(data.keys())
    metadata_values_column = list(data.values())
    table_data = list(zip(metadata_fields_column, metadata_values_column))
    return tabulate(
        table_data, tablefmt="github", headers=("Compliance Check", "Present")
    )


def create_markdown_report(
    desired_metadata_dictionary, repo_name, update: bool = False
):
    report = f"""# Model Card Regulatory Compliance report card {"(updated)" if update else ""}
    \n
This is an automatically produced model card regulatory compliance report card for {repo_name}.
This report is meant as a POC!
    \n 
## Breakdown of metadata fields for your model
\n
{create_metadata_breakdown_table(desired_metadata_dictionary)}
\n
    """
    return report


def create_or_update_report(compliance_check, repo_name):
    report = create_markdown_report(
        compliance_check, repo_name, update=False
    )
    repo_discussions = get_repo_discussions(
        repo_name,
        repo_type="model",
    )
    for discussion in repo_discussions:
        if (
            discussion.title == "Metadata Report Card" and discussion.status == "open"
        ):  # An existing open report card thread
            discussion_details = get_discussion_details(
                repo_name, discussion.num, repo_type="model"
            )
            last_comment = discussion_details.events[-1].content
            if similar(report, last_comment) <= 0.999:
                report = create_markdown_report(
                    compliance_check,
                    repo_name,
                    update=True,
                )
                comment_discussion(
                    repo_name,
                    discussion.num,
                    comment=report,
                    repo_type="model",
                )
            return True
    create_discussion(
        repo_name,
        "Model Card Regulatory Compliance Report Card",
        description=report,
        repo_type="model",
    )
    return True
