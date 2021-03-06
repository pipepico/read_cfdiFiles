#!/usr/bin/env python

# -*- coding:utf-8 -*-
# -*- coding: utf-8 -*-

import time

from datetime import datetime

import os

import sys

import sqlite3

import glob

import shutil

from xml.dom import minidom



class Producto:
    def __init__(self,clave,descripcion,precio):
        self.clave = clave
        self.descripcion = descripcion
        self.precio = precio
        
    def myfunc(self):
        return self.clave,self.descripcion,self.precio
        # print("{} - {} - ${}".format(self.clave,self.descripcion,self.precio))
        # print(self.clave,self.descripcion,"$"+self.precio)

    def printdata(self):
        self.myfunc()


def open_file(file_name):
    """Funcion que extrae informacion de un cfdi, y la devuelve en un diccionario"""

    global datos_cfdi

    global tipo_doc

    global serie

    global folio

    global folio_factura

    global total_factura

    global str_total

    global rfc_emisor

    global rfc_receptor

    global uuid

    global f_exp

    global f_tim

    global uuid_relacionado

    global cAt

    global uAt

    try:

        doc = minidom.parse(file_name)

    except:

        return

    doc = minidom.parse(file_name)

    uuid_relacionado = ''

    datos_cfdi = doc.getElementsByTagName("cfdi:Comprobante")
    
    for dato_cfdi in datos_cfdi:

        get_version = dato_cfdi.getAttribute("Version")
        cAt = datetime.now().isoformat()
        uAt = datetime.now().isoformat()

        if(get_version):

            f_exp = dato_cfdi.getAttribute("Fecha")

            serie = dato_cfdi.getAttribute("Serie")

            folio = dato_cfdi.getAttribute("Folio")

            folio_factura = serie+folio

            total_factura = float(dato_cfdi.getAttribute("Total"))

            str_total = "{:,.2f}".format(total_factura)

            tipo_doc = dato_cfdi.getAttribute("TipoDeComprobante")

            if (tipo_doc == "I"):

                tipo_doc = "INGRESO"

                rfc_emisor = get_rfc(dato_cfdi, "Emisor")

                nombre_emisor = get_nombre(dato_cfdi, "Emisor")

                rfc_receptor = get_rfc(dato_cfdi, "Receptor")

                nombre_receptor = get_nombre(dato_cfdi, "Receptor")

            elif(tipo_doc == "E"):

                tipo_doc = "EGRESO"

                uuid_relacionado = iteracion_relacion_cfdi(doc)

                rfc_emisor = get_rfc(dato_cfdi, "Emisor")

                nombre_emisor = get_nombre(dato_cfdi, "Emisor")

                rfc_receptor = get_rfc(dato_cfdi, "Receptor")

                nombre_receptor = get_nombre(dato_cfdi, "Receptor")

            elif(tipo_doc == "P"):

                tipo_doc = "PAGO"

                uuid_relacionado = iteracion_relacion_cfdi(doc)

                rfc_emisor = get_rfc(dato_cfdi, "Emisor")

                nombre_emisor = get_nombre(dato_cfdi, "Emisor")

                rfc_receptor = get_rfc(dato_cfdi, "Receptor")

                nombre_receptor = get_nombre(dato_cfdi, "Receptor")

        else:

            tipo_doc = ""

            serie = ""

            folio = ""

            folio_factura = ""

            total_factura = ""

            str_total = ""

            rfc_emisor = ""

            rfc_receptor = ""

            uuid = ""

            f_exp = ""

            f_tim = ""

            uuid_relacionado = ""

            return False

    datos_complementos = doc.getElementsByTagName("cfdi:Complemento")

    for dato_c in datos_complementos:

        datos_timbrado = dato_c.getElementsByTagName("tfd:TimbreFiscalDigital")

        for datoTimbrado in datos_timbrado:

            uuid = datoTimbrado.getAttribute("UUID")

            f_tim = datoTimbrado.getAttribute("FechaTimbrado")

    if (tipo_doc == "INGRESO"):

        guardando_en_bd_FACT(folio_factura, total_factura, f_exp,
                             f_tim, uuid, rfc_emisor, rfc_receptor, cAt, uAt)

    elif (tipo_doc == "EGRESO"):

        guardando_en_bd_NC(folio_factura, total_factura, f_exp, f_tim,
                           uuid, uuid_relacionado, rfc_emisor, rfc_receptor, cAt, uAt)

    """elif (tipo_doc = "PAGO"):

        guardando_en_bd_PAGO(folio_factura,str_total,f_exp,uuid,rfc_emisor,rfc_receptor)"""

    print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(folio_factura, total_factura,
                                              f_exp, uuid, rfc_emisor, rfc_receptor, uuid_relacionado))


def get_rfc(doc, tipo):

    datos = doc.getElementsByTagName("cfdi:{}".format(tipo))

    for dato in datos:

        rfc = dato.getAttribute("Rfc")

    return rfc


def get_nombre(doc, tipo):

    datos = doc.getElementsByTagName("cfdi:{}".format(tipo))

    for dato in datos:

        nombre = dato.getAttribute("Nombre")

    return nombre


def iteracion_relacion_cfdi(doc):

    cfdi_relacionados = doc.getElementsByTagName("cfdi:CfdiRelacionados")

    u_relacion = ""

    for dato_nv1 in cfdi_relacionados:

        cfdi_relacionado = doc.getElementsByTagName("cfdi:CfdiRelacionado")

        for dato_nv2 in cfdi_relacionado:

            u_relacion = dato_nv2.getAttribute("UUID")

    return u_relacion

def iteracion_por_producto(doc):
    pass


def consulta(consultar):

    valor = input("Ingrese {}:\t".format(consultar))

    return valor


"""

folio = consulta('folio')

importe = consulta('importe')

f_exp = consulta('f_exp')

uuid = consulta('uuid')

rfc = consulta('rfc')

rfc_e = consulta('rfc_e')

"""


def guardando_en_bd_FACT(folio, importe, f_exp, f_tim, uuid, rfc_e, rfc_r, cAt, uAt):

    conn = sqlite3.connect('cfdis.db')

    c = conn.cursor()

    c.execute("INSERT OR IGNORE INTO facturas(folio,importe,Fecha_expedicion,fecha_timbrado,UUID,id_proveedor,id_empresa,createdAt,updatedAt) VALUES(?,?,?,?,?,?,?,?,?)",
              (folio, importe, f_exp, f_tim, uuid, rfc_e, rfc_r, cAt, uAt))

    conn.commit()

    conn.close()


def guardando_en_bd_NC(folio, importe, f_exp, f_tim, uuid, uuid_relacionado, rfc_e, rfc_r, cAt, uAt):

    conn = sqlite3.connect('cfdis.db')

    c = conn.cursor()

    c.execute("INSERT OR IGNORE INTO notas_creditos(folio,importe,fecha_expedicion,fecha_timbrado,UUID,UUID_RELACIONADO,id_proveedor,id_empresa,createdAt,updatedAt) VALUES(?,?,?,?,?,?,?,?,?,?)",
              (folio, importe, f_exp, f_tim, uuid, uuid_relacionado, rfc_e, rfc_r, cAt, uAt))

    conn.commit()

    conn.close()


if __name__ == '__main__':

    archivos = glob.glob("{}*.xml".format("../Downloads/"))

    contador = 0

    # open_file("../Downloads/xmls/SO1_XM_CFDI_FacturaNormal_CF_242550_242550.xml")
    for i in archivos:

        contador += 1
        open_file(i)
        
        shutil.move(i, '../Downloads/xmls/')

    print('Numero de Archivos consultados:\t{}'.format(contador))

    # guardando_en_bd_FACT(folio,importe,f_exp,uuid,rfc)



"""
    # iteracion para productos
    datos_conceptos = doc.getElementsByTagName("cfdi:Conceptos")
    for dato_concepto in datos_conceptos:
        datos_concepto = dato_concepto.getElementsByTagName("cfdi:Concepto")
        
        for conceptos in datos_concepto:
            # product = Producto(conceptos.getAttribute("ClaveProdServ"),conceptos.getAttribute("Descripcion"),conceptos.getAttribute("ValorUnitario"))
            atributos = conceptos.attributes

            # print(dir(atributos))
            print(atributos.keys)
            # print(product.myfunc())
            # product.printdata()
            # print(conceptos.getAttribute("Descripcion") +" - $" + conceptos.getAttribute("ValorUnitario"))
   """
