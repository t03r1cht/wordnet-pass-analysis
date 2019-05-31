## To Do

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
- [ ] Port OpenBSD/Darwin look tool to Linux
- [ ] Write paper about this

## Issues

## look for big files

Using look on big files (bigger than 2^31-1) works fine on MacOS since MacOS supplies the user with a 64 bit look command. However, Ubuntu saddled the user with a 32 bit look utility.

Fix here: https://github.com/stuartraetaylor/bsdmainutils-look

# Merging to lists

Universal: https://github.com/danielmiessler/SecLists

Names: https://github.com/dominictarr/random-name

See: https://unix.stackexchange.com/questions/50103/merge-two-lists-while-removing-duplicates

# Plot Ideas

- Average hits per passwords depending on the root synset (animals, vehicles etc.) in a scatter plot
- Distribution of found passwords per class in a scatter plot
- Pct Success/Failure distribution based on the root synset
