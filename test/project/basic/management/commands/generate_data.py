from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point

from basic.models import (FK, M2M, BaseModel, Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon)
from basic.generate import generate_data


class Command(BaseCommand):
    """
    Generate objects
    """
    def add_arguments(self, parser):
        parser.add_argument('-c', '--count', nargs=1, type=int, default=10, help='Number of objects to create.')
        parser.add_argument('-d', '--delete', action='store_true', dest='delete', help='Delete old data')

    def handle(self, *args, **options):
        count = options['count']
        delete = options['delete']

        model = Point
        print('Generate %s %s objects' % (count, model._meta.verbose_name))

        if delete:
            model.objects.all().delete()

        generate_data(model=model, count=count)
