import json
from django.db import models
from django.apps import apps
import pandas as pd

from quotes.models import ArcticDataManager



'''def create_arctic_model(collection_name):
    class Meta:
        managed = False  # Не создавать таблицу в базе данных
        db_table = collection_name  # Использовать имя коллекции в качестве имени таблицы

    fields = {
        'ident': models.CharField(max_length=255, unique=True),
        'data': models.JSONField(),
        '__module__': __name__,
        'Meta': Meta,
    }

    return type(collection_name, (models.Model,), fields)'''

'''def create_arctic_manager(model):
    return type(f"{model.__name__}Manager", (models.Manager,), {'model': model})
'''

class arcticData(object):
    def __init__(self, collection_name, mongo_db=None):
        self.collection_name = collection_name
        self.model = apps.get_model('quotes', collection_name)
        self.manager = ArcticDataManager()

    def read(self, ident):
        try:
            arctic_data = self.model.objects.get(ident=ident)
            arctic_data = self.parse_json_data(arctic_data.data)
            # Преобразовать данные обратно в DataFrame
            data_copy = pd.DataFrame(arctic_data)
            # Преобразовать столбец 'index' обратно в формат Timestamp
            data_copy['index'] = pd.to_datetime(data_copy['index'])
            # Установить столбец 'index' в качестве индекса
            data_copy.set_index('index', inplace=True)
            
            return data_copy
        except self.model.DoesNotExist:
            return pd.DataFrame()
        
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
    def parse_json_data(self, json_data):
        """
        Функция для разбора JSON-строки и восстановления данных.

        Args:
            json_data (str): JSON-строка с данными.

        Returns:
            list: Список словарей с восстановленными данными.
        """
        # Удаление дополнительных обратных слешей из JSON-строки
        json_data = json_data.replace("\\", "")
        # Разбор JSON-строки
        parsed_data = json.loads(json_data)

        # Преобразование строковых значений обратно в float
        for item in parsed_data:
            for key, value in item.items():
                if isinstance(value, str) and value.replace('.', '', 1).isdigit():
                    item[key] = float(value)

        return parsed_data

    def write(self, ident: str, data: pd.DataFrame):

        # Создать копию данных
        data_copy = data.copy()
        # Добавить индексы как столбец в данные
        data_copy.reset_index(inplace=True)
        # Преобразовать Timestamp в строковый формат
        data_copy['index'] = data_copy['index'].dt.strftime('%Y-%m-%d %H:%M:%S')
        # Преобразовать данные в словарь
        
        data_present = sorted(data.columns)
        #print(data_present)
        #print(data)
        data_dict = data_copy.to_dict(orient='records')
        data_dict = self.convert_data_to_json(data_dict)
        self.manager.create_arctic_data(model=self.model, ident=ident, data=data_dict)

    def delete(self, ident: str):
        self.model.objects.filter(ident=ident).delete()

    def get_keynames(self) -> list:
        return list(self.model.objects.values_list('ident', flat=True))

    def has_keyname(self, keyname) -> bool:
        return self.model.objects.filter(ident=keyname).exists()
    
    def get_indexes(self):
        index_fields = []

        for field in self.model._meta.get_fields():
            if field.db_index:
                index_fields.append(field.name)

        return len(index_fields), index_fields, index_fields
    
    def create_index(self, indexname, order=''):
        # Проверяем существует ли индекс
        if indexname in self.model._meta.indexes:
            # Если индекс уже существует, ничего не делаем
            pass
        else:
            # Создаем новый индекс с указанным именем и порядком сортировки
            self.model._meta.indexes.append(models.Index(fields=[indexname], name=indexname, unique=True))

    def create_compound_index(self, index_config: dict):
        name_parts = []
        keys = index_config.pop("keys")
        for key, value in keys.items():
            name_parts.append(str(key))
            name_parts.append(str(value))
        new_index_name = "_".join(name_parts)

        # Проверяем существует ли индекс
        if new_index_name in self.model._meta.indexes:
            # Если индекс уже существует, ничего не делаем
            pass
        else:
            # Создаем новый составной индекс
            fields = [(key, value) for key, value in keys.items()]
            self.model._meta.indexes.append(models.Index(fields=fields, name=new_index_name, **index_config))
    
    @property
    def collection(self):
        return self.model.objects.all()

    def get_list_of_keys(self) -> list:
        return list(self.model.objects.values_list('ident', flat=True))

    def get_max_of_keys(self) -> int:
        doc = self.collection.order_by('-ident').first()
        return doc.ident if doc else 0

    def get_list_of_values_for_dict_key(self, dict_key):
        return list(self.collection.filter(ident__exists=True).values_list(dict_key, flat=True))

    def get_result_dict_for_key(self, key) -> dict:
        try:
            result_dict = self.collection.get(ident=key)
            result_dict.pop(MONGO_ID_KEY)
            return result_dict
        except self.model.DoesNotExist:
            raise missingData(f"Key {key} not found in Mongo data")

    def get_result_dict_for_key_without_key_value(self, key) -> dict:
        result_dict = self.get_result_dict_for_key(key)
        result_dict.pop('ident')
        return result_dict

    def get_list_of_result_dict_for_custom_dict(self, custom_dict: dict) -> list:
        return list(self.collection.filter(**custom_dict).values())

    def key_is_in_data(self, key):
        return self.collection.filter(ident=key).exists()

    def delete_data_without_any_warning(self, key):
        try:
            self.collection.filter(ident=key).delete()
        except self.model.DoesNotExist:
            raise missingData(f"{self.key_name}:{key} not in data {self.name}")

    def delete_data_with_any_warning_for_custom_dict(self, custom_dict: dict):
        self.collection.filter(**custom_dict).delete()

    def add_data(self, key, data_dict: dict, allow_overwrite=False, clean_ints=True):
        if clean_ints:
            data_dict = mongo_clean_ints(data_dict)

        defaults = {'data': data_dict}
        if not allow_overwrite and self.key_is_in_data(key):
            raise existingData(f"Can't overwrite existing data {self.key_name}/{key} for {self.name}")
        
        self.manager.create_arctic_data(model=self.model, ident=key, data=data_dict)

    def _update_existing_data_with_cleaned_dict(self, key, cleaned_data_dict):
        self.collection.filter(ident=key).update(data=cleaned_data_dict)

    def _add_new_cleaned_dict(self, key, cleaned_data_dict):
        self.manager.create_arctic_data(model=self.model, ident=key, data=cleaned_data_dict)
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
