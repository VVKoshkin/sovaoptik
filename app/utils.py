# �������� ������������ ���������� �����
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

# ������� � ���������� ��������� � ����� new
def copy_from_new(tempRef):
    oldRef = app.root_path + tempRef
    file_name = ntpath.basename(oldRef)
    newRef = app.root_path + config.SLIDER_PATH + file_name
    shutil.copy(oldRef, newRef)
    os.remove(oldRef)
    return file_name
    

# Slider ORM To Json
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