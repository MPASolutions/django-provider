import random, string, sys, datetime

from django.utils import timezone
from django.contrib.gis import geos
from basic.models import (FK, M2M, BaseModel, Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon)

def generate_data(model, count):
    """
    Generate random data
    :param model: Django model
    :param count: Number of objects
    :return:
    """
    for i in range(count):
        obj = model(
            boolean_field=random.choice([True, False]),
            null_boolean_field=random.choice([True, False, None]),
            small_integer_field=random.randint(-32768, 32767),
            integer_field=random.randint(-2147483648, 2147483647),
            float_field=random.uniform(sys.float_info.min, sys.float_info.max),
            decimal_field=random.uniform(-1000000000, 1000000000),
            char_field=generate_string(),
            choice_field=random.choice(['a', 'b']),
            text_field=generate_string(),
            date_field=generate_datetime(),
            time_field=generate_datetime(),
            date_time_field=generate_datetime(),
            geo_field=generate_geo(model._meta.get_field('geo_field')),
            # fk_field =
            # m2m_field =
        )
        obj.save()


def generate_string():
    return ''.join([random.choice(string.ascii_lowercase) for i in range(10)])


def generate_datetime():
    dt = datetime.datetime.utcfromtimestamp(random.randint(0, 2000000000))
    return timezone.make_aware(dt)


def generate_geo(field):
    box = (-20037508.34, -20037508.34, 20037508.34, 20037508.34)  # EPSG 3857 max extent
    if isinstance(field, models.PointField):
        x = random.uniform(box[0], box[2])
        y = random.uniform(box[1], box[3])
        return geos.Point(x, y, srid=SRID)