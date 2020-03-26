# scrapers

## gov-data-scraper
### Usage
```
source bin/activate
./bin/python gov-data-scraper.py -h
```

## trydash
### Usage
```
source bin/activate
./bin/python trydash.py
```

## flightradar24
### Usage
All flights from China in one click.
Results will be written into 2 csv files. One contains flight details of all airports, the other contains numbers of flights for each airport.
```
source bin/activate
./bin/python flightradar24.py
```

## delete the content of a direct
```
import os
from shutil import rmtree

rmtree('/path/to/folder')
os.makedirs('/path/to/folder')
```