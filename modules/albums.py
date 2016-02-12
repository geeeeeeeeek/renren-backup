import json
import re
from lxml import html

from pip._vendor import requests, os


def get_headers(cookie):
    headers = {'Accept'         : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, sdch',
               'Accept-Language': 'en,en-US;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
               'Connection'     : 'keep-alive',
               'Cache-Control'  : 'max-age=0',
               'Host'           : 'photo.renren.com',
               'User-Agent'     : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36',
               'Cookie'         : cookie}
    return headers


def get_albums(response):
    parsed_body = html.fromstring(response.text)
    js = parsed_body.xpath('//script/text()')
    js = map(lambda x: x.encode('utf-8'), js)

    album_js = js[3]
    album_raw = re.findall(r"'albumList':\s*(\[.*?\]),", album_js)[0]
    album_list = json.loads(album_raw)

    for album in album_list:
        album['albumUrl'] = 'http://photo.renren.com/photo/%s/album-%s/v7' % (album['ownerId'], album['albumId'])
    return album_list


def get_images(album, headers):
    response = requests.get(album['albumUrl'], headers=headers)
    parsed_body = html.fromstring(response.text)
    js = parsed_body.xpath('//script/text()')
    text = js[3].encode('utf-8')
    image_raw = re.findall(r"'photoList':\s*(\[.*?\]),", text)[0]
    image_list = json.loads(image_raw)
    return image_list


def download_images(images, path):
    path = path.replace(' ', '_')

    if not os.path.exists(path):
        os.makedirs(path)

    for image in images:
        image_type = re.findall(r"(\.[a-z|A-Z]*)$", image['url'])[0]
        image_name = "%s%s" % (image['photoId'], image_type)

        response = requests.get(image['url'])
        with open('%s/%s' % (path, image_name), 'wb') as f:
            f.write(response.content)

    print "Downloaded %s images in this album." % (len(images))


def backup_albums(config):
    print '== Module: Albums Backup. This may take a while.'

    user_albums_url = 'http://photo.renren.com/photo/%s/albumlist/v7' % (config.get('user', 'id'))
    headers = get_headers(config.get('user', 'cookie'))
    response = requests.get(user_albums_url, headers=headers)

    albums = get_albums(response)
    count = 1
    total = len(albums)

    for album in albums:
        print '>> [%s/%s] Downloading album `%s`...' % (count, total, album['albumName'])

        images = get_images(album, headers)
        album_dir = '%s/albums/%s' % (config.get('user', 'id'), album['albumName'])
        download_images(images, album_dir)

        count += 1

    print '== Module: Albums Backup. Finished all tasks.'
