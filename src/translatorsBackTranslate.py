# Simple driver program to use the translators package to back translate a set of paragraphs (or any text block)

# The input file should be a JSON structured file consisting of a list of entries with a text block to backtranslate.
# Each entry can contain any metadata fields you want for each text block, but the text to backtranslate must be
# in a field named 'origPara'. It will create entries in the output file with a 'finalPara' field containing the
# resulting back translated text.

# E.g. input format
# [{'fieldX":"value1", "origPara":"Text block to process"}, {'fieldX":"value2", "origPara":"Text block to process"}]

# Note, using Bing is problematic as there seems to be a much smaller length limit on the length of text you can
# provide to translate. Most of the paragraphs in my test set exceeded that limit.

import json

import translators as ts


def googleTranslate(text, origLang, targetLangs):
    curLang = origLang
    workText = text
    for targetLang in targetLangs:
        result = ts.google(origText, from_language=curLang, to_language=targetLang)
        workText = result
        curLang = targetLang

    # now back to the original language
    result = ts.google(workText, from_language=curLang, to_language=origLang)
    return result


def bingTranslate(text, origLang, targetLangs):

    curLang = origLang
    workText = text
    for targetLang in targetLangs:
        result = ts.bing(
            query_text=origText, from_language=curLang, to_language=targetLang, if_ignore_limit_of_length=True
        )
        workText = result
        curLang = targetLang

    # now back to the original language
    result = ts.bing(query_text=origText, from_language=curLang, to_language=origLang, if_ignore_limit_of_length=True)
    return result


inputJsonFile = "/Users/kohlerc/TorturedPhrases/TranslateParas.json"
outputJsonFileTemplate = "/Users/kohlerc/TorturedPhrases/TranslateParasResults_{}.json"

if __name__ == "__main__":

    origLang = "en"
    targetLangs = ["th", "mn"]

    results = []
    with open(inputJsonFile, "r") as fp:
        input_data = json.load(fp)

        for rec in input_data:
            para = rec.get("origPara")
            final_trans = googleTranslate(para, origLang, targetLangs)
            rec["interLangs"] = ",".join(targetLangs)
            rec["finalPara"] = final_trans
            results.append(rec)

        print(results)

    with open(outputJsonFileTemplate.format("_".join(targetLangs)), "w") as f:
        json.dump(results, f)
