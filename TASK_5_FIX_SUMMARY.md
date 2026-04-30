# Task 5: Fix Delete Command and Enable Sandbox Execution

## Problem Summary
1. **Incomplete delete command**: Generated `Remove-Item -Path "面NewFolder"` instead of full path `C:\Users\30779\Desktop\NewFolder`
2. **No sandbox indicator**: Delete commands marked as CRITICAL risk didn't show sandbox execution indicator in UI
3. **Regex pattern bug**: Pattern `r'删除(.+?)(的)?([^\s]+)(文件夹|目录)'` incorrectly captured "桌" as location and "面NewFolder" as folder name

## Root Cause Analysis

### Issue 1: Regex Pattern Bug
The pattern `r'删除(.+?)(的)?([^\s]+)(文件夹|目录)'` used non-greedy `(.+?)` which matched as few characters as possible:
- Input: "删除桌面NewFolder文件夹"
- Captured: Group 1="桌", Group 2=None, Group 3="面NewFolder", Group 4="文件夹"
- Expected: Group 1="桌面", Group 2=None, Group 3="NewFolder", Group 4="文件夹"

### Issue 2: Missing Sandbox Indicator in Frontend
- Backend was correctly executing commands in sandbox and returning `sandbox: true`
- Frontend TypeScript interfaces didn't include `sandbox` field
- UI component didn't display sandbox indicator

## Solutions Implemented

### 1. Fixed Regex Pattern (src/ai_engine/translation.py)
**Before:**
```python
r'删除(.+?)(的)?([^\s]+)(文件夹|目录)': (
    'SPECIAL:delete_folder_at_location',
    '删除指定位置的文件夹',
    0.92
),
```

**After:**
```python
r'删除(桌面|文档|下载|图片|音乐|视频)(\S+)(文件夹|目录)': (
    'SPECIAL:delete_folder_at_location',
    '删除指定位置的文件夹',
    0.95
),
```

**Changes:**
- Replaced `(.+?)` with explicit location keywords `(桌面|文档|下载|图片|音乐|视频)`
- Removed optional `(的)?` group (not needed)
- Changed `([^\s]+)` to `(\S+)` for folder name (more concise)
- Increased confidence from 0.92 to 0.95 (more specific pattern)

### 2. Updated Handler Function (src/ai_engine/translation.py)
**Before:**
```python
# 提取位置（第一个捕获组）
location = match.group(1).strip() if len(match.groups()) >= 1 else ''
# 提取文件夹名称（第三个捕获组）
folder_name = match.group(3).strip() if len(match.groups()) >= 3 else ''
```

**After:**
```python
# 提取位置（第一个捕获组）
location = match.group(1).strip() if len(match.groups()) >= 1 else ''
# 提取文件夹名称（第二个捕获组）
folder_name = match.group(2).strip() if len(match.groups()) >= 2 else ''
```

**Changes:**
- Updated to use group(2) instead of group(3) for folder name (matches new regex)

### 3. Added Sandbox Field to TypeScript Interfaces

#### web-ui/src/api/command.ts
```typescript
export interface ExecuteRequest {
  command: string
  sessionId: string
  timeout?: number
  risk_level?: string  // Added
}

export interface ExecuteResponse {
  success: boolean
  data: {
    output: string | null
    error: string | null
    executionTime: number
    returnCode: number
    sandbox?: boolean  // Added
  }
}
```

#### web-ui/src/stores/chat.ts
```typescript
export interface Message {
  // ... other fields
  result?: {
    output: string
    error: string | null
    executionTime: number
    success: boolean
    sandbox?: boolean  // Added
  }
}
```

### 4. Updated Chat Store to Pass Risk Level (web-ui/src/stores/chat.ts)
```typescript
// Get risk level from the message if available
let riskLevel: string | undefined
if (messageId) {
  const message = messages.value.find((m) => m.id === messageId)
  if (message?.command?.security?.level) {
    riskLevel = message.command.security.level
  }
}

// Call execute API with risk level
const response = await commandApi.execute({
  command,
  sessionId: sessionId.value,
  timeout: 30,
  risk_level: riskLevel  // Pass risk level to backend
})
```

### 5. Added Sandbox Indicator to UI (web-ui/src/components/MessageCard.vue)

**Added Import:**
```typescript
import { User, Cpu, Warning, InfoFilled, DocumentCopy, Lock } from '@element-plus/icons-vue'
```

**Added UI Element:**
```vue
<div class="result-header">
  <el-icon :class="props.message.result?.success ? 'success-icon' : 'error-icon'">
    {{ props.message.result?.success ? '✓' : '✗' }}
  </el-icon>
  <span class="result-title">
    {{ props.message.result?.success ? '执行成功' : '执行失败' }}
  </span>
  <!-- NEW: Sandbox indicator -->
  <el-tag v-if="props.message.result?.sandbox" type="info" size="small" class="sandbox-tag">
    <el-icon><Lock /></el-icon>
    沙箱执行
  </el-tag>
  <span class="result-time">{{ props.message.result?.executionTime.toFixed(3) }}s</span>
</div>
```

**Added Styling:**
```css
.sandbox-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
  margin-right: var(--space-2);
}

.sandbox-tag .el-icon {
  font-size: 12px;
}
```

## Expected Behavior After Fix

### Test Case: "删除桌面NewFolder文件夹"

**Translation Phase:**
- Regex matches: Group 1="桌面", Group 2="NewFolder", Group 3="文件夹"
- Generated command: `Remove-Item -Path "C:\Users\30779\Desktop\NewFolder" -Recurse -Force`
- Risk level: CRITICAL
- Confidence: 95%

**Execution Phase:**
- Backend detects CRITICAL risk level
- Command executes in Docker sandbox (PowerShell container)
- Backend logs: `[沙箱执行] 命令: Remove-Item -Path "C:\Users\30779\Desktop\NewFolder" -Recurse -Force`
- Response includes: `sandbox: true`

**UI Display:**
- Command card shows: "严重风险" badge
- Execution result shows: "✓ 执行成功" with "🔒 沙箱执行" tag
- Execution time displayed

## Files Modified

1. **src/ai_engine/translation.py**
   - Fixed regex pattern for delete folder rule
   - Updated `_handle_delete_folder_at_location()` to use correct group index

2. **web-ui/src/api/command.ts**
   - Added `risk_level` to ExecuteRequest interface
   - Added `sandbox` to ExecuteResponse interface

3. **web-ui/src/stores/chat.ts**
   - Added `sandbox` to Message.result interface
   - Updated `executeCommand()` to extract and pass risk_level
   - Updated result objects to include sandbox field

4. **web-ui/src/components/MessageCard.vue**
   - Added Lock icon import
   - Added sandbox indicator tag in result header
   - Added CSS styling for sandbox tag

## Testing Checklist

- [ ] Test "删除桌面NewFolder文件夹" generates correct path
- [ ] Verify CRITICAL risk commands show sandbox indicator
- [ ] Check backend logs show `[沙箱执行]` marker
- [ ] Verify Docker container is created during execution
- [ ] Test other locations: 文档, 下载, 图片, 音乐, 视频
- [ ] Verify LOW/MEDIUM risk commands don't use sandbox
- [ ] Check sandbox indicator appears in UI for high-risk commands

## Next Steps

1. Restart backend and frontend servers to apply changes
2. Test delete command with various inputs
3. Monitor backend logs for sandbox execution
4. Verify UI displays sandbox indicator correctly
5. Test with Docker Desktop running
