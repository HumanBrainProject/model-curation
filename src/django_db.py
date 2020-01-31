from ...models import ScientificModel
import numpy as np
from django.core.management.base import BaseCommand

import pickle    


model_keys = ['abstraction_level', 'alias', 'app', 'app_id', 'author', 'brain_region', 'cell_type', 'check', 'clean', 'clean_fields', 'clean_something_unique_or_null', 'code_format', 'creation_date', 'date_error_message', 'delete', 'description', 'from_db', 'full_clean', 'get_deferred_fields', 'get_next_by_creation_date', 'get_previous_by_creation_date', 'id', 'images', 'instances', 'license', 'model_scope', 'model_type', 'name', 'objects', 'organization', 'owner', 'parents', 'pk', 'pla_components', 'prepare_database_save', 'private', 'project', 'refresh_from_db', 'save', 'save_base', 'serializable']

version_keys = ['check', 'clean', 'clean_fields', 'code_format', 'date_error_message', 'delete', 'description', 'from_db', 'full_clean', 'get_deferred_fields', 'get_next_by_timestamp', 'get_previous_by_timestamp', 'hash', 'id', 'license', 'model', 'model_id', 'morphology', 'objects', 'parameters', 'pk', 'prepare_database_save', 'refresh_from_db', 'save', 'save_base', 'serializable_value', 'source', 'timestamp', 'unique_error_message', 'validate_unique', 'validationtestresult_set', 'version']


model_keys = ['abstraction_level', 'alias', 'app', 'app_id', 'author', 'brain_region', 'cell_type', 'code_format', 'creation_date', 'description', 'from_db', 'id', 'license', 'model_scope', 'model_type', 'name', 'organization', 'owner', 'pla_components', 'private', 'project']

version_keys = ['code_format', 'description', 'id', 'license', 'morphology', 'parameters', 'source', 'timestamp', 'version']


MODELS = []
class Command(BaseCommand):
    
    def handle(self, *args, **options):
        
        models = ScientificModel.objects.all()
        MODELS = []
        for i, model in enumerate(models):
            print(model)
            MODELS.append({})

            for key in model_keys:
                MODELS[-1][key] = str(getattr(model, key))
            
            model_instances = model.instances.all()
            MODELS[-1]['instances'] = []
            for model_instance in model_instances:
                MODELS[-1]['instances'].append({})
                for key in version_keys:
                    MODELS[-1]['instances'][-1][key] = str(getattr(model_instance, key))
                    
            MODELS[-1]['images']=[{"url": im.url, "caption": im.caption} for im in model.images.all()]

        output = open('Django_DB.pkl', 'wb')
        print('[ok] Database succesfully retrieved from the server')
        pickle.dump(MODELS, output)
        output.close()


