from os import listdir
from os.path import isfile, join
from pathlib import Path

# Note, some of these are marked as FALSE instead of TRUE because the
# information is hidden somewhere non-standard, e.g. described in prose

# Intended Purpose, General Limitations, Computational Requirements, Evaluation
expected_check_results = {
    "albert-base-v2": [True, True, False, True],
    "bert-base-cased": [True, True, False, True],
    "bert-base-multilingual-cased": [True, True, False, False],
    "bert-base-uncased": [True, True, False, True],
    "big-science___bloom": [True, True, True, True],
    "big-science___t0pp": [True, True, False, True],
    "cl-tohoku___bert-base-japanese-whole-word-masking": [False, False, False, False],
    "distilbert-base-cased-distilled-squad": [True, True, True, True],
    "distilbert-base-uncased": [True, True, False, True],
    "distilbert-base-uncased-finetuned-sst-2-english": [True, True, False, False],
    "distilroberta-base": [True, True, False, True],
    "emilyalsentzer___Bio_ClinicalBERT": [False, False, False, False],
    "facebook___bart-large-mnli": [False, False, False, False],
    "google___electra-base-discriminator": [False, False, False, False],
    "gpt2": [True, True, False, True],
    "Helsinki-NLP___opus-mt-en-es": [False, False, False, True],
    "jonatasgrosman___wav2vec2-large-xlsr-53-english": [False, False, False, True],
    "microsoft___layoutlmv3-base": [False, False, False, False],
    "openai___clip-vit-base-patch32": [True, True, False, False],
    "openai___clip-vit-large-patch14": [True, True, False, False],
    "philschmid___bart-large-cnn-samsum": [False, False, False, True],
    "prajjwal1___bert-tiny": [False, False, False, False],
    "roberta-base": [True, True, False, True],
    "roberta-large": [True, True, False, True],
    "runwayml___stable-diffusion-v1-5": [True, True, False, True],
    "sentence-transformers___all-MiniLM-L6-v2": [True, False, False, True],
    "StanfordAIMI___stanford-deidentifier-base": [False, False, False, False],
    "t5-base": [True, False, False, True],
    "t5-small": [True, False, False, True],
    "xlm-roberta-base": [True, True, False, False],
    "xlm-roberta-large": [True, True, False, False],
    "yiyanghkust___finbert-tone": [False, False, False, False],
}


def pytest_generate_tests(metafunc):
    if "real_model_card" in metafunc.fixturenames:
        files = [f"cards/{f}" for f in listdir("cards") if isfile(join("cards", f))]
        cards = [Path(f).read_text() for f in files]
        model_ids = [f.replace("cards/", "").replace(".md", "") for f in files]
        expected_results = [expected_check_results.get(m) for m, c in zip(model_ids, cards)]

        metafunc.parametrize(
            ["real_model_card", "expected_check_results"],
            list(map(list, zip(cards, expected_results)))
        )
