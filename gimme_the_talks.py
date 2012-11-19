#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Codebits TalkGrabber

Fetches Codebits talks videos and presentation files.
 Talk metadata comes from the Codebits API.
'''

__version__ = 0.2
__author__ = 'Tiago Nunes (@tsbnunes) <tiago.nunes [at] ua.pt>'
__license__ = 'WTFPL (http://sam.zoy.org/wtfpl/)'


import re
import os
import sys
import urllib2

try:
    import simplejson as json
except ImportError:
    import json


DESCRIPTION = 'Downloads Codebits Talks videos and presentations.' \
              ' Fetches all talks by default. Give talk IDs for' \
              ' selective download.'

CALENDAR_SERVICE_URL = 'https://services.sapo.pt/Codebits/calendar'
VIDEO_FILE_SUFFIX = '/mov/1'
UNSAFE_FILENAME_REGEX = re.compile('[^a-zA-Z0-9_\-() ]+')
BUFFER_SIZE = 8192  # for downloaded files


def argparser():
    '''CLI interface'''
    import argparse

    ap = argparse.ArgumentParser(description=DESCRIPTION)
    ap.add_argument('-l', '--list', dest='list', action='store_true',
                    help='List available talks and exit')
    ap.add_argument('-t', '--talks', nargs='+', dest='talks',
                    type=int, metavar='talk-id',
                    help='IDs of talks to download')
    ap.add_argument('-d', '--discard-metadata', action='store_false',
                    dest='store_metadata', default=True,
                    help='Don\'t store .json files with talk metadata')
    return ap


def fetch_json(url):
    '''Fetch JSON content as a dictionary'''
    return json.load(urllib2.urlopen(url))


def fetch_calendar(service_url=CALENDAR_SERVICE_URL):
    '''Fetch Codebits calendar as a dictionary'''
    return fetch_json(service_url)


def video_file_url(video_page_url, suffix=VIDEO_FILE_SUFFIX):
    '''Translate Sapo Videos URL to direct download URL'''
    return video_page_url + suffix


def sanitize_filename(filename, blacklist_re=UNSAFE_FILENAME_REGEX,
                      separator='_'):
    '''Remove all chars matched by blacklist regex from filename and
    replace all spaces by separator'''
    return blacklist_re.sub('', filename).replace(' ', separator)


def download_file(url, filename, buffer_size=BUFFER_SIZE, report_progress=True):
    '''Download file to disk, resuming a broken download if possible'''
    request = urllib2.Request(url=url)
    response = None
    downloaded_file = None
    try:
        if os.path.exists(filename):  # resume download
            downloaded_file = open(filename, 'ab')
            downloaded_bytes = os.path.getsize(filename)
            request.add_header('Range', 'bytes=%s-' % (downloaded_bytes))
        else:  # start download
            downloaded_file = open(filename, 'wb')
            downloaded_bytes = 0

        try:
            response = urllib2.urlopen(request)
        except Exception, e:
            print >> sys.stderr, "> Error requesting file at %s - %s" % (url, e)
            return

        file_size = int(response.headers['Content-Length'])
        if file_size == 0 or file_size == downloaded_bytes:
            print '> File "%s" is already here. Skipping download' % (filename)
            return

        if downloaded_bytes > 0:
            if 'Content-Range' in response.headers:
                print '> File "%s" is partially downloaded. Resuming' \
                      % (filename)
                file_size += downloaded_bytes
            else:
                print '> File "%s" is partially downloaded but server does ' \
                      'not support resume. Restarting download' \
                      % (filename)
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

    finally:
        if response:
            response.close()
        if downloaded_file:
            downloaded_file.close()


def print_talk_summary(talk):
    '''Print talk summary'''
    print ' - %s: %s\n' \
          '\tVideo: %s\n' \
          '\tPresentation: %s\n' \
          '\tSlideshare: %s' \
          % (talk['id'], talk['title'],
             talk['video'] or 'NA',
             talk['pfile'] or 'NA',
             talk['slideshare'] or 'NA')


def list_talks(talks):
    '''Print talk names and video/presentation/slideshare links'''
    print '> Listing %d talks...' % len(talks)
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
            json.dump(talk, talk_metadata_file, sort_keys=True, indent=True)
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

    print '> Stats: %d talks, %d videos, %d presentation files ' \
      'and %d slideshare links' % (len(talks), video_count,
                                   presentation_count, slideshare_count)


def main():
    '''Gimme gimme gimme the talks'''
    ap = argparser()
    args = ap.parse_args()

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

    if args.list:
        list_talks(talks)
        return

    if args.talks:  # selective download
        args.talks = list(set(args.talks))  # remove duplicates
        talk_ids = [talk['id'] for talk in talks if talk['id'] in args.talks]
        if len(talk_ids) != len(args.talks):
            missing_talks = [id for id in args.talks if id not in talk_ids]
            ap.error('No talks with ID(s) %s' % (missing_talks))
        talks = [talk for talk in talks if talk['id'] in talk_ids]

    download_talks(talks, args.store_metadata)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
