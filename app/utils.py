import json
import ntpath
import shutil
import os
from PIL import Image
from datetime import datetime
from resizeimage import resizeimage

from werkzeug.utils import secure_filename

import config
import os
from . import app


#  ORM To Json
def sliderImg_list_to_json(slider_img_list):
    arr = []
    for rec in slider_img_list:
        temp = sliderImg_to_json(rec)
        arr.append(temp)
    return json.dumps(arr)


def sliderImg_to_json(slider_img):
    return {
        'id': slider_img.id,
        'ref': slider_img.ref,
        'inner_text': slider_img.inner_text
    }


# закачка в папку new
def store_img_new(file):
    res = {}
    MAX_WIDTH = 1200
    filename = f'{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}'
    i = 1
    while True:
        url_new = f'{config.UPLOAD_FOLDER}{filename}-{i}.jpg'
        path_new = app.root_path + url_new
        if not os.path.isfile(path_new):
            break
        i+=1
    with Image.open(file) as orig_image:
        orig_width = orig_image.width
        if orig_width > MAX_WIDTH:
            # resize to 1200 by width
            # TODO по хорошему чтоб не скакали блоки, надо и по высоте задуматься о строгом ограничении и вырезать верхние и нижние края после ресайза
            # TODO и увеличивать изображение тоже было бы неплохо
            # все это - низкий приоритет. скорее всего, там всегда на вход будут подавать 8000х6000px
            ratio = orig_width / MAX_WIDTH
            # целочисленное деление //, т.к. предвижу проблемы при сохранении дробного числа как количества пикселей
            recalc_height = orig_image.height // ratio
            recacl_size = (MAX_WIDTH, recalc_height)
            new_image = resizeimage.resize_cover(orig_image, recacl_size, Image.ANTIALIAS)
            new_image.save(path_new)  # сохраняется в папку new
        else:
            orig_image.save(path_new)  # сохраняется в папку new
    res['filename'] = filename
    res['url_new'] = url_new
    return res


# закачка в постоянное хранилище с папки new
def copy_from_new(tempRef):
    oldRef = app.root_path + tempRef
    file_name = ntpath.basename(oldRef)
    newRef = app.root_path + config.SLIDER_PATH + file_name
    shutil.copy(oldRef, newRef)
    os.remove(oldRef)
    return file_name


# проверка корректности расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS
