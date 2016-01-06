#!/usr/bin/env python

import argparse
import multiprocessing
import requests
import sys
from os import path, makedirs

API_URL = 'https://api.vk.com/method'
API_VERSION = '5.5'


class VKException(Exception):
    pass


def request_api(method, params=None):
    req_params = {'v': API_VERSION}
    if params is not None:
        req_params.update(params)
    response = requests.get('{}/{}'.format(API_URL, method), params=req_params)
    data = response.json()
    if 'error' in data:
        raise VKException(u'Code - {error_code}. Message - {error_msg}'.format(**data['error']))
    return data['response']


def decode_input(value):
    return value.decode(sys.getfilesystemencoding())


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('owner', help='owner name or id', type=decode_input)
    parser.add_argument('-u', help='owner is user', action='store_true', dest='source_is_user')
    parser.add_argument('-a', '--album', nargs='*', type=int,
                        help='specify album ids to download. if it is empty, user albums list will be printed')
    parser.add_argument('-p', '--path', help='specify path to save photos', type=decode_input,
                        default=path.join(path.dirname(path.abspath(__file__)), 'download/'))
    return parser


def get_download_dir(dir_path, subdir=None):
    abs_path = path.abspath(dir_path)
    if subdir is not None:
        abs_path = path.join(abs_path, subdir)
    if not path.exists(abs_path):
        makedirs(abs_path)
    return abs_path


def downloader(bits):
    pos, url, pos_len, download_dir = bits
    response = requests.get(url, stream=True)
    ext = url.split('.')[-1]
    pos = str(pos + 1).rjust(pos_len, '0')
    file_name = u'{}/{}.{}'.format(download_dir, pos, ext)
    with open(file_name, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)


def download_photos(**kwargs):
    method, params = 'groups.getById', {'group_id': kwargs['owner']}
    if kwargs['source_is_user']:
        method, params = 'users.get', {'user_ids': kwargs['owner']}

    try:
        owner_info = request_api(method, params=params)[0]
    except VKException:
        print(u'Can\'t find owner with name or id {}'.format(kwargs['owner']))
    else:
        owner_id = owner_info['id']
        if not kwargs['source_is_user']:
            owner_id = '-{}'.format(owner_id)

        albums = request_api('photos.getAlbums', params={'owner_id': owner_id})

        if not kwargs['album']:
            print('Album list\n\nid\t\ttitle')
            print('-' * 80)
            for album in albums['items']:
                try:
                    print(u'{id}\t{title}'.format(**album))
                except UnicodeEncodeError:
                    print(u'{id}\tUNKNOWN TITLE'.format(**album))
            return

        queue = []
        for down_album in kwargs['album']:
            if any(down_album == album['id'] for album in albums['items']):
                download_dir = get_download_dir(kwargs['path'], str(down_album))

                print(u'Album {} will be saved to {}'.format(down_album, download_dir))

                photos = request_api('photos.get', params={'owner_id': owner_id, 'album_id': down_album})

                photos_count = photos['count']
                pos_len = len(str(photos_count))
                photo_suffixes = ['2560', '1280', '807', '604', '130', '75']

                for pos, photo in enumerate(photos['items']):
                    for suffix in photo_suffixes:
                        key = 'photo_{}'.format(suffix)
                        if key in photo:
                            queue.append((pos, photo[key], pos_len, download_dir))
                            break
            else:
                print('Wrong album id {}'.format(down_album))

        if queue:
            pool = multiprocessing.Pool()
            pool.map(downloader, queue)


if __name__ == '__main__':
    args_parser = create_parser()
    args = args_parser.parse_args()
    download_photos(**vars(args))
