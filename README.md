Codebits TalkGrabber
====================

* Attended Codebits but couldn't watch all the talks?
* Did not attend Codebits but want to watch the talks at home?

This simple Python script downloads all talks videos and presentation files
for you.


Usage
-----

To fetch all talks just:
``` bash
gimme_the_talks.py
```

List the available talks using:
``` bash
gimme_the_talks.py -l
```

To fetch only some talks use:
``` bash
gimme_the_talks.py 199 218 221
```

Talk details are retrieved from the Codebits API (https://codebits.eu/s/api)
and videos are downloaded as MP4 files from Sapo Videos (http://videos.sapo.pt).

License
-------

Copyright 2011 (C) Tiago Nunes

Licensed under the MIT License