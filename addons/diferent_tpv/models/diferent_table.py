from odoo import models, fields, api
from odoo.exceptions import UserError

class DiferentTable(models.Model):
    _name = 'diferent.table'
    _description = 'Restaurant Table'
    _order = 'room_id, number'

    name = fields.Char('Table Name', compute='_compute_name', store=True)
    number = fields.Char('Table Number', required=True)
    room_id = fields.Many2one('diferent.room', 'Room', required=True, ondelete='cascade')
    capacity = fields.Integer('Capacity', default=4)
    
    # Table state
    state = fields.Selection([
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('cleaning', 'Cleaning')
    ], string='State', default='available')
    
    # Position for floor plan (for future graphic view)
    position_x = fields.Float('Position X', default=0)
    position_y = fields.Float('Position Y', default=0)
    
    # Active order
    active_order_id = fields.Many2one('diferent.order', 'Active Order')
    order_total = fields.Float('Order Total', related='active_order_id.amount_total')
    
    # Additional info
    notes = fields.Text('Notes')
    last_cleaned = fields.Datetime('Last Cleaned')
    
    @api.depends('number', 'room_id.name')
    def _compute_name(self):
        for table in self:
            if table.room_id and table.number:
                table.name = f"Table {table.number} - {table.room_id.name}"
            else:
                table.name = f"Table {table.number or 'New'}"
    
    def action_open_table(self):
        """Action to open table and manage orders"""
        self.ensure_one()
        
        if not self.active_order_id:
            # Create new order
            order = self.env['diferent.order'].create({
                'table_id': self.id,
                'state': 'draft',
                'waiter_id': self.env.user.id,
            })
            self.active_order_id = order.id
            self.state = 'occupied'
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Order - {self.name}',
            'res_model': 'diferent.order',
            'res_id': self.active_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_close_table(self):
        """Close table and finish order"""
        self.ensure_one()
        if self.active_order_id:
            self.active_order_id.action_close()
        self.state = 'cleaning'
        self.active_order_id = False
    
    def action_clean_table(self):
        """Mark table as cleaned and available"""
        self.ensure_one()
        self.state = 'available'
        self.last_cleaned = fields.Datetime.now()