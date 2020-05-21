try:
    from django.urls import re_path, include
except ModuleNotFoundError as e:
    from django.conf.urls import url as re_path, include

# from . import views
from .views import (sdc_analysis, delete_design, get_attributes, get_scenarios,
                   get_leaseblocks, get_leaseblock_features,
                   share_design, copy_design, get_selections, ExportShapefile,
                   ExportGeoJSON, ExportWKT, ExportKML)

urlpatterns = [
    #'',
    # feature reports
    # user requested sdc analysis
    re_path(r'sdc_report/(\d+)', sdc_analysis, name='sdc_analysis'),
    # user deletes scenario (or cancels empty geometry result)
    re_path(r'delete_design/(?P<uid>[\w_]+)/$', delete_design),
    # get attributes for a given scenario
    re_path(r'get_attributes/(?P<uid>[\w_]+)/$', get_attributes),
    re_path(r'get_scenarios$', get_scenarios),
    re_path(r'get_leaseblocks$', get_leaseblocks),
    re_path(r'share_design$', share_design),
    re_path(r'copy_design/(?P<uid>[\w_]+)/$', copy_design),
    re_path(r'get_selections$', get_selections),
    re_path(r'get_leaseblock_features$', get_leaseblock_features),

    re_path(r'export/shp/(?P<feature_id>[\w_]+).zip$',
        ExportShapefile.as_view(), name='export_shp'),
    re_path(r'export/geojson/(?P<feature_id>[\w_]+).geojson$',
        ExportGeoJSON.as_view(), name='export_geojson'),
    re_path(r'export/wkt/(?P<feature_id>[\w_]+)-wkt.txt',
        ExportWKT.as_view(), name='export_wkt'),
    re_path(r'export/kml/(?P<feature_id>[\w_]+).kml',
        ExportKML.as_view(), name='export_kml'),
]
