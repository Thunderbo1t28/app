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
