# Collection of notebooks for the training of a fake news detector
This repository contains most of the code used for the training of the classifiers used in my application *fastidiouscity*. 
Developed for my Master's Degree thesis in Computer Science and Engineering at Politecnico, it consists of five layers:

 - A newsworthiness detector, to determine whether a text is news, opinion or uninteresting
 - A professionality detector, to discriminate between well written texts and poorly written ones
 - An automated fact-checking system, whose job is to detect claims inside texts, looking for evidence online and establishing whether it supports or refutes the claim. The online search is refined through a coreference resolution system.
 - A bias detector, to determine whether a reported article suffered from a political bias
 - An ideology detector, to evaluate the political leaning of a text
 
For most of these classifiers I couldn't find many high-quality datasets, so I had to often build them myself.
The two main sources were:
 - Google Fact-Check API, used for the agreement predictor, from which I built a dataset of roughly 50,000 fact-checking articles, each with its respective claim.
 - Reddit, used to collect articles of different kinds (low-quality, biased, left, right)
 
On top of this part of the work, I performed some experiments to test the performances of BERT, Google's language model that I used throghout the development of *fastidiouscity*.
The experiments were dedicated to analyze:
 - the multilingual performances of BERT, through a comparison between its training results on a multilingual dataset against a monolingual one
 - the multitask performances of BERT, comparing its performances when trained in a multitask environment vs a single task one
