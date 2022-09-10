# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from translate import Translator


class BaseLanguageInstall(models.TransientModel):
    _inherit = "base.language.install"

    def lang_install(self):
        res = super(BaseLanguageInstall, self).lang_install()
        if self._context.get('active_model') == 'res.lang':
            lang_id = self.env['res.lang'].browse(self._context.get('active_id'))
            if lang_id:
                iso_code = lang_id.iso_code
                iso_code = iso_code.split("_")
                type_ids = self.env['stock.picking.type'].sudo().search([('is_return_type', '=', True)])
                for type_id in type_ids:
                    translator = Translator(from_lang='en',to_lang=iso_code[0])
                    translation = translator.translate(type_id.name)
                    data = {
                        'type': 'model',
                        'name': 'stock.picking.type,name',
                        'lang': lang_id.code,
                        'res_id': type_id.id,
                        'src': type_id.name,
                        'value': translation,
                        'state': 'translated',
                    }
                    existing_trans = self.env['ir.translation'].sudo().search([('name', '=', 'stock.picking.type,name'),
                                                                        ('res_id', '=', type_id.id),
                                                                        ('lang', '=', lang_id.code)])
                    if not existing_trans:
                        self.env['ir.translation'].sudo().create(data)
                    else:
                        existing_trans.write(data)
        return res
