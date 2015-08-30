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
from openerp.exceptions import Warning, except_orm
from dateutil.relativedelta import relativedelta

class contract_loan(models.Model):


    @api.one    
    def _compute_invoice(self):
        self.invoiced = True #if self.env['account.invoice'].search([('contract_id', '=', self.id)]) else False        

    """Contrcts & Loans"""
    _name = 'contract.loan'
    _description = 'Contract or Loan'
    _inherit = ['mail.thread', 'ir.needaction_mixin']    
    state                = fields.Selection([('draft','Draft'),('running','Running'),('cancel','Cancel'),('done','Done')],default='draft',string='State')
    name                 = fields.Char(string='Contract Name',  required=True)
    plan_id              = fields.Many2one('contract.plan', string='Plan ')
    partner_id           = fields.Many2one('res.partner',string="Customer")
    company_name         = fields.Many2one('res.partner')
    address              = fields.Char(string= 'Address')
    address1             = fields.Char(string= 'Address') 
    city                 = fields.Char(string= 'City') 
    gender               = fields.Selection([('male','Male'),('female','Female')],string='Gender')  
    dob                  = fields.Date(string='DOB')
    country_id           = fields.Many2one('res.country',string="Nationality")
    state_id             = fields.Many2one('res.country.state',string="State")   
    mobile               = fields.Char(string='Mobile')
    email                = fields.Char(string='Email') 
    occupation           = fields.Char(string='Job Position') 
    description          = fields.Text(string='Description') 
    passport_no          = fields.Char(string='Passport Number')
    passport_issue_date  = fields.Date(string='Passport Issue Date ')
    country_issue        = fields.Many2one('res.country',string='Passport Country')
    expiry_date          = fields.Date(string='Passport Expairy Date ')
    type                 = fields.Selection([('loan','Loan'),('contract','Contract')],string='Type')  
    uae_reference1       = fields.Char(string='Reference')
    ph_no_uae1           = fields.Char(string='Phone Number')
    uae_reference2       = fields.Char(string='Reference') 
    ph_no_uae2           = fields.Char(string='Phone Number')
    int_reference1       = fields.Char(string='Reference')
    ph_no_int1           = fields.Char(string='Phone Number')
    int_reference2       = fields.Char(string='Reference') 
    ph_no_int2           = fields.Char(string='Phone Number')
    free_product_ids     = fields.Many2many('plan.package','free_contract_plan_package','contract_id','plan_line_id')
    paid_product_ids     = fields.Many2many('plan.package','paid_contract_plan_package','contract_id','plan_line_id')
    next_invoice_date = fields.Date('Next Invoice Date', readonly=1)
    invoice_rule = fields.Selection([
            ('1', 'Month(s)'),
            ('12', 'Year(s)'),
            ], 'Recurrency', help="Invoice automatically repeat at specified interval")    
    manager_id = fields.Many2one('res.users', 'Maneger')
    invoiced = fields.Boolean('Invoiced', _compute='_compute_invoice')
    @api.one
    def _prepare_invoice(self):                
        journal_obj = self.env['account.journal']
        fpos_obj = self.env['account.fiscal.position']
        partner = self.partner_id

        if not partner:
            raise except_orm(_('No Customer Defined!'),_("You must first select a Customer for Contract %s!") % self.name )

        fpos_id = fpos_obj.get_fiscal_position(partner.company_id.id, partner.id)
        journal_ids = journal_obj.search([('type', '=','sale'),('company_id', '=', self.company_id.id or False)], limit=1)
        if not journal_ids:
            raise except_orm(_('Error!'),
            _('Please define a sale journal for the company "%s".') % (self.company_id.name or '', ))

        partner_payment_term = partner.property_payment_term and partner.property_payment_term.id or False

        currency_id = False
        if partner.property_product_pricelist:
            currency_id = partner.property_product_pricelist.currency_id.id
        elif self.company_id:
            currency_id = self.company_id.currency_id.id
        invoice_lines = []
        for line in self.paid_items:        
            res = line.product_id
            account_id = res.property_account_income.id
            if not account_id:
                account_id = res.categ_id.property_account_income_categ.id
            account_id = fpos_obj.map_account(fiscal_position, account_id)        
            invoice_lines.append((0, 0, {
                'name': line.name,
                'account_id': account_id,            
                'price_unit': line.price_unit or 0.0,
                'quantity': line.quantity,            
                'product_id': line.product_id.id or False,                
            })) 


        invoice = {
           'account_id': partner.property_account_receivable.id,
           'type': 'out_invoice',
           'partner_id': partner.id,
           'currency_id': currency_id,
           'journal_id': journal_ids and journal_ids.id or False,
           'date_invoice': fields.Date.context_today(self),
           'origin': self.name,
           'self_id':self.id,
           'fiscal_position': fpos_id,
           'payment_term': partner_payment_term,
           'company_id': self.company_id.id or False,
           'user_id': self.manager_id.id or uid,
           'invoice_lines':invoice_lines
        }
        return self.env['account.invoice'].create(invoice)


    @api.model
    def create_invoice(self):

        for row in self.search([('state', '=', 'running'), ('next_invoice_date', '<=', fields.Date.context_today(self))]):
            try:
                row._prepare_invoice()
                duration = int(row.invoice_rule)
                next_date = fields.Date.context_today(self) +  relativedelta(months=+duration)
                row.next_invoice_date= next_date
            except:
                pass        
    @api.multi
    def view_invoice(self):
        ids = [row.id for row in self]    
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contract Invocie',
            'view_type': 'form',
            'view_mode': 'tree,form',        
            'domain' : [('contract_id','in',ids)],
            'res_model': 'account.invoice',
            'nodestroy': True,
        }        

contract_loan()

class contract_plan(models.Model):
    """Event"""
    _name = 'contract.plan'
    _description = 'Contract plan'       

    name = fields.Char(string='Plan Name',  required=True)
    amount = fields.Char(string='Monthly Bill',  required=True)
    service_charge = fields.Char(string='Service Charge',  required=True)
    duration = fields.Selection([('6', '6 Months'),('12', '12 Months'), ('24', '24 Months')], string='Period',  required=True)
    free_items = fields.One2many('plan.package', 'plan_id', 'Free Items', help='Package includes free items')
    paid_items = fields.One2many('plan.package', 'plan_id', 'Free Items', help='Package includes free items')
    type = fields.Selection([('loan', 'Loan'), ('contract', 'Contract')], 'Type')
contract_plan()

class plan_package(models.Model):
    """Event"""
    _name = 'plan.package'
    _description = 'Plan Packages'       

    name = fields.Char(string='Description',  required=True)
    plan_id = fields.Many2one('contract.plan', string='Plan', ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], required=True, change_default=True, ondelete='restrict')
    quantity = fields.Float('Quantity')
    type = fields.Selection([('paid', 'Paid'), ('free', 'Free')], 'Type')
plan_package()
    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
