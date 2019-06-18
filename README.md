## Introduction

## Installation

1. Install sgrep if you are running the script on a Linux-based OS (see section below)
1. Install Python requirements: `python -m pip install -r requirements.txt`
1. Download the WordNet corpus: `python main.py --download-wordnet`

## Alternative to 'look'

`sgrep` seems to be an efficient and reliable alternative to the 64-bit 
look utility provided MacOS.

[Archive](https://sourceforge.net/projects/sgrep/)

Compiling: `cd sgrep/ && make`
Add sgrep to PATH: `PATH=$PATH:/opt/sgrep`


## To Do

- [ ] Write finished lists to intermediate files (Intermediate Lemma List Format `.ill`) so we don't need to lookup those lists again. New lists can be appended as `.ill` files.
  - [ ] Also store the file hash in the `.ill` file so we can detect modifications in already existing lists. If lists that already have corresponding `.ill` files were appended with new lemmas, reload and decode the `.ill` file and only lookup the diff (appended lemmas)
- [ ] Write proposition on how to classify Synsets in WordNet (is a cat and dog an animal (level + 1) or rather a vertebrae (level + 2)?)
- [ ] Transform WordNet recursion to iteration, since iterations are generally more CPU intensive than iterations (each recursion step reserves its own stack frame)

## Done

- [x] Permutations of each lemma
- [x] Plot the results
- [x] Subsume the hit results for each class. Subsume only the "vanilla" lemmas or also their translations?
- [x] Don't replace result files, but rather create a new file for each run (using the date, keyword, command etc.)
- [x] Cat term "bug"
- [x] Replace update_stats by simple spinner
- [x] Count passwords which have not been found
- [x] Check other password brute force tools like John the Ripper or Hashcat which password variations they use
- [x] Show classes of each lemma
- [x] Better form of result visualization in results.txt
- [x] Show synset synonyms in synset selection menu
- [x] Only allow nouns in synset selection menu
- [x] Problem with not_found, found does not add up to total_found
- [x] Combine all permutators with each other
- [x] Create flat password lists, classify them as well
- [X] Add lemma permutation/search statistics to WordNet mode
- [X] Add stats for each word file (for example brands.txt had 40% of all results)
- [X] Add percentages in summary file for each word in list mode
- [X] Show estimated time / progress