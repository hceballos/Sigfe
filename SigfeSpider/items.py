# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SigfespiderItem(scrapy.Item):
    # define the fields for your item here like:
    """
    Id = scrapy.Field()
    DescripcionDevengo = scrapy.Field()
    TipoDeDocumento = scrapy.Field()
    Principal = scrapy.Field()
    RequerimientoCompromiso = scrapy.Field()
    NumeroDocumento = scrapy.Field()
    FechaRecepcionConforme = scrapy.Field()
    NumeroOrdenCompra = scrapy.Field()
    FechaIngreso = scrapy.Field()
    MontoTotalBruto = scrapy.Field()
    CompromisoPresupuestario = scrapy.Field()
    """
    Concepto_Presupuestario = scrapy.Field()
    Principal = scrapy.Field()
    Monto_Documento = scrapy.Field()

    Id = scrapy.Field()
    Folio = scrapy.Field()
    Ejercicio = scrapy.Field()
    Numero_Documento = scrapy.Field()
    Titulo = scrapy.Field()
    Moneda = scrapy.Field()
    Monto = scrapy.Field()

    #Titulo_Devengo = scrapy.Field()
    #Principal = scrapy.Field()
    #Orden_de_Compra = scrapy.Field()

