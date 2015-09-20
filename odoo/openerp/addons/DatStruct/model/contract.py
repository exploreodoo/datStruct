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
from dateutil import relativedelta, parser
import datetime

class contract_loan(models.Model):

      


    @api.one    
    def _compute_invoice(self):    
        self.invoiced = True if self.env['account.invoice'].search([('contract_id', '=', self.id)]) else False        

    """Contrcts & Loans"""
    _name = 'contract.loan'
    _description = 'Contract or Loan'
    _inherit = ['mail.thread', 'ir.needaction_mixin']    
    state                = fields.Selection([('draft','Draft'),('running','Running'),('cancel','Cancel'),('done','Done')],default='draft',string='State')
    name                 = fields.Char(string='Contract Name',  required=True)
    plan_id              = fields.Many2one('contract.plan', string='Plan ')
    partner_id           = fields.Many2one('res.partner',string="Customer", domain=[('customer', '=', True)])
    company_name         = fields.Many2one('res.partner')
    address              = fields.Char(string= 'Address')
    address1             = fields.Char(string= 'Address') 
    city                 = fields.Char(string= 'City') 
    gender               = fields.Selection([('male','Male'),('female','Female')],string='Gender')  
    dob                  = fields.Date(string='DOB')
    country_id           = fields.Many2one('res.country', string="Nationality")
    state_id             = fields.Many2one('res.country.state', string="State")   
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
    free_items = fields.Many2many('plan.package','free_contract_plan_package','contract_id','plan_line_id', 
        domain=[('type', '=', 'free')])
    paid_items = fields.Many2many('plan.package','paid_contract_plan_package','contract_id','plan_line_id', 
        domain=[('type', '=', 'paid')])
    next_invoice_date = fields.Date('Next Invoice Date', readonly=1)
    invoice_rule = fields.Selection([
            ('1', 'Month(s)'),
            ('12', 'Year(s)'),
            ], 'Recurrency', default='1', required=True, help="Invoice automatically repeat at specified interval")    
    manager_id = fields.Many2one('res.users', 'Manager', 
        default=lambda self: self.env.user, track_visibility='onchange')
    invoiced = fields.Boolean('Invoiced', compute='_compute_invoice')
    company_id = fields.Many2one('res.company', 'Company', 
        default=lambda self: self.env['res.company']._company_default_get('contract.loan'))
        
    contact_address1      = fields.Text('Contact Address') 
    contact_address2      = fields.Text('Contact Address') 
    contact_address_international1      = fields.Text('Contact Address') 
    contact_address_international2      = fields.Text('Contact Address') 
    date                  = fields.Date(string='Start Date')
    invoice_ids           = fields.One2many('account.invoice','contract_id','Invoices') 
    emirates_id           = fields.Char('Emerites_id')
    date_end              = fields.Date(string='End Date', compute='_end_date')
    
    
    @api.depends('plan_id','date')
    def _end_date(self):
        if self.plan_id and self.date :
            length = 0
            if self.plan_id.duration == '6' :
                length = 6
            elif self.plan_id.duration == '12' :
                length = 12
            elif self.plan_id.duration == '24':
                length = 24  
            startdate =datetime.datetime.strptime(self.date, '%Y-%m-%d').date()    
            end = startdate  +  relativedelta.relativedelta(months=length)
            self.date_end = end
    
    
    
    @api.onchange('plan_id')
    def on_change_plan_id(self): 
        self.free_items= None 
        self.paid_items= None   
        if self.plan_id :            
            self.free_items=[free_items.id for free_items in self.plan_id.free_items]
            self.paid_items=[paid_item.id for paid_item in self.plan_id.paid_items]

    
    @api.multi
    def action_print(self):
        for contract in self:
            return self.pool['report'].get_action(self._cr, self._uid, [self.id], 'DatStruct.report_loan_contract1', context=self._context)
    
    
    
    
    
    
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):        
        if self.type:
            self.company_name        = self.partner_id and self.partner_id.parent_id and self.partner_id.parent_id.id or False 
            self.address             = self.partner_id and self.partner_id.street or ""
            self.address1            = self.partner_id and self.partner_id.street2 or ""
            self.city                = self.partner_id and self.partner_id.city or "" 
            self.state_id            = self.partner_id and self.partner_id.state_id and self.partner_id.state_id.id or None 
            self.country_id          = self.partner_id and self.partner_id.country_id and self.partner_id.country_id.id or False
            self.mobile              = self.partner_id and self.partner_id.mobile or False
            self.email               = self.partner_id and self.partner_id.email or ''
            self.occupation          = self.partner_id and self.partner_id.function  or ''
            self.passport_no         = self.partner_id and self.partner_id.passport_no or False
            self.passport_issue_date = self.partner_id and self.partner_id.passport_issue_date or False
            self.country_issue       = self.partner_id and self.partner_id.country_issue and self.partner_id.country_issue.id or False
            self.expiry_date         = self.partner_id and self.partner_id.expiry_date or False
    @api.multi
    def view_delivery(self):
        ids = [row.id for row in self]    
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contract Invocie',
            'view_type': 'form',
            'view_mode': 'tree,form',        
            'domain' : [('contract_id','in',ids)],
            'res_model': 'stock.picking',
            'nodestroy': True,
        }        


    @api.one
    def _prepare_invoice(self):                
        journal_obj = self.env['account.journal']
        fpos_obj = self.env['account.fiscal.position']
        partner = self.partner_id

        if not partner:
            raise except_orm(_('No Customer Defined!'),_("You must first select a Customer for Contract %s!") % self.name )

        #fpos_id = fpos_obj.get_fiscal_position(partner.company_id.id, partner.id)
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
            account_id = fpos_obj.map_account(account_id)
            invoice_lines.append((0, 0, {
                'name': line.name,
                'account_id': account_id,            
                'price_unit': line.product_id and line.product_id.list_price or 0.0,
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
           'contract_id':self.id,
          # 'fiscal_position': fpos_id,
           'payment_term': partner_payment_term,
           'company_id': self.company_id.id or False,
           'user_id': self.manager_id.id or self.env.uid,
           'invoice_line':invoice_lines
        }        
        return self.env['account.invoice'].create(invoice)


    @api.model
    def create_invoice(self):        
        for row in self.search([('state', '=', 'running'), ('next_invoice_date', '<=', fields.Date.context_today(self))]):   
            row.create_delivery_order()                               
            row._prepare_invoice()
            duration = int(row.invoice_rule)
            next_date = parser.parse(fields.Date.context_today(self)) +  relativedelta.relativedelta(months=+duration)            
            row.next_invoice_date= next_date.strftime('%Y-%m-%d')            
    

    @api.multi
    def action_done(self):        
        return self.write({'state':'done'})

    @api.multi
    def action_run(self):
        for row in self:
            #TODO check all validations here
            row.next_invoice_date = fields.Date.context_today(self)
            row.state='running'
            # row.create_invoice()
            row.create_delivery_order()  
            row._prepare_invoice()
            duration = int(row.invoice_rule)
            next_date = parser.parse(fields.Date.context_today(self)) +  relativedelta.relativedelta(months=+duration)            
            row.next_invoice_date= next_date.strftime('%Y-%m-%d')

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

    def _get_number_word(self, number):
        if number == 1:
            return "1st"
        if number == 2:
            return "2nd"
        if number == 3:
            return "3rd"        
        return "%sth" % number

    @api.multi
    def get_delivery_details(self):        
        res = []        
        date = self.date        
        if self.plan_id:
            amount = 0.0
            for paid in self.paid_items:
                amount += paid.quantity * paid.product_id.list_price

            for row in range(int(self.plan_id.duration)):
                next_date = parser.parse(date) +  relativedelta.relativedelta(months=+row)
                res.append({'name':'%s Delivery' % (self._get_number_word(row+1)),
                    'date':next_date.strftime('%d-%m-%Y'),
                    'amount':amount})    
        return res
        self.env['ir.model.data'].xmlid_to_res_id('stock.picking_type_out')

    @api.multi 
    def create_delivery_order(self):
        for contract in self :
            try :
                type = self.env['ir.model.data'].xmlid_to_res_id('stock.picking_type_out')
            except:
                type=False
                pass      
            picking_id = self.env['stock.picking'].create({
                    'origin': contract.name,
                    'company_id': self.company_id and self.company_id.id or False,
                    'move_type': 'one',
                    'partner_id': contract.partner_id and contract.partner_id.id or False,
                    'picking_type_id':type,
                    'contract_id': self.id 
                    })
            for item in self.paid_items :
                
                self.env['stock.move'].create({
                'product_uos_qty': item.quantity ,
                'date_expected': fields.Date.context_today(self), 
                'date': fields.Date.context_today(self), 
                'product_id': item.product_id and item.product_id.id ,
                'product_uom':  item.product_uom and item.product_uom.id, 
                'picking_type_id': picking_id and picking_id.picking_type_id.id , 
                'product_uom_qty': item.quantity , 
                'invoice_state': '2binvoiced',
                'product_tmpl_id': False, 
                'product_uos': False, 
                'reserved_quant_ids': [],
                'location_dest_id': picking_id.picking_type_id and picking_id.picking_type_id.default_location_dest_id.id , 
                'procure_method': 'make_to_stock',
                'product_packaging': False, 
                'location_id': picking_id.picking_type_id and picking_id.picking_type_id.default_location_src_id.id ,
                'picking_id': picking_id and picking_id.id  ,
                'name': item.product_id and item.product_id.name 
                })
#                   









contract_loan()

class contract_plan(models.Model):
    """Event"""
    _name = 'contract.plan'
    _description = 'Contract plan'       

    name = fields.Char(string='Plan Name',  required=True)
    amount = fields.Char(string='Monthly Bill')
    service_charge = fields.Char(string='Service Charge')
    duration = fields.Selection([('6', '6 Months'),('12', '12 Months'), ('24', '24 Months')], string='Period',  required=True)
    free_items = fields.One2many('plan.package', 'plan_id', 'Free Items', help='Package includes free items', domain=[('type', '=', 'free')])
    paid_items = fields.One2many('plan.package', 'plan_id', 'Free Items', help='Package includes free items', domain=[('type', '=', 'paid')])
    type = fields.Selection([('loan', 'Loan'), ('contract', 'Contract')], 'Type', default='contract', required=True)

contract_plan()

class plan_package(models.Model):
    """Event"""
    _name = 'plan.package'
    _description = 'Plan Packages'       

    name = fields.Char(string='Description',  required=True)
    plan_id = fields.Many2one('contract.plan', string='Plan', ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], required=True, change_default=True, ondelete='restrict')
    product_uom = fields.Many2one('product.uom', 'Product UoM',required='1')
    quantity = fields.Float('Quantity')
    type = fields.Selection([('paid', 'Paid'), ('free', 'Free')], 'Type')
plan_package()
    


