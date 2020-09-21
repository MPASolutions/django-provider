from qgis.core import QgsAbstractFeatureSource, QgsFeatureIterator, QgsLogger
from .iterator import DjangoFeatureIterator


class DjangoFeatureSource(QgsAbstractFeatureSource):

    def __init__(self, provider, model, qgs_fields, dj_fields, dj_geo_field, crs, is_valid):
        QgsLogger.debug('DjangoFeatureSource.__init__ model = {}'.format(model), 10)
        super(DjangoFeatureSource, self).__init__()
        self.provider = provider
        self.model = model
        self.qgs_fields = qgs_fields
        self.dj_fields = dj_fields
        self.dj_geo_field = dj_geo_field
        self.crs = crs
        self.is_valid = is_valid
        self.iterator = None

    def getFeatures(self, request):
        QgsLogger.debug('DjangoFeatureSource.getFeatures() request = {}'.format(request), 10)
        # Returning QgsFeatureIterator(DjangoFeatureIterator(self, request)) without keeping reference to at least
        # QgsFeatureIterator or DjangoFeatureIterator does not work anymore. Asked on QGIS list:
        # https://lists.osgeo.org/pipermail/qgis-developer/2020-August/062076.html
        # It seems to work if wee keep a reference to just latest created iterator (instead of list of iterators)
        # return QgsFeatureIterator(DjangoFeatureIterator(self, request))
        self.iterator = QgsFeatureIterator(DjangoFeatureIterator(self.provider, self, request, self.is_valid))
        return self.iterator
