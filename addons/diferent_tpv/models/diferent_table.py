from odoo import models, fields, api
from odoo.exceptions import UserError

class DiferentTable(models.Model):
    _name = 'diferent.table'
    _description = 'Restaurant Table'
    _order = 'room_id, number'

    name = fields.Char('Table Name', compute='_compute_name', store=True)
    number = fields.Char('Table Number', required=True)
    room_id = fields.Many2one('diferent.room', string='Room', required=True)
    capacity = fields.Integer('Capacity', required=True, default=2)
    state = fields.Selection([
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('cleaning', 'Cleaning')
    ], default='available', required=True)
    shape = fields.Selection([
        ('round', 'Round'),
        ('square', 'Square'),
        ('rectangle', 'Rectangle')
    ], default='round', required=True)
    position_x = fields.Float('Position X', default=100)
    position_y = fields.Float('Position Y', default=100)
    width = fields.Float('Width', default=80)
    height = fields.Float('Height', default=80)
    
    # CAMPOS AÑADIDOS
    notes = fields.Text('Notes')
    last_cleaned = fields.Datetime('Last Cleaned')
    
    # Relations
    order_ids = fields.One2many('diferent.order', 'table_id', string='Orders')
    active_order_id = fields.Many2one('diferent.order', string='Active Order', compute='_compute_active_order')
    
    # CAMPOS COMPUTADOS AÑADIDOS
    order_total = fields.Float('Order Total', compute='_compute_order_total')
    
    @api.depends('number', 'room_id.name')
    def _compute_name(self):
        for table in self:
            table.name = f"Table {table.number} - {table.room_id.name if table.room_id else ''}"
    
    @api.depends('order_ids.state')
    def _compute_active_order(self):
        for table in self:
            active_order = table.order_ids.filtered(lambda o: o.state == 'draft')
            table.active_order_id = active_order[0] if active_order else False
    
    @api.depends('active_order_id.amount_total')
    def _compute_order_total(self):
        for table in self:
            table.order_total = table.active_order_id.amount_total if table.active_order_id else 0.0

    def action_open_table(self):
        """Acción para abrir el TPV de la mesa"""
        self.ensure_one()
        
        # Crear orden si no existe
        active_order = self.order_ids.filtered(lambda o: o.state == 'draft')
        if not active_order:
            active_order = self.env['diferent.order'].create({
                'table_id': self.id,
                'state': 'draft'
            })
        else:
            active_order = active_order[0]
        
        # Actualizar estado de mesa
        if self.state == 'available':
            self.state = 'occupied'
            
        # ABRIR VISTA TPV COMPLETA
        return {
            'type': 'ir.actions.act_window',
            'name': f'🍽️ TPV - Mesa {self.number} ({self.room_id.name})',
            'res_model': 'diferent.order',
            'res_id': active_order.id,
            'view_mode': 'form',
            'view_id': self.env.ref('diferent_tpv.view_tpv_complete_form').id,
            'context': {
                'active_table_id': self.id,
                'active_order_id': active_order.id,
                'form_view_ref': 'diferent_tpv.view_tpv_complete_form',
            },
            'target': 'current',
            'flags': {
                'mode': 'edit',
            }
        }
    def action_close_table(self):
        """Cerrar mesa y finalizar orden"""
        if self.active_order_id:
            self.active_order_id.action_close()
        self.state = 'cleaning'
        self.last_cleaned = fields.Datetime.now()
    
    def action_clean_table(self):
        """Marcar mesa como limpia"""
        self.state = 'available'
        self.last_cleaned = fields.Datetime.now()