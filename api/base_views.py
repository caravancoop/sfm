from datetime import datetime
import json

from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
from django.db import connection

from sfm_pc.utils import get_org_hierarchy_by_id

OPERATOR_LOOKUP = {
    'lte': '<=',
    'gte': '>=',
    'eq': '=',
    'in': 'IN',
}

class ValidationError(Exception):
    def __init__(self, message):
        self.message = message

def dateValidator(value):
    try:
        datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        raise ValidationError('Incorrect date format. Should be YYYY-MM-DD.')

def integerValidator(value):
    try:
        int(value)
    except ValueError:
        raise ValidationError('{} is not an integer'.format(value))

class JSONResponseMixin(object):
    def render_to_json_response(self, context, **response_kwargs):
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        try:
            del context['view']
        except (KeyError, TypeError):
            pass
        # Make sure things are JSON serializable
        return context

class JSONAPIView(JSONResponseMixin, TemplateView):
    safe = True
    page_count = 20

    def dispatch(self, request, *args, **kwargs):
        errors = []
        self.wheres = []
        self.order_bys = []

        filter_fields = list(getattr(self, 'filter_fields', {}).keys())
        order_by_fields = list(getattr(self, 'order_by_fields', {}).keys())
        required_params = getattr(self, 'required_params', [])
        optional_params = getattr(self, 'optional_params', [])

        valid_params = required_params + filter_fields + order_by_fields + optional_params
        
        incoming_params = list(self.request.GET.keys())
        
        missing = set(required_params) - set(incoming_params)

        if missing:
            if len(missing) > 1:
                errors.append("{} are required fields".format(', '.join(missing)))
            else:
                errors.append('{} is a required field'.format(list(missing)[0]))

        for query_param in self.request.GET.keys():
            try:
                field, operator = query_param.split('__')
            except ValueError:
                field = query_param
                operator = 'eq'

            if field not in valid_params:
                errors.append("'{}' is not a valid query parameter".format(query_param))
            
            elif not self.checkOperator(field, operator):
                errors.append("Invalid operator for '{1}'".format(operator, field))

            elif field in filter_fields:
                
                value = self.request.GET[query_param]
                
                validator = self.filter_fields[field]['validator']
                
                if validator:
                    try:
                        validator(value)
                        self.wheres.append((field, operator, value,))
                    except ValidationError as e:
                        errors.append("Value for '{0}' is not valid: {1}".format(field, e.message))
                else:
                    self.wheres.append((field, operator, value,))
            
            elif field == 'o':
                value = self.request.GET['o']
                if value not in order_by_fields:
                    errors.append("Cannot order by '{}'".format(value))
                else:
                    sort_order = 'ASC'
                    
                    if value.startswith('-'):
                        sort_order = 'DESC'
                        value = value.strip('-')

                    self.order_bys.append((value, sort_order,))

            elif field == 'p':
                value = self.request.GET['p']
                try:
                    int(value)
                except ValueError:
                    errors.append("'{}' is not a valid page number")

            elif field == 'bbox':
                coords = bbox.split(',')
                
                if len(coords) != 4:
                    errors.append('"bbox" should be a comma separated list of four floats')
                
                for point in coords:
                    
                    try:
                        float(point)
                    except ValueError:
                        errors.append('"{}" is not a valid value for a bbox'.format(point))
        
        if errors:
            response = HttpResponse(json.dumps({'errors': errors}), 
                                    content_type='application/json')
            response.status_code = 400
        else:
            response = super().dispatch(request, *args, **kwargs)

        return response
    
    def checkOperator(self, field, operator):
        if field in self.filter_fields:
            if operator not in self.filter_fields[field]['operators']:
                return False
        elif operator != 'eq':
            return False
        
        return True

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.update({'safe': self.safe})
        return self.render_to_json_response(context, **response_kwargs)
        
    def makeFeature(self, geometry, properties):
        
        try:
            del properties['location']
        except KeyError:
            pass
        
        try:
            del properties['geometry']
        except KeyError:
            pass
        
        try:
            del properties['bbox']
        except KeyError:
            pass

        feature = {
            'type': 'Feature',
            'id': properties['id'],
            'properties': properties,
            'geometry': geometry
        }

        return feature
    
    def makeOrganization(self, properties, relationships=True, simple=False):
        
        if relationships:
            hierarchy = get_org_hierarchy_by_id(properties['id'])
            
            properties['root_name'] = None
            properties['root_id'] = None

            if hierarchy:
                top = hierarchy[-1]
                properties['root_name'] = top['name']
                properties['root_id'] = top['id']

        current_commander = ''' 
            SELECT 
              o.id,
              MAX(p.name) AS name,
              m.first_cited AS first_cited,
              m.last_cited AS last_cited,
              COUNT(DISTINCT v.id) AS events_count
            FROM organization AS o
            JOIN membershipperson AS m
              ON o.id = m.organization_id
            JOIN person AS p
              ON m.member_id = p.id
            LEFT JOIN violation AS v
              ON p.id = v.perpetrator_id
            WHERE o.id = %s
              AND m.role = 'Commander'
            GROUP BY o.id, m.first_cited, m.last_cited
            ORDER BY o.id, 
                     m.last_cited DESC, 
                     m.first_cited DESC
        '''
        
        cursor = connection.cursor()
        cursor.execute(current_commander, [properties['id']])
        columns = [c[0] for c in cursor.description]
        
        row = cursor.fetchone()
        
        if row:
            properties['current_commander'] = dict(zip(columns, row))
        else:
            properties['current_commander'] = {}
        
        if not simple:
            site_present = ''' 
                SELECT DISTINCT ON (o.id)
                  g.id,
                  g.name AS location,
                  g.admin_level_1 AS admin_level_1_osm_name,
                  g.osmname AS osm_name,
                  g.first_cited AS date_first_cited,
                  g.last_cited AS date_last_cited
                FROM organization AS o
                JOIN emplacement AS e
                  ON o.id = e.organization_id
                JOIN geosite AS g
                  ON e.site_id = g.id
                WHERE o.id = %s
                ORDER BY o.id, 
                         g.last_cited DESC, 
                         g.first_cited DESC
            '''
            
            cursor = connection.cursor()
            cursor.execute(site_present, [properties['id']])
            columns = [c[0] for c in cursor.description]
            
            row = cursor.fetchone()
            
            if row:
                properties['site_current'] = dict(zip(columns, row))
            else:
                properties['site_current'] = {}
            
            area_present = ''' 
                SELECT DISTINCT ON (o.id)
                  o.id,
                  a.name,
                  a.osmname AS osm_name,
                  a.osmid,
                  ST_AsGeoJSON(a.geometry)::json AS geometry
                FROM organization AS o
                JOIN association AS ass
                  ON o.id = ass.organization_id
                JOIN area AS a
                  ON ass.area_id = a.id
                WHERE o.id = %s
                ORDER BY o.id, 
                         a.last_cited DESC, 
                         a.first_cited DESC
            '''
            
            cursor = connection.cursor()
            cursor.execute(area_present, [properties['id']])
            columns = [c[0] for c in cursor.description]
            
            row = cursor.fetchone()
            
            if row:
                properties['area_current'] = dict(zip(columns, row))
            else:
                properties['area_current'] = {}

        return properties
    
    def makePerson(self, properties):
        
        properties['membership_present'] = None
        properties['membership_former'] = None

        membership_present = '''
            SELECT 
              row_to_json(o.*) AS organization,
              role,
              rank,
              title,
              g.site_present
            FROM membershipperson AS mp
            JOIN (
              SELECT DISTINCT ON (id)
                id, 
                name
              FROM organization
            ) AS o
              ON mp.organization_id = o.id
            JOIN (
              SELECT DISTINCT ON (o.id)
                o.id AS organization_id,
                json_build_object('type', 'Feature',
                                  'id', g.id,
                                  'properties', json_build_object('location', g.name,
                                                                  'osm_name', g.osmname,
                                                                  'admin_level_1_osm_name', g.admin_level_1),
                                  'geometry', ST_AsGeoJSON(g.coordinates)::json) AS site_present
              FROM organization AS o
              LEFT JOIN emplacement AS e
                ON o.id = e.organization_id
              LEFT JOIN geosite AS g
                ON e.site_id = g.id
              ORDER BY o.id, e.end_date DESC, e.start_date DESC
            ) AS g
              ON o.id = g.organization_id
            LEFT JOIN emplacement AS e
              ON mp.organization_id = e.organization_id
            WHERE mp.member_id = %s
              AND (e.end_date IS NULL OR 
                   e.end_date::date > NOW()::date)
        '''
        
        membership_former = '''
            SELECT 
              row_to_json(o.*) AS organization,
              role,
              rank,
              title
            FROM membershipperson AS mp
            JOIN (
              SELECT DISTINCT ON (id)
                id, 
                name
              FROM organization
            ) AS o
              ON mp.organization_id = o.id
            LEFT JOIN emplacement AS e
              ON mp.organization_id = e.organization_id
            WHERE mp.member_id = %s
              AND e.end_date::date < NOW()::date
        '''
        
        cursor = connection.cursor()
        cursor.execute(membership_present, [properties['id']])
        columns = [c[0] for c in cursor.description]
        
        row = cursor.fetchone()
        
        if row:
            properties['membership_present'] = dict(zip(columns, row))
        
        cursor = connection.cursor()
        cursor.execute(membership_former, [properties['id']])
        columns = [c[0] for c in cursor.description]
        
        row = cursor.fetchone()
        
        if row:
            properties['membership_former'] = dict(zip(columns, row))

        return properties

    def makeEvent(self, properties, simple=False):
        properties['violation_types'] = list(set(properties['violation_types']))

        perp_class = [c for c in list(set(properties['perpetrator_classification'])) if c]
        if perp_class:
            properties['perpetrator_classification'] = perp_class
        else:
            properties['perpetrator_classification'] = None

        perp_org_ids = []
        perp_orgs = []
        for org in properties['perpetrator_organization']:
            if org and org['id'] not in perp_org_ids:
                structured_org = self.makeOrganization(org, 
                                                       relationships=False,
                                                       simple=simple)
                
                perp_orgs.append(structured_org)
                perp_org_ids.append(org['id'])

        properties['perpetrator_organization'] = perp_orgs
        
        site_ids = []
        sites = []
        if properties.get('sites_nearby'):
            for site in properties['sites_nearby']:
                if site['id'] not in site_ids:
                    sites.append(site)
                    site_ids.append(site['id'])
        
            properties['sites_nearby'] = sites
        return properties
    
    def makeWhereClauses(self):
        where_clauses = []

        for field, operator, value in self.wheres:
            operator = OPERATOR_LOOKUP[operator]
            
            if self.filter_fields.get(field):
                db_field = self.filter_fields[field]['field']
            
                clause = '{0} {1} %s'.format(db_field, operator)

                if operator == 'IN':
                    value = tuple(v for v in value.split(','))

                where_clauses.append((clause, value,))
        
        return where_clauses
        
    def makeOrderBy(self):
        order_bys = []

        for field, sort_order in self.order_bys:
            db_field = self.order_by_fields[field]['field']
            order_bys.append('{0} {1}'.format(db_field, sort_order))

        return order_bys
    
    def appendWhereClauses(self, query):
        where_clauses = self.makeWhereClauses()
        
        these_args = []
        for clause, value in where_clauses:
            query = '{0} AND {1}'.format(query, clause)
            these_args.append(value)
        
        return query, these_args

    def getFacets(self, 
                  query, 
                  grouper):
        
        group_by = 'GROUP BY TRIM({0}), uuid'.format(grouper)

        facets_counts = '''
            SELECT 
              SUM(facet_count)::int AS facet_count,
              facet 
            FROM (
              {0} 
              {1}
            ) AS s
            GROUP BY facet
        '''.format(query, group_by)
        
        return facets_counts
    
    def retrieveFacetsCounts(self, base_query, query_args):

        for facet in self.facet_fields:
            
            facets_counts = '''
                SELECT 
                  TRIM({0}) AS facet,
                  COUNT(DISTINCT uuid) AS facet_count
                {1}
            '''.format(facet, base_query)
            
            facets_counts, this_facet_args = self.appendWhereClauses(facets_counts)
            
            this_facet_args = query_args + this_facet_args

            facets_counts = self.getFacets(facets_counts, facet)
            
            cursor = connection.cursor()
            cursor.execute(facets_counts, this_facet_args)
            
            facets_counts = [r for r in cursor]
            
            count = int(sum(f[0] for f in facets_counts))
            
            this_facet_args = []

            yield facet, count, facets_counts
    
    def orderPaginate(self, query):
        order_by = self.makeOrderBy()
        
        if order_by:
            order_by = ', '.join(order_by)
            query = '{0} ORDER BY {1}'.format(query, order_by)
        
        query = ''' 
            SELECT * FROM ({0}) AS s LIMIT {1}
        '''.format(query, self.page_count)

        if self.request.GET.get('p'):
            page = self.request.GET.get('p')
            
            if int(page) >= 1:
                offset = (int(page) - 1) * self.page_count
                query = '{0} OFFSET {1}'.format(query, offset)

        return query
