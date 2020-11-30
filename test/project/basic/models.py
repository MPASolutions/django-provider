# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis.db import models

SRID = 3857


class FK(models.Model):
    integer_field = models.IntegerField(blank=True, null=True, verbose_name="Integer")
    char_field = models.CharField(max_length=100, blank=True, verbose_name='Character')


class M2M(models.Model):
    integer_field = models.IntegerField(blank=True, null=True, verbose_name="Integer")
    char_field = models.CharField(max_length=100, blank=True, verbose_name='Character')


class BaseModel(models.Model):
    """
    Abstract base class with the same set of fields
    """
    boolean_field = models.BooleanField()
    null_boolean_field = models.BooleanField(blank=True, null=True)
    small_integer_field = models.SmallIntegerField(blank=True, null=True, verbose_name="Small Integer")
    integer_field = models.IntegerField(blank=True, null=True, verbose_name="Integer")
    float_field = models.FloatField(blank=True, null=True, verbose_name='Float')
    decimal_field = models.DecimalField(blank=True, null=True, decimal_places=5, max_digits=15, verbose_name='Decimal')
    char_field = models.CharField(max_length=100, blank=True, verbose_name='Character')
    choice_field = models.CharField(max_length=10, blank=True, choices=(('a', 'A'), ('b', 'B')), verbose_name='Choice')
    text_field = models.TextField(blank=True, verbose_name='Text')
    date_field = models.DateField(blank=True, null=True, verbose_name='Date')
    time_field = models.TimeField(blank=True, null=True, verbose_name='Time')
    date_time_field = models.DateTimeField(blank=True, null=True, verbose_name='Date Time')
    fk_field = models.ForeignKey('FK', blank=True, null=True, verbose_name='Foreign Key' )
    m2m_field = models.ManyToManyField('M2M', blank=True, verbose_name='Many To Many')

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s.%s.%s' % (self._meta.app_label, self._meta.model_name, self.pk)


class Point(BaseModel):
    geo_field = models.PointField(blank=True, null=True, srid=SRID)


class MultiPoint(BaseModel):
    geo_field = models.MultiPointField(blank=True, null=True, srid=SRID)


class LineString(BaseModel):
    geo_field = models.LineStringField(blank=True, null=True, srid=SRID)


class MultiLineString(BaseModel):
    geo_field = models.MultiLineStringField(blank=True, null=True, srid=SRID)


class Polygon(BaseModel):
    geo_field = models.PolygonField(blank=True, null=True, srid=SRID)


class MultiPolygon(BaseModel):
    geo_field = models.MultiPolygonField(blank=True, null=True, srid=SRID)