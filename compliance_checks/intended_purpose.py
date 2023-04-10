from compliance_checks.base import ComplianceResult, ComplianceCheck, walk_to_next_heading
from bs4 import BeautifulSoup


class IntendedPurposeResult(ComplianceResult):
    name = "Intended Purpose"

    def __init__(
            self,
            direct_use: str = None,
            downstream_use: str = None,
            out_of_scope_use: str = None,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.direct_use = direct_use
        self.downstream_use = downstream_use
        self.out_of_scope_use = out_of_scope_use

    def __eq__(self, other):
        if isinstance(other, IntendedPurposeResult):
            if super().__eq__(other):
                try:
                    # TODO: Either use these, or remove them.
                    # assert self.direct_use == other.direct_use
                    # assert self.downstream_use == other.downstream_use
                    # assert self.out_of_scope_use == other.out_of_scope_use
                    return True
                except AssertionError:
                    return False
        else:
            return False

    def to_string(self):
        if self.status:
            return """\
            It looks like this model card has some documentation for the model's intended purpose! We look for this by \
            searching for headings that say things like:
            - Intended uses & limitations
            - Uses
            - Model Use
            """
        else:
            return """\
            We weren't able to find a section in this model card for the model's intended purpose, but it's easy to \
            add one! You can add the following section to the model card and, once you fill in the \
            `[More Information Needed]` sections, the "Intended Purpose" check should pass 🤗
            
            ```md
            ## Uses
            
            <!-- Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model. -->

            [More Information Needed]
            
            ### Direct Use
            
            <!-- This section is for the model use without fine-tuning or plugging into a larger ecosystem/app. -->
            
            [More Information Needed]
            
            ### Downstream Use [optional]
            
            <!-- This section is for the model use when fine-tuned for a task, or when plugged into a larger ecosystem/app -->
            
            [More Information Needed]
            
            ### Out-of-Scope Use
            
            <!-- This section addresses misuse, malicious use, and uses that the model will not work well for. -->
            [More Information Needed]
            ```
            """


class IntendedPurposeCheck(ComplianceCheck):
    name = "Intended Purpose"

    def run_check(self, card: BeautifulSoup):
        combos = [
            ("h2", "Intended uses & limitations"),
            ("h1", "Uses"), ("h2", "Uses"),
            ("h1", "Usage"),
            ("h2", "Model Use"),
            ("h1", "Intended uses"), ("h2", "Intended uses"),
            ("h2", "Intended Use"),
        ]

        for hX, heading in combos:
            purpose_check = walk_to_next_heading(card, hX, heading)
            if purpose_check:
                return IntendedPurposeResult(
                    status=True,
                )

        return IntendedPurposeResult()
