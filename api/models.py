from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class LoadHistory(models.Model):
    STATUS_CHOICES = (
        ('running', 'Running'),
        ('success', 'Success'),
        ('error', 'Error'),
    )
    
    status = models.CharField(max_length=20)
    message = models.TextField()
    details = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

class OrderStack(models.Model):
    """Базовый класс для стеков ордеров"""
    ident = models.CharField(max_length=255, default='', blank=True)
    data = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} ({self.ident})"

class INSTRUMENT_ORDER_STACK(OrderStack):
    """Модель для хранения инструментальных ордеров"""
    class Meta:
        verbose_name = "Instrument Order Stack"
        verbose_name_plural = "Instrument Order Stacks"
        unique_together = ('ident',)

class CONTRACT_ORDER_STACK(OrderStack):
    """Модель для хранения контрактных ордеров"""
    class Meta:
        verbose_name = "Contract Order Stack"
        verbose_name_plural = "Contract Order Stacks"
        unique_together = ('ident',)

class BROKER_ORDER_STACK(OrderStack):
    """Модель для хранения брокерских ордеров"""
    class Meta:
        verbose_name = "Broker Order Stack"
        verbose_name_plural = "Broker Order Stacks"
        unique_together = ('ident',)

class Task(models.Model):
    """Модель для отслеживания задач Celery"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('started', 'Started'),
        ('success', 'Success'),
        ('failure', 'Failure'),
    )
    
    task_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Task {self.task_id} ({self.status})"

class ContractPosition(models.Model):
    """Модель для хранения позиций по контрактам"""
    contract_id = models.CharField(max_length=255)
    quantity = models.IntegerField(default=0)
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contract Position"
        verbose_name_plural = "Contract Positions"
        unique_together = ('contract_id',)

    def __str__(self):
        return f"Position for {self.contract_id}: {self.quantity} @ {self.average_price}"