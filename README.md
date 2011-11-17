Codebits TalkGrabber
====================

* Attended Codebits but couldn't watch all the talks?
* Did not attend Codebits but want to watch the talks at home?

This Python script helps you download talks videos and presentation files.

Talk details are retrieved from the Codebits API (https://codebits.eu/s/api)
and videos are downloaded as MP4 files from Sapo Videos (http://videos.sapo.pt).


Requirements
------------

* Python 2.5 - 2.7

No additional dependencies are required, unless you use Python 2.5, in which
case you need ```simplejson```.

A separate script version is available for Python 3 under the ```python3```
branch.

Usage
-----

To fetch all talks just:
```
$ ./gimme_the_talks.py
```

List available talks using:
```
$ ./gimme_the_talks.py -l
```

To fetch only some talks use:
```
$ ./gimme_the_talks.py 199 218 221
```
where 199, 218 and 221 are IDs of talks you want to download.

By default talk metadata is stored as .json files alongside the videos. To
skip creation of those files, use:
```
$ ./gimme_the_talks.py -d
```

Help:

```
$ ./gimme_the_talks.py -h
Usage: gimme_the_talks.py [options] [talk-x-id talk-y-id ...]

Downloads Codebits Talks videos and presentations. By default fetches all
talks. Give talk IDs as arguments for selective download.

Options:
  -h, --help            show this help message and exit
  -l, --list            list available talks and exit
  -d, --discard-metadata
                        don't save talk metadata as .json files

```


License
-------

Copyright (C) 2011 Tiago Nunes

Licensed under the MIT License