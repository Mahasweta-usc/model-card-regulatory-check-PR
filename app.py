import gradio as gr
from huggingface_hub import ModelCard

from compliance_checks import (
    ComplianceSuite,
    ComplianceCheck,
    IntendedPurposeCheck,
    GeneralLimitationsCheck,
    ComputationalRequirementsCheck,
)

checks = [
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


def read_file(file_obj):
    with open(file_obj.name) as f:
        return f.read()


model_card_box = gr.TextArea(label="Model Card")

with gr.Blocks(css="""\
#reverse-row {
    flex-direction: row-reverse;
}
#file-upload .boundedheight {
    max-height: 100px;
}
""") as demo:
    gr.Markdown("""\
    # RegCheck AI
    This Space uses model cards’ information as a source of regulatory compliance with some provisions of the proposed \
    [EU AI Act](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A52021PC0206). For the moment being, the \
    demo is a **prototype** limited to specific provisions of Article 13 of the AI Act, related to “Transparency and \
    provision of information to users”. Choose a model card and check whether it has some useful info to comply with \
    the EU AI Act! **(DISCLAIMER: this is NOT a commercial or legal advice-related product)**\
    """)

    with gr.Row(elem_id="reverse-row"):
        with gr.Column():
            submit_markdown = gr.Button(value="Run validation checks")
            with gr.Tab(label="Results"):
                with gr.Column():
                    compliance_results = [compliance_result(c) for c in suite.checks]
                    compliance_accordions = [c[0] for c in compliance_results]
                    compliance_descriptions = [c[1] for c in compliance_results]

        with gr.Column():
            with gr.Tab(label="Load a card from the 🤗 Hugging Face Hub"):
                model_id_search = gr.Text(label="Model ID")
                gr.Examples(
                    examples=[
                        "bigscience/bloom",
                        "roberta-base",
                        "openai/clip-vit-base-patch32",
                        "distilbert-base-cased-distilled-squad",
                    ],
                    fn=lambda x: ModelCard.load(repo_id_or_path=x).content,
                    inputs=[model_id_search],
                    outputs=[model_card_box]
                    # cache_examples=True,  # TODO: Why does this break the app?
                )

                submit_model_search = gr.Button(value="Load model card")

            with gr.Tab(label="Upload your own card"):
                file = gr.UploadButton(label="Upload a Markdown file", elem_id="file-upload")
                file.upload(
                    fn=read_file,
                    inputs=[file],
                    outputs=[model_card_box]
                )

            model_card_box.render()

    submit_model_search.click(
        fn=lambda x: ModelCard.load(repo_id_or_path=x).content,
        inputs=[model_id_search],
        outputs=[model_card_box]
    )

    submit_markdown.click(
        fn=run_compliance_check,
        inputs=[model_card_box],
        outputs=[*compliance_accordions, *compliance_descriptions]
    )

demo.launch()
