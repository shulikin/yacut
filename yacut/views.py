from flask import flash, redirect, render_template, url_for

from . import app
from .error_handlers import URLValidationError
from .forms import URLForm
from .models import URLMap


@app.route('/', methods=('GET', 'POST'))
def page_for_generate_url():
    """Форма генерации."""
    form = URLForm()
    if form.validate_on_submit():
        data = dict(
            url=form.original_link.data,
            custom_id=form.custom_id.data
        )
        try:
            url_obj = URLMap.create_obj(data)
        except URLValidationError as error:
            flash(error.message, 'error')
            return render_template('index.html', form=form)
        flash(url_for('redirect_short_url',
                      url=url_obj.short,
                      _external=True), 'url')
    return render_template('index.html', form=form)


@app.route('/<string:url>')
def redirect_short_url(url):
    """Переадресация с короткой на оригинальную ссылку."""
    return redirect(
        URLMap.query.filter_by(short=url).first_or_404().original
    )
