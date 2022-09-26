import argparse
import json
import os
import time

from tqdm import tqdm
from transformers import pipeline

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("input", help="Input directory containing text files")
parser.add_argument("output", help="Output JSON file to received generated text")
parser.add_argument("--length", default=2048, help="Maximum length of input text to pass in to model")
parser.add_argument("--gpu", action="store_true", help="Runs the model on the GPU rather than CPU")

args = parser.parse_args()


device = 0 if args.gpu else -1

loading = time.time()
MODEL = "pszemraj/led-large-book-summary"

summarizer = pipeline("summarization", model=MODEL, device=device)

loaded = time.time()

# model = "philschmid/bart-large-cnn-samsum" # Extracts pieces
# model="facebook/bart-large-cnn",device=device)#extracts, kind of generative , 2. Yury: bad, adds links to websites and says "For more information, visit"
# model="pszemraj/led-large-book-summary",device=device)#Does a paper review style summary , 1
# model="sshleifer/distilbart-xsum-12-3",device=device)#ok generative stuff. Yury: bad
# model='pszemraj/led-base-16384-finetuned-booksum',device=device)BAD

SAMPLE = False

NUM_FILES = len(os.listdir(args.input))

with open(args.output, "w") as outf:
    for f in tqdm(os.listdir(args.input), total=NUM_FILES):
        with open(os.path.join(args.input, f)) as inf:
            article = inf.read()
            article = article[: int(args.length)]

        summary = summarizer(
            article,
            max_length=min(int(1.2 * int(args.length)), 156),
            min_length=min(int(args.length), 128),
            do_sample=SAMPLE,
            no_repeat_ngram_size=3,
            encoder_no_repeat_ngram_size=3,
        )[0]["summary_text"]

        json.dump({"docId": f, "summary": summary}, outf)
        outf.write("\n")

generated = time.time()

print(f"Model loading time: {round(loaded-loading)} s.")
print(f"Summarization time for {NUM_FILES} texts: {round(generated-loaded)} s.")
