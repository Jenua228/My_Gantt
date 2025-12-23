<template>
  <div class="gantt-container" ref="containerRef" @click="handleContainerClick">
    <!-- Task Sidebar -->
    <div class="gantt-sidebar">
      <div class="sidebar-header">
        <span>Задачи</span>
        <span class="task-count">{{ tasks.length }}</span>
      </div>
      <div class="sidebar-content">
        <template v-for="task in visibleTasks" :key="task.id">
          <div 
            class="sidebar-task"
            :class="{ 
              'is-selected': selectedTaskIds.has(task.id),
              'is-parent': hasChildren(task.id),
              'is-child': task.parent_id != null,
              'is-expanded': expandedTaskIds.has(task.id)
            }"
            :style="{ 
              borderLeftColor: task.color,
              paddingLeft: task.parent_id ? '36px' : '20px'
            }"
            @click="handleSidebarTaskClick($event, task)"
          >
            <!-- Expand/Collapse button for parents -->
            <button 
              v-if="hasChildren(task.id)" 
              class="expand-btn"
              @click.stop="toggleExpand(task.id)"
            >
              <svg 
                width="12" height="12" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                stroke-width="2"
                :class="{ 'rotated': expandedTaskIds.has(task.id) }"
              >
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </button>
            
            <div class="task-info">
              <span class="task-title">
                <span v-if="hasChildren(task.id)" class="parent-badge">Parent</span>
                {{ task.title }}
              </span>
              <span class="task-dates">
                {{ formatDate(task.start_date) }} — {{ formatDate(task.end_date) }}
              </span>
            </div>
            <div class="task-actions">
              <button class="action-btn" @click.stop="$emit('edit-task', task)" title="Редактировать">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
              </button>
              <button class="action-btn danger" @click.stop="$emit('delete-task', task.id)" title="Удалить">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6" />
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                </svg>
              </button>
            </div>
          </div>
        </template>
        <div v-if="tasks.length === 0" class="sidebar-empty">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
          </svg>
          <p>No tasks yet</p>
          <span>Click "Add Task" or "Load Demo" to get started</span>
        </div>
      </div>
    </div>
    
    <!-- Gantt Timeline -->
    <div class="gantt-timeline" ref="timelineRef" @scroll="handleScroll">
      <!-- Timeline Header -->
      <div class="timeline-header" :style="{ width: timelineWidth + 'px' }">
        <div 
          v-for="(unit, index) in timeUnits" 
          :key="index"
          class="time-unit"
          :class="{ 'is-today': isToday(unit.date) }"
          :style="{ width: cellWidth + 'px' }"
        >
          <span class="unit-label">{{ unit.label }}</span>
          <span class="unit-sublabel">{{ unit.sublabel }}</span>
        </div>
      </div>
      
      <!-- Grid and Tasks -->
      <div class="timeline-body" :style="{ width: timelineWidth + 'px', minHeight: gridHeight + 'px' }">
        <!-- Grid background -->
        <div class="grid-background" :style="{ width: timelineWidth + 'px', height: gridHeight + 'px' }"></div>
        
        <!-- Parent-Children Group Backgrounds -->
        <div 
          v-for="group in childGroupBackgrounds" 
          :key="'group-' + group.parentId"
          class="child-group-background"
          :style="{
            top: group.top + 'px',
            height: group.height + 'px',
            width: timelineWidth + 'px',
            borderLeftColor: group.color
          }"
        >
          <div class="group-indicator" :style="{ backgroundColor: group.color }"></div>
        </div>
        
        <!-- Grid Lines -->
        <svg class="grid-lines" :width="timelineWidth" :height="gridHeight">
          <!-- Vertical grid lines -->
          <line 
            v-for="(unit, index) in timeUnits" 
            :key="'v-' + index"
            :x1="index * cellWidth"
            y1="0"
            :x2="index * cellWidth"
            :y2="gridHeight"
            :class="{ 'grid-line': true, 'grid-line-strong': unit.isStrong }"
          />
          <!-- Horizontal grid lines -->
          <line 
            v-for="index in horizontalLinesCount" 
            :key="'h-' + index"
            x1="0"
            :y1="(index - 1) * rowHeight"
            :x2="timelineWidth"
            :y2="(index - 1) * rowHeight"
            class="grid-line"
          />
          <!-- Today marker -->
          <line 
            v-if="todayOffset !== null"
            :x1="todayOffset"
            y1="0"
            :x2="todayOffset"
            :y2="gridHeight"
            class="today-line"
          />
        </svg>
        
        <!-- Connection Arrows (SVG Layer) -->
        <svg class="connections-layer" :width="timelineWidth" :height="gridHeight" @mouseleave="hoveredConnectionId = null">
          <defs>
            <!-- Arrow markers for each connection -->
            <marker 
              v-for="conn in visibleConnections"
              :key="'marker-' + conn.id"
              :id="'arrowhead-' + conn.id"
              markerWidth="10"
              markerHeight="7"
              refX="8"
              refY="3.5"
              orient="auto"
              markerUnits="strokeWidth"
            >
              <polygon points="0 0, 10 3.5, 0 7, 1.5 3.5" :fill="conn.arrow_color" />
            </marker>
            <!-- Start circle markers -->
            <marker 
              v-for="conn in visibleConnections"
              :key="'start-marker-' + conn.id"
              :id="'startpoint-' + conn.id"
              markerWidth="6"
              markerHeight="6"
              refX="3"
              refY="3"
              orient="auto"
            >
              <circle cx="3" cy="3" r="2.5" :fill="conn.arrow_color" />
            </marker>
          </defs>
          
          <g 
            v-for="conn in visibleConnections" 
            :key="conn.id" 
            class="connection-group"
            :class="{ 
              'is-hovered': hoveredConnectionId === conn.id,
              'is-inherited': conn.isInherited 
            }"
            @mouseenter="hoveredConnectionId = conn.id"
            @mouseleave="hoveredConnectionId = null"
          >
            <!-- Invisible wider path for easier clicking -->
            <path
              :d="getConnectionPath(conn)"
              stroke="transparent"
              stroke-width="16"
              fill="none"
              style="cursor: pointer;"
              @click.stop="showConnectionInfo($event, conn)"
              @contextmenu.prevent="$emit('delete-connection', conn.id)"
            />
            <!-- Visible path -->
            <path
              :d="getConnectionPath(conn)"
              :stroke="conn.arrow_color"
              :stroke-dasharray="getStrokeDashArray(conn.arrow_style)"
              :stroke-width="hoveredConnectionId === conn.id ? 3 : 2"
              fill="none"
              :marker-start="`url(#startpoint-${conn.id})`"
              :marker-end="`url(#arrowhead-${conn.id})`"
              class="connection-path"
            />
          </g>
          
          <!-- Connection creation preview -->
          <path
            v-if="connectionPreview"
            :d="connectionPreview"
            stroke="var(--accent-primary)"
            stroke-width="2"
            stroke-dasharray="5,5"
            fill="none"
            opacity="0.7"
          />
        </svg>
        
        <!-- Task Bars -->
        <template v-for="task in displayTasks" :key="task.id">
          <!-- Parent Task Bar (thin line when expanded) -->
          <div 
            v-if="task.isParent && task.isExpanded"
            :ref="el => taskRefs[task.id] = el"
            class="task-bar task-bar-parent"
            :class="{ 
              'is-dragging': isDragging && selectedTaskIds.has(task.id),
              'is-selected': selectedTaskIds.has(task.id)
            }"
            :style="getParentTaskStyle(task)"
            :title="getTaskTooltip(task)"
            @mousedown="handleTaskMouseDown($event, task)"
            @dblclick.stop="$emit('edit-task', task)"
          >
            <div class="parent-task-line" :style="{ backgroundColor: task.color }">
              <span class="parent-task-title">{{ task.title }}</span>
            </div>
          </div>
          
          <!-- Regular Task Bar (or collapsed parent) -->
          <div 
            v-else
            :ref="el => taskRefs[task.id] = el"
            class="task-bar"
            :class="{ 
              'is-dragging': isDragging && selectedTaskIds.has(task.id),
              'is-connecting': connectingFrom?.id === task.id,
              'is-selected': selectedTaskIds.has(task.id),
              'is-parent-collapsed': task.isParent && !task.isExpanded,
              'is-child-task': task.parent_id != null
            }"
            :style="getTaskStyle(task)"
            :title="getTaskTooltip(task)"
            @mousedown="handleTaskMouseDown($event, task)"
            @dblclick.stop="$emit('edit-task', task)"
          >
            <div class="task-progress" :style="{ width: task.progress + '%', backgroundColor: task.color }"></div>
            <div class="task-content" :ref="el => taskContentRefs[task.id] = el">
              <span class="task-bar-title" :ref="el => taskTitleRefs[task.id] = el">
                <button 
                  v-if="task.isParent" 
                  class="expand-toggle-btn"
                  @click.stop="toggleExpand(task.id)"
                  @mousedown.stop
                  :title="task.isExpanded ? 'Свернуть' : 'Развернуть'"
                >
                  {{ task.isExpanded ? '▼' : '▶' }}
                </button>
                {{ task.title }}
              </span>
              <span class="task-bar-progress">{{ task.progress }}%</span>
            </div>
            
            <!-- Floating label for tasks with overflow text -->
            <div class="task-floating-label">
              {{ task.title }}
            </div>
            
            <!-- Connection handles -->
            <div 
              class="connection-handle handle-left" 
              @mousedown.stop="startConnection($event, task, 'start')"
              title="Соединить от начала"
            ></div>
            <div 
              class="connection-handle handle-right"
              @mousedown.stop="startConnection($event, task, 'end')"
              title="Соединить от конца"
            ></div>
            
            <!-- Resize handles -->
            <div 
              class="resize-handle resize-left"
              @mousedown.stop="startResize($event, task, 'left')"
            ></div>
            <div 
              class="resize-handle resize-right"
              @mousedown.stop="startResize($event, task, 'right')"
            ></div>
          </div>
        </template>
      </div>
    </div>
    
    <!-- Connection Info Popup -->
    <Transition name="popup">
      <div v-if="connectionInfo" class="connection-popup" :style="connectionPopupStyle">
        <div class="popup-header">
          <span>Информация о связи</span>
          <button class="popup-close" @click="connectionInfo = null">×</button>
        </div>
        <div class="popup-content">
          <div class="popup-row">
            <span class="popup-label">Откуда:</span>
            <span class="popup-value" :style="{ color: getTaskById(connectionInfo.from_task_id)?.color }">
              {{ getTaskById(connectionInfo.from_task_id)?.title || 'Неизвестно' }}
            </span>
          </div>
          <div class="popup-row">
            <span class="popup-label">Куда:</span>
            <span class="popup-value" :style="{ color: getTaskById(connectionInfo.to_task_id)?.color }">
              {{ getTaskById(connectionInfo.to_task_id)?.title || 'Неизвестно' }}
            </span>
          </div>
          <div class="popup-row">
            <span class="popup-label">Тип:</span>
            <span class="popup-value">{{ formatConnectionType(connectionInfo.arrow_type) }}</span>
          </div>
        </div>
        <div class="popup-footer">
          <button class="btn btn-secondary btn-sm" @click="$emit('edit-connection', connectionInfo); connectionInfo = null">
            Изменить
          </button>
          <button class="btn btn-danger btn-sm" @click="$emit('delete-connection', connectionInfo.id); connectionInfo = null">
            Удалить
          </button>
        </div>
      </div>
    </Transition>
    
    <!-- Selection count indicator -->
    <div v-if="selectedTaskIds.size > 1" class="selection-indicator">
      Выбрано задач: {{ selectedTaskIds.size }} (Shift+Клик для добавления)
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { format, addDays, addWeeks, addMonths, startOfDay, differenceInDays, isToday as checkIsToday, parseISO } from 'date-fns'

const props = defineProps({
  tasks: { type: Array, default: () => [] },
  connections: { type: Array, default: () => [] },
  scale: { type: String, default: 'day' }
})

const emit = defineEmits(['update-task', 'update-task-live', 'delete-task', 'create-connection', 'delete-connection', 'edit-task', 'edit-connection'])

const containerRef = ref(null)
const timelineRef = ref(null)
const taskRefs = reactive({})
const taskContentRefs = reactive({})
const taskTitleRefs = reactive({})

// Selection state
const selectedTaskIds = ref(new Set())
const isDragging = ref(false)
const dragStartPositions = ref({}) // Store initial positions of selected tasks

const draggingTask = ref(null)
const dragOffset = ref({ x: 0, y: 0 })
const resizingTask = ref(null)
const resizeDirection = ref(null)
const connectingFrom = ref(null)
const connectingType = ref(null)
const connectionPreview = ref(null)
const containerHeight = ref(600)
const connectionInfo = ref(null)
const connectionPopupPosition = ref({ x: 0, y: 0 })
const hoveredConnectionId = ref(null)

// Hierarchy expansion state
const expandedTaskIds = ref(new Set())

const rowHeight = 48
const parentRowHeight = 16 // Thin line for expanded parents
const cellWidth = computed(() => {
  switch (props.scale) {
    case 'day': return 40
    case 'week': return 100
    case 'month': return 120
    default: return 40
  }
})

// Calculate date range based on tasks
const dateRange = computed(() => {
  if (props.tasks.length === 0) {
    const now = new Date()
    return {
      start: startOfDay(addDays(now, -7)),
      end: startOfDay(addDays(now, 60))
    }
  }
  
  let minDate = new Date(props.tasks[0].start_date)
  let maxDate = new Date(props.tasks[0].end_date)
  
  props.tasks.forEach(task => {
    const start = new Date(task.start_date)
    const end = new Date(task.end_date)
    if (start < minDate) minDate = start
    if (end > maxDate) maxDate = end
  })
  
  return {
    start: startOfDay(addDays(minDate, -7)),
    end: startOfDay(addDays(maxDate, 14))
  }
})

const sortedTasks = computed(() => {
  return [...props.tasks].sort((a, b) => a.row_index - b.row_index)
})

// Map for O(1) task lookup - used in connection rendering
const tasksMap = computed(() => {
  const map = new Map()
  props.tasks.forEach(t => map.set(t.id, t))
  return map
})

// Children map for hierarchy
const childrenMap = computed(() => {
  const map = new Map()
  props.tasks.forEach(t => {
    if (t.parent_id) {
      if (!map.has(t.parent_id)) {
        map.set(t.parent_id, [])
      }
      map.get(t.parent_id).push(t)
    }
  })
  // Sort children by row_index
  map.forEach((children, parentId) => {
    children.sort((a, b) => a.row_index - b.row_index)
  })
  return map
})

// Check if task has children
const hasChildren = (taskId) => {
  return childrenMap.value.has(taskId) && childrenMap.value.get(taskId).length > 0
}

// Get children of a task
const getChildren = (taskId) => {
  return childrenMap.value.get(taskId) || []
}

// Toggle expand/collapse
const toggleExpand = (taskId) => {
  if (expandedTaskIds.value.has(taskId)) {
    expandedTaskIds.value.delete(taskId)
  } else {
    expandedTaskIds.value.add(taskId)
  }
}

// Visible tasks in sidebar (hierarchical order)
const visibleTasks = computed(() => {
  const result = []
  
  // Get root tasks (no parent)
  const rootTasks = props.tasks
    .filter(t => !t.parent_id)
    .sort((a, b) => a.row_index - b.row_index)
  
  // Add tasks recursively respecting expansion state
  const addTasksRecursively = (tasks, depth = 0) => {
    tasks.forEach(task => {
      result.push(task)
      if (hasChildren(task.id) && expandedTaskIds.value.has(task.id)) {
        addTasksRecursively(getChildren(task.id), depth + 1)
      }
    })
  }
  
  addTasksRecursively(rootTasks)
  return result
})

// Tasks visible on the Gantt chart (same as sidebar but with row positions)
const displayTasks = computed(() => {
  const result = []
  let currentRow = 0
  
  const addTasksRecursively = (tasks, parentExpanded = true) => {
    tasks.forEach(task => {
      const isParent = hasChildren(task.id)
      const isExpanded = expandedTaskIds.value.has(task.id)
      
      // Calculate display row
      const displayTask = {
        ...task,
        displayRow: currentRow,
        isParent,
        isExpanded,
        isChildVisible: parentExpanded
      }
      
      result.push(displayTask)
      currentRow++
      
      // Add children if expanded
      if (isParent && isExpanded) {
        addTasksRecursively(getChildren(task.id), true)
      }
    })
  }
  
  // Get root tasks (no parent)
  const rootTasks = props.tasks
    .filter(t => !t.parent_id)
    .sort((a, b) => a.row_index - b.row_index)
  
  addTasksRecursively(rootTasks)
  return result
})

// Map task ID to display row for connections
const taskDisplayRowMap = computed(() => {
  const map = new Map()
  displayTasks.value.forEach(t => map.set(t.id, t.displayRow))
  return map
})

// Helper to get display row for a task
const getTaskDisplayRow = (taskId) => {
  return taskDisplayRowMap.value.get(taskId) ?? -1
}

// Set of visible task IDs
const visibleTaskIds = computed(() => {
  return new Set(displayTasks.value.map(t => t.id))
})

// Calculate backgrounds for child groups (to visually distinguish children from other tasks)
const childGroupBackgrounds = computed(() => {
  const groups = []
  
  displayTasks.value.forEach(task => {
    if (task.isParent && task.isExpanded) {
      const children = getChildren(task.id)
      if (children.length === 0) return
      
      // Find the display rows of the children
      const childRows = children
        .map(child => getTaskDisplayRow(child.id))
        .filter(row => row !== -1)
      
      if (childRows.length === 0) return
      
      const minRow = Math.min(...childRows)
      const maxRow = Math.max(...childRows)
      
      groups.push({
        parentId: task.id,
        top: minRow * rowHeight,
        height: (maxRow - minRow + 1) * rowHeight,
        color: task.color
      })
    }
  })
  
  return groups
})

// Find the ancestor parent that is visible for a hidden task
const getVisibleAncestor = (taskId) => {
  const task = tasksMap.value.get(taskId)
  if (!task) return null
  
  // If task is visible, return itself
  if (visibleTaskIds.value.has(taskId)) {
    return taskId
  }
  
  // If task has a parent, check if parent is visible
  if (task.parent_id) {
    return getVisibleAncestor(task.parent_id)
  }
  
  return null
}

// Connections with hidden tasks redirected to their visible parent
const visibleConnections = computed(() => {
  const result = []
  const seenConnections = new Set()
  
  props.connections.forEach(conn => {
    const fromTaskId = conn.from_task_id
    const toTaskId = conn.to_task_id
    
    // Get visible task IDs (redirect to parent if hidden)
    const visibleFromId = getVisibleAncestor(fromTaskId)
    const visibleToId = getVisibleAncestor(toTaskId)
    
    // Skip if either task has no visible ancestor
    if (!visibleFromId || !visibleToId) return
    
    // Skip self-connections (when both map to same parent)
    if (visibleFromId === visibleToId) return
    
    // Create unique key to avoid duplicate connections
    const key = `${visibleFromId}-${visibleToId}-${conn.arrow_type}`
    if (seenConnections.has(key)) return
    seenConnections.add(key)
    
    // If connection is unchanged, use original
    if (visibleFromId === fromTaskId && visibleToId === toTaskId) {
      result.push(conn)
    } else {
      // Create modified connection pointing to visible ancestors
      result.push({
        ...conn,
        id: `inherited-${conn.id}`,
        from_task_id: visibleFromId,
        to_task_id: visibleToId,
        isInherited: true
      })
    }
  })
  
  return result
})

const timeUnits = computed(() => {
  const units = []
  let current = new Date(dateRange.value.start)
  const end = dateRange.value.end
  
  while (current <= end) {
    let label, sublabel, isStrong = false
    
    switch (props.scale) {
      case 'day':
        label = format(current, 'd')
        sublabel = format(current, 'EEE')
        isStrong = current.getDay() === 1
        current = addDays(current, 1)
        break
      case 'week':
        label = format(current, "'W'w")
        sublabel = format(current, 'MMM yyyy')
        isStrong = current.getDate() <= 7
        current = addWeeks(current, 1)
        break
      case 'month':
        label = format(current, 'MMM')
        sublabel = format(current, 'yyyy')
        isStrong = current.getMonth() === 0
        current = addMonths(current, 1)
        break
    }
    
    units.push({ label, sublabel, date: new Date(current), isStrong })
  }
  
  return units
})

const timelineWidth = computed(() => timeUnits.value.length * cellWidth.value)

const gridHeight = computed(() => {
  const tasksHeight = displayTasks.value.length * rowHeight
  return Math.max(tasksHeight + rowHeight * 5, containerHeight.value - 60)
})

const horizontalLinesCount = computed(() => {
  return Math.ceil(gridHeight.value / rowHeight) + 1
})

const todayOffset = computed(() => {
  const today = new Date()
  if (today < dateRange.value.start || today > dateRange.value.end) return null
  return getDateOffset(today)
})

const connectionPopupStyle = computed(() => ({
  left: connectionPopupPosition.value.x + 'px',
  top: connectionPopupPosition.value.y + 'px'
}))

const getDateOffset = (date) => {
  const d = typeof date === 'string' ? parseISO(date) : date
  
  switch (props.scale) {
    case 'day':
      return differenceInDays(d, dateRange.value.start) * cellWidth.value
    case 'week':
      return (differenceInDays(d, dateRange.value.start) / 7) * cellWidth.value
    case 'month':
      return (differenceInDays(d, dateRange.value.start) / 30) * cellWidth.value
    default:
      return differenceInDays(d, dateRange.value.start) * cellWidth.value
  }
}

const getTaskStyle = (task) => {
  const left = getDateOffset(task.start_date)
  const right = getDateOffset(task.end_date)
  const width = Math.max(right - left, 20)
  // Use displayRow if available (from displayTasks), otherwise fall back to row_index
  const row = task.displayRow !== undefined ? task.displayRow : task.row_index
  const top = row * rowHeight + 8
  
  return {
    left: `${left}px`,
    width: `${width}px`,
    top: `${top}px`,
    '--task-color': task.color
  }
}

// Style for expanded parent task (thin line spanning children)
const getParentTaskStyle = (task) => {
  // Get all children of this task
  const children = getChildren(task.id)
  if (children.length === 0) {
    return getTaskStyle(task)
  }
  
  // Calculate the span to cover all children
  let minStart = new Date(task.start_date)
  let maxEnd = new Date(task.end_date)
  
  children.forEach(child => {
    const childStart = new Date(child.start_date)
    const childEnd = new Date(child.end_date)
    if (childStart < minStart) minStart = childStart
    if (childEnd > maxEnd) maxEnd = childEnd
  })
  
  const left = getDateOffset(minStart)
  const right = getDateOffset(maxEnd)
  const width = Math.max(right - left, 40)
  
  // Position at the top of the parent's row
  const row = task.displayRow !== undefined ? task.displayRow : task.row_index
  const top = row * rowHeight + 4
  
  return {
    left: `${left}px`,
    width: `${width}px`,
    top: `${top}px`,
    '--task-color': task.color
  }
}

const getTaskDuration = (task) => {
  return differenceInDays(new Date(task.end_date), new Date(task.start_date))
}

const getTaskTooltip = (task) => {
  const duration = getTaskDuration(task)
  return `${task.title}\n${formatDate(task.start_date)} — ${formatDate(task.end_date)}\nDuration: ${duration} day(s)\nProgress: ${task.progress}%`
}

const formatDate = (date) => {
  return format(new Date(date), 'MMM d, yyyy')
}

const isToday = (date) => {
  return checkIsToday(date)
}

const getTaskById = (id) => {
  return tasksMap.value.get(id)
}

const formatConnectionType = (type) => {
  const types = {
    'finish-to-start': 'Окончание → Начало',
    'start-to-start': 'Начало → Начало',
    'finish-to-finish': 'Окончание → Окончание',
    'start-to-finish': 'Начало → Окончание'
  }
  return types[type] || type
}

const showConnectionInfo = (event, conn) => {
  connectionInfo.value = conn
  connectionPopupPosition.value = {
    x: event.clientX - containerRef.value.getBoundingClientRect().left + 10,
    y: event.clientY - containerRef.value.getBoundingClientRect().top + 10
  }
}

const getStrokeDashArray = (style) => {
  switch (style) {
    case 'dashed': return '8,4'
    case 'dotted': return '2,4'
    default: return 'none'
  }
}

// Improved connection path - arrows to right side come from right, not under task
const getConnectionPath = (conn) => {
  const fromTask = tasksMap.value.get(conn.from_task_id)
  const toTask = tasksMap.value.get(conn.to_task_id)
  
  if (!fromTask || !toTask) return ''
  
  // Check if both tasks are visible
  const fromRow = getTaskDisplayRow(conn.from_task_id)
  const toRow = getTaskDisplayRow(conn.to_task_id)
  
  if (fromRow === -1 || toRow === -1) return '' // Task not visible
  
  const fromLeft = getDateOffset(fromTask.start_date)
  const fromRight = getDateOffset(fromTask.end_date)
  const toLeft = getDateOffset(toTask.start_date)
  const toRight = getDateOffset(toTask.end_date)
  
  const fromY = fromRow * rowHeight + rowHeight / 2
  const toY = toRow * rowHeight + rowHeight / 2
  
  let startX, startSide, endX, endSide
  
  switch (conn.arrow_type) {
    case 'start-to-start':
      startX = fromLeft
      startSide = 'left'
      endX = toLeft
      endSide = 'left'
      break
    case 'finish-to-finish':
      startX = fromRight
      startSide = 'right'
      endX = toRight
      endSide = 'right'
      break
    case 'start-to-finish':
      startX = fromLeft
      startSide = 'left'
      endX = toRight
      endSide = 'right'
      break
    default: // finish-to-start
      startX = fromRight
      startSide = 'right'
      endX = toLeft
      endSide = 'left'
  }
  
  const goingDown = toY > fromY
  const goingUp = toY < fromY
  const sameRow = Math.abs(toY - fromY) < 5
  const vertDir = goingDown ? 1 : -1
  
  const routeOffset = 18
  const r = 8 // corner radius
  
  // Same row - simple cases
  if (sameRow) {
    if (startSide === 'right' && endSide === 'left' && startX < endX - 20) {
      return `M ${startX} ${fromY} L ${endX} ${toY}`
    }
    if (startSide === 'left' && endSide === 'right' && startX > endX + 20) {
      return `M ${startX} ${fromY} L ${endX} ${toY}`
    }
    // Need detour
    const detourY = fromY + rowHeight * 0.7
    return buildPath(startX, fromY, endX, toY, startSide, endSide, detourY, r, routeOffset)
  }
  
  // Finish-to-start forward
  if (startSide === 'right' && endSide === 'left' && startX < endX - 30) {
    const midX = startX + (endX - startX) / 2
    return `M ${startX} ${fromY} L ${midX} ${fromY} L ${midX} ${toY} L ${endX} ${toY}`
  }
  
  // Start-to-start or Finish-to-finish (same sides)
  if (startSide === endSide) {
    const offset = startSide === 'left' ? -routeOffset : routeOffset
    const turnX = startSide === 'left' 
      ? Math.min(startX, endX) - routeOffset - 10
      : Math.max(startX, endX) + routeOffset + 10
    
    return `M ${startX} ${fromY} L ${turnX} ${fromY} L ${turnX} ${toY} L ${endX} ${toY}`
  }
  
  // Start-to-finish
  if (startSide === 'left' && endSide === 'right') {
    const exitX = startX - routeOffset
    const entryX = endX + routeOffset
    const midY = goingDown 
      ? fromY + Math.abs(toY - fromY) / 2
      : fromY - Math.abs(toY - fromY) / 2
    
    return `M ${startX} ${fromY} L ${exitX} ${fromY} L ${exitX} ${midY} L ${entryX} ${midY} L ${entryX} ${toY} L ${endX} ${toY}`
  }
  
  // Finish-to-start backward
  if (startSide === 'right' && endSide === 'left') {
    const exitX = startX + routeOffset
    const entryX = endX - routeOffset
    const midY = goingDown 
      ? fromY + Math.abs(toY - fromY) / 2
      : fromY - Math.abs(toY - fromY) / 2
    
    return `M ${startX} ${fromY} L ${exitX} ${fromY} L ${exitX} ${midY} L ${entryX} ${midY} L ${entryX} ${toY} L ${endX} ${toY}`
  }
  
  return `M ${startX} ${fromY} L ${endX} ${toY}`
}

const buildPath = (x1, y1, x2, y2, side1, side2, midY, r, offset) => {
  const exit = side1 === 'right' ? x1 + offset : x1 - offset
  const entry = side2 === 'right' ? x2 + offset : x2 - offset
  return `M ${x1} ${y1} L ${exit} ${y1} L ${exit} ${midY} L ${entry} ${midY} L ${entry} ${y2} L ${x2} ${y2}`
}

// Handle clicks on container to deselect
const handleContainerClick = (event) => {
  if (event.target === containerRef.value || event.target.classList.contains('grid-background')) {
    if (!event.shiftKey) {
      selectedTaskIds.value.clear()
    }
  }
  connectionInfo.value = null
}

// Handle sidebar task click with shift
const handleSidebarTaskClick = (event, task) => {
  if (event.shiftKey) {
    if (selectedTaskIds.value.has(task.id)) {
      selectedTaskIds.value.delete(task.id)
    } else {
      selectedTaskIds.value.add(task.id)
    }
  } else {
    selectedTaskIds.value.clear()
    selectedTaskIds.value.add(task.id)
  }
}

// Handle task mousedown with shift for multi-select
const handleTaskMouseDown = (event, task) => {
  if (event.button !== 0) return
  
  if (event.shiftKey) {
    // Shift+click: add to selection
    selectedTaskIds.value.add(task.id)
  } else {
    // Regular click: toggle if already selected, otherwise select only this
    if (selectedTaskIds.value.has(task.id) && selectedTaskIds.value.size === 1) {
      // If this is the only selected task and we click it again - deselect
      selectedTaskIds.value.delete(task.id)
      return // Don't start drag
    } else if (!selectedTaskIds.value.has(task.id)) {
      // Clicking on unselected task - select only it
      selectedTaskIds.value.clear()
      selectedTaskIds.value.add(task.id)
    }
    // Start dragging all selected tasks
    startDrag(event, task)
  }
}

// Drag handling for multiple tasks
const startDrag = (event, task) => {
  draggingTask.value = task
  isDragging.value = true
  
  const taskEl = event.currentTarget
  const rect = taskEl.getBoundingClientRect()
  
  dragOffset.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
  
  // Store initial positions of all selected tasks
  dragStartPositions.value = {}
  selectedTaskIds.value.forEach(id => {
    const t = tasksMap.value.get(id)
    if (t) {
      dragStartPositions.value[id] = {
        start_date: new Date(t.start_date),
        end_date: new Date(t.end_date),
        row_index: t.row_index
      }
    }
  })
  
  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', stopDrag)
}

const handleDrag = (event) => {
  if (!draggingTask.value || !timelineRef.value) return
  
  const timelineRect = timelineRef.value.getBoundingClientRect()
  const scrollLeft = timelineRef.value.scrollLeft
  
  const newX = event.clientX - timelineRect.left + scrollLeft - dragOffset.value.x
  const newY = event.clientY - timelineRect.top - 60 - dragOffset.value.y
  
  // Calculate delta from original position of dragged task
  const originalPos = dragStartPositions.value[draggingTask.value.id]
  if (!originalPos) return
  
  const originalX = getDateOffset(originalPos.start_date)
  const originalRowIndex = originalPos.row_index
  
  const deltaX = newX - originalX
  const newRowIndex = Math.max(0, Math.round(newY / rowHeight))
  const deltaRow = newRowIndex - originalRowIndex
  
  // Update all selected tasks (live update - local only, no server sync)
  const updates = []
  selectedTaskIds.value.forEach(id => {
    const taskOriginal = dragStartPositions.value[id]
    if (!taskOriginal) return
    
    const task = tasksMap.value.get(id)
    const isChildTask = task && task.parent_id != null
    
    const duration = differenceInDays(taskOriginal.end_date, taskOriginal.start_date)
    
    let newStartDate
    const originalTaskX = getDateOffset(taskOriginal.start_date)
    const targetX = originalTaskX + deltaX
    
    switch (props.scale) {
      case 'week':
        newStartDate = addDays(dateRange.value.start, Math.round(targetX / cellWidth.value * 7))
        break
      case 'month':
        newStartDate = addDays(dateRange.value.start, Math.round(targetX / cellWidth.value * 30))
        break
      default:
        newStartDate = addDays(dateRange.value.start, Math.round(targetX / cellWidth.value))
    }
    
    const newEndDate = addDays(newStartDate, duration)
    // Child tasks don't change row_index (they're positioned relative to parent)
    const taskNewRowIndex = isChildTask ? taskOriginal.row_index : Math.max(0, taskOriginal.row_index + deltaRow)
    
    updates.push({
      id: id,
      start_date: newStartDate.toISOString(),
      end_date: newEndDate.toISOString(),
      row_index: taskNewRowIndex
    })
  })
  
  // Emit all updates at once for batch processing
  if (updates.length > 0) {
    emit('update-task-live', updates)
  }
}

const stopDrag = () => {
  // Emit final updates to save to server
  if (draggingTask.value && Object.keys(dragStartPositions.value).length > 0) {
    selectedTaskIds.value.forEach(id => {
      const task = tasksMap.value.get(id)
      if (task) {
        emit('update-task', {
          id: id,
          start_date: task.start_date,
          end_date: task.end_date,
          row_index: task.row_index
        })
      }
    })
  }
  
  draggingTask.value = null
  isDragging.value = false
  dragStartPositions.value = {}
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// Resize handling
const startResize = (event, task, direction) => {
  // Select only this task when resizing
  selectedTaskIds.value.clear()
  selectedTaskIds.value.add(task.id)
  
  resizingTask.value = task
  resizeDirection.value = direction
  
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
}

const handleResize = (event) => {
  if (!resizingTask.value || !timelineRef.value) return
  
  const timelineRect = timelineRef.value.getBoundingClientRect()
  const scrollLeft = timelineRef.value.scrollLeft
  const x = event.clientX - timelineRect.left + scrollLeft
  
  let newDate
  switch (props.scale) {
    case 'week':
      newDate = addDays(dateRange.value.start, Math.round(x / cellWidth.value * 7))
      break
    case 'month':
      newDate = addDays(dateRange.value.start, Math.round(x / cellWidth.value * 30))
      break
    default:
      newDate = addDays(dateRange.value.start, Math.round(x / cellWidth.value))
  }
  
  if (resizeDirection.value === 'left') {
    if (newDate < new Date(resizingTask.value.end_date)) {
      // Live update during resize (local only)
      emit('update-task-live', [{
        id: resizingTask.value.id,
        start_date: newDate.toISOString()
      }])
    }
  } else {
    if (newDate > new Date(resizingTask.value.start_date)) {
      // Live update during resize (local only)
      emit('update-task-live', [{
        id: resizingTask.value.id,
        end_date: newDate.toISOString()
      }])
    }
  }
}

const stopResize = () => {
  // Emit final update to save to server
  if (resizingTask.value) {
    const task = tasksMap.value.get(resizingTask.value.id)
    if (task) {
      emit('update-task', {
        id: task.id,
        start_date: task.start_date,
        end_date: task.end_date
      })
    }
  }
  
  resizingTask.value = null
  resizeDirection.value = null
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
}

// Connection creation
const startConnection = (event, task, type) => {
  connectingFrom.value = task
  connectingType.value = type
  
  document.addEventListener('mousemove', handleConnectionDrag)
  document.addEventListener('mouseup', stopConnection)
}

const handleConnectionDrag = (event) => {
  if (!connectingFrom.value || !timelineRef.value) return
  
  const timelineRect = timelineRef.value.getBoundingClientRect()
  const scrollLeft = timelineRef.value.scrollLeft
  const scrollTop = timelineRef.value.scrollTop
  
  const fromLeft = getDateOffset(connectingFrom.value.start_date)
  const fromRight = getDateOffset(connectingFrom.value.end_date)
  const fromY = connectingFrom.value.row_index * rowHeight + rowHeight / 2
  
  const startX = connectingType.value === 'start' ? fromLeft : fromRight
  const endX = event.clientX - timelineRect.left + scrollLeft
  const endY = event.clientY - timelineRect.top - 60 + scrollTop
  
  connectionPreview.value = `M ${startX} ${fromY} L ${endX} ${endY}`
}

const stopConnection = (event) => {
  if (connectingFrom.value && timelineRef.value) {
    const timelineRect = timelineRef.value.getBoundingClientRect()
    const scrollTop = timelineRef.value.scrollTop
    const y = event.clientY - timelineRect.top - 60 + scrollTop
    const targetRowIndex = Math.floor(y / rowHeight)
    
    const targetTask = sortedTasks.value.find(t => t.row_index === targetRowIndex)
    
    if (targetTask && targetTask.id !== connectingFrom.value.id) {
      emit('create-connection', {
        from_task_id: connectingFrom.value.id,
        to_task_id: targetTask.id,
        arrow_type: connectingType.value === 'start' ? 'start-to-start' : 'finish-to-start'
      })
    }
  }
  
  connectingFrom.value = null
  connectingType.value = null
  connectionPreview.value = null
  
  document.removeEventListener('mousemove', handleConnectionDrag)
  document.removeEventListener('mouseup', stopConnection)
}

const handleScroll = () => {
  connectionInfo.value = null
  hoveredConnectionId.value = null
}

const updateContainerHeight = () => {
  if (containerRef.value) {
    containerHeight.value = containerRef.value.clientHeight
  }
}

onMounted(() => {
  updateContainerHeight()
  window.addEventListener('resize', updateContainerHeight)
  
  if (todayOffset.value !== null && timelineRef.value) {
    timelineRef.value.scrollLeft = Math.max(0, todayOffset.value - 200)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', updateContainerHeight)
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
  document.removeEventListener('mousemove', handleConnectionDrag)
  document.removeEventListener('mouseup', stopConnection)
})
</script>

<style scoped>
.gantt-container {
  display: flex;
  height: 100%;
  background: var(--bg-primary);
  position: relative;
}

/* Sidebar */
.gantt-sidebar {
  width: var(--sidebar-width);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
}

.sidebar-header {
  height: 60px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-subtle);
  font-weight: 600;
  font-size: 14px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.task-count {
  background: var(--bg-tertiary);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  color: var(--accent-primary);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
}

.sidebar-task {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 16px 0 20px;
  border-left: 3px solid transparent;
  border-bottom: 1px solid var(--border-subtle);
  transition: all 0.15s ease;
  cursor: pointer;
}

.sidebar-task:hover {
  background: var(--bg-tertiary);
}

.sidebar-task.is-selected {
  background: rgba(0, 212, 170, 0.1);
  border-left-color: var(--accent-primary) !important;
}

/* Hierarchy styles for sidebar */
.sidebar-task.is-parent {
  background: var(--bg-tertiary);
}

.sidebar-task.is-child {
  background: rgba(255, 255, 255, 0.02);
  position: relative;
}

/* Visual connector line for child tasks in sidebar */
.sidebar-task.is-child::before {
  content: '';
  position: absolute;
  left: 24px;
  top: 0;
  bottom: 50%;
  width: 2px;
  background: var(--border-subtle);
}

.sidebar-task.is-child::after {
  content: '';
  position: absolute;
  left: 24px;
  top: 50%;
  width: 8px;
  height: 2px;
  background: var(--border-subtle);
}

.sidebar-task.is-expanded {
  border-bottom: none;
}

.expand-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  padding: 0;
  margin-right: 8px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.15s ease;
}

.expand-btn:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.expand-btn svg {
  transition: transform 0.2s ease;
}

.expand-btn svg.rotated {
  transform: rotate(90deg);
}

.parent-badge {
  display: inline-block;
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
  background: var(--accent-primary);
  color: var(--bg-primary);
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 6px;
  letter-spacing: 0.5px;
}

.task-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.task-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-dates {
  font-size: 11px;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.task-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.15s ease;
}

.sidebar-task:hover .task-actions {
  opacity: 1;
}

.action-btn {
  padding: 6px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-btn:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.action-btn.danger:hover {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}

.sidebar-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--text-muted);
  text-align: center;
  padding: 20px;
}

.sidebar-empty svg {
  margin-bottom: 16px;
  opacity: 0.5;
}

.sidebar-empty p {
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.sidebar-empty span {
  font-size: 12px;
}

/* Timeline */
.gantt-timeline {
  flex: 1;
  overflow: auto;
  position: relative;
}

.timeline-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  height: 60px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.time-unit {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-right: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.time-unit.is-today {
  background: rgba(0, 212, 170, 0.1);
}

.unit-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.unit-sublabel {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.timeline-body {
  position: relative;
}

.grid-background {
  position: absolute;
  top: 0;
  left: 0;
  background: var(--bg-primary);
}

/* Child group visual indicator */
.child-group-background {
  position: absolute;
  left: 0;
  background: rgba(255, 255, 255, 0.03);
  border-left: 4px solid transparent;
  pointer-events: none;
  z-index: 1;
}

.group-indicator {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  opacity: 0.6;
}

/* Inherited connection style (dashed) */
.connection-group.is-inherited .connection-path {
  stroke-dasharray: 6, 3;
  opacity: 0.7;
}

/* Grid */
.grid-lines {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}

.grid-line {
  stroke: var(--grid-line);
  stroke-width: 1;
}

.grid-line-strong {
  stroke: var(--grid-line-strong);
}

.today-line {
  stroke: var(--accent-primary);
  stroke-width: 2;
  stroke-dasharray: 4, 4;
}

/* Connections */
.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 2;
}

.connection-group {
  pointer-events: all;
}

.connection-path {
  transition: stroke-width 0.1s ease;
  pointer-events: none;
}

.connection-group.is-hovered .connection-path {
  stroke-width: 3;
}

/* Task Bars */
.task-bar {
  position: absolute;
  height: 32px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  cursor: grab;
  overflow: visible;
  transition: box-shadow 0.15s ease;
  user-select: none;
  z-index: 3;
}

.task-bar:hover {
  box-shadow: 0 0 0 2px var(--task-color), var(--shadow-md);
  z-index: 5;
}

.task-bar.is-selected {
  box-shadow: 0 0 0 2px var(--accent-primary);
  z-index: 6;
}

.task-bar.is-dragging {
  cursor: grabbing;
  box-shadow: 0 0 0 2px var(--accent-primary), var(--shadow-lg);
  z-index: 100;
  opacity: 0.9;
}

.task-bar.is-connecting {
  box-shadow: 0 0 0 2px var(--accent-primary), var(--shadow-glow);
}

/* Parent task bar (thin line style when expanded) */
.task-bar-parent {
  position: absolute;
  height: 12px;
  background: transparent;
  border: none;
  border-radius: 0;
  cursor: pointer;
  overflow: visible;
  user-select: none;
  z-index: 4;
}

.task-bar-parent:hover {
  z-index: 6;
}

.parent-task-line {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 6px;
  transform: translateY(-50%);
  border-radius: 3px;
  opacity: 0.8;
  display: flex;
  align-items: center;
  padding-left: 8px;
}

.parent-task-title {
  font-size: 10px;
  font-weight: 600;
  color: var(--bg-primary);
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

/* Collapsed parent indicator */
.task-bar.is-parent-collapsed {
  border: 2px solid var(--task-color);
}

.parent-indicator {
  font-size: 8px;
  margin-right: 4px;
  opacity: 0.7;
}

.expand-toggle-btn {
  background: none;
  border: none;
  color: white;
  font-size: 10px;
  padding: 0 4px;
  margin-right: 4px;
  cursor: pointer;
  opacity: 0.8;
  transition: opacity 0.15s, transform 0.15s;
}

.expand-toggle-btn:hover {
  opacity: 1;
  transform: scale(1.2);
}

/* Child task visual styling */
.task-bar.is-child-task {
  border-left: 3px solid var(--task-color);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}

.task-bar.is-child-task::before {
  content: '';
  position: absolute;
  left: -12px;
  top: 50%;
  width: 9px;
  height: 2px;
  background: var(--task-color);
  opacity: 0.5;
}

.task-progress {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  opacity: 0.3;
  border-radius: var(--radius-md) 0 0 var(--radius-md);
}

.task-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 10px;
  gap: 8px;
  overflow: hidden;
}

.task-bar-title {
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.task-bar-progress {
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--text-secondary);
  flex-shrink: 0;
}

/* Floating label - shows on hover when text overflows */
.task-floating-label {
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  margin-left: 8px;
  padding: 4px 10px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s ease;
  z-index: 100;
  box-shadow: var(--shadow-md);
}

.task-bar:hover .task-floating-label {
  opacity: 1;
}

/* Connection handles */
.connection-handle {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 12px;
  height: 12px;
  background: var(--bg-secondary);
  border: 2px solid var(--accent-primary);
  border-radius: 50%;
  cursor: crosshair;
  opacity: 0;
  transition: opacity 0.15s ease, transform 0.15s ease;
  z-index: 10;
}

.task-bar:hover .connection-handle {
  opacity: 1;
}

.connection-handle:hover {
  transform: translateY(-50%) scale(1.2);
  background: var(--accent-primary);
}

.handle-left {
  left: -6px;
}

.handle-right {
  right: -6px;
}

/* Resize handles */
.resize-handle {
  position: absolute;
  top: 0;
  width: 8px;
  height: 100%;
  cursor: ew-resize;
  z-index: 5;
}

.resize-left {
  left: 0;
}

.resize-right {
  right: 0;
}

.resize-handle:hover {
  background: rgba(0, 212, 170, 0.2);
}

/* Connection Info Popup */
.connection-popup {
  position: absolute;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  min-width: 220px;
  z-index: 1000;
  overflow: hidden;
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-subtle);
  font-weight: 600;
  font-size: 13px;
}

.popup-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.popup-close:hover {
  color: var(--text-primary);
}

.popup-content {
  padding: 12px 16px;
}

.popup-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.popup-row:last-child {
  margin-bottom: 0;
}

.popup-label {
  font-size: 12px;
  color: var(--text-muted);
  min-width: 40px;
}

.popup-value {
  font-size: 13px;
  font-weight: 500;
}

.popup-footer {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-subtle);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-danger {
  background: var(--danger);
  color: white;
  border: none;
}

.btn-danger:hover {
  opacity: 0.9;
}

/* Selection indicator */
.selection-indicator {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-elevated);
  border: 1px solid var(--accent-primary);
  color: var(--text-primary);
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-size: 12px;
  font-weight: 500;
  z-index: 1000;
  box-shadow: var(--shadow-md);
}

/* Popup animation */
.popup-enter-active,
.popup-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.popup-enter-from,
.popup-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
