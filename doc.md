## Dokumentation

### Aufrufparameter

- `-p/--pass-database`: Pfad zur HIBP-Passwortdatei
- `-d/--depth`: Zieltiefe für die WordNet-Iteration
- `-c/--classification`: Erstellung einer Klassifikation bei WordNet-Iteration (bspw. Subsummierung der Hits)
- `-s/--root-syn-name`: Start-Synset bei WordNet-Iteration, falls nicht bei entity.n.01 gestartet werden soll
- `-l/--from-lists`: Pfad zu Wortlisten bzw. Angabe einer bestimmten Liste
- `-z/--download-wordnet`: Download the WordNet corpus
- `-t/--lookup-utility`: Instead of `look`, use `sgrep`. The path to the sgrep binary must be put into the PATH environment variable
- `-v/--verbose`: Verbose output
- `--purge-db`: Clean all Mongo collections before starting the actual operation
- `--top`: Used for plotting. Limit the number of top values to display
- `--plot`: Plot the graphs.
- `--misc_list`: Lookup miscellaneous word lists, preferably existing word lists from other bruteforcers. Will not generate any word permutations.

### Hauptfunktionalitäten

#### WordNet Lookups

#### Custom List Lookups

#### Data Visualization