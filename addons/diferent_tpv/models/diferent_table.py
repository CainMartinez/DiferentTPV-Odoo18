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

    width = fields.Float('Table Width', default=80)  # píxeles
    height = fields.Float('Table Height', default=80)
    rotation = fields.Float('Rotation Angle', default=0)  # grados
    shape = fields.Selection([
        ('square', 'Square'),
        ('round', 'Round'),
        ('rectangle', 'Rectangle')
    ], default='square', string='Table Shape')
    
    def update_position(self, x, y):
        """Update table position from frontend"""
        self.ensure_one()
        self.write({
            'position_x': x,
            'position_y': y
        })
        return True
        
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
        """Action to open table and show product selection"""
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
        
        # Abrir vista de productos para selección directa
        return {
            'type': 'ir.actions.act_window',
            'name': f'Mesa {self.name} - Seleccionar Productos',
            'res_model': 'product.product',
            'view_mode': 'kanban,list',
            'domain': [('sale_ok', '=', True), ('available_in_pos', '=', True)],
            'context': {
                'active_table_id': self.id,
                'active_order_id': self.active_order_id.id,
                'search_default_consumable': 1,
            },
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