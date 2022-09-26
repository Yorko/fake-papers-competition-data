This repository partially reproduces the data collection process for the COLING workshop SDP [shared task](https://sdproc.org/2022/sharedtasks.html) "DAGPap22: Detecting automatically generated scientific papers".

The data comes from several sources:

1. MICPRO retracted papers (fake)
2. Good MICPRO papers (human-written)
3. Abstracts of SDG-related papers (human-written)
4. Summarized SDG & MICPRO abstracts (fake)
5. Back-translated SDG & MICPRO abstracts (fake)
6. Generated SDG & MICPRO abstracts (fake)
7. Spinbot paraphraser (fake)
8. GPT-3 few-shot generated content (fake)

For sources 4-6, we thank Labs for their help ([repo](https://github.com/elsevier-centraltechnology/labs-fake-paper/)), namely, Tony Scerri, Curt Kohler, and Ron Daniel.

## 0. Setting up the environment

We are using [Poetry](https://python-poetry.org/docs/basic-usage/) as the most up-to-date way of managing dependencies and building packages.

1\. Install Poetry:

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

2\. Dependencies are defined in `pyproject.toml`, depending on your CUDA driver version you might want to change the `torch` version in `pyproject.toml`:

3\. Install the dependencies defined in `pyproject.toml`:

```
poetry install
```

4\. The notebooks listed below are reproduced by running `Jupyter` inside the Poetry environment:

```
poetry run jupyter-notebook
```

## 1. MICPRO retracted papers

These excerpts come from ~6k passages from a list of 167 MICPRO papers published in 2020-2021 and later retracted.



## 2. Good MICPRO papers

Good MICPRO abstracts are sampled from the papers submitted prior to 2020 under the assumption (following the investigation done by Cabanac et.al. in their "Tortured" phrases paper) that those papers were indeed written by humans.


## 3. Abstracts of SDG-related papers

Sustainable Development Goals (SDGs) cover a wide range of topics, from poverty and hunger to climate action and clean energy. Here we use abstracts from a 6k-long evaluation set used in the SDG classification project. This dataset is accesible on request from ICSR Labs, check Data Availability statement in [paper](https://arxiv.org/abs/2209.07285) "Identifying research supporting the United Nations Sustainable Development Goals".


## 4-5. Summarized SDG & MICPRO abstracts


The summarized examples are very easy to distinguish from the real ones (tf-idf & logreg hits ~97% cross-validation accuracy).


**Source code**

- `src/summarize.py` runs the "pszemraj/led-large-book-summary" summarizer with the content from sources 2 and 3 (MICPRO and SDG abstracts).

**Reproducing**

To reproduce the summarizer, put some text excerpts into the folder e.g. `data/interim/abstracts` and run:

```
(poetry run python src/summarize.py  data/interim/abstracts/  \
data/interim/summarized__abstracts.json --gpu \
> logs/summarize__abstracts.log 2>&1 &)
```
This produces an intermediate JSON file `data/interim/summarized_abstracts.json`, each entry looking like `{"docId": "<PII or EID>.txt", "summary": "<TEXT>"}`.



## 6-7. Generated SDG & MICPRO abstracts

These texts are generated using the [EleutherAI/gpt-neo-125M](https://huggingface.co/EleutherAI/gpt-neo-125M) model with the first sentence of the abstract being a prompt.

**Source code**

- `src/generate.py` runs the "EleutherAI/gpt-neo-125M" generator with prompts from sources 2 and 3. 

**Reproducing**


To reproduce the generator models, put some text excerpts into the folder e.g. `data/interim/abstracts` and run:

```
(poetry run python src/generate.py  data/interim/abstracts/  \
data/interim/generated_abstracts.json --title --gpu \
> logs/gen_abstracts.log 2>&1 &)
```
This produces an intermediate JSON file `data/interim/generated_abstracts.json`, each entry looking like `{"docId": "<PII or EID>.txt", "generated": [{"generated_text": "<TEXT>"}]}`.


## 8. Spinbot paraphrased SDG abstracts

We are also using [Spinbot API](https://spinbot.com/) to paraphrase some abstracts from source 3 (SDGs). Spinbot introduces a lot of tortured phrases and hence, Spinbot examples are very easy to distinguish from the real ones (tf-idf & logreg hits >99% validation accuracy).

We used SpinBot API to paraphrase SDG abstracts from source 3. Note that the API is not free and running it incurs costs (~$10 for 2k texts).

## 9. GPT-3 few-shot generated content

Similarly to sources 6-7, we used GPT-3 to add some more fake examples. 

## 10. Back-translated SDG & MICPRO abstracts [rejected]

**Source code**

 - `src/backtranslate_nlpaug.py` runs back-translation with HuggingFace models

The back-translated snippets look almost identical to the originals, hence we don't include them. Repeated back-translation, especially with rare languages (say, En -> Swahili -> Korean -> En) might introduce some artefacts and help the back-translated snippets look "more fake", but we didn't conduct such experiments.

## Merging all data sources

We merge all data sources (skipping only the back-translated content is almost identical to the original), perform 20/80 train-test split (intentionally leaving a small train set), and run binary classification based on text predicting if the text is fake or not.

We merged all data sources described in above (skipping only back-translated content as almost identical to the original), and performed a stratified 20/80 train-test split intentionally leaving a small train set. This resulted in 5327 training records and 21310 test records forming the datasets described on the [competition page](https://www.kaggle.com/competitions/detecting-generated-scientific-papers).

Validation accuracy scores for tf-idf & logreg, grouped by data sources, are:

|          **Source**         | **Validation accuracy** |
|:---------------------------:|:-----------------------:|
| (4) summarized_sdg         |          100%           |
| (5) summarized_micpro      |          99.9%          |
| (8) spinbot\_paraphrased\_sdg |	        98.9%          |
| (9) generated_gpt3          |	        95.5%          |
| (1)  micpro_retracted       |          97%          |
| (7) generated_micpro       |          87.3%          |
| (6) generated_sdg          |          74%          |
| (3) sdg\_abstracts\_original|          57.4%          |
| (2)  micpro_original        |          57.3%          |

Even tf-idf & logreg has no trouble detecting most types of content. However, we notice that with ~70/30 imbalance in favor of fake content, the model is now struggling with the original content (human-written SDG and MICPRO abstracts). 
