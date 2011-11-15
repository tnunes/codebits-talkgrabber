#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# from codebits import talks

'''
Codebits TalkGrabber

Fetches Codebits talks videos and presentation files.
 Talk details come from the Codebits API.

@version: 0.1
@author: Tiago Nunes (@tsbnunes) <tiago.nunes [at] ua.pt>
@license: MIT License

Copyright (C) 2011 Tiago Nunes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the 'Software'), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import urllib2
try: import simplejson as json
except ImportError: import json
import re
import os
import sys


CALENDAR_SERVICE_URL = 'https://services.sapo.pt/Codebits/calendar'
VIDEO_FILE_SUFFIX = '/mov/1'
UNSAFE_FILENAME_REGEX = re.compile('[^a-zA-Z0-9_\-() ]+')
BUFFER_SIZE = 8192 # for downloaded files


def fetch_json(url):
    '''
    Fetch JSON content as a dictionary
    '''
    return json.load(urllib2.urlopen(url))

def fetch_calendar(service_url=CALENDAR_SERVICE_URL):
    '''
    Fetch Codebits calendar as a dictionary
    '''
    return fetch_json(service_url)

def video_file_url(video_page_url, suffix=VIDEO_FILE_SUFFIX):
    '''
    Translate Sapo Videos URL to direct download URL
    '''
    return video_page_url + suffix

def sanitize_filename(filename, blacklist_re=UNSAFE_FILENAME_REGEX,
                      separator='_'):
    '''
    Remove all chars matched by blacklist regex from filename and
    replace all spaces by separator
    '''
    return blacklist_re.sub('', filename).replace(' ', separator)

def download_file(url, filename, buffer_size=BUFFER_SIZE, report_progress=True):
    '''
    Download file to disk, resuming a broken download if possible
    '''
    request = urllib2.Request(url=url)
    response = None
    downloaded_file = None
    try:
        if os.path.exists(filename): # resume download
            downloaded_file = open(filename, 'ab')
            downloaded_bytes = os.path.getsize(filename)
            request.add_header('Range', 'bytes=%s-' % (downloaded_bytes)) 
        else: # start download
            downloaded_file = open(filename, 'wb')
            downloaded_bytes = 0
        
        try:    
            response = urllib2.urlopen(request)
        except Exception, e:
            print >> sys.stderr, "> Couldn't request file at %s - %s" % (url, e)
            return -1
        
        file_size = int(response.headers['Content-Length']) 
        if file_size == 0 or \
           file_size == downloaded_bytes:
            print '> File "%s" is already here. Skipping download' % (filename)
            return 0
        
        if downloaded_bytes > 0:
            if response.headers['Content-Range']:
                print '> File "%s" is partially downloaded. Resuming' \
                      % (filename)
                file_size += downloaded_bytes
            else:
                print '> File "%s" is partially downloaded but server does ' \
                      'not support resume. Restarting download'
                downloaded_file.close()
                downloaded_file = open(filename, 'wb')
                downloaded_bytes = 0
            
        
        while True:
            data = response.read(buffer_size)
            if not data:
                break
            downloaded_file.write(data)
            downloaded_bytes += len(data)
            if report_progress:
                progress = '\r\t%10d/%10d  [%3.2f%%]' \
                    % (downloaded_bytes, file_size,
                       downloaded_bytes * 100. / file_size)
                print progress,
        if report_progress:
            print
        
        return downloaded_bytes
    finally:
        if response: response.close()
        if downloaded_file: downloaded_file.close()
        

def print_talk_summary(talk):
    '''
    Print talk summary to stdout
    '''
    print ' - %s: %s\n' \
          '\tVideo: %s\n' \
          '\tPresentation: %s\n' \
          '\tSlideshare: %s' \
          % (talk['id'], talk['title'],
             talk['video'] or 'NA',
             talk['pfile'] or 'NA',
             talk['slideshare'] or 'NA')

def list_talks(talks):
    '''
    Print talk names and video/presentation/slideshare links to stdout
    '''
    print '> Listing %d talks...' % (len(talks))
    video_count, presentation_count, slideshare_count = 0, 0, 0
    for talk in talks:
        print_talk_summary(talk)
        
        if talk['video']:
            video_count += 1
        if talk['pfile']:
            presentation_count += 1
        if talk['slideshare']:
            slideshare_count += 1
    print '> Stats: %d talks, %d videos, %d presentation files ' \
          'and %d slideshare links' % (len(talks), video_count,
                                       presentation_count, slideshare_count)

def download_talks(talks, store_metadata=True):
    '''
    Download selected talks videos, presentations and slideshare presentations
    '''
    print '> Downloading %d talks...' % (len(talks))
    video_count, presentation_count, slideshare_count = 0, 0, 0
    for talk in talks:
        print_talk_summary(talk)
        
        talk_filename = sanitize_filename(talk['title'])
        if store_metadata:
            talk_metadata_filename = talk_filename + '.json'
            talk_metadata_file = open(talk_metadata_filename, 'wt')
            json.dump(talk, talk_metadata_file, sort_keys=True, indent=4)
            print '> Saved talk %s metadata to %s' % (talk['id'],
                                                      talk_metadata_filename)
            talk_metadata_file.close()

        if talk['video']:
            video_count += 1
            video_url = video_file_url(talk['video'])
            video_file = talk_filename + '.mp4'
            print '> Fetching talk %s video at %s to %s' \
                  % (talk['id'], video_url, video_file)
            download_file(video_url, video_file)
            
#        # No talk has presentation or slideshare link yet, so the code below
#        #  needs to be tested and updated when presentations are available
#                 
#        if talk['pfile']:
#            presentation_count += 1
#            presentation_url = talk['presentation']
#            presentation_file = talk_filename + '.presentation' # FIXME
#            print '> Fetching talk %s presentation at %s to %s' \
#                  % (talk['id'], presentation_url, presentation_file)
#            download_file(presentation_url, presentation_file)
#        if talk['slideshare']:
#            slideshare_count += 1
#            presentation_url = talk['slideshare']
#            presentation_file = talk_filename + '.slideshare' # FIXME
#            print '> Fetching talk %s slideshare presentation at %s to %s' \
#                  % (talk['id'], presentation_url, presentation_file)
#            download_file(presentation_url, presentation_file)

    print '> Stats: %d talks, %d videos, %d presentation files ' \
      'and %d slideshare links' % (len(talks), video_count,
                                   presentation_count, slideshare_count)

def main():
    '''
    Gimme gimme gimme the talks
    '''
    from optparse import OptionParser
    
    usage = 'usage: %prog [options] [talk-x-id talk-y-id ...]'
    description = 'Downloads Codebits Talks videos and presentations. By' \
                  ' default fetches all talks. Give talk IDs as arguments for' \
                  ' selective download.'
    parser = OptionParser(usage=usage, description=description)
    parser.add_option('-l', '--list', action='store_true', dest='list',
                      help='list available talks and exit')
    parser.add_option('-d', '--discard-metadata', action='store_false',
                      dest='store_metadata', default=True,
                      help="don't save talk metadata as .json files")
    
    (options, args) = parser.parse_args()

    print '> Fetching Codebits calendar...',
    sys.stdout.flush()
    try:
        events = fetch_calendar()
    except Exception, e:
        print >> sys.stderr, "\n> Couldn't fetch Codebits calendar - %s" % (e)
        return
    print 'done.'
    
    # events with id are talks
    talks = [event for event in events if 'id' in event]

    if options.list:
        return list_talks(talks)
    
    if args: # selective download
        args = list(set(args)) # remove duplicates
        talk_ids = [talk['id'] for talk in talks if talk['id'] in args]
        if len(talk_ids) != len(args):
            missing_talks = [id for id in args if id not in talk_ids]
            parser.error('No talks with ID(s) %s' % (missing_talks))
        talks = [talk for talk in talks if talk['id'] in talk_ids]
    
    download_talks(talks, options.store_metadata)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
