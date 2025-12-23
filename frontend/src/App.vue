<template>
  <div class="app">
    <header class="app-header">
      <div class="logo">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="4" width="18" height="4" rx="1" />
          <rect x="3" y="10" width="14" height="4" rx="1" />
          <rect x="3" y="16" width="10" height="4" rx="1" />
        </svg>
        <span>{{ $t('app.title') }}</span>
      </div>
      
      <div class="header-controls">
        <!-- Language Selector -->
        <div class="language-selector">
          <button 
            v-for="lang in languages" 
            :key="lang.code"
            :class="['lang-btn', { active: currentLanguage === lang.code }]"
            @click="changeLanguage(lang.code)"
            :title="lang.name"
          >
            {{ lang.flag }}
          </button>
        </div>
        
        <div class="time-scale-selector">
          <button 
            v-for="scale in timeScales" 
            :key="scale.value"
            :class="['scale-btn', { active: currentScale === scale.value }]"
            @click="currentScale = scale.value"
          >
            {{ $t(`scales.${scale.value}`) }}
          </button>
        </div>
        
        <button class="btn btn-secondary" @click="loadDemoData">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <path d="M3 3v5h5" />
          </svg>
          {{ $t('app.loadDemo') }}
        </button>
        
        <button class="btn btn-primary" @click="openCreateTaskModal">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          {{ $t('app.addTask') }}
        </button>
      </div>
    </header>
    
    <main class="app-main">
      <GanttChart 
        :tasks="tasks" 
        :connections="connections"
        :scale="currentScale"
        @update-task="updateTask"
        @update-task-live="updateTaskLive"
        @delete-task="deleteTask"
        @create-connection="createConnection"
        @delete-connection="deleteConnection"
        @edit-task="editTask"
        @edit-connection="editConnection"
        @change-scale="changeScale"
      />
    </main>
    
    <!-- Task Modal -->
    <Transition name="fade">
      <div v-if="showTaskModal" class="modal-overlay" @click.self="closeTaskModal">
        <div class="modal modal-lg">
          <div class="modal-header">
            <h2>{{ editingTask ? $t('taskModal.editTask') : $t('taskModal.newTask') }}</h2>
            <button class="btn btn-icon" @click="closeTaskModal">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          
          <div class="modal-body">
            <div class="form-group">
              <label>{{ $t('taskModal.title') }}</label>
              <input v-model="taskForm.title" type="text" :placeholder="$t('taskModal.titlePlaceholder')" />
            </div>
            
            <div class="form-group">
              <label>{{ $t('taskModal.description') }}</label>
              <textarea v-model="taskForm.description" rows="2" :placeholder="$t('taskModal.descriptionPlaceholder')"></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>{{ $t('taskModal.startDate') }}</label>
                <input v-model="taskForm.start_date" type="datetime-local" />
              </div>
              <div class="form-group">
                <label>{{ $t('taskModal.endDate') }}</label>
                <input v-model="taskForm.end_date" type="datetime-local" />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>{{ $t('taskModal.progress') }} ({{ taskForm.progress }}%)</label>
                <input v-model.number="taskForm.progress" type="range" min="0" max="100" />
              </div>
              <div class="form-group">
                <label>{{ $t('taskModal.color') }}</label>
                <div class="color-picker-wrapper">
                  <div class="color-preview" :style="{ backgroundColor: taskForm.color }"></div>
                  <input v-model="taskForm.color" type="color" />
                  <input v-model="taskForm.color" type="text" style="flex: 1" />
                </div>
              </div>
            </div>
            
            <!-- Parent Task (Hierarchy) Section -->
            <div class="form-group">
              <label>{{ $t('taskModal.parentTask') }}</label>
              <select v-model="taskForm.parent_id">
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
                        @click="removeParentConnection(conn.id)"
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
                        <select v-model="taskForm.conn_parent_task_id">
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
                        <select v-model="taskForm.conn_parent_connection_type" :disabled="!taskForm.conn_parent_task_id">
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
                        @click="removeChildConnection(conn.id)"
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
                        <select v-model="taskForm.conn_child_task_id">
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
                        <select v-model="taskForm.conn_child_connection_type" :disabled="!taskForm.conn_child_task_id">
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
            <button class="btn btn-secondary" @click="closeTaskModal">{{ $t('taskModal.cancel') }}</button>
            <button class="btn btn-primary" @click="saveTask">
              {{ editingTask ? $t('taskModal.save') : $t('taskModal.create') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
    
    <!-- Connection Modal -->
    <Transition name="fade">
      <div v-if="showConnectionModal" class="modal-overlay" @click.self="closeConnectionModal">
        <div class="modal modal-sm">
          <div class="modal-header">
            <h2>{{ $t('connectionModal.title') }}</h2>
            <button class="btn btn-icon" @click="closeConnectionModal">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          
          <div class="modal-body">
            <div class="form-group">
              <label>{{ $t('connectionModal.arrowColor') }}</label>
              <div class="color-picker-wrapper">
                <div class="color-preview" :style="{ backgroundColor: connectionForm.arrow_color }"></div>
                <input v-model="connectionForm.arrow_color" type="color" />
                <input v-model="connectionForm.arrow_color" type="text" style="flex: 1" />
              </div>
            </div>
            
            <div class="form-group">
              <label>{{ $t('connectionModal.lineStyle') }}</label>
              <select v-model="connectionForm.arrow_style">
                <option value="solid">{{ $t('connectionModal.solid') }}</option>
                <option value="dashed">{{ $t('connectionModal.dashed') }}</option>
                <option value="dotted">{{ $t('connectionModal.dotted') }}</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>{{ $t('connectionModal.connectionType') }}</label>
              <select v-model="connectionForm.arrow_type">
                <option value="finish-to-start">{{ $t('connectionTypes.finishToStart') }}</option>
                <option value="start-to-start">{{ $t('connectionTypes.startToStart') }}</option>
                <option value="finish-to-finish">{{ $t('connectionTypes.finishToFinish') }}</option>
                <option value="start-to-finish">{{ $t('connectionTypes.startToFinish') }}</option>
              </select>
            </div>
          </div>
          
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeConnectionModal">{{ $t('taskModal.cancel') }}</button>
            <button class="btn btn-primary" @click="saveConnection">{{ $t('taskModal.save') }}</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import GanttChart from './components/GanttChart.vue'
import { taskApi, connectionApi } from './api'
import { setLanguage } from './i18n'

const { t, locale } = useI18n()

const tasks = ref([])
const connections = ref([])
const currentScale = ref('day')

// Language support
const languages = [
  { code: 'ru', name: 'Русский', flag: 'RU' },
  { code: 'en', name: 'English', flag: 'EN' },
  { code: 'ar', name: 'العربية', flag: 'AR' }
]

const currentLanguage = computed(() => locale.value)

const changeLanguage = (lang) => {
  setLanguage(lang)
}

// Map for O(1) task lookup
const tasksMap = computed(() => {
  const map = new Map()
  tasks.value.forEach(t => map.set(t.id, t))
  return map
})
const showTaskModal = ref(false)
const showConnectionModal = ref(false)
const editingTask = ref(null)
const editingConnection = ref(null)
const parentConnectionsExpanded = ref(true)
const childConnectionsExpanded = ref(true)

const timeScales = [
  { value: 'day' },
  { value: 'week' },
  { value: 'month' }
]

// Change scale from zoom
const changeScale = (newScale) => {
  currentScale.value = newScale
}

const taskForm = reactive({
  title: '',
  description: '',
  start_date: '',
  end_date: '',
  progress: 0,
  color: '#4A90D9',
  row_index: 0,
  parent_id: null, // Parent task for hierarchy
  // Connection fields (arrows)
  conn_parent_task_id: null,
  conn_parent_connection_type: 'finish-to-start',
  conn_child_task_id: null,
  conn_child_connection_type: 'finish-to-start'
})

const connectionForm = reactive({
  arrow_color: '#666666',
  arrow_style: 'solid',
  arrow_type: 'finish-to-start'
})

// Available tasks for hierarchy parent selection (can't be self or own children)
const availableHierarchyParents = computed(() => {
  if (!editingTask.value) {
    // For new tasks, any task without a parent can be a parent
    return tasks.value.filter(t => !t.parent_id)
  }
  // For existing task: exclude self and own children (to prevent circular reference)
  const childIds = new Set(tasks.value.filter(t => t.parent_id === editingTask.value.id).map(t => t.id))
  return tasks.value.filter(t => 
    t.id !== editingTask.value.id && !childIds.has(t.id)
  )
})

// Available tasks for parent/child connection (arrows) selection (exclude current task and already connected tasks)
const availableParentTasks = computed(() => {
  if (!editingTask.value) {
    return tasks.value
  }
  const existingParentIds = existingParentConnections.value.map(c => c.from_task_id)
  return tasks.value.filter(t => 
    t.id !== editingTask.value.id && !existingParentIds.includes(t.id)
  )
})

const availableChildTasks = computed(() => {
  if (!editingTask.value) {
    return tasks.value
  }
  const existingChildIds = existingChildConnections.value.map(c => c.to_task_id)
  return tasks.value.filter(t => 
    t.id !== editingTask.value.id && !existingChildIds.includes(t.id)
  )
})

// Existing connections for the editing task
const existingParentConnections = computed(() => {
  if (!editingTask.value) return []
  return connections.value.filter(c => c.to_task_id === editingTask.value.id)
})

const existingChildConnections = computed(() => {
  if (!editingTask.value) return []
  return connections.value.filter(c => c.from_task_id === editingTask.value.id)
})

// Helper functions - O(1) lookup using Map
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

// Remove connection functions
const removeParentConnection = async (connectionId) => {
  try {
    await connectionApi.delete(connectionId)
    await loadTasks()
  } catch (error) {
    console.error('Failed to remove parent connection:', error)
  }
}

const removeChildConnection = async (connectionId) => {
  try {
    await connectionApi.delete(connectionId)
    await loadTasks()
  } catch (error) {
    console.error('Failed to remove child connection:', error)
  }
}

const resetTaskForm = () => {
  const now = new Date()
  const nextWeek = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
  
  taskForm.title = ''
  taskForm.description = ''
  taskForm.start_date = now.toISOString().slice(0, 16)
  taskForm.end_date = nextWeek.toISOString().slice(0, 16)
  taskForm.progress = 0
  taskForm.color = '#4A90D9'
  taskForm.row_index = tasks.value.length
  taskForm.parent_id = null
  taskForm.conn_parent_task_id = null
  taskForm.conn_parent_connection_type = 'finish-to-start'
  taskForm.conn_child_task_id = null
  taskForm.conn_child_connection_type = 'finish-to-start'
}

const loadTasks = async () => {
  try {
    const [tasksRes, connectionsRes] = await Promise.all([
      taskApi.getAll(),
      connectionApi.getAll()
    ])
    tasks.value = tasksRes.data
    connections.value = connectionsRes.data
  } catch (error) {
    console.error('Failed to load tasks:', error)
  }
}

const loadDemoData = async () => {
  try {
    await taskApi.seed()
    await loadTasks()
  } catch (error) {
    console.error('Failed to load demo data:', error)
  }
}

const openCreateTaskModal = () => {
  resetTaskForm()
  showTaskModal.value = true
}

const saveTask = async () => {
  try {
    const data = {
      title: taskForm.title,
      description: taskForm.description,
      start_date: new Date(taskForm.start_date).toISOString(),
      end_date: new Date(taskForm.end_date).toISOString(),
      progress: taskForm.progress,
      color: taskForm.color,
      row_index: taskForm.row_index,
      parent_id: taskForm.parent_id
    }
    
    let savedTask
    if (editingTask.value) {
      const response = await taskApi.update(editingTask.value.id, data)
      savedTask = response.data
    } else {
      const response = await taskApi.create(data)
      savedTask = response.data
    }
    
    // Create new parent connection (arrow) if selected
    if (taskForm.conn_parent_task_id) {
      try {
        await connectionApi.create({
          from_task_id: taskForm.conn_parent_task_id,
          to_task_id: savedTask.id,
          arrow_type: taskForm.conn_parent_connection_type,
          arrow_color: taskForm.color
        })
      } catch (e) {
        console.log('Parent connection may already exist')
      }
    }
    
    // Create new child connection (arrow) if selected
    if (taskForm.conn_child_task_id) {
      try {
        await connectionApi.create({
          from_task_id: savedTask.id,
          to_task_id: taskForm.conn_child_task_id,
          arrow_type: taskForm.conn_child_connection_type,
          arrow_color: taskForm.color
        })
      } catch (e) {
        console.log('Child connection may already exist')
      }
    }
    
    await loadTasks()
    closeTaskModal()
  } catch (error) {
    console.error('Failed to save task:', error)
  }
}

// Calculate parent date span from children
const updateParentDatesFromChildren = (parentId) => {
  const children = tasks.value.filter(t => t.parent_id === parentId)
  if (children.length === 0) return null
  
  let minStart = new Date(children[0].start_date)
  let maxEnd = new Date(children[0].end_date)
  
  children.forEach(child => {
    const start = new Date(child.start_date)
    const end = new Date(child.end_date)
    if (start < minStart) minStart = start
    if (end > maxEnd) maxEnd = end
  })
  
  return {
    start_date: minStart.toISOString(),
    end_date: maxEnd.toISOString()
  }
}

// Live update - only update local state, no server sync
const updateTaskLive = (updates) => {
  const parentsToUpdate = new Set()
  const movedParentIds = new Set()
  
  // First pass: identify which parents are being moved
  updates.forEach(update => {
    const task = tasks.value.find(t => t.id === update.id)
    if (task && !task.parent_id) {
      // This is a root-level task (potential parent)
      const hasChildren = tasks.value.some(t => t.parent_id === task.id)
      if (hasChildren && (update.start_date || update.end_date)) {
        movedParentIds.add(task.id)
      }
    }
  })
  
  // Calculate date deltas for moved parents to apply to children
  const parentDateDeltas = new Map()
  movedParentIds.forEach(parentId => {
    const update = updates.find(u => u.id === parentId)
    const parent = tasks.value.find(t => t.id === parentId)
    if (update && parent && update.start_date) {
      const oldStart = new Date(parent.start_date)
      const newStart = new Date(update.start_date)
      const deltaMs = newStart.getTime() - oldStart.getTime()
      parentDateDeltas.set(parentId, deltaMs)
    }
  })
  
  // Apply updates
  updates.forEach(update => {
    const taskIndex = tasks.value.findIndex(t => t.id === update.id)
    if (taskIndex !== -1) {
      const task = tasks.value[taskIndex]
      // Track parent for date update (only if parent is NOT being moved)
      if (task.parent_id && !movedParentIds.has(task.parent_id)) {
        parentsToUpdate.add(task.parent_id)
      }
      // Merge update into existing task
      tasks.value[taskIndex] = { ...tasks.value[taskIndex], ...update }
    }
  })
  
  // Move children of moved parents
  parentDateDeltas.forEach((deltaMs, parentId) => {
    tasks.value.forEach((task, index) => {
      if (task.parent_id === parentId) {
        const oldStart = new Date(task.start_date)
        const oldEnd = new Date(task.end_date)
        tasks.value[index] = {
          ...task,
          start_date: new Date(oldStart.getTime() + deltaMs).toISOString(),
          end_date: new Date(oldEnd.getTime() + deltaMs).toISOString()
        }
      }
    })
  })
  
  // Update parent dates to span children (only for parents that weren't explicitly moved)
  parentsToUpdate.forEach(parentId => {
    const parentIndex = tasks.value.findIndex(t => t.id === parentId)
    if (parentIndex !== -1) {
      const newDates = updateParentDatesFromChildren(parentId)
      if (newDates) {
        tasks.value[parentIndex] = { ...tasks.value[parentIndex], ...newDates }
      }
    }
  })
}

// Debounce helper for batching server updates
const pendingUpdates = new Map()
let updateDebounceTimer = null

const updateTask = async (task) => {
  // Add to pending updates
  pendingUpdates.set(task.id, { ...pendingUpdates.get(task.id), ...task })
  
  const currentTask = tasks.value.find(t => t.id === task.id)
  
  // If this is a parent task being moved, also add children to pending updates
  const hasChildren = tasks.value.some(t => t.parent_id === task.id)
  if (hasChildren && !currentTask?.parent_id) {
    // This is a parent - children already updated in live update, just add them to pending
    tasks.value.filter(t => t.parent_id === task.id).forEach(child => {
      pendingUpdates.set(child.id, {
        ...pendingUpdates.get(child.id),
        id: child.id,
        start_date: child.start_date,
        end_date: child.end_date
      })
    })
  }
  
  // Check if this task has a parent and update parent's dates
  if (currentTask?.parent_id) {
    const newDates = updateParentDatesFromChildren(currentTask.parent_id)
    if (newDates) {
      pendingUpdates.set(currentTask.parent_id, { 
        ...pendingUpdates.get(currentTask.parent_id), 
        id: currentTask.parent_id,
        ...newDates 
      })
    }
  }
  
  // Debounce server sync
  if (updateDebounceTimer) {
    clearTimeout(updateDebounceTimer)
  }
  
  updateDebounceTimer = setTimeout(async () => {
    const updates = Array.from(pendingUpdates.values())
    pendingUpdates.clear()
    
    try {
      // Send all updates in parallel
      await Promise.all(updates.map(u => taskApi.update(u.id, u)))
    } catch (error) {
      console.error('Failed to update tasks:', error)
      // Reload on error to get consistent state
      await loadTasks()
    }
  }, 100)
}

const deleteTask = async (taskId) => {
  try {
    await taskApi.delete(taskId)
    await loadTasks()
  } catch (error) {
    console.error('Failed to delete task:', error)
  }
}

const editTask = (task) => {
  editingTask.value = task
  taskForm.title = task.title
  taskForm.description = task.description || ''
  taskForm.start_date = new Date(task.start_date).toISOString().slice(0, 16)
  taskForm.end_date = new Date(task.end_date).toISOString().slice(0, 16)
  taskForm.progress = task.progress
  taskForm.color = task.color
  taskForm.row_index = task.row_index
  taskForm.parent_id = task.parent_id || null
  
  // Reset connection (arrow) fields (existing connections shown in list, these are for adding new)
  taskForm.conn_parent_task_id = null
  taskForm.conn_parent_connection_type = 'finish-to-start'
  taskForm.conn_child_task_id = null
  taskForm.conn_child_connection_type = 'finish-to-start'
  
  // Expand connections sections if there are existing connections
  parentConnectionsExpanded.value = true
  childConnectionsExpanded.value = true
  
  showTaskModal.value = true
}

const closeTaskModal = () => {
  showTaskModal.value = false
  editingTask.value = null
  resetTaskForm()
}

const createConnection = async (connection) => {
  try {
    await connectionApi.create(connection)
    await loadTasks()
  } catch (error) {
    console.error('Failed to create connection:', error)
  }
}

const deleteConnection = async (connectionId) => {
  try {
    await connectionApi.delete(connectionId)
    await loadTasks()
  } catch (error) {
    console.error('Failed to delete connection:', error)
  }
}

const editConnection = (connection) => {
  editingConnection.value = connection
  connectionForm.arrow_color = connection.arrow_color
  connectionForm.arrow_style = connection.arrow_style
  connectionForm.arrow_type = connection.arrow_type
  showConnectionModal.value = true
}

const saveConnection = async () => {
  try {
    await connectionApi.update(editingConnection.value.id, connectionForm)
    await loadTasks()
    closeConnectionModal()
  } catch (error) {
    console.error('Failed to update connection:', error)
  }
}

const closeConnectionModal = () => {
  showConnectionModal.value = false
  editingConnection.value = null
}

onMounted(() => {
  resetTaskForm()
  loadTasks()
})

onUnmounted(() => {
  if (updateDebounceTimer) {
    clearTimeout(updateDebounceTimer)
  }
})
</script>

<style scoped>
.app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: var(--accent-primary);
}

.logo svg {
  color: var(--accent-primary);
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.language-selector {
  display: flex;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  padding: 2px;
  border: 1px solid var(--border-subtle);
  gap: 2px;
}

.lang-btn {
  padding: 6px 10px;
  border: none;
  background: transparent;
  font-size: 16px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1;
}

.lang-btn:hover {
  background: var(--bg-elevated);
}

.lang-btn.active {
  background: var(--accent-primary);
}

.time-scale-selector {
  display: flex;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  padding: 4px;
  border: 1px solid var(--border-subtle);
}

.scale-btn {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 500;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.scale-btn:hover {
  color: var(--text-primary);
}

.scale-btn.active {
  background: var(--accent-primary);
  color: var(--bg-primary);
}

.app-main {
  flex: 1;
  overflow: hidden;
}

/* Modal styles */
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

.modal-sm {
  max-width: 400px;
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

.connection-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 12px;
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

.connection-box .form-group {
  margin-bottom: 0;
}

.connection-box .form-row {
  gap: 12px;
}

.connection-box select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Expandable connection sections */
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
  margin-bottom: 0;
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

</style>
