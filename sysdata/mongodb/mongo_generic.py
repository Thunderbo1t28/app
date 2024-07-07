import ast
from copy import copy
from datetime import date, time
import json
from types import NoneType
from unittest import result
from django.db import models
import numpy as np
import pandas as pd
from pymongo import ASCENDING
from quotes.models import MyData

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
from dateutil import parser

from django.db.models import Q

from sysexecution.orders.named_order_objects import missing_order

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
        #print(self._mongo.model)
        result = list(self._mongo.model.objects.values_list('ident', flat=True))
        print(result)
        return result

    def get_max_of_keys(self) -> int:
        doc = self.collection.order_by('-ident').first()
        return doc.ident if doc else 0

    def get_list_of_values_for_dict_key(self, dict_key):
        return list(self.collection.filter(ident__exists=True).values_list(dict_key, flat=True))

    def get_result_dict_for_key(self, key) -> dict:
        try:
            #print(self._mongo.model)
            #print(key)
            existing_key = self.collection.filter(ident=key)
            if existing_key.exists():
                data = self._mongo.model.objects.filter(ident=key).order_by('id').last()
                
                result_dict = data.data
                #print(result_dict)
                result_dict = self.parse_json_data(result_dict)
                #print(result_dict)
                return result_dict
        
            #result_dict = self.collection.get(ident=key)
            
            #print(result_dict)
            
        except self._mongo.model.DoesNotExist:
            raise missingData(f"Key {key} not found in Mongo data")

    def get_result_dict_for_key_without_key_value(self, key) -> dict:
        key_name = self.key_name
        result_object = self.get_result_dict_for_key(key)
        #print(key)
        result_dict = result_object
        if result_dict is None:
            return None
        if key_name in result_dict:
            result_dict.pop(key_name)
        else:
            # Можно добавить обработку случая, когда ключ 'process_name' отсутствует
            pass
        #result_dict.pop('ident')
        return result_dict

    def get_list_of_result_dict_for_custom_dict(self, custom_dict: dict) -> list:
        #print(custom_dict)
        #print(self._mongo.model)
        
        start_date = custom_dict['fill_datetime']['$gte']
        end_date = custom_dict['fill_datetime']['$lt']
        json_data = self._mongo.model.objects.all()
        if json_data.exists():
            json_data = self._mongo.model.objects.get()
                            
            #print(json_data)
            json_data = self.parse_json_data(json_data.data)
            # Преобразуйте данные JSON в словарь Python
            data_dict = json.loads(json_data)

            # Создайте объект MyData и сохраните его в базе данных
            my_data = MyData.objects.create(
                key=data_dict['key'],
                trade=data_dict['trade'],
                fill=data_dict['fill'],
                fill_datetime=datetime.strptime(data_dict['fill_datetime'], "%Y-%m-%d %H:%M:%S") if data_dict['fill_datetime'] else None,
                filled_price=data_dict['filled_price'],
                locked=data_dict['locked'],
                order_id=data_dict['order_id'],
                parent=data_dict['parent'],
                children=data_dict['children'],
                active=data_dict['active'],
                order_type=data_dict['order_type'],
                limit_contract=data_dict['limit_contract'],
                limit_price=data_dict['limit_price'],
                reference_contract=data_dict['reference_contract'],
                reference_price=data_dict['reference_price'],
                manual_trade=data_dict['manual_trade'],
                roll_order=data_dict['roll_order'],
                reference_datetime=datetime.strptime(data_dict['reference_datetime'], "%Y-%m-%d %H:%M:%S"),
                generated_datetime=datetime.strptime(data_dict['generated_datetime'], "%Y-%m-%d %H:%M:%S")
            )
            # Применяем фильтр к данным
            filtered_data = MyData.objects.filter(fill_datetime__gte=start_date,
                                                fill_datetime__lt=end_date)
            MyData.objects.all().delete()
        else:
            return []
        #print(fill_datetime_range)
        return list(filtered_data)

    def key_is_in_data(self, key):
        #print(self._mongo.model)
        #print(key)
        return self.collection.filter(ident=key).exists()

    def delete_data_without_any_warning(self, key):
        try:
            self.collection.filter(ident=key).delete()
        except self._mongo.model.DoesNotExist:
            raise missingData(f"{self.key_name}:{key} not in data {self.name}")

    def delete_data_with_any_warning_for_custom_dict(self, custom_dict: dict):
        #print(custom_dict)
        #self.collection.filter(**custom_dict).delete()
        self.collection.delete()

    def add_data(self, key, data_dict: dict, allow_overwrite=False, clean_ints=True):

        if clean_ints:
            cleaned_data_dict = self.convert_data_to_json(data_dict) #mongo_clean_ints(data_dict)
        else:
            cleaned_data_dict = copy(data_dict)
        #print(data_dict)
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
        #cleaned_data_dict[key_name] = key
        self._mongo.manager.create_arctic_data(model=self._mongo.model, ident=key, data=cleaned_data_dict) 

    
    
    def convert_data_to_json(self, data):
        """
        Функция для преобразования данных в JSON с учетом значений типа float.

        Args:
            data (list): Список словарей с данными.

        Returns:
            str: JSON-строка с преобразованными данными.
        """
        #print(data)
        # Рекурсивная функция для обработки каждого уровня вложенности
        def process_dict(data_dict):
            processed_dict = {}
            for key, value in data_dict.items():
                if isinstance(value, float):
                    try:
                        # Пробуем преобразовать в целое число
                        int_value = int(value)
                        # Преобразуем в строку только в том случае, если преобразование в int прошло успешно
                        processed_dict[key] = str(int_value)
                        #print(type(item[key]), item[key])
                    except ValueError:
                        # Если преобразование в int не удалось, оставляем значение как строку
                        processed_dict[key] = str(value)
                        #print(type(item[key]), item[key])
                elif isinstance(value, datetime.datetime):
                    processed_dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, np.int64):
                    processed_dict[key] = int(value)
                elif isinstance(value, NoneType):
                    processed_dict[key] = None
                
                elif isinstance(value, dict):
                    processed_dict[key] = process_dict(value)
                elif isinstance(value, list):
                    processed_dict[key] = [process_dict(item) if isinstance(item, dict) else str(item) for item in value]
                else:
                    processed_dict[key] = value
            return processed_dict
        # for key, value in data.items():
        #     if isinstance(value, float):
        #         data[key] = str(value)
        #     elif isinstance(value, datetime.datetime):
        #         data[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        #     if pd.isna(value):
        #         data[key] = None
        #     if 'running_methods' in data:
        #         for key, value in data['running_methods'].items():
        #             if isinstance(value, datetime.datetime):
        #                 data['running_methods'][key] = value.strftime('%Y-%m-%d %H:%M:%S')

       # Преобразование данных с учетом каждого уровня вложенности
        processed_data = process_dict(data)
        #print(processed_data)
        # Сериализация данных в JSON-строку
        #print(processed_data)
        json_data = json.dumps(processed_data)
        #print(json_data)

        return json_data
    def parse_json_data(self, json_data):
        """
        Функция для разбора JSON-строки и восстановления данных.

        Args:
            json_data (str): JSON-строка с данными.

        Returns:
            list: Список словарей с восстановленными данными.
        """
        # # Удаление дополнительных обратных слешей из JSON-строки
        # json_data = json_data.replace("\\", "")
        # # Разбор JSON-строки
        # parsed_data = json.loads(json_data)

        # # Преобразование строковых значений обратно в float
        
        # for key, value in parsed_data.items():
        #     if isinstance(value, str) and value.replace('.', '', 1).isdigit():
        #         parsed_data[key] = float(value)
        #print(json_data)
        # Удаление дополнительных обратных слешей из JSON-строки
        if "\\" in json_data:
            json_data = json_data.replace("\\", "")
        #json_data = json_data.replace("\\", "")
        if isinstance(json_data, dict):
            return json_data
        # Разбор JSON-строки
        #print(json_data)
        parsed_data = json.loads(json_data)
        #print(parsed_data)
        # Функция для восстановления вложенных словарей и списков
        def restore_values(value):
            if isinstance(value, str) and value.replace('.', '', 1).isdigit():
                try:
                    return float(value)
                except ValueError:
                    pass
            elif isinstance(value, str) and value.isdigit():
                try:
                    return int(value)
                except ValueError:
                    pass
            elif isinstance(value, str) and value.replace('-', '', 1).isdigit():
                try:
                    return float(value)
                except ValueError:
                    pass
            elif isinstance(value, str) and value.replace('.', '', 1).isdigit() and value.replace('-', '', 1).isdigit():
                try:
                    return float(value)
                except ValueError:
                    pass
            elif isinstance(value, str) and value.replace('-', '', 1).isdigit():
                try:
                    return float(value)
                except ValueError:
                    pass
            elif isinstance(value, str) and value == 'nan':
                    return 0.0
            
            elif isinstance(value, dict):
                return {k: restore_values(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [restore_values(item) for item in value]
            else:
                return value

        # Восстановление данных
        parsed_data = restore_values(parsed_data)

        return parsed_data

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
        cursor = list(self._mongo.model.objects.values_list('ident', flat=True))
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
        try:
            self.get_result_dict_for_dict_keys(dict_of_keys)
        except missingData:
            return False
        else:
            return True

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
        
    def convert_data_to_json(self, data):
        """
        Функция для преобразования данных в JSON с учетом значений типа float.

        Args:
            data (list): Список словарей с данными.

        Returns:
            str: JSON-строка с преобразованными данными.
        """
        # Преобразование значений float в строковый формат
        for item in data:
            for key, value in item.items():
                if isinstance(value, float):
                    item[key] = str(value)
                if pd.isna(value):
                    item[key] = None
        # Сериализация данных в JSON-строку
        json_data = json.dumps(data)

        return json_data

_date = date
_time = time
