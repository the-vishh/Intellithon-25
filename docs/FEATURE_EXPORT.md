# 📊 Export Analytics Feature

## Overview

Allow users to download their personal analytics data in JSON or CSV format.

## Backend Implementation

### Add Export Endpoint

File: `backend/src/handlers/user_analytics.rs`

```rust
use actix_web::http::header;

/// GET /api/user/{user_id}/export?format=json|csv
/// Export user's complete analytics data
pub async fn export_analytics(
    pool: web::Data<DbPool>,
    user_id_path: web::Path<Uuid>,
    query: web::Query<ExportQuery>,
) -> ActixResult<HttpResponse> {
    let user_id = *user_id_path;
    let format = query.format.as_deref().unwrap_or("json");

    let result = web::block(move || {
        let mut conn = pool.get().map_err(|e| {
            diesel::result::Error::DatabaseError(
                diesel::result::DatabaseErrorKind::UnableToSendCommand,
                Box::new(format!("{}", e)),
            )
        })?;

        // Get all user data
        let activities: Vec<UserActivity> = user_activity::table
            .filter(user_activity::user_id.eq(user_id))
            .order(user_activity::timestamp.desc())
            .load::<UserActivity>(&mut conn)?;

        let threat_stats = user_threat_stats::table
            .filter(user_threat_stats::user_id.eq(user_id))
            .first::<UserThreatStats>(&mut conn)
            .optional()?;

        let threat_sources: Vec<UserThreatSource> = user_threat_sources::table
            .filter(user_threat_sources::user_id.eq(user_id))
            .order(user_threat_sources::threat_count.desc())
            .load::<UserThreatSource>(&mut conn)?;

        let device_metrics: Vec<DeviceMetrics> = device_metrics::table
            .filter(device_metrics::user_id.eq(user_id))
            .order(device_metrics::last_updated.desc())
            .load::<DeviceMetrics>(&mut conn)?;

        Ok::<_, diesel::result::Error>(ExportData {
            activities,
            threat_stats,
            threat_sources,
            device_metrics,
        })
    }).await
    .map_err(|e| actix_web::error::ErrorInternalServerError(format!("Database error: {}", e)))?;

    let export_data = result
        .map_err(|e| actix_web::error::ErrorInternalServerError(format!("Query error: {}", e)))?;

    match format {
        "csv" => {
            let csv_content = export_to_csv(&export_data);
            Ok(HttpResponse::Ok()
                .content_type("text/csv")
                .insert_header((
                    header::CONTENT_DISPOSITION,
                    format!("attachment; filename=\"phishguard_analytics_{}.csv\"", user_id),
                ))
                .body(csv_content))
        }
        "json" | _ => {
            Ok(HttpResponse::Ok()
                .content_type("application/json")
                .insert_header((
                    header::CONTENT_DISPOSITION,
                    format!("attachment; filename=\"phishguard_analytics_{}.json\"", user_id),
                ))
                .json(export_data))
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct ExportQuery {
    pub format: Option<String>,  // "json" or "csv"
}

#[derive(Debug, Serialize)]
pub struct ExportData {
    pub activities: Vec<UserActivity>,
    pub threat_stats: Option<UserThreatStats>,
    pub threat_sources: Vec<UserThreatSource>,
    pub device_metrics: Vec<DeviceMetrics>,
}

fn export_to_csv(data: &ExportData) -> String {
    let mut csv = String::from("Export Type,Timestamp,Data\n");

    // Activities
    for activity in &data.activities {
        csv.push_str(&format!(
            "Activity,{},\"{}\",{},{},{}\n",
            activity.timestamp,
            activity.encrypted_domain,
            activity.is_phishing,
            activity.threat_type.as_deref().unwrap_or("N/A"),
            activity.confidence.unwrap_or(0.0)
        ));
    }

    // Threat stats
    if let Some(stats) = &data.threat_stats {
        csv.push_str(&format!(
            "ThreatStats,{},Phishing:{},Malware:{},Crypto:{},Total:{}\n",
            stats.updated_at,
            stats.phishing_count,
            stats.malware_count,
            stats.cryptojacking_count,
            stats.total_blocked
        ));
    }

    // Geographic sources
    for source in &data.threat_sources {
        csv.push_str(&format!(
            "ThreatSource,{},{},{},{}\n",
            source.last_seen,
            source.country_code.as_deref().unwrap_or("Unknown"),
            source.country_name.as_deref().unwrap_or("Unknown"),
            source.threat_count
        ));
    }

    csv
}
```

### Add Route

File: `backend/src/main.rs`

```rust
.service(
    web::scope("/api")
        // ... existing routes ...
        .route("/user/{user_id}/export", web::get().to(handlers::user_analytics::export_analytics))
)
```

## Frontend Implementation

### Add Export Buttons to Popup

File: `popup-enhanced.html`

```html
<div class="export-section">
  <h3>📊 Export Your Data</h3>
  <div class="export-buttons">
    <button id="export-json" class="btn btn-primary">
      <span class="btn-icon">📄</span>
      Export JSON
    </button>
    <button id="export-csv" class="btn btn-secondary">
      <span class="btn-icon">📊</span>
      Export CSV
    </button>
    <button id="export-delete" class="btn btn-danger">
      <span class="btn-icon">🗑️</span>
      Delete All Data
    </button>
  </div>
  <div class="export-info">
    <small>Your data is encrypted. Export includes ciphertext only.</small>
  </div>
</div>
```

### Add Export Logic

File: `popup-enhanced.js`

```javascript
// Add to setupEventListeners()
function setupEventListeners() {
  // ... existing listeners ...

  // Export JSON
  document.getElementById("export-json").addEventListener("click", async () => {
    await exportData("json");
  });

  // Export CSV
  document.getElementById("export-csv").addEventListener("click", async () => {
    await exportData("csv");
  });

  // Delete all data
  document
    .getElementById("export-delete")
    .addEventListener("click", async () => {
      await deleteAllData();
    });
}

async function exportData(format) {
  try {
    showLoading("Preparing export...");

    const response = await fetch(
      `${API_BASE}/user/${userId}/export?format=${format}`,
      {
        method: "GET",
        headers: {
          Accept: format === "json" ? "application/json" : "text/csv",
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Export failed: ${response.status}`);
    }

    // Get filename from Content-Disposition header
    const disposition = response.headers.get("Content-Disposition");
    const filename = disposition
      ? disposition.split("filename=")[1].replace(/"/g, "")
      : `phishguard_export_${Date.now()}.${format}`;

    // Download file
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    hideLoading();
    showSuccess(`Data exported as ${format.toUpperCase()}!`);
  } catch (error) {
    hideLoading();
    showError(`Export failed: ${error.message}`);
  }
}

async function deleteAllData() {
  if (!confirm("⚠️ Delete ALL your analytics data? This cannot be undone!")) {
    return;
  }

  if (
    !confirm(
      "Are you absolutely sure? This will permanently delete:\n- All activity history\n- Threat statistics\n- Geographic data\n- Device metrics"
    )
  ) {
    return;
  }

  try {
    showLoading("Deleting all data...");

    const response = await fetch(`${API_BASE}/user/${userId}/data`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error(`Delete failed: ${response.status}`);
    }

    hideLoading();
    showSuccess("All data deleted successfully!");

    // Reload analytics (should be empty now)
    setTimeout(() => loadUserAnalytics(), 1000);
  } catch (error) {
    hideLoading();
    showError(`Delete failed: ${error.message}`);
  }
}

function showLoading(message) {
  const overlay = document.createElement("div");
  overlay.id = "loading-overlay";
  overlay.innerHTML = `
    <div class="loading-spinner"></div>
    <div class="loading-message">${message}</div>
  `;
  document.body.appendChild(overlay);
}

function hideLoading() {
  const overlay = document.getElementById("loading-overlay");
  if (overlay) {
    overlay.remove();
  }
}

function showSuccess(message) {
  showNotification(message, "success");
}

function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  document.body.appendChild(notification);

  setTimeout(() => notification.classList.add("show"), 10);
  setTimeout(() => {
    notification.classList.remove("show");
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}
```

### Add Styles

File: `popup-enhanced.css`

```css
/* Export Section */
.export-section {
  margin-top: 20px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.export-section h3 {
  font-size: 14px;
  margin-bottom: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.export-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 8px;
}

.export-buttons .btn {
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.btn-secondary {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  grid-column: 1 / -1;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.export-info {
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  font-size: 10px;
  margin-top: 8px;
}

/* Loading Overlay */
#loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-message {
  margin-top: 16px;
  color: white;
  font-size: 14px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Notifications */
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  font-size: 13px;
  font-weight: 600;
  transform: translateX(400px);
  opacity: 0;
  transition: all 0.3s;
  z-index: 9999;
}

.notification.show {
  transform: translateX(0);
  opacity: 1;
}

.notification-success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.notification-error {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.notification-info {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}
```

## Delete Data Endpoint

File: `backend/src/handlers/user_analytics.rs`

```rust
/// DELETE /api/user/{user_id}/data
/// Delete all user's analytics data (GDPR compliance)
pub async fn delete_user_data(
    pool: web::Data<DbPool>,
    user_id_path: web::Path<Uuid>,
) -> ActixResult<HttpResponse> {
    let user_id = *user_id_path;

    let result = web::block(move || {
        let mut conn = pool.get().map_err(|e| {
            diesel::result::Error::DatabaseError(
                diesel::result::DatabaseErrorKind::UnableToSendCommand,
                Box::new(format!("{}", e)),
            )
        })?;

        // Delete all user data (CASCADE will handle related records)
        diesel::delete(user_activity::table.filter(user_activity::user_id.eq(user_id)))
            .execute(&mut conn)?;

        diesel::delete(user_threat_stats::table.filter(user_threat_stats::user_id.eq(user_id)))
            .execute(&mut conn)?;

        diesel::delete(user_threat_sources::table.filter(user_threat_sources::user_id.eq(user_id)))
            .execute(&mut conn)?;

        diesel::delete(device_metrics::table.filter(device_metrics::user_id.eq(user_id)))
            .execute(&mut conn)?;

        Ok::<_, diesel::result::Error>(())
    }).await
    .map_err(|e| actix_web::error::ErrorInternalServerError(format!("Database error: {}", e)))?;

    result.map_err(|e| actix_web::error::ErrorInternalServerError(format!("Delete error: {}", e)))?;

    Ok(HttpResponse::Ok().json(serde_json::json!({
        "success": true,
        "message": "All user data deleted successfully"
    })))
}
```

Add route:

```rust
.route("/user/{user_id}/data", web::delete().to(handlers::user_analytics::delete_user_data))
```

## Testing

1. **Export JSON**:

```bash
curl -O "http://localhost:8080/api/user/YOUR_USER_ID/export?format=json"
```

2. **Export CSV**:

```bash
curl -O "http://localhost:8080/api/user/YOUR_USER_ID/export?format=csv"
```

3. **Delete Data**:

```bash
curl -X DELETE "http://localhost:8080/api/user/YOUR_USER_ID/data"
```

4. **Test in UI**:

- Open popup
- Click "Export JSON" → downloads file
- Click "Export CSV" → downloads spreadsheet
- Click "Delete All Data" → confirms twice, then deletes

## Features

✅ **Export Formats**: JSON and CSV
✅ **File Download**: Automatic with proper filename
✅ **Privacy**: Only encrypted data exported
✅ **GDPR Compliant**: Complete data deletion
✅ **Confirmation**: Double-check before deleting
✅ **Loading States**: Shows progress
✅ **Notifications**: Success/error feedback

---

**Status**: 🔧 Manual implementation required
**Complexity**: Easy
**Time**: 20-30 minutes
