from qgis.core import (
    QgsAbstractFeatureIterator,
    QgsFeatureRequest,
    QgsCoordinateTransform,
    QgsCsException,
    QgsGeometry,
    QgsFeature,
    QgsLogger,
)

from django.db.models import Q
from django.contrib.gis.geos import Polygon


class DjangoFeatureIterator(QgsAbstractFeatureIterator):

    def __init__(self, provider, source, request, is_valid):
        QgsLogger.debug('DjangoFeatureIterator.__init__ source = {}'.format(source), 5)
        super().__init__(request)
        self._request = request if request is not None else QgsFeatureRequest()
        self._provider = provider
        self._source = source
        self._is_valid = is_valid
        self._transform = QgsCoordinateTransform()
        if self._request.destinationCrs().isValid() and self._request.destinationCrs() != self._source.crs:
            self._transform = QgsCoordinateTransform(self._source.crs, self._request.destinationCrs(),
                                                     self._request.transformContext())
        try:
            rect = self.filterRectToSourceCrs(self._transform)
            self._filter_geo = None
            if not rect.isNull():
                self._filter_geo = Polygon.from_bbox((rect.xMinimum(), rect.yMinimum(), rect.xMaximum(), rect.yMaximum()))
        except QgsCsException as e:
            self.close()
            return

        # self._queryset = self._source.model.objects.get_queryset().order_by(self._source.model._meta.pk.name)
        self._queryset = self._provider.get_queryset()
        if self._filter_geo and self._source.dj_geo_field:
            if self._request.flags() & QgsFeatureRequest.ExactIntersect:
                # TODO
                pass
            else:
                self._queryset = self._queryset.filter(Q(('%s__intersects' % self._source.dj_geo_field.name, self._filter_geo)))

        if self._request.filterType() == QgsFeatureRequest.FilterExpression:
            # TODO: compile to Django filter
            pass
        elif self._request.filterType() == QgsFeatureRequest.FilterFids:
            self._queryset = self._queryset.filter(Q(self._source.model._meta.pk.name, self._request.filterFid()))
        elif self._request.filterType() == QgsFeatureRequest.FilterFid:
            self._queryset = self._queryset.filter(
                Q('%s__in' % self._source.model._meta.pk.name, self._request.filterFids()))

        self._iterator = self._queryset.iterator()

        # TODO: attributes subset

    def isValid(self):
        return self._is_valid

    def fetchFeature(self, feature):
        QgsLogger.debug('DjangoFeatureIterator.fetchFeature feature = {}'.format(feature), 0)
        try:
            obj = next(self._iterator)
            feature.setId(obj.pk)  # Only integers supported
            if self._source.dj_geo_field:
                dj_geo = getattr(obj, self._source.dj_geo_field.name)
                qgs_geo = QgsGeometry()
                qgs_geo.fromWkb(dj_geo.wkb.tobytes())
                feature.setGeometry(qgs_geo)
                self.geometryToDestinationCrs(feature, self._transform)
            else:
                feature.setGeometry(None)

            feature.setFields(self._source.qgs_fields)

            # TODO: attributes subset
            for idx, qgs_field in enumerate(self._source.qgs_fields):
                value = getattr(obj, qgs_field.name())  # field names are the same
                # TODO: value conversion required?
                feature.setAttribute( idx, value )
            feature.setValid(True)
            return True
        except StopIteration as e:
            feature.setValid(False)
            return False

    def __iter__(self):
        self.rewind()
        return self

    def __next__(self):
        feature = QgsFeature()
        if not self.nextFeature(feature):
            raise StopIteration
        else:
            return feature

    def rewind(self):
        if self._iterator:
            self._iterator.close()
        self._iterator = self._queryset.iterator()
        return True

    def close(self):
        if self._iterator:
            self._iterator.close()
        return True
