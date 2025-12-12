# Statistics API Documentation

## Overview

Statistics API provides endpoints for tracking and analyzing user focus sessions, including hourly patterns, monthly comparisons, and goal achievement tracking.

## Base URL

```
/api/v1/stats
```

---

## Endpoints

### 1. Record Session

Record a completed pomodoro session.

```http
POST /stats/session
Content-Type: application/json

{
  "user_id": "uuid",
  "room_id": "uuid",
  "session_type": "work",  // or "break"
  "duration_minutes": 25
}
```

**Response 201:**
```json
{
  "status": "recorded",
  "session_id": "uuid"
}
```

---

### 2. Get User Statistics

Get user statistics for a date range or last N days.

```http
GET /stats/user/{user_id}?days=7
GET /stats/user/{user_id}?start_date=2024-01-01&end_date=2024-01-31
```

**Query Parameters:**
- `days` (optional, default: 7): Number of days to look back (1-365)
- `start_date` (optional): Start date in ISO format (YYYY-MM-DD)
- `end_date` (optional): End date in ISO format (YYYY-MM-DD)

**Response 200:**
```json
{
  "total_focus_time": 1250,  // minutes
  "total_sessions": 50,
  "average_session": 25,  // minutes
  "sessions": [
    {
      "session_id": "uuid",
      "user_id": "uuid",
      "room_id": "uuid",
      "session_type": "work",
      "duration_minutes": 25,
      "completed_at": "2024-01-15T10:30:00Z",
      "room_name": "Study Room 1"
    }
  ]
}
```

---

### 3. Get Hourly Pattern

Get hourly focus pattern for radar chart (우선순위 3: 시간대별 집중 패턴).

```http
GET /stats/user/{user_id}/hourly-pattern?days=30
```

**Query Parameters:**
- `days` (optional, default: 30): Number of days to analyze (1-365)

**Response 200:**
```json
{
  "hourly_focus_time": [0, 0, 0, 0, 0, 0, 0, 15, 45, 60, 45, 30, 25, 30, 45, 60, 45, 30, 25, 15, 0, 0, 0, 0],
  "total_days": 30,
  "peak_hour": 9  // Hour with most focus time (0-23)
}
```

**Note:** `hourly_focus_time` is an array of 24 integers representing focus time (in minutes) for each hour (0-23).

---

### 4. Get Monthly Comparison

Get monthly comparison data for line chart (우선순위 3: 월별 비교).

```http
GET /stats/user/{user_id}/monthly-comparison?months=6
```

**Query Parameters:**
- `months` (optional, default: 6): Number of months to compare (1-24)

**Response 200:**
```json
{
  "monthly_data": [
    {
      "month": "2024-01",
      "focus_time_minutes": 1250,
      "focus_time_hours": 20.83,
      "sessions": 50,
      "break_time_minutes": 250,
      "average_session": 25
    },
    {
      "month": "2024-02",
      "focus_time_minutes": 1500,
      "focus_time_hours": 25.0,
      "sessions": 60,
      "break_time_minutes": 300,
      "average_session": 25
    }
  ],
  "total_months": 2
}
```

---

### 5. Get Goal Achievement

Get goal achievement rate for progress ring (우선순위 3: 목표 달성률).

```http
GET /stats/user/{user_id}/goal-achievement?goal_type=focus_time&goal_value=120&period=week
```

**Query Parameters:**
- `goal_type` (required): Type of goal - `focus_time` or `sessions`
- `goal_value` (required): Target value for the goal (must be > 0)
- `period` (optional, default: "week"): Time period - `day`, `week`, or `month`

**Response 200:**
```json
{
  "goal_type": "focus_time",
  "goal_value": 120,  // minutes
  "current_value": 90,  // minutes
  "achievement_rate": 75,  // percentage (0-100)
  "period": "week",
  "is_achieved": false,
  "remaining": 30  // minutes remaining to reach goal
}
```

**Example for sessions goal:**
```http
GET /stats/user/{user_id}/goal-achievement?goal_type=sessions&goal_value=10&period=week
```

**Response 200:**
```json
{
  "goal_type": "sessions",
  "goal_value": 10,
  "current_value": 8,
  "achievement_rate": 80,
  "period": "week",
  "is_achieved": false,
  "remaining": 2
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid date format. Use ISO format (YYYY-MM-DD)"
}
```

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to retrieve stats: <error message>"
}
```

---

## Usage Examples

### Date Range Filtering (우선순위 2: 날짜 범위 선택)

```bash
# Get stats for specific date range
curl -X GET "http://localhost:8000/api/v1/stats/user/{user_id}?start_date=2024-01-01&end_date=2024-01-31"
```

### Hourly Pattern for Radar Chart

```bash
# Get hourly pattern for last 30 days
curl -X GET "http://localhost:8000/api/v1/stats/user/{user_id}/hourly-pattern?days=30"
```

### Monthly Comparison for Line Chart

```bash
# Get monthly comparison for last 6 months
curl -X GET "http://localhost:8000/api/v1/stats/user/{user_id}/monthly-comparison?months=6"
```

### Goal Achievement for Progress Ring

```bash
# Get weekly focus time goal achievement
curl -X GET "http://localhost:8000/api/v1/stats/user/{user_id}/goal-achievement?goal_type=focus_time&goal_value=120&period=week"

# Get daily sessions goal achievement
curl -X GET "http://localhost:8000/api/v1/stats/user/{user_id}/goal-achievement?goal_type=sessions&goal_value=5&period=day"
```

---

## Notes

- All timestamps are in ISO 8601 format with UTC timezone
- Focus time is measured in minutes
- Date ranges are inclusive (start_date and end_date are both included)
- Hourly pattern uses 24-hour format (0-23)
- Monthly data is sorted chronologically
- Goal achievement rate is capped at 100%

