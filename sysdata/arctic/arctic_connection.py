import copy
import datetime
import json
from django.db import models
from django.apps import apps
import pandas as pd
from datetime import datetime
import quotes
from quotes.models import ArcticDataManager
from syscore.exceptions import existingData, missingData



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
            #print(ident)
            arctic_data = self.model.objects.get(ident=ident)
            arctic_data = self.parse_json_data(arctic_data.data)
            
            # Проверка наличия данных и их корректности
            if not arctic_data or not isinstance(arctic_data, list):
                raise ValueError("Invalid or empty data")
            
            # Преобразование данных в DataFrame
            data_copy = pd.DataFrame(arctic_data)
            
            # Проверка наличия столбца 'index'
            if 'index' not in data_copy.columns:
                raise ValueError("Missing 'index' column in data")
            
            # Преобразование столбца 'index' в формат Timestamp
            data_copy['index'] = pd.to_datetime(data_copy['index'])
            
            # Установка столбца 'index' в качестве индекса
            data_copy.set_index('index', inplace=True)
            
            return data_copy
        except self.model.DoesNotExist:
            raise ValueError(f"Data with ident={ident} not found")
        
    def convert_data_to_json(self, data):
        """
        Функция для преобразования данных в JSON с учетом значений типа float.

        Args:
            data (list): Список словарей с данными.

        Returns:
            str: JSON-строка с преобразованными данными.
        """
        
        # Преобразование значений float в строковый формат
        #print(data)
        for item in data:
            for key, value in item.items():
                #print(type(value), value)
                if isinstance(value, float):
                    try:
                        # Пробуем преобразовать в целое число
                        int_value = int(value)
                        # Преобразуем в строку только в том случае, если преобразование в int прошло успешно
                        item[key] = str(int_value)
                        #print(type(item[key]), item[key])
                    except ValueError:
                        # Если преобразование в int не удалось, оставляем значение как строку
                        item[key] = str(value)
                        #print(type(item[key]), item[key])
                elif pd.isna(value):
                    item[key] = None
                


        
        
        # Сериализация данных в JSON-строку
        json_data = json.dumps(data)
        #print(f"arctic {json_data}")
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

        if self.model == quotes.models.optimal_positions:
            for item in parsed_data:
                for key, value in item.items():
                    if isinstance(value, str):
                        try:
                            # Преобразуем в строку только в том случае, если преобразование в int прошло успешно
                            item[key] = int(value)
                            #print(type(item[key]), item[key])
                        except ValueError:
                            if '.' in value:  # Если есть десятичная точка
                                try:
                                    date_value = datetime.strptime(value.split('.')[0], '%Y%m%d')
                                    # Проверяем, что дата входит в интервал
                                    if 2010 <= date_value.year <= 2025:
                                        item[key] = date_value.strftime('%Y%m%d') # Преобразуем в формат без точки
                                except ValueError:
                                    pass
                                try:
                                    item[key] = float(value)  # Попробуем преобразовать в float
                                except ValueError:
                                    pass  # Если не удалось преобразовать, оставляем как строку
                    elif value.isdigit():  # Если это целое число
                        item[key] = int(value)
                    elif value == 'nan':
                        item[key] = None
                    elif pd.isna(value):
                        item[key] = None
        # Преобразование строковых значений обратно в float
        else:
            for item in parsed_data:
                for key, value in item.items():
                    if isinstance(value, str):
                        if '.' in value:  # Если есть десятичная точка
                            # try:
                            #     date_value = datetime.strptime(value.split('.')[0], '%Y%m%d')
                            #     # Проверяем, что дата входит в интервал
                            #     if 2010 <= date_value.year <= 2025:
                            #         item[key] = date_value.strftime('%Y%m%d') # Преобразуем в формат без точки
                            # except ValueError:
                            try:
                                item[key] = float(value)  # Попробуем преобразовать в float
                            except ValueError:
                                pass  # Если не удалось преобразовать, оставляем как строку
                        elif value.isdigit():  # Если это целое число
                            item[key] = int(value)
                        elif value == 'nan':
                            item[key] = None
                        elif pd.isna(value):
                            item[key] = None
        
        #print(self.model)
        #print(f"arctic {parsed_data}")
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
        #print(self.model)
        #print(list(self.model.objects.values_list('ident', flat=True)))
        return list(self.model.objects.values_list('ident', flat=True))

    def has_keyname(self, keyname) -> bool:
        return self.model.objects.filter(ident=keyname).exists()
    
    
