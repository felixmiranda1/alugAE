from django.contrib import admin
from .models import Template, Contract, Clause, Document

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default', 'created_at')
    search_fields = ('name',)

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('landlord', 'tenant', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('landlord__username', 'tenant__username')

@admin.register(Clause)
class ClauseAdmin(admin.ModelAdmin):
    list_display = ('contract', 'added_by')
    search_fields = ('contract__id', 'added_by__username')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('contract', 'created_at')
    search_fields = ('contract__id',)
