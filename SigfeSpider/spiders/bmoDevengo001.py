# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.http import FormRequest
from urllib.parse import urlencode
import scrapy
import os
import re
import requests
import json
from ..items import SigfespiderItem


class SigfeSpiderSpider(scrapy.Spider):

    def obtener_monto(self, monto):
        return re.findall('(?<="><nobr>).*?(?=<\/nobr>)',monto)

    def obtener_principal(self, response):
        try:
            return re.search('(?<=VisualizaVariacionPopup:idIntePrincipal-V. disabled class=.af_inputText_content. type=.text. value=.).*?(?="><\/td>)', response.text)[0]
        except TypeError:
            return re.search('(?<=idIntePrincipal-V" disabled class="af_inputText_content" type="text" value=").*?(?="><\/td><\/tr)', response.text)[0]
        except:
            return "N#A"

    def obtener_titulo(self, response):
        try:
            return re.findall('(?<=af_column_data-cell">).*?(?=<\/td><td)',response.meta.get('linea'))[4]
        except (IndexError):
            return re.findall('(?<=af_column_banded-data-cell">).*?(?=<\/td><td)',response.meta.get('linea'))[4]
    # =================================================================================================================================
    URL = 'https://www.sigfe.gob.cl/sigfe/faces/autenticacion'
    name = 'bmoDevengo001'
    start_urls = [URL]

    rules = (Rule(LinkExtractor(allow=(), restrict_xpaths=('//a[@class="button next"]',)), callback="parse_page", follow= True),)

    def parse(self, response):
        if len(response.xpath('//html').re(r"2008, Oracle and")) == 1:
            return scrapy.Request(
                url = response.url + '?_afrLoop=' + response.xpath('//html').re(r"_afrLoop=(\d+)")[0],
                callback = self.parse
            )

        if len(response.xpath('//html').re(r"Formulario de Autenticaci")) == 1:
            return scrapy.FormRequest.from_response(
                response,
                formdata = {
                    'j_username': ' ',
                    'j_password': ' ',
                    'event': 'idCBIngresar',
                    'event.idCBIngresar': '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'
                },
                callback = self.redireccionador
            )

    def redireccionador(self, response):
        if len(response.xpath('//html').re(r"2008, Oracle and")) == 1:
            return scrapy.Request(
                url = response.url+'?_afrWindowMode=0&_afrLoop='+response.xpath('//html').re(r"_afrLoop=(\d+)")[0],
                callback = self.bienvenido
            )

    def bienvenido(self, response):
        if response.xpath('//*[@id="cmdLSC"]/text()').extract_first() == 'Cerrar Sesion Activa':
            print("          >>>>>>>>>>>>>>>>>>>>>>> ESTADO :", re.findall('(?<=href="#">).*?(?=<\/a><div><\/div>)',response.text)[0], "<<<<<<<<<<<<<<<<<<<<<<<" )
            return scrapy.FormRequest.from_response(
                response,
                url = 'https://www.sigfe.gob.cl/sigfe/faces/errorAutenticacion?error=used_user;1494;Pefernandez',
                formdata = {
                    '_adf.ctrl-state': re.findall(r'ctrl-state=(.+)', response.url)[0],
                    'org.apache.myfaces.trinidad.faces.FORM': 'idFormGeneraVariacion',
                    'event': 'cmdLSC',
                    'event.cmdLSC': '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'
                },
                callback = self.parse
            )

        if len(response.xpath('//html').re(r"2008, Oracle and")) == 1:
            return scrapy.Request(
                url = response.url+'&_afrLoop='+response.xpath('//html').re(r"_afrLoop=(\d+)")[0],
                callback = self.bienvenido
            )


        return scrapy.FormRequest.from_response(
            response,
            formdata = {
                'event'                 : 'idPgTpl:j_id43',
                'event.idPgTpl:j_id43'  : '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'
            },
            callback= self.consulta
        )

    def consulta(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata = {
                'idTmpB:idSeonraOpcionBusqueda'                         : '0' ,
                'idTmpB:filtroEjercicioId'                              : '10' ,
                #'idTmpB:idFolioVariacion'                               : '39823',
                'org.apache.myfaces.trinidad.faces.FORM'                : 'idTmpB:idFormBuscarVariacion',
                'event'                                                 : 'idTmpB:compBotonBuscarVarPresu:idCmbIrBuscar',
                'event.idTmpB:compBotonBuscarVarPresu:idCmbIrBuscar'    : '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'
            },
            callback= self.CriteriosDeBusqueda
        )

    def CriteriosDeBusqueda(self, response):
        filename = 'Tabla'+str(re.findall(r'(?<=href="#"> ).*?(?= <\/a><a id="idTmpB:itLink:)', response.text)[-1])+'.html'
        with open(filename, 'w') as f:
            f.write(response.text)
        self.log('Saved file %s' % filename)
        print(" ------------------------------------- >>>>>>>>>>>> Tabla <<<<<<<<<<<<<<<<< ------------------------------------- ")
        print()
        # =================================================================================================================================

        # filas - Obtengo toda la linea completa
        filas= response.xpath('//html').re(r'(?<=_afrrk=").*?(?=Historial de Ajustes)')
        #print("=================== filas : ", filas)
        for linea in filas:
            print(">>>>>>>>>>>>>>>>>> LINEA : ", linea)
            # numero -Get el numero de la linea del 0 al 9
            numero = str(re.findall('(?<="idTmpB:tRes:).(?=:idCmlIrVisualizar)',linea)[0])
            print("numero : ", numero, type(numero))
            print()

        # -------------------------------------------------------------------------------------------------------------
        print(" >>>>>>>> : 0")
        yield scrapy.FormRequest.from_response(
            response,
            dont_filter = True,
            formdata = {
                'Request URL': response.url,
                'idTmpB:idSeonraOpcionBusqueda':'0',
                'idTmpB:filtroEjercicioId': '10',
                'org.apache.myfaces.trinidad.faces.FORM': 'idTmpB:idFormBuscarVariacion',
                'oracle.adf.view.rich.DELTAS': '{idTmpB:tRes={rows=10,scrollTopRowKey|p=0,selectedRowKeys=0}}',
                'event': 'idTmpB:tRes:0:idCmlIrVisualizar',
                'event.'+'idTmpB:tRes:0:idCmlIrVisualizar' : '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'
            }
        )

        yield scrapy.FormRequest.from_response(
            response,
            dont_filter = True,
            formdata = {
                'Request URL': response.url,
                'Adf-Rich-Message': 'true',
                'event': 'VisualizaVariacionPopup:idPopVisualizaVariacion',
                'event.VisualizaVariacionPopup:idPopVisualizaVariacion': '<m xmlns="http://oracle.com/richClient/comm"><k v="suppressMessageClear"><s>true</s></k><k v="type"><s>fetch</s></k></m>'
            },
            callback = self.modal
        )
        # -------------------------------------------------------------------------------------------------------------
        #scrapy.shell.inspect_response(response, self)

        # 2) seguir los enlaces de pagina siguiente
        siguiente = re.findall(r'(?<=id="idTmpB:itLink:).*?(?=:linkDinamic")', response.text)[-1:]
        for x in siguiente:
            print(">>>>>>>>>>>>>>>>>>>< SIGUIENTE : ", x)

            yield scrapy.FormRequest.from_response(
                response,
                formdata = {
                    'idTmpB:idSeonraOpcionBusqueda': '0',
                    'idTmpB:filtroEjercicioId': '10',
                    'org.apache.myfaces.trinidad.faces.FORM': 'idTmpB:idFormBuscarVariacion',
                    'oracle.adf.view.rich.DELTAS': '{idTmpB:tRes={rows=10,scrollTopRowKey|p=0}}',
                    'event': 'idTmpB:itLink:'+x+':linkDinamic',
                    'event.idTmpB:itLink:'+x+':linkDinamic': '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'
                },
                callback= self.CriteriosDeBusqueda
            )

    def modal(self, response):
        print('           : _adf.ctrl-state : ', re.findall(r'ctrl-state=(.+)', response.url)[0])
        #print('           : javax.faces.ViewState : ', re.findall(r'.ViewState" value="(\S+)["]', response.text )[0] )

        print(" ")
        print("========================================== INICIO MODAL =================================")
        numero  = response.meta.get('numero')
        linea   = response.meta.get('linea')

        filename = str(numero)+'.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        for concepto in re.findall('(?<=variacion generar componenteConceptoPresupuestarioVariacion conceptoPresupuestario texto).*?(?=<\/td><\/tr><\/tbody><\/table>)',response.text):
            item = SigfespiderItem()
            item["Concepto_Presupuestario"] = re.findall('(?<=af_commandLink p_AFDisabled">).*?(?=<\/a><div><\/div><div><\/div><\/div><div )',concepto)[0]
            item["Principal"]               = self.obtener_principal(response)
            item["Monto_Neto"]             = re.findall('(?<=type="text" value=").*?(?=">)',concepto)[0]
            yield item
        print("========================================== FIN MODAL =================================")
        print(" ")

