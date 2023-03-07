import gradio as gr

from compliance_checks import (
    ComplianceSuite,
    ModelProviderIdentityCheck,
    IntendedPurposeCheck,
    GeneralLimitationsCheck,
    ComputationalRequirementsCheck,
)

from bloom_card import bloom_card


def run_compliance_check(model_card: str):
    suite = ComplianceSuite(checks=[
        ModelProviderIdentityCheck(),
        IntendedPurposeCheck(),
        GeneralLimitationsCheck(),
        ComputationalRequirementsCheck(),
    ])

    results = suite.run(model_card)

    return str([r[0] for r in results])


with gr.Blocks() as demo:
    gr.Markdown("""\
    # Model Card Validator
    Following Article 13 of the EU AI Act
    """)

    with gr.Row():
        with gr.Column():
            model_card_box = gr.TextArea()
            populate_sample = gr.Button(value="Populate Sample")
            submit = gr.Button()

        with gr.Column():
            results_list = gr.Text()

    submit.click(
        fn=run_compliance_check,
        inputs=[model_card_box],
        outputs=[results_list]
    )

    populate_sample.click(
        fn=lambda: bloom_card,
        inputs=[],
        outputs=[model_card_box]
    )

demo.launch()
