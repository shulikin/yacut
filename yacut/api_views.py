from http import HTTPStatus

from flask import jsonify, request

from yacut import app
from yacut.error_handlers import InvalidAPIUsage, URLValidationError
from yacut.models import URLMap


@app.route('/api/id/', methods=['POST'])
def generate_short_url():
    """API генерации short ссылки."""
    if not request.data or not (data := request.get_json()):
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    try:
        url_obj = URLMap.create_obj(data)
    except URLValidationError as error:
        raise InvalidAPIUsage(error.message)
    return jsonify(url_obj.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<string:url>/', methods=['GET'])
def get_original_url(url):
    """API получение ссылки."""
    url_obj = URLMap.obj_short(url)
    if url_obj is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_obj.original}), HTTPStatus.OK
