## Imputation Pipeline For MTOB
In our imputation experiments, we focus on translations from Kalamang to English.
This repository outlines the steps to replicate the imputation process and recreate our published results.

### Clone MTOB
The first step involves cloning the MTOB benchmark under the current directory. 

`git clone https://github.com/lukemelas/mtob.git`

The mtob folder must be placed directly under the root of the project, i.e. mtob_impute. The materials of MTOB can be found here https://lukemelas.github.io/mtob/.
Follow the setup steps as prescribed in the README of MTOB in https://github.com/lukemelas/mtob/blob/main/README.md
1. Ensure you have correctly setup installing baselines/requirements.txt.
2. Ensure the contents of the kalamang dataset has been unzipped. Our imputation script will directly modify the wordlist in the mtob directory. We ask that the integrity of the dataset be maintained to prevent potential test set contamination into training data of LLMs as outlined in MTOB, i.e. avoid publishing to public repositories with the test sets.
3. Ensure the correct API keys have been added to .env.
4. We note that within the wordlist.json, there are markings that may need to be removed, such as "textscpl", "textscsg", "textscex", "textscin" and "endletter. In our experiments we manually removed these instances in the wordlist prior to running the imputation pipeline.

### Run Imputation Pipeline
1. Ensure you have an OpenAI API key setup in a .env file. See `.env.example` for an example.
2. Run preprocessing.py to produce a temporary wordlist with affix alterations. This is so that we can detect affixes within words in the subword segmentations process.
3. Run query_builder.py to build queries for GPT.
4. To impute, run query_llm.py, this will automatically update the wordlist in mtob.

### Generate Translations
Run mtob/baselines/main.py with appropriate parameters, i.e. --use_reference_wordlist --use_reference_sentences --use_reference_book_passages. Example: 

`python main.py --direction ke --model_type openai --model_name gpt-3.5-turbo --use_reference_wordlist`

Refer to https://github.com/lukemelas/mtob/blob/main/README.md on available parameters.

Note that after the imputation steps, the wordlist.json file has been imputed. 

If MTOB doesn't pick up your .env, it may be useful to add the keys to the virtual env via CLI or manually enter the keys in the parameters of the LLM instantiation step in mtob/baselines/main.py (i.e. openai_api_key argument).

The output translations are found in mtob/baselines/outputs/ke.

At times, running on GPT-4 or Claude 2.0 may result in LLMs refusing to translate or adding supplementary information. In our experiments, we re-run the failed queries by GPT-4 manually with forceful_manual_llm.py, using the prescribed approach from MTOB with a more forceful prompt and manually replacing the failed translations. We also remove supplementary explanations that are often seen in Claude 2.0 outputs by filtering with regex to extract the predicted English translation prior to running with eval.py.

### Evaluation
Run mtob/baselines/eval.py on the results file to compute the metrics on translations generated by main.py. Example:

`python eval.py --direction ke --input_file ./outputs/ke/results_test_openai_gpt-3.5-turbo_temp_0.05_reference_wordlist_2.json`

The evaluations are found in mtob/baselines/outputs/eval-ke. While LLM temperature is set to 0.05, we expect small deviations from reported results in chrF due to minor stochasticness of LLMs.

While conducting our evaluation with eval.py in mtob/baselines, we found it useful to comment out `assert len(rr_preds) == sum([pred != new_pred for pred, new_pred in zip(preds, new_preds, strict=True)])` in the `load()` function which appeared to arbitrarily prevent eval.py from running. This line appears to be intended to help validate reruns with a more "forceful" prompt when GPT-4 refuses to provide translation and can be commented. Within our experiments, we chose to manually rerun the generated prompts rather than using the --rerun argument, we expect no impact on results with this approach.

# References
* [MTOB](https://github.com/lukemelas/mtob) - MTOB benchmarks and baselines. Tanzer, et al.
