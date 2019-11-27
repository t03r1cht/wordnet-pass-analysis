## Introduction

## About

Systematic password generation and analysis of the HaveIBeenPwned password hash collection to approximate user password generation patterns.

## Installation

1. Install sgrep if you are running the script on a Linux-based OS (see section below)
1. Install Python requirements: `python -m pip install -r requirements.txt`
1. Download the WordNet corpus: `python main.py --download-wordnet`

Install MongoDB:

```x
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 68818C72E52529D4
```

```x
sudo echo "deb http://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
```

```x
sudo apt-get update
```

```x
sudo apt-get install -y mongodb-org
```

```x
sudo systemctl start mongod
sudo systemctl enable mongod
```

Open Mongo shell

```x
mongo
```

## Matplotlib and Ubuntu

When running something using `matplotlib` on Ubuntu, make sure you set the display environment variable properly.

```x
export DISPLAY=localhost:0.0
```

## Alternative to 'look'

`sgrep` seems to be an efficient and reliable alternative to the 64-bit 
look utility provided MacOS.

[Archive](https://sourceforge.net/projects/sgrep/)

Compiling: `cd sgrep/ && make`
Add sgrep to PATH: `PATH=$PATH:/opt/sgrep`


## To Do
- [ ] Fix (unused) imports
- [ ] Write proposition on how to classify Synsets in WordNet (is a cat and dog an animal (level + 1) or rather a vertebrae (level + 2)?)
- [ ] Transform WordNet recursion to iteration, since iterations are generally more CPU intensive than iterations (each recursion step reserves its own stack frame)
