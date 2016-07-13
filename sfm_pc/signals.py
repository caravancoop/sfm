from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.db import connection

from source.models import Source, Publication
from organization.models import OrganizationName, OrganizationAlias
from person.models import PersonAlias, PersonName
from violation.models import ViolationDescription

def update_index():
    
    with connection.cursor() as c:
        c.execute(''' 
            REFRESH MATERIALIZED VIEW CONCURRENTLY search_index
        ''')

@receiver(post_save, sender=Source)
def update_source_index(sender, **kwargs):
    update_index()

@receiver(post_save, sender=Publication)
def update_publication_index(sender, **kwargs):
    update_index()

@receiver(post_save, sender=OrganizationName)
def update_orgname_index(sender, **kwargs):
    update_index()

@receiver(post_save, sender=OrganizationAlias)
def update_orgalias_index(sender, **kwargs):
    update_index()

@receiver(post_save, sender=OrganizationAlias)
def update_orgalias_index(sender, **kwargs):
    update_index()

@receiver(post_save, sender=PersonName)
def update_personname_index(sender, **kwargs):
    update_index()

@receiver(post_save, sender=PersonAlias)
def update_personalias_index(sender, **kwargs):
    update_index()

@receiver(post_save, sender=ViolationDescription)
def update_violation_index(sender, **kwargs):
    update_index()

@receiver(post_delete, sender=Source)
def delete_source_index(sender, **kwargs):
    update_index()

@receiver(post_delete, sender=Publication)
def delete_publication_index(sender, **kwargs):
    update_index()

@receiver(post_delete, sender=OrganizationName)
def delete_orgname_index(sender, **kwargs):
    update_index()

@receiver(post_delete, sender=OrganizationAlias)
def delete_orgalias_index(sender, **kwargs):
    update_index()

@receiver(post_delete, sender=OrganizationAlias)
def delete_orgalias_index(sender, **kwargs):
    update_index()

@receiver(post_delete, sender=PersonName)
def delete_personname_index(sender, **kwargs):
    update_index()

@receiver(post_delete, sender=PersonAlias)
def delete_personalias_index(sender, **kwargs):
    update_index()

@receiver(post_delete, sender=ViolationDescription)
def delete_violation_index(sender, **kwargs):
    update_index()
