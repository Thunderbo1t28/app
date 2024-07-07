import os
from django.core.management.base import BaseCommand
from scipy.stats import t

class Command(BaseCommand):
    help = 'Test'

    
    def handle(self, *args, **options):
        result = t.ppf(0.025,1303)
        result2 = t.ppf(0.975,1303)

        print(result, result2)
        

