import os
import gradio as gr
from huggingface_hub import ModelCard, HfApi

from compliance_checks import (
    ComplianceSuite,
    ComplianceCheck,
    IntendedPurposeCheck,
    GeneralLimitationsCheck,
    ComputationalRequirementsCheck,
    EvaluationCheck,
)

hf_writer = gr.HuggingFaceDatasetSaver(
    os.getenv('HUGGING_FACE_HUB_TOKEN'),
    organization="society-ethics",
    dataset_name="model-card-regulatory-check-flags",
    private=True
)

hf_api = HfApi()

checks = [
    IntendedPurposeCheck(),
    GeneralLimitationsCheck(),
    ComputationalRequirementsCheck(),
    EvaluationCheck(),
]
suite = ComplianceSuite(checks=checks)


def status_emoji(status: bool):
    return "✅" if status else "🛑"


def search_for_models(query: str):
    if query.strip() == "":
        return examples, ",".join([e[0] for e in examples])
    models = [m.id for m in list(iter(hf_api.list_models(search=query, limit=10)))]
    model_samples = [[m] for m in models]
    models_text = ",".join(models)
    return model_samples, models_text


def load_model_card(index, options_string: str):
    options = options_string.split(",")
    model_id = options[index]
    card = ModelCard.load(repo_id_or_path=model_id).content
    return card


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
        model_card = f.read()
        return model_card


model_card_box = gr.TextArea(label="Model Card")

# Have to destructure everything since I need to delay rendering.
col = gr.Column()
tab = gr.Tab(label="Results")
col2 = gr.Column()
compliance_results = [compliance_result(c) for c in suite.checks]
compliance_accordions = [c[0] for c in compliance_results]
compliance_descriptions = [c[1] for c in compliance_results]

examples = [
    ["bigscience/bloom"],
    ["roberta-base"],
    ["openai/clip-vit-base-patch32"],
    ["distilbert-base-cased-distilled-squad"],
]

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
    This Space matches information in [model cards](https://huggingface.co/docs/hub/model-cards) to proposed regulatory \
    compliance descriptions in the [EU AI Act](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A52021PC0206). \
    This is a  **prototype** to explore the feasibility of automatic checks for compliance, \
    and is limited to specific provisions of Article 13 of the Act, “Transparency and \
    provision of information to users”. \
    **This is research work and NOT a commercial or legal product**
    
    To check a model card, first load it by doing any one of the following:
    - If the model is on the Hugging Face Hub, search for a model and select it from the results.
    - If you have the model card on your computer as a Markdown file, select the "Upload your own card" tab and click \
      "Upload a Markdown file".
    - Paste your model card's text directly into the "Model Card" text area.
    """)

    with gr.Row():
        with gr.Column():
            with gr.Tab(label="Load a card from the 🤗 Hugging Face Hub"):
                with gr.Row():
                    model_id_search = gr.Text(label="Model ID")

                search_results_text = gr.Text(visible=False, value=",".join([e[0] for e in examples]))
                search_results_index = gr.Dataset(
                    label="Search Results",
                    components=[model_id_search],
                    samples=examples,
                    type="index",
                )

                model_id_search.change(
                    fn=search_for_models,
                    inputs=[model_id_search],
                    outputs=[search_results_index, search_results_text]
                )

            with gr.Tab(label="Upload your own card"):
                file = gr.UploadButton(label="Upload a Markdown file", elem_id="file-upload")
                # TODO: Bug – uploading more than once doesn't trigger the function? Gradio bug?
                file.upload(
                    fn=read_file,
                    inputs=[file],
                    outputs=[model_card_box]
                )

            model_card_box.render()

        with col.render():
            with tab.render():
                with col2.render():
                    for a, d in compliance_results:
                        with a.render():
                            d.render()

            flag = gr.Button(value="Disagree with the result? Click here to flag it! 🚩")
            flag_message = gr.Text(
                show_label=False,
                visible=False,
                value="Thank you for flagging this! We'll use your report to improve the tool 🤗"
            )

    search_results_index.click(
        fn=load_model_card,
        inputs=[search_results_index, search_results_text],
        outputs=[model_card_box]
    )

    model_card_box.change(
        fn=run_compliance_check,
        inputs=[model_card_box],
        outputs=[*compliance_accordions, *compliance_descriptions]
    )

    flag.click(
        fn=lambda x: hf_writer.flag(flag_data=[x]) and gr.Text.update(visible=True),
        inputs=[model_card_box],
        outputs=[flag_message]
    )

hf_writer.setup(
    components=[model_card_box],
    flagging_dir="flagged"
)

demo.launch()
