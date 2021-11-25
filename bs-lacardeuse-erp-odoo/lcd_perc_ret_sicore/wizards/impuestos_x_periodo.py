# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo import tools
from datetime import datetime,date  
from odoo.exceptions import UserError
import base64,math
import logging
_logger = logging.getLogger(__name__)

class Wzd_impuestos_x_periodo(models.TransientModel):
    _name = 'nybble.wzd_impuestos_x_periodo'
    _description = 'Wizard para generar archivos de impuestos por período'

    # @api.depends('export_data')
    # def _compute_files(self):
    #    self.ensure_one()
    #    if type(self.id) == int:
    #        if self.export_data:
    #            nombre = ''
    #            if self.tipo_txt == 'piibbarbaa':
    #                nombre = 'PIIBBARBAA'
    #            elif self.tipo_txt == 'riibbarbaa':
    #                nombre = 'RIIBBARBAA'
    #            elif self.tipo_txt == 'priibbcabaa':
    #                nombre = 'PRIIBBCABAA'
    #            elif self.tipo_txt == 'piibbcabaanc':
    #                nombre = 'PIIBBCABAANCred'
    #             elif self.tipo_txt == 'sicore':
    #                 nombre = 'SICORE'
    #             if self.tipo_txt == 'sicore':
    #                 self.export_filename = _('Sicore_%s_%s.txt') % (str(self.fecha_desde), str(self.fecha_hasta))
    #             else:
    #                 self.export_filename = _('%s_%s_%s.txt') % (nombre, str(self.fecha_desde), str(self.fecha_hasta))




    name= fields.Char('Descripción',required=True)
    fecha_desde= fields.Date('Fecha Desde',required=True)
    fecha_hasta=fields.Date('Fecha Hasta',required=True)
#    impuestos=fields.Many2many('account.tax',string='Impuestos',required=True)
#    impuesto=fields.Many2one('account.tax',string='Impuesto',required=True)
    tipo_txt=fields.Selection([('piibbarbaa', 'Percepción IIBB ARBA Aplicada'),('riibbarbaa', 'Retención IIBB ARBA Aplicada'),('priibbcabaa', 'Percepción/Retención IIBB CABA Aplicada'),('piibbcabaanc', 'Percepción IIBB CABA Aplicada (Notas de Crédito)'),('sicore', 'Sicore')],'Tipo')
    export_data = fields.Text(string='Contenido archivo')
    export_file = fields.Binary('Archivo')
    export_filename = fields.Char('Archivo nombre')
    



    # @api.multi
    def generar_archivo(self):
        #Busco apuntes contables que tengan ese impuesto
        if self.tipo_txt=='piibbcabaanc':
            apuntes=self.env['account.move.line'].search([('date','>=',self.fecha_desde),('date','<=',self.fecha_hasta),('tax_line_id.tipo_txt','=','piibbcabaa')],order='date')
        elif self.tipo_txt=='priibbcabaa':
            apuntes=self.env['account.move.line'].search([('date','>=',self.fecha_desde),('date','<=',self.fecha_hasta),('tax_line_id.tipo_txt','in',['piibbcabaa','riibbcabaa'])],order='date')
        elif self.tipo_txt=='sicore':
            self.ensure_one()
            payments = self.env['account.payment'].search([('payment_type','=','outbound'),('state','not in',['cancelled','draft']),('payment_date','<=',self.fecha_hasta),('payment_date','>=',self.fecha_desde)],order='payment_date')
        else:
            apuntes  = self.env['account.move.line'].search([('date','>=',self.fecha_desde),('date','<=',self.fecha_hasta),('tax_line_id.tipo_txt','=',self.tipo_txt)],order='date')
            #import pdb; pdb.set_trace()
        #genero archivo
        windows_line_ending = '\r' + '\n'
        #windows_line_ending = '\n'
        string = ''
        if self.tipo_txt=='riibbarbaa':
            nombre = 'RIIBBARBAA'
            for apunte in apuntes:
                #1er campo: cuit separado por guiones
                print('1er campo: cuit separado por guiones:',apunte.partner_id.main_id_number[:2]+'-'+apunte.partner_id.main_id_number[2:-2].zfill(8)+'-'+apunte.partner_id.main_id_number[-2:])
                string+=apunte.partner_id.main_id_number[:2]+'-'+apunte.partner_id.main_id_number[2:-1].zfill(8)+'-'+apunte.partner_id.main_id_number[-1:]
                #2do campo: fecha formato dd/mm/yyyy
                #string+=apunte.date[-2:]+'/'+apunte.date[5:-3]+'/'+apunte.date[:4]
                d=''
                if len(str(apunte.date.day)) == 1:
                    d ='0'+ str(apunte.date.day)
                else:
                    d =str(apunte.date.day)
                m=''
                if len(str(apunte.date.month)) == 1:
                    m ='0'+ str(apunte.date.month)
                else:
                    m =str(apunte.date.month)
                string+=str(d)+'/'+str(m)+'/'+str(apunte.date.year)
                #3er campo: 4 digitos para numero de sucursal 0001 ???? Chequear
                print('3er campo: 4 digitos para numero de sucursal 0001 ???? Chequear:','0001')
                string+='0001'
                #4to campo: 8 digitos para numero de retención ???? Chequear
                print('4to campo: 8 digitos para numero de retención ???? Chequear:',apunte.name.zfill(8))
                string+=apunte.name.zfill(8)
                #string+=apunte.payment_id.name.zfill(8)
                #5to campo: importe de la percepción retención 11 digitos incluida la coma
                parte_decimal, parte_entera = math.modf(apunte.credit)
                parte_entera=str(parte_entera).split('.')[0]
                parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                string+=(parte_entera+','+parte_decimal).zfill(11)
                #5to campo: Letra "A" ?????
                string+='A'
                string+=windows_line_ending
        elif self.tipo_txt=='piibbarbaa':
            #ARMAARRRRRR
            nombre = 'PIIBBARBAA'
            for apunte in apuntes:
                #1er campo: cuit separado por guiones
                print('1er campo: cuit separado por guiones:',apunte.partner_id.main_id_number[:2]+'-'+apunte.partner_id.main_id_number[2:-2].zfill(8)+'-'+apunte.partner_id.main_id_number[-2:])
                string+=apunte.partner_id.main_id_number[:2]+'-'+apunte.partner_id.main_id_number[2:-1].zfill(8)+'-'+apunte.partner_id.main_id_number[-1:]
                #2do campo: fecha formato dd/mm/yyyy
                # string+=apunte.date[-2:]+'/'+apunte.date[5:-3]+'/'+apunte.date[:4]
                d=''
                if len(str(apunte.date.day)) == 1:
                    d ='0'+ str(apunte.date.day)
                else:
                    d =str(apunte.date.day)
                m=''
                if len(str(apunte.date.month)) == 1:
                    m ='0'+ str(apunte.date.month)
                else:
                    m =str(apunte.date.month)
                string+=str(d)+'/'+str(m)+'/'+str(apunte.date.year)
                #3er campo: tipo de comprobante (F=Factura, R=Recibo, C=Nota Crédito, D =Nota Debito, V=Nota de Venta)
                #4to campo: letra de comprobante (ABC o "blanco")
                if apunte.invoice_id.journal_document_type_id.document_type_id.doc_code_prefix[0:2]=="FA":
                    comprob="F"+apunte.invoice_id.journal_document_type_id.document_type_id.document_letter_id.name
                elif apunte.invoice_id.journal_document_type_id.document_type_id.doc_code_prefix[0:2]=="ND":
                    comprob="D"+apunte.invoice_id.journal_document_type_id.document_type_id.document_letter_id.name
                elif apunte.invoice_id.journal_document_type_id.document_type_id.doc_code_prefix[0:2]=="NC":
                    comprob="C"+apunte.invoice_id.journal_document_type_id.document_type_id.document_letter_id.name
                else:
                    comprob="NN"
                print('3,4to campo: tipo y letra de comprobante (ABC o "blanco"):',comprob)
                string+=comprob
                #5to campo: numero de sucursal, 4 digitos (nro pto vta)
                #6to campo: numero de emision 8 digitos (num factura)
                print('5to y 6to campo: numero de sucursal 4 letra y num de emision 8 digitos (num factura):',apunte.invoice_id.document_number.replace('-',''))
                numcompro = str(apunte.invoice_id.document_number).split('-')
                ptoventa = str(apunte.invoice_id.document_number)[1:5]
                print('ptoventa 4 caracteres:',ptoventa)
                numcom = str(numcompro[1].zfill(8))
                print('numcom 8 caracteres:',numcom)
                numcompro = str(ptoventa+numcom)
                string+=numcompro
                #string+=apunte.invoice_id.document_number.replace('-','').zfill(12)
                #7mo campo: base imponible 12 digitos con la coma
                parte_decimal, parte_entera = math.modf(apunte.invoice_id.amount_untaxed)
                parte_entera=str(parte_entera).split('.')[0]
                parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                if comprob[:1]!='C':
                    string+=(parte_entera+','+parte_decimal).zfill(12)
                else:
                    string+='-'+(parte_entera+','+parte_decimal).zfill(11)
                print('7mo campo: base imponible 12 digitos con la coma:',(parte_entera+','+parte_decimal).zfill(12))
                #8vo campo: importe percibido 11 digitos con la coma
                if comprob[:1]!='C':
                    parte_decimal, parte_entera = math.modf(apunte.credit)
                else:
                    parte_decimal, parte_entera = math.modf(apunte.debit)
                parte_entera=str(parte_entera).split('.')[0]
                parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                if comprob[:1]!='C':
                    string+=(parte_entera+','+parte_decimal).zfill(11)
                else:
                    string+='-'+(parte_entera+','+parte_decimal).zfill(10)
                print('8vo campo: importe percibido 11 digitos con la coma:',(parte_entera+','+parte_decimal).zfill(11))
                #9no campo: Letra "A"  Alta?????
                string+='A'
                string+=windows_line_ending
        elif self.tipo_txt=='priibbcabaa':
            nombre = 'PRIIBBCABAA'
            for apunte in apuntes:
                #1  campo: largo 01 tipo operación (1:retencion 2:percepcion)
                if apunte.tax_line_id.type_tax_use=='supplier':
                    tipo_operacion='1'
                elif apunte.tax_line_id.type_tax_use=='sale':
                    tipo_operacion='2'
                    if apunte.invoice_id.journal_document_type_id.document_type_id.doc_code_prefix[0:2]=='NC':
                        continue
                else:
                    tipo_operacion='0'
                string+=tipo_operacion
                #2  campo: largo 03 codigo de norma (segun tipo de operacion)
                string+='029'
                #3  campo: largo 10 fecha de retencion/percepcion 
                #string+=apunte.date[-2:]+'/'+apunte.date[5:-3]+'/'+apunte.date[:4]
                d=''
                if len(str(apunte.date.day)) == 1:
                    d ='0'+ str(apunte.date.day)
                else:
                    d =str(apunte.date.day)
                m=''
                if len(str(apunte.date.month)) == 1:
                    m ='0'+ str(apunte.date.month)
                else:
                    m =str(apunte.date.month)
                string+=str(d)+'/'+str(m)+'/'+str(apunte.date.year)
                #4  campo: largo 02 tipo cbte origen de la ret (si tipo op =1 :01 fac 02 ndeb 03 ordenpago 04 boleta de dep 05 liq de pago 06 cert de obra 07 recibo 08 con de loc de serv 09 otro comb si tipo op =2 01 factura 09 otro comp)
                #5  campo: largo 01 letra del comprobante (A,M,B,C o espacio blanco)
                if tipo_operacion=='1':
                    comprob="03 "
                elif tipo_operacion=='2':
                    comprob="01"+apunte.invoice_id.journal_document_type_id.document_type_id.document_letter_id.name
                else:
                    comprob="NNN"
                string+=comprob
                #6  campo: largo 16 nro de comprobante
                if tipo_operacion=='1':
                    num_cbte=('0001'+apunte.name).zfill(16)
                elif tipo_operacion=='2':
                    num_cbte=apunte.invoice_id.document_number.replace('-','').zfill(16)
                else:
                    num_cbte="NNNNNNNNNNNNNNNN"
                string+=num_cbte
                #7  campo: largo 10 fecha
                #string+=apunte.date[-2:]+'/'+apunte.date[5:-3]+'/'+apunte.date[:4]
                d=''
                if len(str(apunte.date.day)) == 1:
                    d ='0'+ str(apunte.date.day)
                else:
                    d =str(apunte.date.day)
                m=''
                if len(str(apunte.date.month)) == 1:
                    m ='0'+ str(apunte.date.month)
                else:
                    m =str(apunte.date.month)
                string+=str(d)+'/'+str(m)+'/'+str(apunte.date.year)
###################################################################### DIVIDO EL CODIGO -- Queda pendiente optimizarlo
                if tipo_operacion=='1':
                    #CALCULO TOTALES DE TODOO (Monto,Importe otros conceptos,Importe IVA,Monto Sujeto a Retención/ Percepción,Alícuota,Retención/Percepción Practicada)
                    imp_caba=apunte.credit
                    #Calculo imp iva
                    imp_iva='0000000000000,00'
                    #Calculo imp otros
                    imp_otros='0000000000000,00'
                    #Calculo Alícuota
                    #padron=self.env['nybble.padron'].search([('cuit','=',apunte.partner_id.main_id_number)])
                    padron=self.env['padron'].search([('cuit','=',apunte.partner_id.main_id_number),('fecha_vig_desde','>=',self.fecha_desde),('fecha_vig_hasta','<=',self.fecha_hasta)])
                    logging.info('padron: {} - padron.percepcion: {} - padron.retencion {}'.format(padron,padron.percepcion,padron.retencion))
                    if padron:
                        logging.info('tipo_operacion: {} - len(str(padron.retencion)): {} '.format(tipo_operacion,len(str(padron.retencion))))
                        if tipo_operacion=='1':
                            alicuota=float(padron.retencion)
                        else:
                            alicuota=0.0
                    else:
                        alicuota=round((imp_caba/apunte.invoice_id.amount_untaxed*100),2)
                    #Calculo monto sujeto
                    alicuota = str(alicuota).replace(',','.')
                    monto_sujeto=round(float(imp_caba)*100/float(alicuota),2)
                    parte_decimal, parte_entera = math.modf(monto_sujeto)
                    parte_entera=str(parte_entera).split('.')[0]
                    parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                    monto_sujeto=(parte_entera+','+parte_decimal).zfill(16)
                    parte_decimal, parte_entera = math.modf(imp_caba)
                    parte_entera=str(parte_entera).split('.')[0]
                    parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                    imp_caba=(parte_entera+','+parte_decimal).zfill(16)
                    parte_decimal, parte_entera = math.modf(float(alicuota))
                    parte_entera=str(parte_entera).split('.')[0]
                    parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                    alicuota=(parte_entera+','+parte_decimal).zfill(5)
                    #Calculo monto sujeto
                    monto_total=monto_sujeto
    ######################################################################
                    #8  campo: largo 16 monto del comprobante
                    string+=monto_total
                    #9  campo: largo 16 nro de cert propio (blancos o nro cert)
                    string+=' '*16
                    #10 campo: largo 01 tipo de doc del retenido (1: CDI 2: CUIL 3:CUIT)
                    if apunte.partner_id.main_id_category_id.code=='CDI':
                        tipo_doc='1'
                    elif apunte.partner_id.main_id_category_id.code=='CUIL':
                        tipo_doc='2'
                    elif apunte.partner_id.main_id_category_id.code=='CUIT':
                        tipo_doc='3'
                    else:
                        tipo_doc='N'
                    string+=tipo_doc
                    #11 campo: largo 11 nro de documento del retenido 
                    string+=apunte.partner_id.main_id_number.zfill(11)
                    #12 campo: largo 01 situacion IB del retenido (1:local 2:convenio multilateral 4:no inscripto 5: reg. simplificado) si tipo doc 1 o 2 =4
                    if tipo_doc in ['1','4']:
                        string+='4'
                    else:
                        string+='4'
                    #13 campo: largo 11 nro inscripcion ID del Retenido  Si Situación IB del Retenido=4 : 00000000000 
                    string+='0'*11
                    #14 campo: largo 01 situacion frente al iva del retenido (1 -RI 2- Exento 3-monotributo)
                    if apunte.partner_id.afip_responsability_type_id.id in [1,2,12]:
                        string+='1'
                    elif apunte.partner_id.afip_responsability_type_id.id in [5]:
                        string+='2'
                    elif apunte.partner_id.afip_responsability_type_id.id in [7,14]:
                        string+='3'
                    else:
                        string+='N'
                    #15 campo: largo 30 Razon social del retenido
                    string+=apunte.partner_id.name[0:25].replace('ñ','n').replace('Ñ','N').replace("\n"," ").replace("\r"," ").ljust(30)
                    print('num_cbte:',num_cbte)
                    #16 campo: largo 16 importe otros conceptos
                    string+=imp_otros
                    print('imp_otros:',imp_otros)
                    #17 campo: largo 16 importe iva (completar si letra comp =A,M)
                    string+=imp_iva
                    print('imp_iva:',imp_iva)
                    #18 campo: largo 16 Monto sujeto a retencion/ recepcion (Monto Sujeto a Retención/ Percepción=(Monto del comprobante - Importe Iva -Importe otros conceptos))
                    string+=monto_sujeto
                    #19 campo: largo 05 Alícuota
                    string+=alicuota
                    #20 campo: largo 16 Retención/Percepción Practicada
                    string+=imp_caba
                    #21 campo: largo 16 Monto Total Retenido/Percibido (igual a campo 20)
                    string+=imp_caba
                elif tipo_operacion=='2':
                    #Calculo importes -- Modifico monto total para que coincida con el monto imponible
                    imp_iva=0.0
                    imp_otros=0.0
                    imp_caba=0.0
                    if tipo_operacion=='2':
                        for impuesto in apunte.invoice_id.tax_line_ids:
                            if impuesto.name.find('IVA') != -1:
                                imp_iva+=impuesto.amount_total
                            elif impuesto.name.find('CABA') != -1:
                                imp_caba+=impuesto.amount_total
                            else:
                                imp_otros+=impuesto.amount_total
                    #8  campo: largo 16 monto del comprobante
                    if tipo_operacion=='2':
                        parte_decimal, parte_entera = math.modf(apunte.invoice_id.amount_untaxed+imp_iva+imp_otros)
                        parte_entera=str(parte_entera).split('.')[0]
                        parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                        monto=(parte_entera+','+parte_decimal).zfill(16)
                    else:
                        monto="NNNNNNNNNNNNNNNN"
                    string+=monto
                    #9  campo: largo 16 nro de cert propio (blancos o nro cert)
                    string+=' '*16
                    #10 campo: largo 01 tipo de doc del retenido (1: CDI 2: CUIL 3:CUIT)
                    if apunte.partner_id.main_id_category_id.code=='CDI':
                        tipo_doc='1'
                    elif apunte.partner_id.main_id_category_id.code=='CUIL':
                        tipo_doc='2'
                    elif apunte.partner_id.main_id_category_id.code=='CUIT':
                        tipo_doc='3'
                    else:
                        tipo_doc='N'
                    string+=tipo_doc
                    #11 campo: largo 11 nro de documento del retenido 
                    string+=apunte.partner_id.main_id_number.zfill(11)
                    #12 campo: largo 01 situacion IB del retenido (1:local 2:convenio multilateral 4:no inscripto 5: reg. simplificado) si tipo doc 1 o 2 =4
                    if tipo_doc in ['1','4']:
                        string+='4'
                    else:
                        string+='4'
                    #13 campo: largo 11 nro inscripcion ID del Retenido  Si Situación IB del Retenido=4 : 00000000000 
                    string+='0'*11
                    #14 campo: largo 01 situacion frente al iva del retenido (1 -RI 2- Exento 3-monotributo)
                    if apunte.partner_id.afip_responsability_type_id.id in [1,2,12]:
                        string+='1'
                    elif apunte.partner_id.afip_responsability_type_id.id in [5]:
                        string+='2'
                    elif apunte.partner_id.afip_responsability_type_id.id in [7,14]:
                        string+='3'
                    else:
                        string+='N'
                    #15 campo: largo 30 Razon social del retenido
                    string+=apunte.partner_id.name[0:29].replace('ñ','n').replace('Ñ','N').replace('\n'," ").replace('\r'," ").ljust(30)
                    print('num_cbte:',num_cbte)
                    #16 campo: largo 16 importe otros conceptos
                    parte_decimal, parte_entera = math.modf(imp_otros)
                    parte_entera=str(parte_entera).split('.')[0]
                    parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                    monto=(parte_entera+','+parte_decimal).zfill(16)
                    string+=monto
                    print('imp_otros:',monto)
                    #17 campo: largo 16 importe iva (completar si letra comp =A,M)
                    parte_decimal, parte_entera = math.modf(imp_iva)
                    parte_entera=str(parte_entera).split('.')[0]
                    parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                    monto=(parte_entera+','+parte_decimal).zfill(16)
                    string+=monto
                    print('imp_iva:',monto)
                    #18 campo: largo 16 Monto sujeto a retencion/ recepcion (Monto Sujeto a Retención/ Percepción=(Monto del comprobante - Importe Iva -Importe otros conceptos))
                    if tipo_operacion=='2':
                        parte_decimal, parte_entera = math.modf(apunte.invoice_id.amount_untaxed)
                        parte_entera=str(parte_entera).split('.')[0]
                        parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                        monto=(parte_entera+','+parte_decimal).zfill(16)
                    else:
                        monto="NNNNNNNNNNNNNNNN"
                    string+=monto
                    #19 campo: largo 05 Alícuota
                    #padron=self.env['nybble.padron'].search([('cuit','=',apunte.partner_id.main_id_number)])
                    padron=self.env['padron'].search([('cuit','=',apunte.partner_id.main_id_number),('fecha_vig_desde','>=',self.fecha_desde),('fecha_vig_hasta','<=',self.fecha_hasta)])
                    if padron:
                        if tipo_operacion=='2':
                            alicuota=padron.percepcion
                        else:
                            alicuota=0.0
                    else:
                        alicuota=round((imp_caba/apunte.invoice_id.amount_untaxed*100),2)
                    parte_decimal, parte_entera = math.modf(alicuota)
                    parte_entera=str(parte_entera).split('.')[0]
                    parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                    monto=(parte_entera+','+parte_decimal).zfill(5)
                    print('alicuota:',monto)
                    string+=monto
                    #20 campo: largo 16 Retención/Percepción Practicada
                    parte_decimal, parte_entera = math.modf(imp_caba)
                    parte_entera=str(parte_entera).split('.')[0]
                    parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                    monto=(parte_entera+','+parte_decimal).zfill(16)
                    string+=monto
                    #21 campo: largo 16 Monto Total Retenido/Percibido (igual a campo 20)
                    parte_decimal, parte_entera = math.modf(imp_caba)
                    parte_entera=str(parte_entera).split('.')[0]
                    parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                    monto=(parte_entera+','+parte_decimal).zfill(16)
                    string+=monto
                    print('imp_caba:',monto)
                #string+=' '
                string+=windows_line_ending
            string=string.encode('utf-8')
            print('codificado')
###################Percepciones CABA NOTA CREDITO
        elif self.tipo_txt=='piibbcabaanc':
            nombre = 'PIIBBCABAANCred'
            #CABAAA Operación 2 --> FActuras de clientes Percepcion supuestamente
            for apunte in apuntes.filtered(lambda r: r.invoice_id.journal_document_type_id.document_type_id.doc_code_prefix[0:2]=='NC' and r.invoice_id.refund_invoice_id.id!=False and r.invoice_id.journal_document_type_id.document_type_id.document_letter_id.name=='A'):
                tipo_operacion='2'
                imp_caba2=0.0
                if tipo_operacion=='2':
                    for impuesto2 in apunte.invoice_id.tax_line_ids:
                        if impuesto2.name.find('CABA') != -1:
                            imp_caba2+=impuesto2.amount_total
                parte_decimal2, parte_entera2 = math.modf(imp_caba2)
                parte_entera2=str(parte_entera2).split('.')[0]
                parte_decimal2=(str(round(parte_decimal2,2)).split('.')[1][:2]).ljust(2,'0')
                monto3=(parte_entera2+','+parte_decimal2).zfill(16)
                if monto3 != '0000000000000,00':
                    #1  campo: largo 01 tipo operación (1:retencion 2:percepcion)
                    string+=tipo_operacion
                    #2  campo: largo 12 nro nota de credito
                    if tipo_operacion=='2':
                        num_cbte=apunte.invoice_id.document_number.replace('-','').zfill(12)
                    else:
                        num_cbte="NNNNNNNNNNNNNNNN"
                    if len(num_cbte) == 13:
                        num_cbte = num_cbte[1:13]
                    string+=num_cbte
                    #3  campo: largo 10 fech a de nota de credito
                    #string+=apunte.date[-2:]+'/'+apunte.date[5:-3]+'/'+apunte.date[:4]
                    d=''
                    if len(str(apunte.date.day)) == 1:
                        d ='0'+ str(apunte.date.day)
                    else:
                        d =str(apunte.date.day)
                    m=''
                    if len(str(apunte.date.month)) == 1:
                        m ='0'+ str(apunte.date.month)
                    else:
                        m =str(apunte.date.month)
                    string+=str(d)+'/'+str(m)+'/'+str(apunte.date.year)
                    #4 campo: largo 16 Monto nota de credito
                    if tipo_operacion=='2':
                        parte_decimal, parte_entera = math.modf(apunte.invoice_id.amount_untaxed)
                        parte_entera=str(parte_entera).split('.')[0]
                        parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                        monto=(parte_entera+','+parte_decimal).zfill(16)
                    else:
                        monto="NNNNNNNNNNNNNNNN"
                    string+=monto
                    #5  campo: largo 16 nro de cert propio (blancos o nro cert)
                    string+=' '*16
                    #6  campo: largo 02 tipo cbte origen de la ret (si tipo op =1 :01 fac 02 ndeb 03 ordenpago 04 boleta de dep 05 liq de pago 06 cert de obra 07 recibo 08 con de loc de serv 09 otro comb si tipo op =2 01 factura 09 otro comp)
                    #7  campo: largo 01 letra del comprobante (A,M,B,C o espacio blanco)
                    if tipo_operacion=='2':
                        comprob="01"+apunte.invoice_id.journal_document_type_id.document_type_id.document_letter_id.name
                    else:
                        comprob="NNN"
                    string+=comprob
                    #8  campo: largo 16 nro de comprobante
                    if tipo_operacion=='2':
                        num_cbte=apunte.invoice_id.refund_invoice_id.document_number.replace('-','').zfill(16)
                    else:
                        num_cbte="NNNNNNNNNNNNNNNN"
                    string+=num_cbte
                    #9 campo: largo 11 nro de documento del retenido 
                    string+=apunte.partner_id.main_id_number.zfill(11)
                    #10 campo: largo 03 codigo de norma (segun tipo de operacion)
                    string+='029'
                    #11 campo: largo 10 fecha de retencion/percepcion
                    #string+=apunte.invoice_id.refund_invoice_id.date_invoice[-2:]+'/'+apunte.invoice_id.refund_invoice_id.date_invoice[5:-3]+'/'+apunte.invoice_id.refund_invoice_id.date_invoice[:4]
                    d=''
                    if len(str(apunte.invoice_id.refund_invoice_id.date_invoice.day)) == 1:
                        d ='0'+ str(apunte.invoice_id.refund_invoice_id.date_invoice.day)
                    else:
                        d =str(apunte.invoice_id.refund_invoice_id.date_invoice.day)
                    m=''
                    if len(str(apunte.invoice_id.refund_invoice_id.date_invoice.month)) == 1:
                        m ='0'+ str(apunte.invoice_id.refund_invoice_id.date_invoice.month)
                    else:
                        m =str(apunte.invoice_id.refund_invoice_id.date_invoice.month)
                    #string+=str(d)+'/'+str(m)+'/'+str(apunte.invoice_id.refund_invoice_id.date_invoice.year)
                    #12 campo: largo 16 REt/percep a deducir
                    imp_caba=0.0
                    if tipo_operacion=='2':
                        for impuesto in apunte.invoice_id.tax_line_ids:
                            if impuesto.name.find('CABA') != -1:
                                imp_caba+=impuesto.amount_total
                    parte_decimal, parte_entera = math.modf(imp_caba)
                    parte_entera=str(parte_entera).split('.')[0]
                    parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                    monto=(parte_entera+','+parte_decimal).zfill(16)
                    string+=monto
                    #13 campo: largo 05 Alícuota
                    #padron=self.env['nybble.padron'].search([('cuit','=',apunte.partner_id.main_id_number)])
                    padron=self.env['padron'].search([('cuit','=',apunte.partner_id.main_id_number),('fecha_vig_desde','>=',self.fecha_desde),('fecha_vig_hasta','<=',self.fecha_hasta)])
                    logging.info('padron: {} - padron.percepcion: {} - padron.retencion {}'.format(padron,padron.percepcion,padron.retencion))
                    alicuota=0.0
                    if padron:
                        if tipo_operacion=='2':
                            if len(str(padron.percepcion)) == 1:
                                alicuota=float(padron.percepcion)
                        else:
                            alicuota=0.0
                    else:
                        alicuota=0.0
                    alicuota = str(alicuota).replace(',','.')
                    parte_decimal, parte_entera = math.modf(float(alicuota))
                    parte_entera=str(parte_entera).split('.')[0]
                    parte_decimal=(str(round(parte_decimal,2)).split('.')[1][:2]).ljust(2,'0')
                    monto=(parte_entera+','+parte_decimal).zfill(5)
                    print('alicuota:',monto)
                    string+=monto
                    #string+=' '
                    string+=windows_line_ending
            string=string.encode('utf-8')
            print('codificado')
        elif self.tipo_txt=='sicore':
            nombre = 'SICORE'
            for payment in payments:
                if payment.tax_withholding_id.tax_group_id.type == 'withholding' or payment.tax_withholding_id.tax_group_id.type == 'perception':
                    print('################################################################')
                    print('name:',payment.journal_id.name)
                    print('payment.communication:',payment.communication)
                    print('payment.withholding_number:',payment.withholding_number)
                    print('payment.tax_withholding_id.tax_group_id.type:',payment.tax_withholding_id.tax_group_id.type)
                    #if payment.payment_date < str(self.date_from) or payment.payment_date > str(self.date_to):
                    #    print('NO ENTRA por fecha')
                    #    continue
                    #import pdb; pdb.set_trace()
                    if not payment.communication or not payment.withholding_number:
                        print('NO ENTRA por comu o numero ret')
                        continue
                    if 'Retenciones' not in payment.journal_id.name:
                        print('NO ENTRA porque no dice retenciones el journal')
                        continue
                    print('entra')
                    # 1er campo codigo de comprobante: pago 06
                    string = string + '06'
                    # 2do campo fecha de emision de comprobante
                    d=''
                    if len(str(payment.payment_date.day)) == 1:
                        d ='0'+ str(payment.payment_date.day)
                    else:
                        d =str(payment.payment_date.day)
                    m=''
                    if len(str(payment.payment_date.month)) == 1:
                        m ='0'+ str(payment.payment_date.month)
                    else:
                        m =str(payment.payment_date.month)
                    string = string + str(d) + '/' + str(m) + '/' + str(payment.payment_date.year)
                    # 3er campo nro de comprobante - imprimimos nro de retenciontring = string + payment_data['withholding_number'].zfill(16)
                    print('3er campo nro de comprobante:',payment.payment_group_id.name[10:].zfill(12))
                    payment_n = payment.payment_group_id.document_number.split('-')
                    payment_pto = payment_n[0]
                    #payment_pto = payment_p[1]
                    #payment_pto = payment_p   + str(payment_n[0:1]) + '---' +str(payment_n[1:5]) + '---'
                    payment_name = str(payment_pto)+str(payment_n[1])
                    string = string + '0000' + payment_name.zfill(12)
                    # 4to campo amoun   
                    print('4to campo amoun:',payment.payment_group_id.payments_amount)
                    if payment.payment_group_id.payments_amount > 0:
                        cadena = "%.2f"%payment.payment_group_id.payments_amount
                        cadena = cadena.replace('.',',')
                    else:
                        cadena = '0,00'
                    #string = string + cadena.rjust(16)
                    string = string + cadena.zfill(16)
                    #string = string + str(payment_data['withholding_base_amount']).zfill(16)
                    # 5to Campo - Codigo de Impuesto - 217 tomado de tabla de codigos de sicore
                    print('5to Campo - Codigo de Impuesto:',str(payment.tax_withholding_id.tax_group_id.afip_code).zfill(3)[:3])
                    string = string + '0217'#str(payment.tax_withholding_id.tax_group_id.afip_code).zfill(3)[:3]
                    # 6to campo - Codigo de regimen 078 tomado de tabla de codigos de sicore - Enajenacion de bienes de cambio
                    #string = string + '078'
                    #string = string + partner_data[0]['default_regimen_ganancias_id'][1].zfill(3)[:3]
                    print('6to campo - Codigo de regimen:',payment.communication[:3])
                    #if payment.communication[:3].isnumeric(): partner_id.default_
                    if payment.payment_group_id.regimen_ganancias_id.codigo_de_regimen:
                        concepto = int(str(payment.payment_group_id.regimen_ganancias_id.codigo_de_regimen.zfill(3)))
                    else:
                        concepto = int('000')
                    string = string + str(concepto).zfill(3)
                    # 7mo campo - codigo de operacion 1 tomado de ejemplo XLS
                    string = string + '1'
                    # 8vo campo - base de calculo (52 a 65)
                    print('8vo campo - base de calculo (52 a 65):',payment.withholding_base_amount)
                    cadena = "%.2f"%payment.withholdable_base_amount
                    cadena = cadena.replace('.',',')
                    string = string + cadena.zfill(14)
                    # 9vo campo - fecha de emision de la retencion (66 a 75)
                    #print('9vo campo - fecha de emision de la retencion (66 a 75):',payment.payment_date[8:10] + '/' + payment.payment_date[5:7] + '/' + payment.payment_date[:4])
                    #string = string + payment.payment_date[8:10] + '/' + payment.payment_date[5:7] + '/' + payment.payment_date[:4]
                    d=''
                    if len(str(payment.payment_date.day)) == 1:
                        d ='0'+ str(payment.payment_date.day)
                    else:
                        d =str(payment.payment_date.day)
                    m=''
                    if len(str(payment.payment_date.month)) == 1:
                        m ='0'+ str(payment.payment_date.month)
                    else:
                        m =str(payment.payment_date.month)
                    string = string + str(d) + '/' + str(m) + '/' + str(payment.payment_date.year)
                    # 10 (76 a 77) codigo de condicioon
                    print('codigo de condicioon:',payment.tax_withholding_id.tax_group_id.type)
                    if payment.tax_withholding_id.tax_group_id.type == 'withholding':
                        string = string + '01'
                    elif payment.tax_withholding_id.tax_group_id.type == 'perception':
                        string = string + '02'
                    else:
                        string = '99'
                    #(78 a 78) 11- retencion a sujetos suspendidos REVISAR
                    string = string + '0'
                    # 12 mo campo - importe retencion - 79 a 92
                    #    cadena = str(round(payment_data['amount'],2))
                    cadena = "%.2f"%payment.amount
                    cadena = cadena.replace('.',',')
                    #string = string + str(payment_data['amount']).zfill(14)
                    string = string + cadena.zfill(14)
                    # 13vo campo - porcentaje de la exclusion
                    cadena = '000,00'
                    string = string + cadena
                    # 14vo campo - fecha de emision del boletin REVISAR
                    #string = string + payment_data['payment_date'][8:10] + '/' + payment_data['payment_date'][5:7] + '/' + payment_data['payment_date'][:4]
                    d=''
                    if len(str(payment.payment_date.day)) == 1:
                        d ='0'+ str(payment.payment_date.day)
                    else:
                        d =str(payment.payment_date.day)
                    m=''
                    if len(str(payment.payment_date.month)) == 1:
                        m ='0'+ str(payment.payment_date.month)
                    else:
                        m =str(payment.payment_date.month)
                    string = string + str(d) + '/' + str(m) + '/' + str(payment.payment_date.year)
                    #string = string + ' '.rjust(10)
                    # 15 tipo de documento del retenido
                    string = string + '80'
                    # 16vo campo - ro de CUIT revisar
                    print('15vo campo - ro de CUIT:',payment.partner_id.main_id_number)
                    string = string + '000000000' + payment.partner_id.main_id_number
                    # 17vo campo nro certificado original
                    #string = string + payment_data['withholding_number'].zfill(14)
                    string = string + payment.withholding_number.zfill(14)
                    # Denominacion del ordenante
                    #string = string + partner_data[0]['name'][:30].ljust(30)
                    #string = string + ' '.ljust(30)
                    # Acrecentamiento
                    #string = string + '0'
                    # cuit pais retenido
                    #string = string + '00000000000'
                    # cuit del ordenante
                    #string = string + '00000000000'
                    # CRLF
                    string = string + windows_line_ending
                    print('################################################################')
        else:
            raise UserError('El formato de generación TXT seleccionado no está definido')

        self.export_data = string
        if self.tipo_txt in ['piibbcabaa', 'piibbcabaanc', 'riibbcabaa']:
            self.export_file = base64.encodestring(self.export_data.encode('UTF-8'))
        else:
            self.export_file = base64.encodestring(self.export_data.encode('ISO-8859-1'))

