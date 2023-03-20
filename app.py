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
        *[gr.Accordion.update(label=f"{r.name} - {status_emoji(r.status)}", open=not r.status) for r in results],
        *[gr.Markdown.update(value=r.to_string()) for r in results],
    ]


def fetch_and_run_compliance_check(model_id: str):
    model_card = ModelCard.load(repo_id_or_path=model_id).content
    return run_compliance_check(model_card=model_card)


def compliance_result(compliance_check: ComplianceCheck):
    accordion = gr.Accordion(label=f"{compliance_check.name}", open=False)
    description = gr.Markdown("Run an evaluation to see results...")

    return accordion, description


def read_file(file_obj):
    with open(file_obj.name) as f:
        return f.read()


model_card_box = gr.TextArea(label="Model Card")

# Have to destructure everything since I need to delay rendering.
col = gr.Column()
submit_markdown = gr.Button(value="Run validation checks")
tab = gr.Tab(label="Results")
col2 = gr.Column()
compliance_results = [compliance_result(c) for c in suite.checks]
compliance_accordions = [c[0] for c in compliance_results]
compliance_descriptions = [c[1] for c in compliance_results]

with gr.Blocks(css="""\
#file-upload .boundedheight {
    max-height: 100px;
}

code {
    overflow: scroll;
}
""") as demo:
    gr.Markdown("""\
    # RegCheck AI
    This Space uses [model cards’](https://huggingface.co/docs/hub/model-cards) information as a source of regulatory \
    compliance with some provisions of the proposed \
    [EU AI Act](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A52021PC0206). For the moment being, the \
    demo is a **prototype** limited to specific provisions of Article 13 of the AI Act, related to “Transparency and \
    provision of information to users”. **(DISCLAIMER: this is NOT a commercial or legal advice-related product)**
    
    To check a model card, first load it by doing any one of the following:
    - If the model is on the Hugging Face Hub, enter its model ID and click "Load model card".
    - If you have the model card on your computer as a Markdown file, select the "Upload your own card" tab and click \
      "Upload a Markdown file".
    - Paste your model card's text directly into the "Model Card" text area.
    
    Once your card is loaded, click "Run validation checks" to receive your results.
    """)

    with gr.Row():
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

        with col.render():
            submit_markdown.render()
            with tab.render():
                with col2.render():
                    for a, d in compliance_results:
                        with a.render():
                            d.render()

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
