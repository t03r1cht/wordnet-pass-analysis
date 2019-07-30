# Dokumentation

## Aufrufparameter

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

## Hauptfunktionalitäten

### WordNet Lookups

Das Skript verwendet das WordNet als Basis, um verschiedene Passwörter zu generieren. Dazu verwendet es den WordNet Korpus des `nltk` Packages. 

Das WordNet enthält die semantischen Relationen verschiedener Wortarten der englischen Sprache. Visualisiert wird das WordNet als ein gerichteter, azyklischer Graph (Directed acyclic graph, DAG). Im Kontext des WordNet werden die Knoten in diesem gerichteten Graphen als _Synonym Sets_ (kurz: _Synsets_) bezeichnet. Jedes Synset besitzt eine eindeutige ID, die unter Anderem aus dem Bezeichner besteht, als auch eine Menge (null oder mehrere) zu diesem Bezeichner zugehöriger Synonyme, auch _Lemmas_ genannt.

Der WordNet-Graph wird in Schichten aufgeteilt, wobei der Wurzelknoten auf Schicht 0 angesiedelt ist.

![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Struktur des WordNets")

Um verschiedene Passwörter mithilfe des WordNets zu generieren, läuft das Skript das gesamte WordNet, beginnend beim Wurzelknoten `entity.n.01`, ab. Für jeden begegneten Knoten werden dessen Lemmas ermittelt. Mit jedem Lemma als Wortbasis werden anschließend verschiedene Permutationen gebildet. Besonders ist hierbei, dass nicht ausschließlich naiv permutiert, sondern ebenfalls verschiedene Permutationen miteinander kombiniert werden, wie im folgenden Beispiel dargestellt.

```x
Wortbasis w: password

Permutation p: Leetspeak
Ergebnis: p(w) = p4ssw0rd

Permutation p1: Ziffernsuffix
Permutation p2: Leetspeak
Ergebnis: p1(p2(w)) = p4ssw0rd123456
```



#### Permutatoren

#### Kombinatoren

### Custom List Lookups

### Data Visualization

