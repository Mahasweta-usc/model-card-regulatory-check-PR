import os

from huggingface_hub import (comment_discussion,
                             create_discussion, get_discussion_details,
                             get_repo_discussions)
from tabulate import tabulate
from difflib import SequenceMatcher

KEY = os.environ.get("KEY")


def similar(a, b):
    """Check similarity of two sequences"""
    return SequenceMatcher(None, a, b).ratio()


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
