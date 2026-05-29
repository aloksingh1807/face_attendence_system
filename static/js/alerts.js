/* SECURITY INTRUSION ALERTS CENTER CONTROLLER */

document.addEventListener("DOMContentLoaded", function() {
    const alertsContainer = document.getElementById("alerts-directory-container");
    const statusFilter = document.getElementById("alerts-status-filter");
    
    function loadAlerts() {
        if (!alertsContainer) return;
        
        const status = statusFilter ? statusFilter.value : "Unresolved";
        
        fetch(`/api/alerts?status=${status}`)
            .then(res => res.json())
            .then(data => {
                renderAlerts(data);
            })
            .catch(err => {
                console.error("Alerts fetch error:", err);
                alertsContainer.innerHTML = `
                    <div class="directory-error">
                        <i class="fa-solid fa-triangle-exclamation"></i>
                        <p>Failed to scan active security alerts database.</p>
                    </div>
                `;
            });
    }

    function renderAlerts(alerts) {
        alertsContainer.innerHTML = "";
        
        if (alerts.length === 0) {
            alertsContainer.innerHTML = `
                <div class="directory-empty-state">
                    <i class="fa-solid fa-shield-heart text-gradient"></i>
                    <p>Excellent! No security visitor breaches matching these filters are active.</p>
                </div>
            `;
            return;
        }
        
        alerts.forEach(alert => {
            const card = document.createElement("div");
            const isUnresolved = alert.status === 'Unresolved';
            const alertClass = isUnresolved ? 'alert-card animate-pulse-glow' : 'alert-card';
            
            card.className = `${alertClass} animate-fade-in`;
            
            const actionButton = isUnresolved 
                ? `<button class="btn btn-danger alert-btn-resolve" onclick="resolveIntrusionAlert(${alert.id})">
                       <i class="fa-solid fa-shield-virus"></i> Mark Resolved
                   </button>`
                : `<span class="badge badge-success">Resolved by ${alert.resolved_by_name || 'Admin'}</span>
                   <span class="resolved-at-label">At ${alert.resolved_at}</span>`;
            
            const imagePath = alert.photo_path 
                ? `/${alert.photo_path}` 
                : "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=150&h=150";
                
            card.innerHTML = `
                <div class="alert-card-header">
                    <span class="badge ${isUnresolved ? 'badge-danger' : 'badge-success'}">${alert.status}</span>
                    <span class="alert-id">#ID-${alert.id}</span>
                </div>
                <img class="alert-img" src="${imagePath}" alt="Security Intrusion">
                <span class="alert-time"><i class="fa-regular fa-clock"></i> ${alert.timestamp}</span>
                ${actionButton}
            `;
            
            alertsContainer.appendChild(card);
        });
    }

    if (statusFilter) {
        statusFilter.addEventListener("change", loadAlerts);
    }

    // Expose resolve alert to global window scope
    window.resolveIntrusionAlert = function(alertId) {
        fetch(`/api/alerts/${alertId}/resolve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showNotificationToast("Intrusion security alert resolved successfully.", "success");
                loadAlerts();
                
                // Trigger global header badge count refresh
                if (window.updateAlertCounts) window.updateAlertCounts();
            } else {
                showNotificationToast(data.error || "Failed resolving alert.", "danger");
            }
        })
        .catch(err => {
            console.error("Resolve alert error:", err);
            showNotificationToast("Server error resolving security intrusion alert.", "danger");
        });
    };

    // Expose loadAlerts function globally so main.js SSE handler can trigger reloads
    window.loadAlerts = loadAlerts;
    
    // Initial fetch logs
    loadAlerts();
});
