/**
 * Composable for handling security confirmation dialogs
 */
import { ref } from 'vue';

export interface SecurityConfirmOptions {
  command: string;
  riskLevel: 'safe' | 'low' | 'medium' | 'high' | 'critical';
  warnings?: string[];
  requiresElevation?: boolean;
  requiresConfirmation?: boolean;
}

export function useSecurityConfirm() {
  const showDialog = ref(false);
  const currentOptions = ref<SecurityConfirmOptions | null>(null);
  const resolveCallback = ref<((confirmed: boolean) => void) | null>(null);

  /**
   * Show security confirmation dialog
   * Returns a promise that resolves to true if confirmed, false if cancelled
   */
  function confirm(options: SecurityConfirmOptions): Promise<boolean> {
    return new Promise((resolve) => {
      currentOptions.value = options;
      showDialog.value = true;
      resolveCallback.value = resolve;
    });
  }

  /**
   * Handle confirmation
   */
  function handleConfirm() {
    showDialog.value = false;
    if (resolveCallback.value) {
      resolveCallback.value(true);
      resolveCallback.value = null;
    }
    currentOptions.value = null;
  }

  /**
   * Handle cancellation
   */
  function handleCancel() {
    showDialog.value = false;
    if (resolveCallback.value) {
      resolveCallback.value(false);
      resolveCallback.value = null;
    }
    currentOptions.value = null;
  }

  /**
   * Check if command needs confirmation based on risk level
   */
  function needsConfirmation(riskLevel: string, requiresConfirmation: boolean): boolean {
    // Always confirm for high and critical risk
    if (riskLevel === 'high' || riskLevel === 'critical') {
      return true;
    }
    
    // Confirm if explicitly required
    if (requiresConfirmation) {
      return true;
    }
    
    return false;
  }

  return {
    showDialog,
    currentOptions,
    confirm,
    handleConfirm,
    handleCancel,
    needsConfirmation
  };
}
