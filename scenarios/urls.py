from django.conf.urls import patterns, url
from views import (sdc_analysis, delete_design, get_attributes, get_scenarios,
                   get_leaseblocks, get_leaseblock_features,
                   share_design, copy_design, get_selections) 

urlpatterns = patterns('',
    # feature reports
    # user requested sdc analysis
    url(r'sdc_report/(\d+)', sdc_analysis, name='sdc_analysis'),
    # user deletes scenario (or cancels empty geometry result)
    url(r'delete_design/(?P<uid>[\w_]+)/$', delete_design), 
    # get attributes for a given scenario
    url(r'get_attributes/(?P<uid>[\w_]+)/$', get_attributes), 
    url(r'get_scenarios$', get_scenarios),
    url(r'get_leaseblocks$', get_leaseblocks),
    url(r'share_design$', share_design),
    url(r'copy_design/(?P<uid>[\w_]+)/$', copy_design),
    url(r'get_selections$', get_selections),
    url(r'get_leaseblock_features$', get_leaseblock_features)
)
