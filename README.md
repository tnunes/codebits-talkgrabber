Codebits TalkGrabber
====================

* Attended Codebits but couldn't watch all the talks?
* Did not attend Codebits but want to watch the talks at home?

This Python script helps you download talks videos and presentation files.

Talk details are retrieved from the Codebits API (https://codebits.eu/s/api)
and videos are downloaded as MP4 files from Sapo Videos (http://videos.sapo.pt).


Usage
-----

To fetch all talks just:
```
gimme_the_talks.py
```

List available talks using:
```
gimme_the_talks.py -l             # --list
```

To fetch only some talks use:
```
gimme_the_talks.py 199 218 221
```

By default talk metadata is stored as .json files alongside the videos. To
skip the creation of those files, use:

```
gimme_the_talks.py -d             # --discard-metadata
```


License
-------

Copyright 2011 (C) Tiago Nunes

Licensed under the MIT License
