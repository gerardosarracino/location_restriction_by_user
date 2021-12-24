from odoo import models, fields, api
from lxml import etree
from odoo.exceptions import UserError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'
    user_ids = fields.Many2many('res.users', string='Asignado a ')


class StockLocation(models.Model):
    _inherit = 'stock.location'

    user_ids_01 = fields.Many2many('res.users', string='Asignado a ')
    user_ids_02 = fields.Many2many('res.users', relation='responsable_', string='Responsable')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res_view = super(StockPicking, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            user = self.env.user
            doc = etree.XML(res_view['arch'])
            value = "//field[@name='picking_type_id']"
            for node in doc.xpath(value):
                domain = "[ '|', ('warehouse_id.user_ids', 'in', {}), ('warehouse_id.user_ids', '=', False)]".format(user.id)
                domain = node.set("domain", domain)
            value = "//field[@name='location_id']"
            for node in doc.xpath(value):
                domain = "[ '|', ('user_ids_01', 'in', {}), ('user_ids_01', '=', False)]".format(user.id)
                domain = node.set("domain", domain)
            res_view['arch'] = etree.tostring(doc, encoding='unicode')
        return res_view

    def button_validate(self):
        message = "No puedes validar esta transacción, porque no eres el usuario responsable de " \
                  "la ubicación a la que estás enviando la Mercadería. Comunícate con el usuario responsable de " \
                  "la ubicación de Destino para que valide esta transacción."
        user = self.env.user

        if len(self.location_dest_id.user_ids_02) == 0:
            return super(StockPicking, self).button_validate()
        else:
            for i in range(len(self.location_dest_id.user_ids_02)):
                if self.location_dest_id.user_ids_02[i].id == user.id:
                    return super(StockPicking, self).button_validate()
        raise UserError(message)
