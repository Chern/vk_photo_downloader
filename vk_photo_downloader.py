#!/usr/bin/env python

import argparse
import multiprocessing
import requests
import sys
from os import path, makedirs

API_URL = 'https://api.vk.com/method'
API_VERSION = '5.42'

SIZE_WEIGHTS = {
    's': 1,
    'm': 2,
    'x': 3,
    'y': 4,
    'z': 5,
    'w': 6
}


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
    parser.add_argument('owner', help='name or id of user or community', type=decode_input)
    parser.add_argument('-u', help='specify that owner is user', action='store_true', dest='source_is_user')
    parser.add_argument('-a', '--albums', nargs='*', type=int,
                        help='specify album ids to download. if it is empty and `--download-all` is not provided, '
                             'user albums list will be printed')
    parser.add_argument('--download-all', help='download all available photos', action='store_true')
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
    _id, url, max_digits, download_dir = bits
    response = requests.get(url, stream=True)
    ext = url.split('.')[-1]
    pos = str(_id + 1).rjust(max_digits, '0')
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

        raw_albums = request_api('photos.getAlbums', params={'owner_id': owner_id})
        albums = {album['id']: album['title'] for album in raw_albums['items']}

        if not (kwargs['albums'] or kwargs['download_all']):
            print('Album list\n\nid\t\ttitle')
            print('-' * 80)
            for album_id, album_title in albums.items():
                try:
                    print(u'{}\t{}'.format(album_id, album_title))
                except UnicodeEncodeError:
                    print(u'{}\tUNKNOWN TITLE'.format(album_id))
            return

        existing_album_ids = albums.keys()

        if kwargs['download_all']:
            required_album_ids = existing_album_ids
        else:
            required_album_ids, invalid_album_ids = [], []
            for album_id in kwargs['albums']:
                if album_id in existing_album_ids:
                    required_album_ids.append(album_id)
                else:
                    invalid_album_ids.append(album_id)

            for album_id in invalid_album_ids:
                print('Wrong album id {}'.format(album_id))

        queue = []
        for album_id in required_album_ids:
            download_dir = get_download_dir(kwargs['path'], albums[album_id])

            print(u'Album {} will be saved to {}'.format(album_id, download_dir))

            photos = request_api('photos.get', params={'owner_id': owner_id, 'album_id': album_id, 'photo_sizes': 1})

            photos_count = photos['count']
            max_digits = len(str(photos_count))

            for _id, photo in enumerate(photos['items']):
                sizes = photo['sizes']
                sizes.sort(key=lambda x: SIZE_WEIGHTS.get(x['type'], 0), reverse=True)
                queue.append((_id, sizes[0]['src'], max_digits, download_dir))

        if queue:
            pool = multiprocessing.Pool()
            pool.map(downloader, queue)


if __name__ == '__main__':
    args_parser = create_parser()
    args = args_parser.parse_args()
    download_photos(**vars(args))
