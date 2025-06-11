from odoo import models, fields, api
from odoo.exceptions import UserError

class DiferentOrder(models.Model):
    _name = 'diferent.order'
    _description = 'Restaurant Table Order'
    _order = 'create_date desc'

    name = fields.Char('Order Number', default='New', readonly=True)
    table_id = fields.Many2one('diferent.table', 'Table', required=True)
    room_id = fields.Many2one('diferent.room', related='table_id.room_id', store=True)
    
    # Order state
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('kitchen', 'In Kitchen'),
        ('ready', 'Ready to Serve'),
        ('served', 'Served'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='State', default='draft')
    
    # Order lines
    line_ids = fields.One2many('diferent.order.line', 'order_id', 'Order Lines')
    
    # Amounts
    amount_total = fields.Float('Total Amount', compute='_compute_amount_total', store=True)
    amount_tax = fields.Float('Tax Amount', compute='_compute_amount_total', store=True)
    amount_untaxed = fields.Float('Untaxed Amount', compute='_compute_amount_total', store=True)
    
    # People and timing
    waiter_id = fields.Many2one('res.users', 'Waiter', default=lambda self: self.env.user)
    customer_count = fields.Integer('Number of Customers', default=1)
    order_date = fields.Datetime('Order Date', default=fields.Datetime.now)
    kitchen_date = fields.Datetime('Sent to Kitchen')
    ready_date = fields.Datetime('Ready Date')
    served_date = fields.Datetime('Served Date')
    
    # Notes
    notes = fields.Text('Special Notes')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('diferent.order') or 'New'
        return super().create(vals)
    
    @api.depends('line_ids.subtotal', 'line_ids.tax_amount')
    def _compute_amount_total(self):
        for order in self:
            amount_untaxed = sum(line.subtotal for line in order.line_ids)
            amount_tax = sum(line.tax_amount for line in order.line_ids)
            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = amount_untaxed + amount_tax
    
    def action_confirm(self):
        """Confirm order and send to kitchen"""
        self.state = 'confirmed'
        self.kitchen_date = fields.Datetime.now()
        # Here you can add logic to notify kitchen
    
    def action_to_kitchen(self):
        """Send order to kitchen"""
        if not self.line_ids:
            raise UserError("Cannot send empty order to kitchen")
        self.state = 'kitchen'
        self.kitchen_date = fields.Datetime.now()
    
    def action_ready(self):
        """Mark order as ready to serve"""
        self.state = 'ready'
        self.ready_date = fields.Datetime.now()
    
    def action_served(self):
        """Mark order as served"""
        self.state = 'served'
        self.served_date = fields.Datetime.now()
    
    def action_close(self):
        """Close order and generate sale"""
        self.state = 'paid'
        # Here you can create sale.order for invoicing
    
    def action_cancel(self):
        """Cancel order"""
        self.state = 'cancelled'
        if self.table_id.active_order_id == self:
            self.table_id.active_order_id = False
            self.table_id.state = 'available'

class DiferentOrderLine(models.Model):
    _name = 'diferent.order.line'
    _description = 'Restaurant Order Line'

    order_id = fields.Many2one('diferent.order', 'Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    quantity = fields.Float('Quantity', default=1.0)
    unit_price = fields.Float('Unit Price', related='product_id.list_price')
    subtotal = fields.Float('Subtotal', compute='_compute_subtotal', store=True)
    tax_amount = fields.Float('Tax Amount', compute='_compute_subtotal', store=True)
    
    # Special instructions
    notes = fields.Text('Special Instructions')
    
    # Stock control
    available_stock = fields.Float('Available Stock', related='product_id.qty_available')
    
    # Kitchen status for this line
    kitchen_state = fields.Selection([
        ('waiting', 'Waiting'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready')
    ], string='Kitchen State', default='waiting')
    
    @api.depends('quantity', 'unit_price', 'product_id.taxes_id')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
            # Basic tax calculation (you might want to improve this)
            if line.product_id.taxes_id:
                tax_rate = sum(line.product_id.taxes_id.mapped('amount')) / 100
                line.tax_amount = line.subtotal * tax_rate
            else:
                line.tax_amount = 0.0
    
    @api.constrains('quantity', 'product_id')
    def _check_stock(self):
        for line in self:
            if line.product_id.type == 'product':  # Only storable products
                if line.quantity > line.available_stock:
                    raise UserError(
                        f'Not enough stock for {line.product_id.name}. '
                        f'Available: {line.available_stock}'
                    )
    
    def action_start_preparing(self):
        """Mark this line as being prepared in kitchen"""
        self.kitchen_state = 'preparing'
    
    def action_ready(self):
        """Mark this line as ready"""
        self.kitchen_state = 'ready'