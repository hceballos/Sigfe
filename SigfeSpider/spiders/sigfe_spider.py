# -*- coding: utf-8 -*-

# documentos
#   * id
#   * folio
#   * ejercicio
#   * numero documento
#   - monto
#   - titulo devengo
#   - descripcion devengo
#   - tipo presupuesto

# factura
#   * principal
#   * numero documento
#   - tipo documento
#   - requerimiento
#   - descripcion
#   - fecha documento
#   - fecha recepcion conforme
#   - numero orden compra
#   - fecha ingreso
#   - moneda documento
#   - monto total bruto clp
#   - compromiso presupuestario
#   - iniciativa de inversion
#   - concepto presupuestario
#   - monto documento
#   - fecha cumplimiento

  
from urllib.parse import urlencode
import scrapy

class SigfeSpiderSpider(scrapy.Spider):

    URL = 'https://www.sigfe.gob.cl/sigfe/faces/autenticacion'

    name = 'sigfe_spider'
    start_urls = [URL]

    def get_afrloops(self, response):
        return response.xpath('//html').re(r"_afrLoop=(\d+)")

    def get_url_with_afrloop(self, response):
        params = {
            '_afrLoop': self.get_afrloops(response)[0]
        }
        return response.url + '?' + urlencode(params)

    def process_loopback(self, response):
        print('>>>process_loopback')
        if len(self.get_afrloops(response)) == 0:
            return

        print('>>>process_loopback ok')
        yield scrapy.Request(
            url = self.get_url_with_afrloop(response),
            callback = self.process_loopback
        )

    def parse(self, response):
        print('>>>parse0')
        self.process_loopback(response)
        print('>>>parse1')

        with open('a.html', 'wb') as f:
            f.write(response.body)
        scrapy.shell.inspect_response(response, self)

        yield scrapy.FormRequest.from_response(
            response,
            formdata = {
                'j_username':'',
                'j_password':'',
                'event':'idCBIngresar',
                'event.idCBIngresar':'<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'
            },
            callback = self.welcome_loopback
        )

    def welcome_loopback(self, response):
        yield scrapy.Request(
            url = self.get_url_with_afrloop(response),
            callback = self.welcome
        )

    def welcome(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            formdata = {
                'event': 'idPgTpl:j_id43',
                'event.idPgTpl:j_id43': '<m xmlns="http://oracle.com/richClient/comm"><k v="type"><s>action</s></k></m>'
            },
            callback = self.main_form
        )

    def main_form(self, response):
        with open('b.html', 'wb') as f:
            f.write(response.body)
        scrapy.shell.inspect_response(response, self)