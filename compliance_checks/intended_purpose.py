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
        return str((self.direct_use, self.direct_use, self.out_of_scope_use))


class IntendedPurposeCheck(ComplianceCheck):
    name = "Intended Purpose"

    def run_check(self, card: BeautifulSoup):
        combos = [
            ("h2", "Intended uses & limitations"),
            ("h1", "Uses"), ("h2", "Uses"),
            ("h2", "Model Use"),
            ("h2", "Intended uses"),
        ]

        for hX, heading in combos:
            purpose_check = walk_to_next_heading(card, hX, heading)
            if purpose_check:
                return IntendedPurposeResult(
                    status=True,
                )

        return IntendedPurposeResult()
