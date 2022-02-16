class SliderImage {
    // ����: ID, ������, ����� ��� ��������
    constructor(ID, imgSrc, subText) {
        this.ID = ID;
        this.imgSrc = imgSrc;
        this.subText = subText;
    }
}

const sliderPicChange = (direction) => {
    // DOM elements
    const sliderDOMElem = document.getElementById('slider');
    const sliderDOMImgElem = sliderDOMElem.getElementsByClassName('slider-img')[0];
    const sliderDOMTextElem = sliderDOMElem.getElementsByClassName('slider-text')[0];
    // �� DOM �������� ���������� ID �������� �������
    let picId = parseInt(sliderDOMElem.dataset.picId);
    const newPic = getImgInfoFromDB(picId, direction); // �������� ����� ������ ��������
    // changing DOMs
    sliderDOMElem.dataset.picId = newPic.ID;
    sliderDOMImgElem.src = 'img/' + newPic.imgSrc;
    sliderDOMTextElem.innerText = newPic.subText;
}

// ���� �������� - ��������, ����� ����� �������� �� REST ������ �����-���� �����������
const getImgInfoFromDB = (picId, direction) => {
    // �������� � ����� ���� �� ����� ������ � ��
    const allPicObjectsFromDB = [
        {
            id: 1,
            link: '1200x900.jpg',
            text: 'Lorem ipsum dolor sit amet'
        },
        {
            id: 2,
            link: '1200x900_2.jpg',
            text: 'consectetur adipisicing elit. Sed natus'
        },
        {
            id: 3,
            link: '1200x900_3.jpg',
            text: 'doloremque fugiat repudiandae minus alias?'
        }
    ];
    // ��� ������ ����� ����������� ����� ������ �����
    let newPicId = picId + direction;
    if (newPicId > 3) newPicId = 1; // ��������� ����� - ������ ����������
    else if (newPicId < 1) newPicId = 3; // ��������� ����� - � ����� ���������
    let img = null;
    for (let pic of allPicObjectsFromDB) {
        if (pic["id"] === newPicId) {
            img = new SliderImage(pic["id"], pic["link"], pic["text"]);
            break;
        }
    }
    if (img == null) {
        img = new SliderImage(0, 'sample.jpg', 'DEFAULT');
    }
    return img; // � img �� ������ ����� ���������� ��� ���� �� �������� ������ �� ��
}