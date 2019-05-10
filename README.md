## To Do

- [X] Permutations of each lemma
- [X] Plot the results
- [X] Subsume the hit results for each class. Subsume only the "vanilla" lemmas or also their translations?
- [X] Don't replace result files, but rather create a new file for each run (using the date, keyword, command etc.)
- [X] Cat term "bug"
- [ ] Count passwords which have not been found
- [ ] Check other password brute force tools like John the Ripper or Hashcat which password variations they use
- [ ] Visualize Wordnet with hyperbolic tree (hypertree)
- [ ] Make results.txt results.json
- [X] Show classes of each lemma
- [X] Better form of result visualization in results.txt
- [ ] Write paper about this


## Issues

## look for big files

Using look on big files (bigger than 2^31-1) works fine on MacOS since MacOS supplies the user with a 64 bit look command. However, Ubuntu saddled the user with a 32 bit look utility.

Fix here: https://github.com/stuartraetaylor/bsdmainutils-look
