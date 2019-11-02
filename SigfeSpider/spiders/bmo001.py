# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
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

    SIGFE_USERNAME = os.environ['SIGFE_USERNAME']
    SIGFE_PASSWORD = os.environ['SIGFE_PASSWORD']

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
    name = 'bmo001'
    start_urls = [URL]

    def parse(self, response):
        print(self.SIGFE_USERNAME)
        print(type(self.SIGFE_USERNAME))
        print(self.SIGFE_PASSWORD)
        print(type(self.SIGFE_PASSWORD))
        print(" ============================================== PARSE ============================================================ ")
        if len(response.xpath('//html').re(r"2008, Oracle and")) == 1:
            return scrapy.Request(
                url = response.url + '?_afrWindowMode=0&_afrLoop=' + response.xpath('//html').re(r"_afrLoop=(\d+)")[0],
                callback = self.parse)

        if len(response.xpath('//html').re(r"Formulario de Autenticaci")) == 1:
            return scrapy.FormRequest.from_response(
                response, 
                formdata = {'j_username'            :'',
                            'j_password'            :'',
                            'event'                 :'idCBIngresar',
                            'event.idCBIngresar'    :'<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'},
                callback = self.redireccionador)

    def redireccionador(self, response):
        if len(response.xpath('//html').re(r"2008, Oracle and")) == 1:
            return scrapy.Request(
                url = response.url + '?_afrWindowMode=0&_afrLoop=' + response.xpath('//html').re(r"_afrLoop=(\d+)")[0],
                callback = self.bienvenido)

    def bienvenido(self, response):
        if response.xpath('//*[@id="cmdLSC"]/text()').extract_first() == 'Cerrar Sesion Activa':
            print("   >>>>>>>>>>>>>>>>>>>>>>> ESTADO :", response.xpath('//*[@id="cmdLSC"]/text()').extract_first().upper(), "<<<<<<<<<<<<<<<<<<<<<<<" )
            return scrapy.FormRequest.from_response(
                response,
                url = 'https://www.sigfe.gob.cl/sigfe/faces/errorAutenticacion?error=used_user;1494;Pefernandez',
                formdata = {
                    '_adf.ctrl-state': re.findall(r'ctrl-state=(.+)', response.url)[0],
                    'org.apache.myfaces.trinidad.faces.FORM': 'idFormGeneraVariacion',
                    'event': 'cmdLSC',
                    'event.cmdLSC': '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'},
                callback = self.parse)

        print("   >>>>>>>>>>>>>>>>>>>>>>> ESTADO :", re.search('(?<=<strong>).*?(?=<\/strong>)', response.text)[0].upper(), "<<<<<<<<<<<<<<<<<<<<<<<" )
        print("   >>>>>>>>>>>>>>>>>>>>>>> ESTADO :", re.search('(?<=<\/strong>).*?(?=<\/p><p>)', response.text)[0].upper(), "<<<<<<<<<<<<<<<<<<<<<<<" )
        return scrapy.FormRequest.from_response(
            response,
            formdata = {'event'                 : 'idPgTpl:j_id43',
                        'event.idPgTpl:j_id43'  : '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'},
            callback= self.consulta)

    def consulta(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata = {'idTmpB:idSeonraOpcionBusqueda'                         : '0' ,
                        'idTmpB:filtroEjercicioId'                              : '10' ,
                        'org.apache.myfaces.trinidad.faces.FORM'                : 'idTmpB:idFormBuscarVariacion',
                        'event'                                                 : 'idTmpB:compBotonBuscarVarPresu:idCmbIrBuscar',
                        'event.idTmpB:compBotonBuscarVarPresu:idCmbIrBuscar'    : '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'},
            callback= self.CriteriosDeBusqueda)

    def CriteriosDeBusqueda(self, response):
        print( 'SIGUIENTE               :' , re.findall(r'(?<=href="#"> ).*?(?= <\/a><a id="idTmpB:itLink:)', response.text) )
        print( 'URL                     :' , response.url )
        print( 'javax.faces.ViewState   : ', response.xpath('//html').re(r'ViewState" value="(\S+)["]')[0] )
        print( 'ctrl-state              :' , re.findall(r'ctrl-state=(.+)', response.url)[0]  )

        filename = 'Tabla'+str(re.findall(r'(?<=href="#"> ).*?(?= <\/a><a id="idTmpB:itLink:)', response.text)[-1])+'.html'
        with open(filename, 'w') as f:
            f.write(response.text)
        self.log('Saved file %s' % filename)


        filas= response.xpath('//html').re(r'(?<=_afrrk=").*?(?=Historial de Ajustes)')

        for linea in filas: #OK
            yield self.cb1(response, linea)
            print("FormRequest : ", str(re.findall('.(?=:idCmlIrVisualizar)',linea)[0]) )

        print(">>>>>>>>", 'https://www.sigfe.gob.cl/sigfe/faces/task-flow-variacion-busqueda/busquedaVariacionPresupuestaria?_adf.ctrl-state='+re.findall(r'ctrl-state=(.+)', response.url)[0]  )
        print(">>>>>>>>", 'javax.faces.ViewState', response.xpath('//html').re(r'ViewState" value="(\S+)["]')[0]  )
        #

    def cb1(self, response, linea):
        print('<<<<<<cb1')
        return scrapy.FormRequest.from_response(response,
            meta={
                'numero': re.findall(
                    '(?<="idTmpB:tRes:).(?=:idCmlIrVisualizar)',
                    linea
                )[0],
                'linea': linea
            },
            dont_filter=True,
            formdata = {'Request URL': response.url,
                        'idTmpB:idSeonraOpcionBusqueda':'0',
                        'idTmpB:filtroEjercicioId': '10',
                        'org.apache.myfaces.trinidad.faces.FORM': 'idTmpB:idFormBuscarVariacion',
                        'oracle.adf.view.rich.DELTAS': '{VisualizaVariacionPopup:idPopVisualizaVariacion={_shown=},idTmpB:tRes={selectedRowKeys='+str(re.findall('.(?=:idCmlIrVisualizar)',linea)[0])+'}}',
                        'event': 'idTmpB:tRes:'+str(re.findall('.(?=:idCmlIrVisualizar)',linea)[0])+':idCmlIrVisualizar',
                        'event.'+'idTmpB:tRes:'+str(re.findall('.(?=:idCmlIrVisualizar)',linea)[0])+':idCmlIrVisualizar' : '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'},
            callback=self.cb2)

    def cb2(self, response):
        print('<<<<<<cb2')
        linea = response.meta.get('linea')
        return scrapy.FormRequest.from_response(
            response,
            meta={
                'numero': (
                    re.findall(
                        '(?<="idTmpB:tRes:).(?=:idCmlIrVisualizar)',
                        linea
                    )[0]
                ),
                'linea': linea
            },
            dont_filter=True,
            formdata = {'Request URL': response.url,
                        'Adf-Rich-Message': 'true',
                        'event': 'VisualizaVariacionPopup:idPopVisualizaVariacion',
                        'event.VisualizaVariacionPopup:idPopVisualizaVariacion': '<m xmlns="http://oracle.com/richClient/comm"><k v="suppressMessageClear"><s>true</s></k><k v="type"><s>fetch</s></k></m>'},
            callback=self.modal)

    def modal(self, response):
        print("modal :", str(re.findall('.(?=:idCmlIrVisualizar)',response.meta.get('linea'))[0])    )

        filename = str(re.findall('.(?=:idCmlIrVisualizar)',response.meta.get('linea'))[0])+'.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        for concepto in re.findall('(?<=variacion generar componenteConceptoPresupuestarioVariacion conceptoPresupuestario texto).*?(?=<\/td><\/tr><\/tbody><\/table>)',response.text ):
            item = SigfespiderItem()
            item["Concepto_Presupuestario"] = re.findall('(?<=af_commandLink p_AFDisabled">).*?(?=<\/a><div><\/div><div><\/div><\/div><div )',concepto)[0]
            item["Principal"]               = self.obtener_principal(response)
            item["Monto_Documento"]         = re.findall('(?<=type="text" value=").*?(?=">)',concepto)[0]
            item["Id"]                      = re.findall('(?<="><nobr>).*?(?=<\/nobr>)',response.meta.get('linea'))[0]
            item["Folio"]                   = re.findall('(?<="><nobr>).*?(?=<\/nobr>)',response.meta.get('linea'))[1]
            item["Ejercicio"]               = re.findall('(?<="><nobr>).*?(?=<\/nobr>)',response.meta.get('linea'))[2]
            item["Numero_Documento"]        = re.findall('(?<="><nobr>).*?(?=<\/nobr>)',response.meta.get('linea'))[3]
            item["Titulo"]                  = self.obtener_titulo(response)
            item["Moneda"]                  = re.findall('(?<="><nobr>).*?(?=<\/nobr>)',response.meta.get('linea'))[4]
            item["Monto"]                   = self.obtener_monto(response.meta.get('linea'))[5]
            yield item
