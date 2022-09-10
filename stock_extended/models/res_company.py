# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from translate import Translator


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    @api.model
    def create(self, vals):
        res = super(ResCompany, self).create(vals)
        if res:
            warehouse_id = self.env['stock.warehouse'].sudo().search([('name', '=', res.name)], limit=1)
            type_id = self.env['stock.picking.type'].sudo().create({
                'name': 'Return',
                'is_return_type':True,
                'company_id': res.id,
                'warehouse_id': warehouse_id.id if warehouse_id else False ,
                'sequence_id': self.env['ir.sequence'].sudo().create({
                        'code': 'stock.return',
                        'name': 'stock_return_sequence',
                        'active':True,
                        'company_id': res.id,
                    }).id,
                'code': 'incoming',
                'default_location_src_id': self.env.ref('stock.stock_location_suppliers').id,
                'default_location_dest_id': self.env.ref('stock.stock_location_customers').id,
                'sequence_code': 'RTN',
                'active':True,
            })
            for lang_code  in  self.env['res.lang'].sudo().get_installed():
                try:
                    iso_code = self.env['res.lang'].sudo().search([('code', '=', lang_code[0])]).iso_code
                    iso_code = iso_code.split("_")
                    translator = Translator(from_lang='en', to_lang=iso_code[0])
                    translation = translator.translate(type_id.name)
                    data = {
                        'type': 'model',
                        'name': 'stock.picking.type,name',
                        'lang': lang_code[0],
                        'res_id': type_id.id,
                        'src': type_id.name,
                        'value': translation,
                        'state': 'translated',
                    }
                    existing_trans = self.env['ir.translation'].sudo().search([('name', '=', 'stock.picking.type,name'),
                                                                        ('res_id', '=', type_id.id),
                                                                        ('lang', '=', lang_code)])
                    if not existing_trans:
                        self.env['ir.translation'].sudo().create(data)
                    else:
                        existing_trans.write(data)
                except:
                     continue
        return res
