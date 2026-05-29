/* GLOBAL CLIENT CONTROL BLUEPRINT */

document.addEventListener("DOMContentLoaded", function() {
    // 1. Navbar Live Clock Widget
    const clockElement = document.getElementById("live-clock");
    if (clockElement) {
        setInterval(() => {
            const now = new Date();
            clockElement.textContent = now.toLocaleTimeString();
        }, 1000);
    }
    
    // 2. SSE Alert stream receiver
    const sseStatus = document.getElementById("sse-status");
    const sseStatusText = document.getElementById("sse-status-text");
    
    if (sseStatus) {
        // Initialize persistent event stream listener
        const eventSource = new EventSource('/api/alerts/stream');
        
        eventSource.onopen = function() {
            sseStatus.style.borderColor = "rgba(16, 185, 129, 0.2)";
            sseStatus.style.backgroundColor = "rgba(16, 185, 129, 0.05)";
            sseStatusText.textContent = "Online";
        };
        
        eventSource.onerror = function() {
            sseStatus.style.borderColor = "rgba(239, 68, 68, 0.2)";
            sseStatus.style.backgroundColor = "rgba(239, 68, 68, 0.05)";
            sseStatusText.textContent = "Offline";
        };
        
        eventSource.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                
                // Ignore pings and keep-alives
                if (data.ping || data.keep_alive) return;
                
                // Trigger real-time visual and audio intrusion warnings
                showNotificationToast("Security Intrusion Detected!", "danger");
                playAlarmSound();
                
                // Increment badges
                incrementAlertBadges();
                
                // If we are currently on the alerts dashboard or overview feed, reload
                if (window.loadAlerts) window.loadAlerts();
                if (window.loadDashboardFeed) window.loadDashboardFeed();
            } catch (err) {
                console.error("SSE parse error:", err);
            }
        };
    }
    
    // Fetch initial unresolved alert counts to initialize badges
    updateAlertCounts();
});

// Toast system
function showNotificationToast(message, category = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    
    const toast = document.createElement("div");
    toast.className = `toast toast-${category} animate-pulse-glow`;
    
    const iconClass = category === 'success' 
        ? 'fa-solid fa-circle-check' 
        : (category === 'danger' || category === 'warning' ? 'fa-solid fa-triangle-exclamation' : 'fa-solid fa-circle-info');
        
    toast.innerHTML = `
        <div class="toast-content">
            <i class="${iconClass}"></i>
            <span>${message}</span>
        </div>
        <button class="toast-close-btn" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Audio synthesizer warning
function playAlarmSound() {
    const alarm = document.getElementById("alarm-sound");
    if (alarm) {
        alarm.muted = false;
        alarm.play().catch(err => {
            console.log("Audio play blocked by browser permission policy:", err);
        });
    }
}

// Badge controllers
function incrementAlertBadges() {
    const badges = [
        document.getElementById("sidebar-alert-badge"),
        document.getElementById("bell-alert-badge")
    ];
    
    badges.forEach(badge => {
        if (badge) {
            let count = parseInt(badge.textContent) || 0;
            count++;
            badge.textContent = count;
            badge.classList.remove("hidden");
        }
    });
}

function updateAlertCounts() {
    fetch('/api/alerts?status=Unresolved')
        .then(res => res.json())
        .then(data => {
            const count = data.length;
            const badges = [
                document.getElementById("sidebar-alert-badge"),
                document.getElementById("bell-alert-badge")
            ];
            
            badges.forEach(badge => {
                if (badge) {
                    if (count > 0) {
                        badge.textContent = count;
                        badge.classList.remove("hidden");
                    } else {
                        badge.classList.add("hidden");
                    }
                }
            });
        })
        .catch(err => console.log("Failed updating alert counts:", err));
}
