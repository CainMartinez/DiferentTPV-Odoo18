from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    def action_add_to_tpv_order(self):
        """Añadir producto al pedido activo del TPV"""
        self.ensure_one()
        
        # Verificar si es desde TPV
        from_tpv = self.env.context.get('from_tpv', False)
        
        # Verificar stock
        if self.type == 'product' and self.qty_available <= 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '❌ Sin Stock',
                    'message': f'No hay stock disponible de {self.name}',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Obtener datos del contexto o del active_id
        table_id = self.env.context.get('active_table_id')
        order_id = self.env.context.get('active_order_id')
        
        # Si no tenemos los IDs del contexto, intentar obtenerlos del active_id
        if not order_id and self.env.context.get('active_model') == 'diferent.order':
            order_id = self.env.context.get('active_id')
            order = self.env['diferent.order'].browse(order_id)
            table_id = order.table_id.id if order.exists() else None
        
        if not table_id or not order_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '⚠️ Error',
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
                    'title': '⚠️ Error',
                    'message': 'Orden no encontrada',
                    'type': 'warning'
                }
            }
        
        # Buscar si ya existe una línea con este producto
        existing_line = order.line_ids.filtered(lambda l: l.product_id.id == self.id)
        
        if existing_line:
            # Incrementar cantidad
            existing_line[0].quantity += 1
            message = f'🔄 {self.name} - Cantidad: {existing_line[0].quantity}'
            title = 'Cantidad Actualizada'
        else:
            # Crear nueva línea
            self.env['diferent.order.line'].create({
                'order_id': order_id,
                'product_id': self.id,
                'quantity': 1,
                'unit_price': self.list_price,
            })
            message = f'✅ {self.name} añadido al pedido'
            title = 'Producto Añadido'
        
        # Actualizar estado de la mesa
        table = self.env['diferent.table'].browse(table_id)
        if table.state != 'occupied':
            table.state = 'occupied'
        
        # Si es desde TPV, recargar la vista
        if from_tpv:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            # Mostrar notificación normal
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': title,
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }
            
    def action_view_order_details(self):
        """Ver detalles del pedido actual"""
        table_id = self.env.context.get('active_table_id')
        order_id = self.env.context.get('active_order_id')
        
        if not order_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'No hay pedido activo',
                    'type': 'warning'
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pedido Actual',
            'res_model': 'diferent.order',
            'res_id': order_id,
            'view_mode': 'form',
            'target': 'new',
        }