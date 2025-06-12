from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    def action_add_to_tpv_order(self):
        """Añadir producto al pedido activo del TPV"""
        self.ensure_one()
        
        # Obtener datos del contexto
        table_id = self.env.context.get('active_table_id')
        order_id = self.env.context.get('active_order_id')
        
        if not table_id or not order_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'No se encontró una mesa u orden activa',
                    'type': 'warning'
                }
            }
        
        # Buscar la orden
        order = self.env['diferent.order'].browse(order_id)
        if not order.exists():
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'Orden no encontrada',
                    'type': 'warning'
                }
            }
        
        # Buscar si ya existe una línea con este producto
        existing_line = order.line_ids.filtered(lambda l: l.product_id.id == self.id)
        
        if existing_line:
            # Incrementar cantidad
            existing_line[0].quantity += 1
            message = f'Cantidad aumentada: {self.name}'
        else:
            # Crear nueva línea
            self.env['diferent.order.line'].create({
                'order_id': order_id,
                'product_id': self.id,
                'quantity': 1,
                'unit_price': self.list_price,
            })
            message = f'Producto añadido: {self.name}'
        
        # Mostrar notificación de éxito
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Éxito',
                'message': message,
                'type': 'success'
            }
        }