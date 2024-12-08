import random
import re
from collections import OrderedDict
from datetime import datetime

from flask import url_for

from yacut import db
from yacut.constants import (
    EFFORT,
    LEN_SHORT,
    MAX_LEN_ORIGINAL,
    MAX_LEN_SHORT,
    PATTERN_FOR_CHECK_URL,
    STR_FOR_GEN_URL
)
from yacut.error_handlers import URLValidationError


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_LEN_ORIGINAL), nullable=False)
    short = db.Column(db.String(MAX_LEN_SHORT), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def from_dict(self, data):
        self.original = data['url']
        self.short = data['custom_id']

    def to_dict(self):
        return OrderedDict([
            ("url", self.original),
            ("short_link", url_for('redirect_short_url',
                                   url=self.short, _external=True))
        ])

    @staticmethod
    def get_unique_short_id():
        """Генератор короткой ссылки."""
        for _ in range(EFFORT):
            short_url = ''.join(random.choices(
                population=STR_FOR_GEN_URL,
                k=LEN_SHORT
            ))
            if URLMap.query.filter_by(short=short_url).first() is None:
                return short_url
        raise RuntimeError(f'Не удалось создать ссылку ({EFFORT} попыток).')

    @staticmethod
    def obj_short(url):
        """Короткая ссылка - объект."""
        return URLMap.query.filter_by(short=url).first()

    @staticmethod
    def validate_data(data):
        """Валидация полей модели."""
        if not data.get('custom_id'):
            data['custom_id'] = URLMap.get_unique_short_id()
        if re.search(PATTERN_FOR_CHECK_URL, data['custom_id']) is None:
            raise URLValidationError(
                'Указано недопустимое имя для короткой ссылки'
            )
        if URLMap.obj_short(data['custom_id']) is not None:
            raise URLValidationError(
                'Предложенный вариант короткой ссылки уже существует.'
            )
        return data

    @staticmethod
    def create_obj(data):
        """Создания объекта."""
        data = URLMap.validate_data(data)
        url_obj = URLMap(original=data['url'], short=data['custom_id'])
        db.session.add(url_obj)
        db.session.commit()
        return url_obj
