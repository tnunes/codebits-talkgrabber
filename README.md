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
$ ./gimme_the_talks.py -t 199 218 221
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
usage: gimme_the_talks.py [-h] [-l] [-t talk-id [talk-id ...]] [-d]

Downloads Codebits Talks videos and presentations. Fetches all talks by
default. Give talk IDs for selective download.

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            List available talks and exit
  -t talk-id [talk-id ...], --talks talk-id [talk-id ...]
                        IDs of talks to download
  -d, --discard-metadata
                        Don't store .json files with talk metadata

```


License
-------

Do What The Fuck You Want To Public License
