from django.db import models
import pandas as pd

class ArcticDataModel(models.Model):
    ident = models.CharField(max_length=255, unique=True)
    data = models.JSONField()

    def __str__(self):
        return self.ident

class ArcticDataManager(models.Manager):
    def create_arctic_data(self, ident, data):
        arctic_data = self.create(ident=ident, data=data)
        return arctic_data

class arcticData(object):
    def __init__(self, collection_name, mongo_db=None):
        self.collection_name = collection_name
        self.manager = ArcticDataManager()

    def read(self, ident):
        try:
            arctic_data = ArcticDataModel.objects.get(ident=ident)
            return pd.DataFrame(arctic_data.data)
        except ArcticDataModel.DoesNotExist:
            return pd.DataFrame()

    def write(self, ident: str, data: pd.DataFrame):
        data_dict = data.to_dict(orient='records')
        self.manager.create_arctic_data(ident=ident, data=data_dict)

    def delete(self, ident: str):
        ArcticDataModel.objects.filter(ident=ident).delete()

    def get_keynames(self) -> list:
        return list(ArcticDataModel.objects.values_list('ident', flat=True))

    def has_keyname(self, keyname) -> bool:
        return ArcticDataModel.objects.filter(ident=keyname).exists()