from odoo import models, fields, api

class DiferentRoom(models.Model):
    _name = 'diferent.room'
    _description = 'Restaurant Room'
    _order = 'sequence, name'

    name = fields.Char('Room Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)
    color = fields.Char('Color', default='#3498db')
    description = fields.Text('Description')
    
    # Relations
    table_ids = fields.One2many('diferent.table', 'room_id', string='Tables')
    
    # Computed fields
    table_count = fields.Integer('Number of Tables', compute='_compute_table_count')
    occupied_tables = fields.Integer('Occupied Tables', compute='_compute_occupied_tables')
    
    @api.depends('table_ids')
    def _compute_table_count(self):
        for room in self:
            room.table_count = len(room.table_ids)
    
    @api.depends('table_ids.state')
    def _compute_occupied_tables(self):
        for room in self:
            room.occupied_tables = len(room.table_ids.filtered(lambda t: t.state == 'occupied'))
    
    def action_view_tables(self):
        """Action to view tables in this room"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Tables - {self.name}',
            'res_model': 'diferent.table',
            'view_mode': 'kanban,tree,form',
            'domain': [('room_id', '=', self.id)],
            'context': {'default_room_id': self.id},
        }

    def action_floor_plan(self):
        """Open floor plan view for this room"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Floor Plan - {self.name}',
            'res_model': 'diferent.table',
            'view_mode': 'kanban',
            'view_id': self.env.ref('diferent_tpv.view_diferent_table_floor_plan_kanban').id,
            'domain': [('room_id', '=', self.id)],
            'context': {
                'default_room_id': self.id,
                'room_name': self.name,
                'floor_plan_mode': True
            },
        }