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

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class contract_loan(models.Model):
    """Event"""
    _name = 'contract.loan'
    _description = 'Contract or Loan'
    _inherit = ['mail.thread', 'ir.needaction_mixin']    

    name = fields.Char(string='Contract Name',  required=True)
    plan_id = fields.Many2one('contract.plan', string='Plan')
contract_loan()

class contract_plan(models.Model):
    """Event"""
    _name = 'contract.plan'
    _description = 'Contract plan'       

    name = fields.Char(string='Plan Name',  required=True)
    amount = fields.Char(string='Monthly Bill',  required=True)
    service_charge = fields.Char(string='Service Charge',  required=True)
    duration = fields.Selection([('6', '6 Months'),('12', '12 Months'), ('24', '24 Months')], string='Period',  required=True)
    free_items = fields.One2many('plan.package', 'paln_id', 'Free Items', help='Package includes free items')
    paid_items = fields.One2many('plan.package', 'paln_id', 'Free Items', help='Package includes free items')
contract_plan()

class plan_package(models.Model):
    """Event"""
    _name = 'plan.package'
    _description = 'Plan Packages'       

    name = fields.Char(string='Description',  required=True)
    plan_id = fields.Many2one('contract.plan', string='Plan', ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], required=True, change_default=True, ondelete='restrict')
    quantity = fields.Float('Quantity')
    
plan_package()
    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
