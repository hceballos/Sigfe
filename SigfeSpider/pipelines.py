# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3

class SigfespiderPipeline(object):

    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        self.conn = sqlite3.connect("data.db")
        self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute("""DROP TABLE IF EXISTS sigfe""")
        self.curr.execute("""create table sigfe(
            Concepto_Presupuestario text,
            Principal text,

            Monto_Neto text
            )""")

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self, item):
        self.curr.execute('''INSERT into sigfe values (?, ?, ?)''',(
            item['Concepto_Presupuestario'],
            item['Principal'],

            item['Monto_Neto']
            #item['oc']
             ))
        self.conn.commit()
