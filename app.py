import gradio as gr
from huggingface_hub import ModelCard

from compliance_checks import (
    ComplianceSuite,
    ComplianceCheck,
    ModelProviderIdentityCheck,
    IntendedPurposeCheck,
    GeneralLimitationsCheck,
    ComputationalRequirementsCheck,
)

from bloom_card import bloom_card

checks = [
    ModelProviderIdentityCheck(),
    IntendedPurposeCheck(),
    GeneralLimitationsCheck(),
    ComputationalRequirementsCheck(),
]
suite = ComplianceSuite(checks=checks)


def status_emoji(status: bool):
    return "✅" if status else "🛑"


def run_compliance_check(model_card: str):
    results = suite.run(model_card)

    return [
        *[gr.Accordion.update(label=f"{r.name} - {status_emoji(r.status)}") for r in results],
        *[gr.Markdown.update(value=r.to_string()) for r in results],
    ]


def fetch_and_run_compliance_check(model_id: str):
    model_card = ModelCard.load(repo_id_or_path=model_id).content
    return run_compliance_check(model_card=model_card)


def compliance_result(compliance_check: ComplianceCheck):
    accordion = gr.Accordion(label=f"{compliance_check.name}", open=False)
    with accordion:
        description = gr.Markdown("Run an evaluation to see results...")

    return accordion, description


with gr.Blocks(css="#reverse-row { flex-direction: row-reverse; }") as demo:
    gr.Markdown("""\
    # Model Card Validator
    Following Article 13 of the EU AI Act
    """)

    with gr.Row(elem_id="reverse-row"):
        with gr.Tab(label="Results"):
            with gr.Column():
                compliance_results = [compliance_result(c) for c in suite.checks]
                compliance_accordions = [c[0] for c in compliance_results]
                compliance_descriptions = [c[1] for c in compliance_results]

        with gr.Column():
            with gr.Tab(label="Markdown"):
                model_card_box = gr.TextArea()
                populate_sample_card = gr.Button(value="Populate Sample")
                submit_markdown = gr.Button()
            with gr.Tab(label="Search for Model"):
                model_id_search = gr.Text()
                submit_model_search = gr.Button()
                gr.Examples(
                    examples=["society-ethics/model-card-webhook-test"],
                    inputs=[model_id_search],
                    outputs=[*compliance_accordions, *compliance_descriptions],
                    fn=fetch_and_run_compliance_check,
                    # cache_examples=True,  # TODO: Why does this break the app?
                )

    submit_markdown.click(
        fn=run_compliance_check,
        inputs=[model_card_box],
        outputs=[*compliance_accordions, *compliance_descriptions]
    )

    submit_model_search.click(
        fn=fetch_and_run_compliance_check,
        inputs=[model_id_search],
        outputs=[*compliance_accordions, *compliance_descriptions]
    )

    populate_sample_card.click(
        fn=lambda: bloom_card,
        inputs=[],
        outputs=[model_card_box]
    )

demo.launch()
