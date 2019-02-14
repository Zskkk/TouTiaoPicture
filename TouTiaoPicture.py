import requests
from urllib.parse import urlencode
import os
from hashlib import md5
from multiprocessing.pool import Pool

GROUP_START = 1
GROUP_END = 5

def get_page(offset,keyword):
    """
    拿到json
    :param offset:
    :return:
    """
    params = {
        'aid': '24',
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis'
    }
    url ='https://www.toutiao.com/api/search/content/?' + urlencode(params)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None

def get_image(json):
    """
    得到每一张图片
    :param json:
    :return:
    """
    data = json.get('data')
    if data:
        for item in data:
            #print(item)
            image_list = item.get('image_list')
            title = item.get('title')
            #print(image_list)
            if image_list:
                for image in image_list:
                    yield {
                        'image': image.get('url'),
                        'title': title
                    }

def save_image(item):
    """
    保存图片
    :param item:
    :return:
    """
    if not os.path.exists(item.get('title')):
        os.mkdir(item.get('title'))
    try:
        local_image_url = item.get('image')
        new_iamge_url = local_image_url.replace('list', 'large')
        response = requests.get(new_iamge_url)
        if response.status_code == 200:
            file_path = '{0}/{1}.{2}'.format(item.get('title'), md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                print('已经下载', file_path)
    except requests.ConnectionError:
        print('下载图片失败')

def main(offset):
    json = get_page(offset, '街拍')
    for item in get_image(json):
        print(item)
        save_image(item)

if __name__ == '__main__':
    """
    开启线程池
    """
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
    pool.map(main, groups)
    pool.close()
    pool.join()
