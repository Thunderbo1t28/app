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
            return pd.DataFrame(arctic_data.data)
        except self.model.DoesNotExist:
            return pd.DataFrame()

    def write(self, ident: str, data: pd.DataFrame):

        '''# Создать копию данных
        data_copy = data.copy()
        # Добавить индексы как столбец в данные
        data_copy.reset_index(inplace=True)
        # Преобразовать Timestamp в строковый формат
        data_copy['index'] = data_copy['index'].dt.strftime('%Y-%m-%d %H:%M:%S')
        # Преобразовать данные в словарь
        '''
        data_present = sorted(data.columns)
        #print(data_present)
        #print(data)
        data_dict = data.to_dict(orient='records')
        self.manager.create_arctic_data(model=self.model, ident=ident, data=data_dict)

    def delete(self, ident: str):
        self.model.objects.filter(ident=ident).delete()

    def get_keynames(self) -> list:
        return list(self.model.objects.values_list('ident', flat=True))

    def has_keyname(self, keyname) -> bool:
        return self.model.objects.filter(ident=keyname).exists()
