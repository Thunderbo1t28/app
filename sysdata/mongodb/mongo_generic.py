import ast
from copy import copy
from datetime import date, time
import json
from django.db import models

from syscore.constants import arg_not_supplied
from syscore.exceptions import missingData, existingData
from sysdata.arctic.arctic_connection import arcticData
from sysdata.mongodb.mongo_connection import (
    mongoConnection,
    MONGO_ID_KEY,
    mongo_clean_ints,
    clean_mongo_host,
)
from syslogging.logger import *


class mongoDataWithSingleKey:
    """
    Read and write data class to get data from a mongo database

    """

    def __init__(self, collection_name, key_name, mongo_db=arg_not_supplied):
        self.init_mongo(collection_name, key_name, mongo_db=mongo_db)

    def init_mongo(
        self,
        collection_name: str,
        key_name: str,
        mongo_db=arg_not_supplied,
    ):
        self._mongo = arcticData(collection_name, mongo_db=mongo_db)
        self._key_name = key_name

        # this won't create the index if it already exists
        # if a different index exists (FIX ME WILL HAPPEN UNTIL NEW DATA READY)...
        try:
            self._mongo.create_index(key_name)
        except:
            pass
            ## no big deal

    def __repr__(self):
        return self.name

    @property
    def key_name(self) -> str:
        return self._key_name

    @property
    def name(self) -> str:
        col = self._mongo.collection_name
        return f"mongoData connection for {col}"

    '''@property
    def collection(self):
        return self._mongo.collection'''

    def get_indexes(self):
        index_fields = []

        for field in self._mongo.model._meta.get_fields():
            if field.db_index:
                index_fields.append(field.name)

        return len(index_fields), index_fields, index_fields
    
    def create_index(self, indexname, order=''):
        # Проверяем существует ли индекс
        if indexname in self._mongo.model._meta.indexes:
            # Если индекс уже существует, ничего не делаем
            pass
        else:
            # Создаем новый индекс с указанным именем и порядком сортировки
            self.self._mongo.model._meta.indexes.append(models.Index(fields=[indexname], name=indexname))

    def create_compound_index(self, index_config: dict):
        name_parts = []
        keys = index_config.pop("keys")
        for key, value in keys.items():
            name_parts.append(str(key))
            name_parts.append(str(value))
        new_index_name = "_".join(name_parts)

        # Проверяем существует ли индекс
        if new_index_name in self._mongo.model._meta.indexes:
            # Если индекс уже существует, ничего не делаем
            pass
        else:
            # Создаем новый составной индекс
            fields = [(key, value) for key, value in keys.items()]
            self._mongo.model._meta.indexes.append(models.Index(fields=fields, name=new_index_name, **index_config))
    
    @property
    def collection(self):
        return self._mongo.model.objects.all()

    def get_list_of_keys(self) -> list:
        return list(self._mongo.model.objects.values_list('ident', flat=True))

    def get_max_of_keys(self) -> int:
        doc = self.collection.order_by('-ident').first()
        return doc.ident if doc else 0

    def get_list_of_values_for_dict_key(self, dict_key):
        return list(self.collection.filter(ident__exists=True).values_list(dict_key, flat=True))

    def get_result_dict_for_key(self, key) -> dict:
        try:
            existing_key = self.collection.filter(ident=key)
            if existing_key.exists():
                data = self._mongo.model.objects.get(ident=key)
                
                result_dict = data.data
                #print(result_dict)
            else:
                result_dict = {}
            #result_dict = self.collection.get(ident=key)
            
            #result_dict.pop(MONGO_ID_KEY)
            return result_dict
        
        except self._mongo.model.DoesNotExist:
            raise missingData(f"Key {key} not found in Mongo data")

    def get_result_dict_for_key_without_key_value(self, key) -> dict:
        key_name = self.key_name
        result_object = self.get_result_dict_for_key(key)
        result_dict = result_object
        if key_name in result_dict:
            result_dict.pop(key_name)
        else:
            # Можно добавить обработку случая, когда ключ 'process_name' отсутствует
            pass
        #result_dict.pop('ident')
        return result_dict

    def get_list_of_result_dict_for_custom_dict(self, custom_dict: dict) -> list:
        return list(self.collection.filter(**custom_dict).values())

    def key_is_in_data(self, key):
        return self.collection.filter(ident=key).exists()

    def delete_data_without_any_warning(self, key):
        try:
            self.collection.filter(ident=key).delete()
        except self._mongo.model.DoesNotExist:
            raise missingData(f"{self.key_name}:{key} not in data {self.name}")

    def delete_data_with_any_warning_for_custom_dict(self, custom_dict: dict):
        self.collection.filter(**custom_dict).delete()

    def add_data(self, key, data_dict: dict, allow_overwrite=False, clean_ints=True):
        if clean_ints:
            cleaned_data_dict = {}#mongo_clean_ints(data_dict)
        else:
            cleaned_data_dict = copy(data_dict)

        if self.key_is_in_data(key):
            if allow_overwrite:
                self._update_existing_data_with_cleaned_dict(key, cleaned_data_dict)
            else:
                raise existingData(
                    "Can't overwrite existing data %s/%s for %s"
                    % (self.key_name, key, self.name)
                )
        else:
            try:
                #print(key)
                self._add_new_cleaned_dict(key, cleaned_data_dict)
            except:
                ## this could happen if the key has just been added most likely for logs
                raise existingData(
                    "Can't overwrite existing data %s/%s for %s"
                    % (self.key_name, key, self.name)
                )

    def _update_existing_data_with_cleaned_dict(self, key, cleaned_data_dict):
        #key_name = self.key_name
        self.collection.filter(ident=key).update(data=cleaned_data_dict)

    '''def _add_new_cleaned_dict(self, key, cleaned_data_dict):
        self.manager.create_arctic_data(model=self.model, ident=key, data=cleaned_data_dict)'''

    def _add_new_cleaned_dict(self, key, cleaned_data_dict):
        key_name = self.key_name
        #print(cleaned_data_dict)
        cleaned_data_dict[key_name] = key
        self._mongo.manager.create_arctic_data(model=self._mongo.model, ident=key, data=cleaned_data_dict) 

def mongo_clean_ints(dict_to_clean):
    """
    Mongo doesn't like ints

    :param dict_to_clean: dict
    :return: dict
    """
    pass


def clean_mongo_host(host_string):
    """
    If the host string is a mongodb connection URL with authentication values, then return just the host and port part
    :param host_string
    :return: host and port only
    """
    pass

class mongoDataWithMultipleKeys:
    """
    Read and write data class to get data from a mongo database

    Use this if you want a collection with a compound index, ie if you need to
    search for documents using more than one field
    """

    def __init__(
        self,
        collection_name: str,
        mongo_db=arg_not_supplied,
        index_config: dict = None,
    ):
        #self._log = get_logger("mongoDataWithMultipleKeys")
        self.init_mongo(collection_name, mongo_db=mongo_db, index_config=index_config)

    def init_mongo(
        self,
        collection_name: str,
        mongo_db=arg_not_supplied,
        index_config=None,
    ):
        self._mongo = arcticData(collection_name, mongo_db=mongo_db)

        if index_config:
            try:
                self._mongo.create_compound_index(index_config)
            except Exception as exc:
                self._log.error(
                    "Failed to create compound index for collection '%s', "
                    "check config: %s" % (collection_name, exc),
                )

    def __repr__(self):
        return self.name

    @property
    def name(self) -> str:
        col = self._mongo.collection_name
        db = self._mongo.database_name
        host = clean_mongo_host(self._mongo.host)

        return f"mongoData connection for {col}/{db}, {host}"
    @property
    def collection(self):
        return self._mongo.model.objects.all()
    
    def get_list_of_all_dicts(self) -> list:
        cursor = self._mongo.get_list_of_keys()
        data_list = []

        for i in cursor:
            data_string = i.strip('[]')
            data_string = data_string.strip('"')
            data_dict = ast.literal_eval(data_string)
            data_list.append(data_dict)

        dict_list = [db_entry for db_entry in data_list]
        
        #_ = [dict_item.pop(MONGO_ID_KEY) for dict_item in dict_list]
        #print(dict_list)
        return dict_list

    def get_result_dict_for_dict_keys(self, dict_of_keys: dict) -> dict:
        try:
            #print(dict_of_keys)
            #print(self._mongo.model)
            if 'key' in dict_of_keys:
                existing_key = self.collection.filter(ident=dict_of_keys['key'])
            else:
                existing_key = self.collection.filter(ident=dict_of_keys['instrument_code'])
            
            if existing_key.exists():
                data = self._mongo.model.objects.get(ident=dict_of_keys)
                
                result_dict = data.data
                #print(result_dict)
            else:
                result_dict = {}
            #result_dict = self.collection.get(ident=key)
            
            #result_dict.pop(MONGO_ID_KEY)
            return result_dict
        
        except self._mongo.model.DoesNotExist:
            raise missingData(f"Key {key} not found in Mongo data")

    def get_list_of_result_dicts_for_dict_keys(self, dict_of_keys: dict) -> list:
        list_of_result_dicts = self._mongo.get_list_of_result_dict_for_custom_dict(dict_of_keys)
        for result_dict in list_of_result_dicts:
            result_dict.pop(MONGO_ID_KEY)
        return list_of_result_dicts

    def key_dict_is_in_data(self, dict_of_keys: dict) -> bool:
        return self._mongo.key_is_in_data(dict_of_keys)

    def add_data(
        self,
        dict_of_keys: dict,
        data_dict: dict,
        allow_overwrite=False,
        clean_ints=True,
    ):
        if clean_ints:
            data_dict = mongo_clean_ints(data_dict)

        if self.key_dict_is_in_data(dict_of_keys):
            if allow_overwrite:
                self._update_existing_data_with_cleaned_dict(
                    dict_of_keys, data_dict
                )
            else:
                raise existingData(
                    "Can't overwrite existing data %s for %s"
                    % (str(dict_of_keys), self.name)
                )
        else:
            self._add_new_cleaned_dict(dict_of_keys, data_dict)

    def _update_existing_data_with_cleaned_dict(
        self, dict_of_keys: dict, cleaned_data_dict: dict
    ):
        self._mongo.collection.filter(**dict_of_keys).update(data=cleaned_data_dict)

    def _add_new_cleaned_dict(self, dict_of_keys: dict, cleaned_data_dict: dict):
        data_dict = {**cleaned_data_dict, **dict_of_keys}
        self._mongo.add_data(key=dict_of_keys, data_dict=data_dict)
    
    def delete_data_without_any_warning(self, dict_of_keys):
        self._mongo.delete_data_without_any_warning(dict_of_keys)


_date = date
_time = time
