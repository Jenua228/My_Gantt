<template>
  <Transition name="fade">
    <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h2>{{ editingTask ? $t('taskModal.editTask') : $t('taskModal.newTask') }}</h2>
          <button class="btn btn-icon" @click="$emit('close')">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>{{ $t('taskModal.title') }}</label>
            <input v-model="form.title" type="text" :placeholder="$t('taskModal.titlePlaceholder')" />
          </div>
          
          <div class="form-group">
            <label>{{ $t('taskModal.description') }}</label>
            <textarea v-model="form.description" rows="2" :placeholder="$t('taskModal.descriptionPlaceholder')"></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>{{ $t('taskModal.startDate') }}</label>
              <input v-model="form.start_date" type="datetime-local" />
            </div>
            <div class="form-group">
              <label>{{ $t('taskModal.endDate') }}</label>
              <input v-model="form.end_date" type="datetime-local" />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>{{ $t('taskModal.progress') }} ({{ form.progress }}%)</label>
              <input v-model.number="form.progress" type="range" min="0" max="100" />
            </div>
            <div class="form-group">
              <label>{{ $t('taskModal.color') }}</label>
              <div class="color-picker-wrapper">
                <div class="color-preview" :style="{ backgroundColor: form.color }"></div>
                <input v-model="form.color" type="color" />
                <input v-model="form.color" type="text" style="flex: 1" />
              </div>
            </div>
          </div>
          
          <!-- Parent Task (Hierarchy) Section -->
          <div class="form-group">
            <label>{{ $t('taskModal.parentTask') }}</label>
            <select v-model="form.parent_id">
              <option :value="null">{{ $t('taskModal.noParent') }}</option>
              <option 
                v-for="task in availableHierarchyParents" 
                :key="task.id" 
                :value="task.id"
              >
                {{ task.title }}
              </option>
            </select>
            <span class="form-hint">{{ $t('taskModal.parentHint') }}</span>
          </div>
          
          <!-- Connection Section (Arrows) -->
          <div class="form-section">
            <div class="section-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <polyline points="15 3 21 3 21 9" />
                <line x1="10" y1="14" x2="21" y2="3" />
              </svg>
              {{ $t('taskModal.connections') }}
            </div>
            
            <!-- Parent Connections (Arrows FROM other tasks TO this task) -->
            <div class="connection-box">
              <div 
                class="connection-header" 
                @click="parentConnectionsExpanded = !parentConnectionsExpanded"
              >
                <div class="connection-label">
                  <span class="arrow-icon">→</span>
                  <span>{{ $t('taskModal.predecessorsSection') }}</span>
                  <span class="connection-count" v-if="existingParentConnections.length">
                    {{ existingParentConnections.length }}
                  </span>
                </div>
                <svg 
                  class="expand-icon" 
                  :class="{ expanded: parentConnectionsExpanded }"
                  width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </div>
              
              <div v-show="parentConnectionsExpanded" class="connection-content">
                <!-- Existing parent connections list -->
                <div v-if="existingParentConnections.length" class="connections-list">
                  <div 
                    v-for="conn in existingParentConnections" 
                    :key="conn.id" 
                    class="connection-item"
                  >
                    <div class="connection-item-info">
                      <span 
                        class="connection-task-name" 
                        :style="{ borderLeftColor: getTaskById(conn.from_task_id)?.color }"
                      >
                        {{ getTaskById(conn.from_task_id)?.title || 'Unknown' }}
                      </span>
                      <span class="connection-type-badge">{{ formatConnectionType(conn.arrow_type) }}</span>
                    </div>
                    <button 
                      class="btn-remove" 
                      @click="$emit('remove-connection', conn.id)"
                      :title="$t('taskModal.removeConnection')"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                      </svg>
                    </button>
                  </div>
                </div>
                <div v-else class="no-connections">{{ $t('taskModal.noPredecessors') }}</div>
                
                <!-- Add new parent connection -->
                <div class="add-connection">
                  <div class="add-connection-title">{{ $t('taskModal.addPredecessor') }}</div>
                  <div class="form-row">
                    <div class="form-group">
                      <select v-model="form.conn_parent_task_id">
                        <option :value="null">{{ $t('taskModal.selectTask') }}</option>
                        <option 
                          v-for="task in availableParentTasks" 
                          :key="task.id" 
                          :value="task.id"
                        >
                          {{ task.title }}
                        </option>
                      </select>
                    </div>
                    <div class="form-group">
                      <select v-model="form.conn_parent_connection_type" :disabled="!form.conn_parent_task_id">
                        <option value="finish-to-start">{{ $t('connectionTypes.finishToStart') }}</option>
                        <option value="finish-to-finish">{{ $t('connectionTypes.finishToFinish') }}</option>
                        <option value="start-to-start">{{ $t('connectionTypes.startToStart') }}</option>
                        <option value="start-to-finish">{{ $t('connectionTypes.startToFinish') }}</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Child Connections (Arrows FROM this task TO other tasks) -->
            <div class="connection-box">
              <div 
                class="connection-header" 
                @click="childConnectionsExpanded = !childConnectionsExpanded"
              >
                <div class="connection-label">
                  <span class="arrow-icon">←</span>
                  <span>{{ $t('taskModal.successorsSection') }}</span>
                  <span class="connection-count" v-if="existingChildConnections.length">
                    {{ existingChildConnections.length }}
                  </span>
                </div>
                <svg 
                  class="expand-icon" 
                  :class="{ expanded: childConnectionsExpanded }"
                  width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </div>
              
              <div v-show="childConnectionsExpanded" class="connection-content">
                <!-- Existing child connections list -->
                <div v-if="existingChildConnections.length" class="connections-list">
                  <div 
                    v-for="conn in existingChildConnections" 
                    :key="conn.id" 
                    class="connection-item"
                  >
                    <div class="connection-item-info">
                      <span 
                        class="connection-task-name" 
                        :style="{ borderLeftColor: getTaskById(conn.to_task_id)?.color }"
                      >
                        {{ getTaskById(conn.to_task_id)?.title || 'Unknown' }}
                      </span>
                      <span class="connection-type-badge">{{ formatConnectionType(conn.arrow_type) }}</span>
                    </div>
                    <button 
                      class="btn-remove" 
                      @click="$emit('remove-connection', conn.id)"
                      :title="$t('taskModal.removeConnection')"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                      </svg>
                    </button>
                  </div>
                </div>
                <div v-else class="no-connections">{{ $t('taskModal.noSuccessors') }}</div>
                
                <!-- Add new child connection -->
                <div class="add-connection">
                  <div class="add-connection-title">{{ $t('taskModal.addSuccessor') }}</div>
                  <div class="form-row">
                    <div class="form-group">
                      <select v-model="form.conn_child_task_id">
                        <option :value="null">{{ $t('taskModal.selectTask') }}</option>
                        <option 
                          v-for="task in availableChildTasks" 
                          :key="task.id" 
                          :value="task.id"
                        >
                          {{ task.title }}
                        </option>
                      </select>
                    </div>
                    <div class="form-group">
                      <select v-model="form.conn_child_connection_type" :disabled="!form.conn_child_task_id">
                        <option value="finish-to-start">{{ $t('connectionTypes.finishToStart') }}</option>
                        <option value="finish-to-finish">{{ $t('connectionTypes.finishToFinish') }}</option>
                        <option value="start-to-start">{{ $t('connectionTypes.startToStart') }}</option>
                        <option value="start-to-finish">{{ $t('connectionTypes.startToFinish') }}</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="$emit('close')">{{ $t('taskModal.cancel') }}</button>
          <button class="btn btn-primary" @click="$emit('save', form)">
            {{ editingTask ? $t('taskModal.save') : $t('taskModal.create') }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  show: Boolean,
  editingTask: Object,
  tasks: Array,
  connections: Array
})

const emit = defineEmits(['close', 'save', 'remove-connection'])

const parentConnectionsExpanded = ref(true)
const childConnectionsExpanded = ref(true)

const form = ref({
  title: '',
  description: '',
  start_date: '',
  end_date: '',
  progress: 0,
  color: '#4A90D9',
  row_index: 0,
  parent_id: null,
  conn_parent_task_id: null,
  conn_parent_connection_type: 'finish-to-start',
  conn_child_task_id: null,
  conn_child_connection_type: 'finish-to-start'
})

// Map for O(1) task lookup
const tasksMap = computed(() => {
  const map = new Map()
  props.tasks.forEach(t => map.set(t.id, t))
  return map
})

const getTaskById = (id) => {
  return tasksMap.value.get(id)
}

const formatConnectionType = (type) => {
  const types = {
    'finish-to-start': 'Finish → Start',
    'start-to-start': 'Start → Start',
    'finish-to-finish': 'Finish → Finish',
    'start-to-finish': 'Start → Finish'
  }
  return types[type] || type
}

// Available tasks for hierarchy parent selection
const availableHierarchyParents = computed(() => {
  if (!props.editingTask) {
    return props.tasks.filter(t => !t.parent_id)
  }
  const childIds = new Set(props.tasks.filter(t => t.parent_id === props.editingTask.id).map(t => t.id))
  return props.tasks.filter(t => 
    t.id !== props.editingTask.id && !childIds.has(t.id)
  )
})

// Existing connections for the editing task
const existingParentConnections = computed(() => {
  if (!props.editingTask) return []
  return props.connections.filter(c => c.to_task_id === props.editingTask.id)
})

const existingChildConnections = computed(() => {
  if (!props.editingTask) return []
  return props.connections.filter(c => c.from_task_id === props.editingTask.id)
})

// Available tasks for connection selection
const availableParentTasks = computed(() => {
  if (!props.editingTask) {
    return props.tasks
  }
  const existingParentIds = existingParentConnections.value.map(c => c.from_task_id)
  return props.tasks.filter(t => 
    t.id !== props.editingTask.id && !existingParentIds.includes(t.id)
  )
})

const availableChildTasks = computed(() => {
  if (!props.editingTask) {
    return props.tasks
  }
  const existingChildIds = existingChildConnections.value.map(c => c.to_task_id)
  return props.tasks.filter(t => 
    t.id !== props.editingTask.id && !existingChildIds.includes(t.id)
  )
})

// Reset form when modal opens/closes or editingTask changes
watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.editingTask) {
      form.value = {
        title: props.editingTask.title,
        description: props.editingTask.description || '',
        start_date: new Date(props.editingTask.start_date).toISOString().slice(0, 16),
        end_date: new Date(props.editingTask.end_date).toISOString().slice(0, 16),
        progress: props.editingTask.progress,
        color: props.editingTask.color,
        row_index: props.editingTask.row_index,
        parent_id: props.editingTask.parent_id || null,
        conn_parent_task_id: null,
        conn_parent_connection_type: 'finish-to-start',
        conn_child_task_id: null,
        conn_child_connection_type: 'finish-to-start'
      }
    } else {
      const now = new Date()
      const nextWeek = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
      form.value = {
        title: '',
        description: '',
        start_date: now.toISOString().slice(0, 16),
        end_date: nextWeek.toISOString().slice(0, 16),
        progress: 0,
        color: '#4A90D9',
        row_index: props.tasks.length,
        parent_id: null,
        conn_parent_task_id: null,
        conn_parent_connection_type: 'finish-to-start',
        conn_child_task_id: null,
        conn_child_connection_type: 'finish-to-start'
      }
    }
    parentConnectionsExpanded.value = true
    childConnectionsExpanded.value = true
  }
}, { immediate: true })
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow: auto;
  box-shadow: var(--shadow-lg);
}

.modal-lg {
  max-width: 600px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
}

.form-group {
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
}

.form-group input[type="range"] {
  accent-color: var(--accent-primary);
}

.form-hint {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 6px;
  font-style: italic;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* Connection section styles */
.form-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-subtle);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-title svg {
  color: var(--accent-primary);
}

.connection-box {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 16px;
  margin-bottom: 12px;
}

.connection-box:last-child {
  margin-bottom: 0;
}

.connection-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  padding: 4px 0;
  margin: -4px 0;
}

.connection-header:hover {
  opacity: 0.8;
}

.connection-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.arrow-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--accent-primary);
  color: var(--bg-primary);
  border-radius: 50%;
  font-size: 14px;
  font-weight: bold;
}

.connection-count {
  background: var(--accent-primary);
  color: var(--bg-primary);
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
}

.expand-icon {
  transition: transform 0.2s ease;
  color: var(--text-secondary);
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.connection-content {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-subtle);
}

.connections-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.connection-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
}

.connection-item-info {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.connection-task-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  padding-left: 10px;
  border-left: 3px solid var(--accent-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.connection-type-badge {
  font-size: 10px;
  color: var(--text-muted);
  background: var(--bg-tertiary);
  padding: 3px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.btn-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.btn-remove:hover {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}

.no-connections {
  font-size: 12px;
  color: var(--text-muted);
  text-align: center;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  margin-bottom: 12px;
}

.add-connection {
  padding-top: 8px;
}

.add-connection-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.add-connection .form-row {
  gap: 8px;
}

.add-connection .form-group {
  margin-bottom: 0;
}

.connection-box select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

