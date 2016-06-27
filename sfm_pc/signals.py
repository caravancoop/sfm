from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.db import connection

from source.models import Source, Publication
from organization.models import OrganizationName, OrganizationAlias
from person.models import PersonAlias, PersonName
from violation.models import ViolationDescription

def update_index(model, instance, created, deleted):
    
    # TODO: Make this work for reals.

    fmt_args = {
        'content_type': model._meta.app_label.title(),
        'value_type': model._meta.model_name,
        'table_name': model._meta.db_table,
        'app_name': model._meta.app_label,
        'id_col': 'object_ref_id',
        'col_name': 'value'
    }
    if model in [Source, Publication]:
        fmt_args['id_col'] = 'id'
        fmt_args['col_name'] = 'title'
        content = instance.title
        obj_id = instance.id
    
    elif model in [OrganizationAlias, PersonAlias]:
        content = instance.value_id
        obj_id = instance.object_ref_id
    else:
        content = instance.value
        obj_id = instance.object_ref_id
    
    if model == Publication:
        obj_id = instance.source.id

    if model in [OrganizationAlias, PersonAlias]:
        select = ''' 
          SELECT
            to_tsvector('english', a.value) AS content,
            '{content_type}' AS content_type,
            '{value_type}' AS value_type,
            oa.object_ref_id AS id
          FROM {table_name} AS oa
          JOIN {app_name}_alias AS a
            ON oa.value_id = a.id
          WHERE oa.object_ref_id = %s
        '''.format(**fmt_args)
    else:
        select = ''' 
          SELECT
            to_tsvector('english', {col_name}) AS content,
            '{content_type}' AS content_type,
            '{value_type}' AS value_type,
            {id_col} AS id
          FROM {table_name}
          WHERE {id_col} = %s
        '''.format(**fmt_args)
    
    if created:
        stmt = ''' 
            INSERT INTO search_index (
              content,
              content_type,
              value_type,
              object_ref_id
            ) 
            {select}
        '''.format(select=select)
        params = (obj_id,)

    elif not created and not deleted:
        stmt = ''' 
            UPDATE search_index SET
              content = s.content
            FROM (
              {select}
            ) AS s
            WHERE search_index.id = s.id
              AND search_index.value_type = %s
        '''.format(select=select)
        
        params = (obj_id, 
                  fmt_args['value_type'],)

    elif deleted:
        stmt = ''' 
            DELETE FROM search_index 
            WHERE object_ref_id = %s
              AND value_type = %s
        '''
        
        params = (obj_id, fmt_args['value_type'])
    
    print(stmt)
    print(params)
    with connection.cursor() as c:
        c.execute(stmt, params)

@receiver(post_save, sender=Source)
def update_source_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 False)

@receiver(post_save, sender=Publication)
def update_publication_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 False)

@receiver(post_save, sender=OrganizationName)
def update_orgname_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 False)

@receiver(post_save, sender=OrganizationAlias)
def update_orgalias_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 False)

@receiver(post_save, sender=OrganizationAlias)
def update_orgalias_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 False)

@receiver(post_save, sender=PersonName)
def update_personname_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 False)

@receiver(post_save, sender=PersonAlias)
def update_personalias_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 False)

@receiver(post_save, sender=ViolationDescription)
def update_violation_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 False)

@receiver(post_delete, sender=Source)
def delete_source_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 True)

@receiver(post_delete, sender=Publication)
def delete_publication_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 True)

@receiver(post_delete, sender=OrganizationName)
def delete_orgname_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 True)

@receiver(post_delete, sender=OrganizationAlias)
def delete_orgalias_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 True)

@receiver(post_delete, sender=OrganizationAlias)
def delete_orgalias_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 True)

@receiver(post_delete, sender=PersonName)
def delete_personname_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 True)

@receiver(post_delete, sender=PersonAlias)
def delete_personalias_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 True)

@receiver(post_delete, sender=ViolationDescription)
def delete_violation_index(sender, **kwargs):
    update_index(sender, 
                 kwargs['instance'], 
                 kwargs['created'],
                 True)
