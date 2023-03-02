import gradio as gr
from huggingface_hub import ModelCard
from compliance_checks import (
    ComplianceSuite,
    ModelProviderIdentityCheck,
    IntendedPurposeCheck
)

def run_compliance_check(repo_name):
    model_card = ModelCard.load(repo_id_or_path=repo_name).content

    suite = ComplianceSuite(checks=[
        ModelProviderIdentityCheck(),
        IntendedPurposeCheck()
    ])

    results = suite.run(model_card)

    return str(results)


gr.Interface(
    fn=run_compliance_check,
    inputs="text",
    outputs="text",
    examples=[["society-ethics/model-card-webhook-test"]]
).launch()
