import io
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from features.models import Feature
from features.registry import get_feature_by_uid
from json import dumps
from nursery.geojson.geojson import srid_to_urn, get_feature_json

from django.http import HttpResponse, Http404, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from scenarios.export import geometries_to_shp, create_metadata_xml, zip_objects

from scenarios.models import Scenario, LeaseBlockSelection, LeaseBlock
from django.conf import settings
import json


def sdc_analysis(request, sdc_id):
    from sdc_analysis import display_sdc_analysis
    sdc_obj = get_object_or_404(Scenario, pk=sdc_id)
    # check permissions
    viewable, response = sdc_obj.is_viewable(request.user)
    if not viewable:
        return response
    return display_sdc_analysis(request, sdc_obj)
    

@csrf_exempt
def copy_design(request, uid):
    try:
        design_obj = get_feature_by_uid(uid)
    except Feature.DoesNotExist:
        raise Http404
       
    #check permissions
    viewable, response = design_obj.is_viewable(request.user)
    if not viewable:
        return response
        
    design_obj.pk = None
    design_obj.user = request.user
    design_obj.save()
    
    json = []
    json.append({
        'id': design_obj.id,
        'uid': design_obj.uid,
        'name': design_obj.name,
        'description': design_obj.description,
        'attributes': design_obj.serialize_attributes()
    })
    
    return HttpResponse(dumps(json), status=200)
    

@csrf_exempt
def delete_design(request, uid):
    try:
        design_obj = get_feature_by_uid(uid)
    except Feature.DoesNotExist:
        raise Http404
    
    #check permissions
    viewable, response = design_obj.is_viewable(request.user)
    if not viewable:
        return response
        
    design_obj.delete()
    #design_obj.active = False
    #design_obj.save(rerun=False)
    
    return HttpResponse("", status=200)

@login_required()
def get_scenarios(request):
    json = []
    
    scenarios = Scenario.objects.filter(user=request.user, active=True).order_by('date_created')
    for scenario in scenarios:
        # Allow for "sharing groups" without an associated MapGroup, for "special" cases
        sharing_groups = [group.mapgroup_set.get().name
                          for group in scenario.sharing_groups.all()
                          if group.mapgroup_set.exists()]
        json.append({
            'id': scenario.id,
            'uid': scenario.uid,
            'name': scenario.name,
            'description': scenario.description,
            'attributes': scenario.serialize_attributes(),
            'sharing_groups': sharing_groups
        })
        
    shared_scenarios = Scenario.objects.shared_with_user(request.user)
    for scenario in shared_scenarios:
        if scenario.active and scenario not in scenarios:
            username = scenario.user.username
            actual_name = scenario.user.first_name + ' ' + scenario.user.last_name
            json.append({
                'id': scenario.id,
                'uid': scenario.uid,
                'name': scenario.name,
                'description': scenario.description,
                'attributes': scenario.serialize_attributes(),
                'shared': True,
                'shared_by_username': username,
                'shared_by_name': actual_name
            })
        
    return HttpResponse(dumps(json))

@login_required()
def get_selections(request):
    json = []
    selections = LeaseBlockSelection.objects.filter(user=request.user).order_by('date_created')
    for selection in selections:
        sharing_groups = [group.mapgroup_set.get().name
                          for group in selection.sharing_groups.all()
                          if group.mapgroup_set.exists()]
        json.append({
            'id': selection.id,
            'uid': selection.uid,
            'name': selection.name,
            'description': selection.description,
            'attributes': selection.serialize_attributes(),
            'sharing_groups': sharing_groups
        })
        
    shared_selections = LeaseBlockSelection.objects.shared_with_user(request.user)
    for selection in shared_selections:
        if selection not in selections:
            username = selection.user.username
            actual_name = selection.user.first_name + ' ' + selection.user.last_name
            json.append({
                'id': selection.id,
                'uid': selection.uid,
                'name': selection.name,
                'description': selection.description,
                'attributes': selection.serialize_attributes(),
                'shared': True,
                'shared_by_username': username,
                'shared_by_name': actual_name
            })
        
    return HttpResponse(dumps(json))    
    
'''
'''    
def get_leaseblock_features(request):
    srid = settings.GEOJSON_SRID
    leaseblock_ids = request.GET.getlist('leaseblock_ids[]')
    leaseblocks = LeaseBlock.objects.filter(prot_numb__in=leaseblock_ids)
    feature_jsons = []
    for leaseblock in leaseblocks:
        try:
            geom = leaseblock.geometry.transform(srid, clone=True).json
        except:
            srid = settings.GEOJSON_SRID_BACKUP
            geom = leaseblock.geometry.transform(srid, clone=True).json
        feature_jsons.append(get_feature_json(geom, json.dumps('')))#json.dumps(props)))
        #feature_jsons.append(leaseblock.geometry.transform(srid, clone=True).json)
        '''
        geojson = """{
          "type": "Feature",
          "geometry": %s,
          "properties": {}
        }""" %leaseblock.geometry.transform(settings.GEOJSON_SRID, clone=True).json
        '''
        #json.append({'type': "Feature", 'geometry': leaseblock.geometry.geojson, 'properties': {}})
    #return HttpResponse(dumps(json[0]))
    geojson = """{ 
      "type": "FeatureCollection",
      "crs": { "type": "name", "properties": {"name": "%s"}},
      "features": [ 
      %s 
      ]
    }""" % (srid_to_urn(srid), ', \n'.join(feature_jsons),)
    return HttpResponse(geojson)
    

def get_attributes(request, uid):
    try:
        scenario_obj = get_feature_by_uid(uid)
    except Scenario.DoesNotExist:
        raise Http404
    
    #check permissions
    viewable, response = scenario_obj.is_viewable(request.user)
    if not viewable:
        return response
    
    return HttpResponse(dumps(scenario_obj.serialize_attributes()))

'''
'''    
@csrf_exempt
def share_design(request):
    group_names = request.POST.getlist('groups[]')
    design_uid = request.POST['scenario']
    design = get_feature_by_uid(design_uid)
    viewable, response = design.is_viewable(request.user)
    if not viewable:
        return response
    #remove previously shared with groups, before sharing with new list
    design.share_with(None)
    groups = request.user.mapgroupmember_set.all()
    groups = groups.filter(map_group__name__in=group_names)
    groups = [g.map_group.permission_group for g in groups]
    design.share_with(groups, append=False)
    return HttpResponse("", status=200)
    
'''
'''
@cache_page(60 * 60 * 24, key_prefix="scenarios_get_leaseblocks")
def get_leaseblocks(request):
    json = []
    leaseblocks = LeaseBlock.objects.filter(avg_depth__lt=0.0, min_wind_speed_rev__isnull=False)
    for ocs_block in leaseblocks:
        json.append({
            'id': ocs_block.id,
            #'ais_density': ocs_block.ais_density,
            #'ais_min_density': ocs_block.ais_min_density,
            #'ais_max_density': ocs_block.ais_max_density,
            'ais_mean_density': ocs_block.ais_all_vessels_maj,
            #'min_distance': ocs_block.min_distance,
            #'max_distance': ocs_block.max_distance,
            'avg_distance': ocs_block.avg_distance,
            'awc_min_distance': ocs_block.awc_min_distance,
            'substation_min_distance': ocs_block.substation_min_distance,
            #'awc_max_distance': ocs_block.awc_max_distance,
            #'awc_avg_distance': ocs_block.awc_avg_distance,
            'avg_depth': -ocs_block.avg_depth,
            #'min_depth': meters_to_feet(-ocs_block.min_depth, 1),
            #'max_depth': meters_to_feet(-ocs_block.max_depth, 1),
            'min_wind_speed': ocs_block.min_wind_speed_rev,
            #'max_wind_speed': ocs_block.max_wind_speed_rev,
            'tsz_min_distance': ocs_block.tsz_min_distance,
            #'tsz_max_distance': ocs_block.tsz_max_distance,
            #'tsz_mean_distance': ocs_block.tsz_mean_distance,
            #'wea_name': ocs_block.wea_name,
            #'wea_number': ocs_block.wea_number,
            #'wea_state_name': ocs_block.wea_state_name  
            'uxo': ocs_block.uxo
        })
    return HttpResponse(dumps(json))

class GeometryExporter(View):
    def get_feature(self, feature_id):
        """Get a feature by ID.
        Return tuple of (feature, geometry), or raise 404
        """
        try:
            feature = get_feature_by_uid(feature_id)
        except feature.__class__.DoesNotExist:
            raise Http404()

        if not feature.user == self.request.user:
            # if we don't own the feature, see if it's shared with us
            shared_with_user = feature.__class__.objects.shared_with_user(self.request.user)
            shared_with_user = shared_with_user.filter(id=feature.id)
            if not shared_with_user.exists():
                raise Http404()

        def getattr_alot(obj, attrs, default=None):
            """Return the first attribute that isn't an attribute error,
            or default
            """
            for attr in attrs:
                if hasattr(obj, attr):
                    return getattr(obj, attr, default)
            return getattr(obj, attrs[-1]) # trigger AttributeError

        # Even though the three objects are all subclasses of feature, they
        # all have different names for the variable that they store geometry in.
        # AOIs have "geometry_final", LeaseBlockSelections have 'geometry_actual'
        # and Wind energy ("Scenario") has geometry_dissolved.
        # Write a quick function to keep trying until it finds the right
        # attribute name.
        # A proper fix is, of course, to rename every reference to the same
        # thing instead of inventing new names in subclasses.

        geometry = getattr_alot(feature, ['geometry_final', 'geometry_actual',
                                          'geometry_dissolved'])

        return feature, geometry

class ExportShapefile(GeometryExporter):
    http_method_names = ['get']

    def get(self, request, feature_id):
        """Generate a zipped shape file & return it.
        """

        feature, geometry = self.get_feature(feature_id)
        items = []

        attrs = {'name': feature.name, 'description': feature.description}
        items.extend(geometries_to_shp(feature.name, ((geometry, attrs),)))

        # Other items for the zip file go here.

        zip = zip_objects(items)
        response = HttpResponse(content=zip.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=%s.zip' % feature.name

        return response


class ExportGeoJSON(GeometryExporter):
    http_method_names = ['get']

    def get(self, request, feature_id):
        """Generate a geojson file & return it.
        """
        feature, geometry = self.get_feature(feature_id)

        gj = ('{"type": "Feature",'
              '"crs": { "type": "name", "properties": {"name": "%s"}},'
              '"properties": {}, "geometry": %s}')

        # Transform to 4326. A lot of online tools (http://geojson.io)
        # apparently don't understand anything else.
        geom = geometry.transform(4326, clone=True)
        gj = gj % (srid_to_urn(geom.srid), geom.geojson)

        response = HttpResponse(content=gj, content_type='application/vnd.geo+json')
        response['Content-Disposition'] = 'attachment; filename=%s.geojson' % feature.name

        return response



class ExportWKT(GeometryExporter):
    http_method_names = ['get']

    def get(self, request, feature_id):
        """Generate a WKT string & return it in a text file.
        """
        feature, geometry = self.get_feature(feature_id)

        wkt = geometry.wkt

        response = HttpResponse(content=wkt, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s-wkt.txt' % feature.name

        return response



class ExportKML(GeometryExporter):
    http_method_names = ['get']

    def get(self, request, feature_id):
        """Generate a KML file & return it.
        """
        feature, geometry = self.get_feature(feature_id)

        geom = geometry.transform(4326, clone=True)
        kml = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.1">
<Document>
    <name>{name}</name>
    <Placemark>
        <name>{name}</name>
        {kmldata}
    </Placemark>
</Document>
</kml>
'''.format(name=feature.name, kmldata=geom.kml)

        response = HttpResponse(content=kml, content_type='application/vnd.google-earth.kml+xml')
        response['Content-Disposition'] = 'attachment; filename=%s.kml' % feature.name

        return response


