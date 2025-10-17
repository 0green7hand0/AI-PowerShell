# History API Quick Reference Guide

## Overview
The History API provides endpoints for managing command execution history, including listing, searching, viewing details, and deleting history records.

## Base URL
```
http://localhost:5000/api/history
```

## Endpoints

### 1. List History (with Pagination & Search)

**GET** `/api/history`

#### Query Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number (1-indexed) |
| limit | integer | 20 | Items per page |
| search | string | - | Search keyword (case-insensitive) |

#### Example Requests
```bash
# Get first page (default 20 items)
curl http://localhost:5000/api/history

# Get specific page with custom limit
curl "http://localhost:5000/api/history?page=2&limit=10"

# Search for specific keyword
curl "http://localhost:5000/api/history?search=CPU"

# Combine pagination and search
curl "http://localhost:5000/api/history?page=1&limit=5&search=Get-Process"
```

#### Response
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "hist_20250108103000",
        "user_input": "显示CPU使用率最高的5个进程",
        "command": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5",
        "success": true,
        "output": "ProcessName    CPU\n-----------    ---\nchrome.exe     45.2",
        "error": null,
        "execution_time": 0.234,
        "timestamp": "2025-10-08T10:30:00"
      }
    ],
    "total": 25,
    "page": 1,
    "limit": 20
  }
}
```

---

### 2. Get History Detail

**GET** `/api/history/:id`

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | History item ID |

#### Example Request
```bash
curl http://localhost:5000/api/history/hist_20250108103000
```

#### Response
```json
{
  "success": true,
  "data": {
    "id": "hist_20250108103000",
    "user_input": "显示当前时间",
    "command": "Get-Date",
    "success": true,
    "output": "2025-10-08 10:30:00",
    "error": null,
    "execution_time": 0.123,
    "timestamp": "2025-10-08T10:30:00"
  }
}
```

#### Error Response (404)
```json
{
  "success": false,
  "error": {
    "message": "History item not found: hist_invalid",
    "code": 404
  }
}
```

---

### 3. Delete History Item

**DELETE** `/api/history/:id`

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | History item ID to delete |

#### Example Request
```bash
curl -X DELETE http://localhost:5000/api/history/hist_20250108103000
```

#### Response
```json
{
  "success": true,
  "message": "History item hist_20250108103000 deleted successfully"
}
```

#### Error Response (404)
```json
{
  "success": false,
  "error": {
    "message": "History item not found: hist_invalid",
    "code": 404
  }
}
```

---

### 4. Clear All History

**DELETE** `/api/history`

#### Example Request
```bash
curl -X DELETE http://localhost:5000/api/history
```

#### Response
```json
{
  "success": true,
  "message": "All history cleared successfully"
}
```

---

## Data Models

### HistoryItem
```typescript
interface HistoryItem {
  id: string;                    // Unique identifier
  user_input: string;            // Original user input in natural language
  command: string;               // Translated PowerShell command
  success: boolean;              // Whether execution was successful
  output: string | null;         // Command output (if successful)
  error: string | null;          // Error message (if failed)
  execution_time: number;        // Execution time in seconds
  timestamp: string;             // ISO 8601 timestamp
}
```

### HistoryListResponse
```typescript
interface HistoryListResponse {
  items: HistoryItem[];          // Array of history items
  total: number;                 // Total number of items (before pagination)
  page: number;                  // Current page number
  limit: number;                 // Items per page
}
```

---

## Features

### Pagination
- Default page size: 20 items
- Configurable via `limit` parameter
- Returns total count for UI pagination controls
- Efficient for large datasets

### Search
- Case-insensitive keyword search
- Searches across both `user_input` and `command` fields
- Filters results before pagination
- Example: `search=CPU` matches "显示CPU使用率" and "Get-Process"

### Sorting
- Automatic sorting by timestamp
- Newest items appear first (descending order)
- Consistent across all requests

### ID Generation
- Automatic ID generation for legacy items
- Format: `hist_<timestamp_without_special_chars>`
- IDs are preserved across operations

---

## Error Handling

### HTTP Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 404 | History item not found |
| 500 | Internal server error |

### Error Response Format
```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "code": 500
  }
}
```

---

## Usage Examples

### JavaScript/TypeScript (Axios)
```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

// Get history list
async function getHistory(page = 1, limit = 20, search = '') {
  const params = { page, limit };
  if (search) params.search = search;
  
  const response = await axios.get(`${API_BASE}/history`, { params });
  return response.data;
}

// Get history detail
async function getHistoryDetail(id: string) {
  const response = await axios.get(`${API_BASE}/history/${id}`);
  return response.data;
}

// Delete history item
async function deleteHistory(id: string) {
  const response = await axios.delete(`${API_BASE}/history/${id}`);
  return response.data;
}

// Clear all history
async function clearAllHistory() {
  const response = await axios.delete(`${API_BASE}/history`);
  return response.data;
}
```

### Python (requests)
```python
import requests

API_BASE = 'http://localhost:5000/api'

# Get history list
def get_history(page=1, limit=20, search=''):
    params = {'page': page, 'limit': limit}
    if search:
        params['search'] = search
    
    response = requests.get(f'{API_BASE}/history', params=params)
    return response.json()

# Get history detail
def get_history_detail(history_id):
    response = requests.get(f'{API_BASE}/history/{history_id}')
    return response.json()

# Delete history item
def delete_history(history_id):
    response = requests.delete(f'{API_BASE}/history/{history_id}')
    return response.json()

# Clear all history
def clear_all_history():
    response = requests.delete(f'{API_BASE}/history')
    return response.json()
```

---

## Testing

### Run Unit Tests
```bash
cd web-ui/backend
python -m pytest tests/test_history_api.py -v
```

### Run Manual Verification
```bash
cd web-ui/backend
python verify_history_api.py
```

---

## Integration with Frontend

### Recommended Pinia Store Structure
```typescript
// stores/history.ts
import { defineStore } from 'pinia';
import { getHistory, getHistoryDetail, deleteHistory } from '@/api/history';

export const useHistoryStore = defineStore('history', {
  state: () => ({
    items: [],
    total: 0,
    currentPage: 1,
    pageSize: 20,
    searchQuery: '',
    loading: false,
  }),
  
  actions: {
    async fetchHistory(page?: number) {
      this.loading = true;
      try {
        const response = await getHistory(
          page || this.currentPage,
          this.pageSize,
          this.searchQuery
        );
        
        if (response.success) {
          this.items = response.data.items;
          this.total = response.data.total;
          this.currentPage = response.data.page;
        }
      } finally {
        this.loading = false;
      }
    },
    
    async searchHistory(query: string) {
      this.searchQuery = query;
      this.currentPage = 1;
      await this.fetchHistory();
    },
    
    async deleteHistoryItem(id: string) {
      const response = await deleteHistory(id);
      if (response.success) {
        await this.fetchHistory();
      }
      return response;
    },
  },
});
```

---

## Performance Considerations

### Optimization Tips
1. Use pagination to limit data transfer
2. Implement debouncing for search input
3. Cache results when appropriate
4. Use virtual scrolling for large lists

### Expected Response Times
- List history: < 100ms (typical dataset)
- Get detail: < 50ms
- Delete item: < 200ms (includes save)
- Clear all: < 100ms

---

## Security Notes

1. **CORS**: Configured to allow requests from frontend (localhost:5173, localhost:3000)
2. **Input Validation**: All parameters are validated
3. **Error Messages**: No sensitive information exposed
4. **Logging**: All operations are logged for audit

---

## Troubleshooting

### Common Issues

**Issue**: "History item not found"
- **Cause**: Invalid or non-existent history ID
- **Solution**: Verify the ID exists by listing history first

**Issue**: Empty history list
- **Cause**: No commands have been executed yet
- **Solution**: Execute some commands via the command API first

**Issue**: Search returns no results
- **Cause**: No matching items or typo in search query
- **Solution**: Try broader search terms or check spelling

**Issue**: Connection refused
- **Cause**: Backend server not running
- **Solution**: Start the Flask server: `python app.py`

---

## Support

For issues or questions:
1. Check the verification report: `TASK_2.4_VERIFICATION.md`
2. Review the implementation summary: `TASK_2.4_SUMMARY.md`
3. Run the verification script: `python verify_history_api.py`
4. Check server logs for error details

---

## Version
- API Version: 1.0.0
- Last Updated: 2025-10-08
- Status: Production Ready
