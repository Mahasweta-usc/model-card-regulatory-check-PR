from os import listdir
from os.path import isfile, join
from pathlib import Path


# TODO: I have the option of maybe making a check for accuracy/metrics?

# Note, some of these are marked as FALSE instead of TRUE because the
# information is hidden somewhere non-standard, e.g. described in prose

# Intended Purpose, General Limitations, Computational Requirements
expected_check_results = {
    "albert-base-v2": [True, True, False],
    "bert-base-cased": [True, True, False],
    "bert-base-multilingual-cased": [True, True, False],
    "bert-base-uncased": [True, True, False],
    "cl-tohoku___bert-base-japanese-whole-word-masking": [False, False, False],
    "distilbert-base-cased-distilled-squad": [True, True, True],
    "distilbert-base-uncased": [True, True, False],
    "distilbert-base-uncased-finetuned-sst-2-english": [True, True, False],
    "distilroberta-base": [True, True, False],
    "emilyalsentzer___Bio_ClinicalBERT": [False, False, False],
    "facebook___bart-large-mnli": [False, False, False],
    "google___electra-base-discriminator": [False, False, False],
    "gpt2": [True, True, False],
    "Helsinki-NLP___opus-mt-en-es": [False, False, False],
    "jonatasgrosman___wav2vec2-large-xlsr-53-english": [False, False, False],
    "microsoft___layoutlmv3-base": [False, False, False],
    "openai___clip-vit-base-patch32": [True, True, False],
    "openai___clip-vit-large-patch14": [True, True, False],
    "philschmid___bart-large-cnn-samsum": [False, False, False],
    "prajjwal1___bert-tiny": [False, False, False],
    "roberta-base": [True, True, True],  # For the computational requirements, sort of?
    "roberta-large": [True, True, True],
    "runwayml___stable-diffusion-v1-5": [True, True, True],
    "sentence-transformers___all-MiniLM-L6-v2": [True, False, False],
    "StanfordAIMI___stanford-deidentifier-base": [False, False, False],
    "t5-base": [True, False, False],
    "t5-small": [True, False, False],
    "xlm-roberta-base": [True, False, False],
    "xlm-roberta-large": [True, False, False],
    "yiyanghkust___finbert-tone": [False, False, False],
}


def pytest_generate_tests(metafunc):
    if "real_model_card" in metafunc.fixturenames:
        files = [f"cards/{f}" for f in listdir("cards") if isfile(join("cards", f))]
        cards = [Path(f).read_text() for f in files]
        model_ids = [f.replace("cards/", "").replace(".md", "") for f in files]

        # TODO: IMPORTANT – remove the default [False, False, False]
        expected_results = [expected_check_results.get(m, [False, False, False]) for m, c in zip(model_ids, cards)]

        metafunc.parametrize(
            ["real_model_card", "expected_check_results"],
            list(map(list, zip(cards, expected_results)))
        )

    # rows = read_csvrows()
    # if 'row' in metafunc.fixturenames:
    #     metafunc.parametrize('row', rows)
    # if 'col' in metafunc.fixturenames:
    #     metafunc.parametrize('col', list(itertools.chain(*rows)))

