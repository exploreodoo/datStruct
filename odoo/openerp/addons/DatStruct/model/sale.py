# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import timedelta

import pytz
from datetime import date
from openerp import models, fields, api, _
from openerp.exceptions import Warning



class sale_order(models.Model):
    _inherit = 'sale.order'
    purchase_id = fields.Many2one('purchase.order','Purchase')
    
    
    
sale_order()



class sale_order_line(models.Model):
    _inherit='sale.order.line'

    landed_cost = fields.Float('Landed Costs',  compute ='_get_landed_cost')
    
    
    
    
    @api.depends('product_id')
    def _get_landed_cost(self):
        landed_cost=0.0
        if self.order_id and self.order_id.purchase_id :
            if self.product_id :
                purchaseline = self.env['purchase.order.line'].search([('product_id', '=', self.product_id.id),('order_id', '=', self.order_id.purchase_id.id)])
                landed_cost = purchaseline and purchaseline[0].price_unit 
         
        self.landed_cost = landed_cost  
        
    
