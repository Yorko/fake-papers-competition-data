import argparse
import json
import os
import time

from transformers import pipeline

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("input", help="Input directory containing text files")
parser.add_argument("output", help="Output JSON file to received generated text")
parser.add_argument("--title", action="store_true", help="Uses the first line only of the input file")
parser.add_argument(
    "--abstract", action="store_true", help="Adds a abstract header to the end of the prompt after the file contents"
)
parser.add_argument("--gpu", action="store_true", help="Runs the model on the GPU rather than CPU")

args = parser.parse_args()

device = 0 if args.gpu else -1

loading = time.time()

MODEL = "EleutherAI/gpt-neo-125M"
# MODEL = "EleutherAI/gpt-neo-2.7B"

generator = pipeline("text-generation", model=MODEL, device=device)

loaded = time.time()

SAMPLE = True

with open(args.output, "w") as outf:
    for f in os.listdir(args.input):
        with open(os.path.join(args.input, f)) as inf:
            if args.title:
                title = inf.read().split(". ")[0]
            else:
                title = inf.read()
            # print(len(title))

        # gen=generator("EleutherAI has", do_sample=False, min_length=50)#Repeats more

        # Initial runsdidnt generate very long texts
        # gen=generator(title, do_sample=True, min_length=150)
        # gen=generator(title+"\nAbstract\n", do_sample=True, min_length=150)

        # Change the parameters to get some long text
        if args.abstract:
            gen = generator(title + "\nAbstract\n", do_sample=SAMPLE, min_length=512, max_length=2048)
        else:
            gen = generator(title, do_sample=SAMPLE, min_length=128, max_length=512)
        json.dump({"docId": f, "generated": gen}, outf)
        outf.write("\n")

        # print(gen)

generated = time.time()

print(f"Model loading time: {round(loaded-loading, 1)}")
print(f"generation time: {round(generated-loaded)}")
