## To Do

- [X] Permutations of each lemma
- [X] Plot the results
- [X] Subsume the hit results for each class. Subsume only the "vanilla" lemmas or also their translations?
- [X] Don't replace result files, but rather create a new file for each run (using the date, keyword, command etc.)
- [X] Cat term "bug"
- [X] Replace update_stats by simple spinner
- [X] Count passwords which have not been found
- [X] Check other password brute force tools like John the Ripper or Hashcat which password variations they use
- [X] Show classes of each lemma
- [X] Better form of result visualization in results.txt
- [X] Show synset synonyms in synset selection menu
- [X] Only allow nouns in synset selection menu
- [ ] Combine all permutators with each other
- [ ] Flush memory to the disk if the script is supposed to run for a long time
- [ ] Create flat password lists, classify them as well
- [ ] Port OpenBSD/Darwin look tool to Linux
- [X] Problem with not_found, found does not add up to total_found
- [ ] Write paper about this
- [ ] Visualize Wordnet with hyperbolic tree (hypertree)

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