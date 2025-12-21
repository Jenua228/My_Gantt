<template>
  <div class="app">
    <header class="app-header">
      <div class="logo">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="4" width="18" height="4" rx="1" />
          <rect x="3" y="10" width="14" height="4" rx="1" />
          <rect x="3" y="16" width="10" height="4" rx="1" />
        </svg>
        <span>Gantt Scheduler</span>
      </div>
      
      <div class="header-controls">
        <div class="time-scale-selector">
          <button 
            v-for="scale in timeScales" 
            :key="scale.value"
            :class="['scale-btn', { active: currentScale === scale.value }]"
            @click="currentScale = scale.value"
          >
            {{ scale.label }}
          </button>
        </div>
        
        <button class="btn btn-secondary" @click="loadDemoData">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <path d="M3 3v5h5" />
          </svg>
          Load Demo
        </button>
        
        <button class="btn btn-primary" @click="openCreateTaskModal">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Add Task
        </button>
      </div>
    </header>
    
    <main class="app-main">
      <GanttChart 
        :tasks="tasks" 
        :connections="connections"
        :scale="currentScale"
        @update-task="updateTask"
        @delete-task="deleteTask"
        @create-connection="createConnection"
        @delete-connection="deleteConnection"
        @edit-task="editTask"
        @edit-connection="editConnection"
      />
    </main>
    
    <!-- Task Modal -->
    <Transition name="fade">
      <div v-if="showTaskModal" class="modal-overlay" @click.self="closeTaskModal">
        <div class="modal modal-lg">
          <div class="modal-header">
            <h2>{{ editingTask ? 'Edit Task' : 'New Task' }}</h2>
            <button class="btn btn-icon" @click="closeTaskModal">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          
          <div class="modal-body">
            <div class="form-group">
              <label>Task Title</label>
              <input v-model="taskForm.title" type="text" placeholder="Enter task title" />
            </div>
            
            <div class="form-group">
              <label>Description</label>
              <textarea v-model="taskForm.description" rows="2" placeholder="Optional description"></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Start Date</label>
                <input v-model="taskForm.start_date" type="datetime-local" />
              </div>
              <div class="form-group">
                <label>End Date</label>
                <input v-model="taskForm.end_date" type="datetime-local" />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Progress ({{ taskForm.progress }}%)</label>
                <input v-model.number="taskForm.progress" type="range" min="0" max="100" />
              </div>
              <div class="form-group">
                <label>Color</label>
                <div class="color-picker-wrapper">
                  <div class="color-preview" :style="{ backgroundColor: taskForm.color }"></div>
                  <input v-model="taskForm.color" type="color" />
                  <input v-model="taskForm.color" type="text" style="flex: 1" />
                </div>
              </div>
            </div>
            
            <!-- Connection Section -->
            <div class="form-section">
              <div class="section-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                  <polyline points="15 3 21 3 21 9" />
                  <line x1="10" y1="14" x2="21" y2="3" />
                </svg>
                Task Connections (Optional)
              </div>
              
              <!-- Parent Connection (Arrow FROM another task TO this task) -->
              <div class="connection-box">
                <div class="connection-label">
                  <span class="arrow-icon">→</span>
                  Parent Task (arrow comes FROM)
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Select Parent Task</label>
                    <select v-model="taskForm.parent_task_id">
                      <option :value="null">— None —</option>
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
                    <label>Connection Type</label>
                    <select v-model="taskForm.parent_connection_type" :disabled="!taskForm.parent_task_id">
                      <option value="finish-to-start">Finish → Start</option>
                      <option value="finish-to-finish">Finish → Finish</option>
                      <option value="start-to-start">Start → Start</option>
                      <option value="start-to-finish">Start → Finish</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <!-- Child Connection (Arrow FROM this task TO another task) -->
              <div class="connection-box">
                <div class="connection-label">
                  <span class="arrow-icon">←</span>
                  Child Task (arrow goes TO)
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>Select Child Task</label>
                    <select v-model="taskForm.child_task_id">
                      <option :value="null">— None —</option>
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
                    <label>Connection Type</label>
                    <select v-model="taskForm.child_connection_type" :disabled="!taskForm.child_task_id">
                      <option value="finish-to-start">Finish → Start</option>
                      <option value="finish-to-finish">Finish → Finish</option>
                      <option value="start-to-start">Start → Start</option>
                      <option value="start-to-finish">Start → Finish</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeTaskModal">Cancel</button>
            <button class="btn btn-primary" @click="saveTask">
              {{ editingTask ? 'Update' : 'Create' }} Task
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
            <h2>Edit Connection</h2>
            <button class="btn btn-icon" @click="closeConnectionModal">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          
          <div class="modal-body">
            <div class="form-group">
              <label>Arrow Color</label>
              <div class="color-picker-wrapper">
                <div class="color-preview" :style="{ backgroundColor: connectionForm.arrow_color }"></div>
                <input v-model="connectionForm.arrow_color" type="color" />
                <input v-model="connectionForm.arrow_color" type="text" style="flex: 1" />
              </div>
            </div>
            
            <div class="form-group">
              <label>Arrow Style</label>
              <select v-model="connectionForm.arrow_style">
                <option value="solid">Solid</option>
                <option value="dashed">Dashed</option>
                <option value="dotted">Dotted</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Connection Type</label>
              <select v-model="connectionForm.arrow_type">
                <option value="finish-to-start">Finish → Start</option>
                <option value="start-to-start">Start → Start</option>
                <option value="finish-to-finish">Finish → Finish</option>
                <option value="start-to-finish">Start → Finish</option>
              </select>
            </div>
          </div>
          
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeConnectionModal">Cancel</button>
            <button class="btn btn-primary" @click="saveConnection">Update</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import GanttChart from './components/GanttChart.vue'
import { taskApi, connectionApi } from './api'

const tasks = ref([])
const connections = ref([])
const currentScale = ref('day')
const showTaskModal = ref(false)
const showConnectionModal = ref(false)
const editingTask = ref(null)
const editingConnection = ref(null)

const timeScales = [
  { label: 'Hour', value: 'hour' },
  { label: 'Day', value: 'day' },
  { label: 'Week', value: 'week' },
  { label: 'Month', value: 'month' }
]

const taskForm = reactive({
  title: '',
  description: '',
  start_date: '',
  end_date: '',
  progress: 0,
  color: '#4A90D9',
  row_index: 0,
  // Connection fields
  parent_task_id: null,
  parent_connection_type: 'finish-to-start',
  child_task_id: null,
  child_connection_type: 'finish-to-start'
})

const connectionForm = reactive({
  arrow_color: '#666666',
  arrow_style: 'solid',
  arrow_type: 'finish-to-start'
})

// Available tasks for parent/child selection (exclude current task when editing)
const availableParentTasks = computed(() => {
  return tasks.value.filter(t => !editingTask.value || t.id !== editingTask.value.id)
})

const availableChildTasks = computed(() => {
  return tasks.value.filter(t => !editingTask.value || t.id !== editingTask.value.id)
})

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
  taskForm.parent_task_id = null
  taskForm.parent_connection_type = 'finish-to-start'
  taskForm.child_task_id = null
  taskForm.child_connection_type = 'finish-to-start'
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
      row_index: taskForm.row_index
    }
    
    let savedTask
    if (editingTask.value) {
      const response = await taskApi.update(editingTask.value.id, data)
      savedTask = response.data
    } else {
      const response = await taskApi.create(data)
      savedTask = response.data
    }
    
    // Create parent connection if selected
    if (taskForm.parent_task_id) {
      try {
        await connectionApi.create({
          from_task_id: taskForm.parent_task_id,
          to_task_id: savedTask.id,
          arrow_type: taskForm.parent_connection_type,
          arrow_color: taskForm.color
        })
      } catch (e) {
        console.log('Parent connection may already exist')
      }
    }
    
    // Create child connection if selected
    if (taskForm.child_task_id) {
      try {
        await connectionApi.create({
          from_task_id: savedTask.id,
          to_task_id: taskForm.child_task_id,
          arrow_type: taskForm.child_connection_type,
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

const updateTask = async (task) => {
  try {
    await taskApi.update(task.id, task)
    await loadTasks()
  } catch (error) {
    console.error('Failed to update task:', error)
  }
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
  taskForm.parent_task_id = null
  taskForm.parent_connection_type = 'finish-to-start'
  taskForm.child_task_id = null
  taskForm.child_connection_type = 'finish-to-start'
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
</style>
