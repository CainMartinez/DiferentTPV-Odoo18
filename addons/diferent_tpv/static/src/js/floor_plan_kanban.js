odoo.define('diferent_tpv.FloorPlanKanban', function (require) {
    'use strict';

    var KanbanView = require('web.KanbanView');
    var KanbanController = require('web.KanbanController');
    var KanbanRenderer = require('web.KanbanRenderer');
    var view_registry = require('web.view_registry');

    var FloorPlanKanbanRenderer = KanbanRenderer.extend({
        className: KanbanRenderer.prototype.className + ' o_floor_plan_view',

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self._setupDragDrop();
                self._addToolbar();
            });
        },

        _addToolbar: function () {
            var $toolbar = $(`
                <div class="o_floor_plan_toolbar">
                    <div class="o_floor_plan_info">
                        <h4>Floor Plan - ${this.state.context.room_name || 'All Rooms'}</h4>
                    </div>
                    <div class="o_floor_plan_tools">
                        <button class="btn btn-primary btn-sm o_add_table">
                            <i class="fa fa-plus"/> Add Table
                        </button>
                        <button class="btn btn-secondary btn-sm o_save_layout">
                            <i class="fa fa-save"/> Save Layout
                        </button>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-secondary o_zoom_in">
                                <i class="fa fa-search-plus"/>
                            </button>
                            <button class="btn btn-outline-secondary o_zoom_out">
                                <i class="fa fa-search-minus"/>
                            </button>
                        </div>
                    </div>
                </div>
            `);
            this.$el.prepend($toolbar);
            this._bindToolbarEvents($toolbar);
        },

        _bindToolbarEvents: function ($toolbar) {
            var self = this;
            
            $toolbar.find('.o_add_table').on('click', function () {
                self.trigger_up('add_table');
            });
            
            $toolbar.find('.o_save_layout').on('click', function () {
                self.trigger_up('save_layout');
            });
            
            $toolbar.find('.o_zoom_in').on('click', function () {
                self._zoom(1.2);
            });
            
            $toolbar.find('.o_zoom_out').on('click', function () {
                self._zoom(0.8);
            });
        },

        _setupDragDrop: function () {
            var self = this;
            
            // Hacer las mesas arrastrables
            this.$('.o_table_kanban_card').draggable({
                containment: '.o_floor_plan_kanban',
                snap: '.o_floor_plan_kanban',
                snapMode: 'inner',
                grid: [10, 10], // Snap to grid
                stop: function (event, ui) {
                    var $table = $(this);
                    var tableId = parseInt($table.data('table-id'));
                    var position = ui.position;
                    
                    // Actualizar posición en el backend
                    self._rpc({
                        model: 'diferent.table',
                        method: 'write',
                        args: [tableId, {
                            position_x: position.left,
                            position_y: position.top
                        }]
                    }).then(function () {
                        self.trigger_up('reload');
                    });
                }
            });

            // Click para abrir mesa
            this.$('.o_table_kanban_card').on('click', function (e) {
                if (!$(e.target).closest('.o_table_actions').length) {
                    var tableId = $(this).data('table-id');
                    self.trigger_up('open_table', {tableId: tableId});
                }
            });
        },

        _zoom: function (factor) {
            var $canvas = this.$('.o_floor_plan_kanban');
            var currentZoom = parseFloat($canvas.css('transform').replace(/[^0-9.-]/g, '') || 1);
            var newZoom = currentZoom * factor;
            
            newZoom = Math.max(0.5, Math.min(2, newZoom)); // Límites de zoom
            $canvas.css('transform', `scale(${newZoom})`);
        }
    });

    var FloorPlanKanbanController = KanbanController.extend({
        custom_events: _.extend({}, KanbanController.prototype.custom_events, {
            'add_table': '_onAddTable',
            'save_layout': '_onSaveLayout',
            'open_table': '_onOpenTable',
        }),

        _onAddTable: function () {
            this.do_action({
                type: 'ir.actions.act_window',
                name: 'Add Table',
                res_model: 'diferent.table',
                view_mode: 'form',
                target: 'new',
                context: this.initialState.context
            });
        },

        _onSaveLayout: function () {
            this.displayNotification({
                message: 'Layout saved successfully!',
                type: 'success'
            });
        },

        _onOpenTable: function (ev) {
            var self = this;
            this._rpc({
                model: 'diferent.table',
                method: 'action_open_table',
                args: [ev.data.tableId]
            }).then(function (action) {
                self.do_action(action);
            });
        }
    });

    var FloorPlanKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: FloorPlanKanbanController,
            Renderer: FloorPlanKanbanRenderer,
        })
    });

    view_registry.add('floor_plan_kanban', FloorPlanKanbanView);

    return {
        FloorPlanKanbanView: FloorPlanKanbanView,
        FloorPlanKanbanController: FloorPlanKanbanController,
        FloorPlanKanbanRenderer: FloorPlanKanbanRenderer,
    };
});