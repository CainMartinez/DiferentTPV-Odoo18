from odoo import models, fields, api
from odoo.exceptions import UserError

class DiferentOrder(models.Model):
    _name = 'diferent.order'
    _description = 'Restaurant Order'
    _order = 'date_created desc'

    name = fields.Char('Order Number', default='New', readonly=True)
    table_id = fields.Many2one('diferent.table', string='Table', required=True)
    room_id = fields.Many2one('diferent.room', string='Room', related='table_id.room_id', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('kitchen', 'In Kitchen'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled')
    ], default='draft', required=True, tracking=True)
    
    # Dates
    date_created = fields.Datetime('Created', default=fields.Datetime.now, readonly=True)
    date_confirmed = fields.Datetime('Confirmed', readonly=True)
    date_closed = fields.Datetime('Closed', readonly=True)
    
    # Relations
    line_ids = fields.One2many('diferent.order.line', 'order_id', string='Order Lines')
    waiter_id = fields.Many2one('res.users', string='Waiter', default=lambda self: self.env.user)
    
    # Computed fields
    total_items = fields.Integer('Total Items', compute='_compute_totals', store=True)
    amount_untaxed = fields.Float('Untaxed Amount', compute='_compute_totals', store=True)
    amount_tax = fields.Float('Tax Amount', compute='_compute_totals', store=True)
    amount_total = fields.Float('Total Amount', compute='_compute_totals', store=True)
    
    # Other fields
    notes = fields.Text('Notes')
    
    @api.depends('line_ids.quantity', 'line_ids.unit_price', 'line_ids.total_price')
    def _compute_totals(self):
        for order in self:
            order.total_items = sum(order.line_ids.mapped('quantity'))
            order.amount_untaxed = sum(order.line_ids.mapped('total_price'))
            order.amount_tax = order.amount_untaxed * 0.21  # 21% IVA by default
            order.amount_total = order.amount_untaxed + order.amount_tax
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('diferent.order') or 'New'
        return super(DiferentOrder, self).create(vals)
    
    def action_confirm(self):
        """Confirmar el pedido"""
        self.ensure_one()
        if not self.line_ids:
            raise UserError('Cannot confirm an order without products.')
        self.state = 'confirmed'
        self.date_confirmed = fields.Datetime.now()
        return True
    
    def action_to_kitchen(self):
        """Enviar a cocina"""
        self.ensure_one()
        self.state = 'kitchen'
        return True
    
    def action_ready(self):
        """Marcar como listo"""
        self.ensure_one()
        self.state = 'ready'
        return True
    
    def action_served(self):
        """Marcar como servido"""
        self.ensure_one()
        self.state = 'served'
        return True
    
    def action_close(self):
        """Cerrar pedido"""
        self.ensure_one()
        self.state = 'closed'
        self.date_closed = fields.Datetime.now()
        # Liberar mesa
        if self.table_id:
            self.table_id.state = 'cleaning'
        return True
    
    def action_cancel(self):
        """Cancelar pedido"""
        self.ensure_one()
        self.state = 'cancelled'
        return True


class DiferentOrderLine(models.Model):
    _name = 'diferent.order.line'
    _description = 'Order Line'

    order_id = fields.Many2one('diferent.order', string='Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float('Quantity', default=1.0, required=True)
    unit_price = fields.Float('Unit Price', required=True)
    total_price = fields.Float('Total', compute='_compute_total', store=True)
    notes = fields.Text('Notes')
    
    @api.depends('quantity', 'unit_price')
    def _compute_total(self):
        for line in self:
            line.total_price = line.quantity * line.unit_price
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.list_price
    
    def action_remove_line(self):
        """Eliminar línea del pedido"""
        self.ensure_one()
        self.unlink()
        return {'type': 'ir.actions.client', 'tag': 'reload'}