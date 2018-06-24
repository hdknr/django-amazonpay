try:
    from django.core.urlresolvers import reverse
except:
    from django.urls import reverse

from django.template import Template, Context, loader
from django.template.loader import get_template
from django.utils import timezone
from functools import reduce
import os


def admin_change_url_name(model):
    return 'admin:{0}_{1}_change'.format(
            model._meta.app_label, model._meta.model_name, )


def admin_change_url(instance):
    return reverse(admin_change_url_name(instance), args=[instance.id])


def find_template(dirname, basename):
    return get_template(os.path.join(dirname, basename))


def render(src, request=None, **kwargs):
    return Template(src).render(Context(kwargs))


def render_by(name, request=None, **kwargs):
    return loader.get_template(name).render(context=kwargs)


def value_from_dict(data, *keys):
    return reduce(
        lambda r, i: (isinstance(r, str) and data.get(r, {}) or r)[i], keys)


def value_from_response(response, *keys):
    try:
        path = './' + '/{}'.format(response._ns).join([''] + list(keys))
        data = response._etree_to_dict(response._root.find(path))
        return data[keys[-1]]
    except:
        return None


def datekey(now=None, salt=None):
    now = now or timezone.localtime(timezone.now())
    salt = salt or now.microsecond
    key = u"{}-{:04x}".format(now.strftime('%y%m%d-%H%M%S'), salt)
    return key
