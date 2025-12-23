<template>
  <Transition name="fade">
    <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>{{ $t('connectionModal.title') }}</h2>
          <button class="btn btn-icon" @click="$emit('close')">
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
              <div class="color-preview" :style="{ backgroundColor: form.arrow_color }"></div>
              <input v-model="form.arrow_color" type="color" />
              <input v-model="form.arrow_color" type="text" style="flex: 1" />
            </div>
          </div>
          
          <div class="form-group">
            <label>{{ $t('connectionModal.lineStyle') }}</label>
            <select v-model="form.arrow_style">
              <option value="solid">{{ $t('connectionModal.solid') }}</option>
              <option value="dashed">{{ $t('connectionModal.dashed') }}</option>
              <option value="dotted">{{ $t('connectionModal.dotted') }}</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>{{ $t('connectionModal.connectionType') }}</label>
            <select v-model="form.arrow_type">
              <option value="finish-to-start">{{ $t('connectionTypes.finishToStart') }}</option>
              <option value="start-to-start">{{ $t('connectionTypes.startToStart') }}</option>
              <option value="finish-to-finish">{{ $t('connectionTypes.finishToFinish') }}</option>
              <option value="start-to-finish">{{ $t('connectionTypes.startToFinish') }}</option>
            </select>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="$emit('close')">{{ $t('taskModal.cancel') }}</button>
          <button class="btn btn-primary" @click="$emit('save', form)">{{ $t('taskModal.save') }}</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  show: Boolean,
  editingConnection: Object
})

const emit = defineEmits(['close', 'save'])

const form = ref({
  arrow_color: '#666666',
  arrow_style: 'solid',
  arrow_type: 'finish-to-start'
})

// Reset form when modal opens or editingConnection changes
watch(() => props.show, (newVal) => {
  if (newVal && props.editingConnection) {
    form.value = {
      arrow_color: props.editingConnection.arrow_color,
      arrow_style: props.editingConnection.arrow_style,
      arrow_type: props.editingConnection.arrow_type
    }
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

.modal-sm {
  max-width: 400px;
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

