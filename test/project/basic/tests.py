# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys

from qgis.core import (
    QgsVectorLayer,
    QgsFeatureRequest,
    QgsProviderMetadata,
    QgsProviderRegistry,
    QgsApplication, QgsDataProvider, QgsGeometry)

# QgsApplication() must be created before TestCase.setUp(), otherwise when layer is created,
# it ends with strange segfault in QGuiApplication::font()
# QGIS_PREFIX_PATH environment variable is read by QgsApplication
# QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX_PATH'], True)
qgs = QgsApplication([], False)
qgs.initQgis()

from django.test import TestCase
from basic.models import (FK, M2M, BaseModel, Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon)


from basic.generate import generate_data

# from ....djangoprovider.provider import DjangoProvider  # doesn't work in python3
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
from djangoprovider.provider import DjangoProvider


class ReadTestCase(TestCase):

    def setUp(self):
        model = Point
        generate_data(model=model, count=5)

        print('QGIS settings: %s' % QgsApplication.showSettings())

        registry = QgsProviderRegistry.instance()
        metadata = QgsProviderMetadata(DjangoProvider.providerKey(), DjangoProvider.description(), DjangoProvider.createProvider)
        self.assertTrue(registry.registerProvider(metadata))
        self.assertTrue(registry.providerMetadata(DjangoProvider.providerKey()) == metadata)

    def test_read(self):
        model = Point
        uri = '%s' % self.get_model_full_name(model)
        error_prefix = '%s' % self.get_model_full_name(model)

        print('model %s: %s objects' % (self.get_model_full_name(model), model.objects.all().count()))
        object_iterator = model.objects.all().iterator()

        print('create django provider')
        provider = QgsProviderRegistry.instance().createProvider('django', uri, QgsDataProvider.ProviderOptions())
        self.assertTrue(provider.isValid())
        print('provider valid: %s' % provider.isValid())
        print('provider feature count: %s' % (provider.featureCount()))

        feature_iterator = provider.getFeatures(QgsFeatureRequest())
        for obj in object_iterator:
            feature = next(feature_iterator)
            obj_error_prefix = '%s.%s' % (error_prefix, obj.pk)
            self.assertTrue(feature.id() == obj.pk, '%s: feature id does not match, expected %s, found %s' % (obj_error_prefix, obj.pk+1, feature.id()))
            for qgs_field in feature.fields():
                qgs_value = feature.attribute(qgs_field.name())
                dj_value = getattr(obj, qgs_field.name())
                # print('%s %s: %s x %s' % (obj_error_prefix, qgs_field.name(), dj_value, qgs_value))
                self.assertTrue(qgs_value == dj_value,
                                '%s attribute %s value does not match, expected %s (type %s), found %s (type %s)' %
                                (obj_error_prefix, qgs_field.name(), dj_value, type(dj_value), qgs_value, type(dj_value)))

                qgs_geo = QgsGeometry()
                qgs_geo.fromWkb(obj.geo_field.wkb.tobytes())
                self.assertTrue(feature.geometry().equals(qgs_geo), '%s geometry does not match, expected %s, found %s' % (obj_error_prefix, obj.geo_field.wkt, feature.geometry().asWkt()))

        print('create django layer')
        layer = QgsVectorLayer(uri, 'test', 'django')
        print('layer valid: %s' % layer.isValid())
        self.assertTrue(layer.isValid())

    def get_model_full_name(self, model):
        return '%s.%s' % (model._meta.app_label, model._meta.model_name)
