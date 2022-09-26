import argparse
import json
import os
import time

import nlpaug.augmenter.word as naw
from tqdm import tqdm

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("input", help="Input directory containing text files")
parser.add_argument("output", help="Output JSON file to received generated text")
parser.add_argument(
    "--from_model_name", default="facebook/wmt19-en-de", help="Huggingface model name for the forward translation"
)
parser.add_argument(
    "--to_model_name", default="facebook/wmt19-de-en", help="Huggingface model name for the backward translation"
)
parser.add_argument("--length", default=2048, help="Maximum length of input text to pass in to model")
parser.add_argument("--gpu", action="store_true", help="Runs the model on the GPU rather than CPU")
parser.add_argument("--batch_size", default=16, help="Batch size")

args = parser.parse_args()


device = "cuda" if args.gpu else "cpu"

loading = time.time()

back_translation_aug = naw.BackTranslationAug(
    from_model_name=args.from_model_name, to_model_name=args.to_model_name, device=device
)

loaded = time.time()


def back_translate(text: str, augmenter: naw.BackTranslationAug):
    back_translated_text = augmenter.augment(text)
    return back_translated_text


NUM_FILES = len(os.listdir(args.input))

with open(args.output, "w") as outf:
    for f in tqdm(os.listdir(args.input), total=NUM_FILES):
        with open(os.path.join(args.input, f)) as inf:
            article = inf.read()
            article = article[: int(args.length)]

        backtranslated_content = back_translate(text=article, augmenter=back_translation_aug)

        json.dump({"docId": f, "backtranslated": backtranslated_content}, outf)
        outf.write("\n")

finish_time = time.time()

print(f"Model loading time: {round(loaded-loading)} s.")
print(f"Back-translation time for {NUM_FILES} texts: {round(finish_time-loaded)} s.")
