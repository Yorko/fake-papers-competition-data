# Run text paragraphs (or any text block) through AWS Translate.
# Update the list of various languages to run through if you want multiple layers of translation

# The input file should be a JSON structured file consisting of a list of entries with a text block to backtranslate.
# Each entry can contain any metadata fields you want for each text block, but the text to backtranslate must be
# in a field named 'origPara'. It will create entries in the output file with a 'finalPara' field containing the
# # resulting back translated text.

# E.g. input format
# [{'fieldX":"value1", "origPara":"Text block to process"}, {'fieldX":"value2", "origPara":"Text block to process"}]

# You also need AWS credentials enabled within the user account that is running this script (or be running on an EC2
# with the proper access..

import json

import boto3


def contortText(text, origLang, targetLangs):

    # Run the text through the various target languages
    curLang = origLang
    workText = text
    for targetLang in targetLangs:
        result = aws_translator.translate_text(
            Text=workText, SourceLanguageCode=curLang, TargetLanguageCode=targetLang
        )
        workText = result.get("TranslatedText")
        curLang = targetLang

    # now back to the original language
    result = aws_translator.translate_text(Text=workText, SourceLanguageCode=curLang, TargetLanguageCode=origLang)
    return result.get("TranslatedText")


if __name__ == "__main__":

    origLang = "en"
    # one or more translations to chain together before going back to the origLang
    targetLangs = ["th", "mn"]

    aws_translator = boto3.client(service_name="translate", region_name="us-east-1", use_ssl=True)

    results = []
    with open("/Users/kohlerc/Desktop/TranslateParas.json", "r") as fp:
        input_data = json.load(fp)

        for rec in input_data:
            para = rec.get("origPara")
            # para = 'Clerodane diterpenoids are a class of naturally occurring secondary metabolites found in hundreds of plants, and they account for the majority of diterpenoids [1,2]. Some of these compounds exhibit attractive biological and pharmacological activities, such as insect antifeedant, opioid-receptor agonist, cytotoxic, antiparasitic, antifungal, antibacterial, and antitumor activities [1,2]. The structure of clerodanes is classified according to the relative configuration of the A/B ring junction and the relationship between the methyl groups at C-8 and C-9. Thus, four clerodane types are defined based on the configuration of H3-19/H-10–H3-17/H3-20: trans–cis (TC), trans–trans (TT), cis–cis (CC), and cis–trans (CT) (Fig. 1) [1]. Additionally, two conformations (steroidal and nonsteroidal) can exist in the CC and CT types because of the cis A/B ring. However, the structures confirmed by X-ray diffraction measurements demonstrated that the conformations of the cis A/B ring are steroidal and nonsteroidal for the CC- and CT-type compounds, respectively [[3], [4], [5], [6]]. Approximately 75% of the clerodanes isolated from plants to date have been established to have the trans A/B ring junction [1], and the cis relationship between H3-17 and H3-20 have been identified in most clerodanes [7]. In addition, regarding the absolute configuration, studies have shown that neo-clerodanes (ent-clerodanes) predominate in number over ent-neo-clerodanes (clerodanes) [7]. These results imply that CT-type ent-neo-clerodanes (clerodanes) are rarely present in clerodane diterpenoids.'
            final_trans = contortText(para, origLang, targetLangs)
            rec["interLangs"] = ",".join(targetLangs)
            rec["finalPara"] = final_trans
            results.append(rec)

        print(results)

    with open("/Users/kohlerc/Desktop/TranslateParasResults_{}.json".format("_".join(targetLangs)), "w") as f:
        json.dump(results, f)
