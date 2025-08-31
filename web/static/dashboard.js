const ws = new WebSocket(`ws://${window.location.host}/ws`);

ws.onopen = () => {
    setStatus('Connected to live updates');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    // Live data pretty-printed
    const liveArea = document.getElementById('live-data');
    if (liveArea) {
        liveArea.textContent = JSON.stringify(data, null, 2);
    }

    // Show instant threats in alerts-area, if present
    const alertArea = document.getElementById('alerts-area');
    if (alertArea && data.type === 'instant_threat' && data.data) {
        alertArea.textContent = JSON.stringify(data.data, null, 2);

        // Toast notification for CRITICAL or HIGH
        if (data.data.threat_level === "CRITICAL") {
            showToast(`CRITICAL THREAT: ${data.data.location}`, "danger");
        } else if (data.data.threat_level === "HIGH") {
            showToast(`HIGH THREAT: ${data.data.location}`, "warning");
        }
    }
};

ws.onerror = (e) => {
    setStatus('WebSocket error occurred', true);
};

ws.onclose = () => {
    setStatus('WebSocket disconnected', true);
    const liveArea = document.getElementById('live-data');
    if (liveArea) liveArea.textContent = 'WebSocket disconnected';
    const alertArea = document.getElementById('alerts-area');
    if (alertArea) alertArea.textContent = 'WebSocket disconnected';
};

function setStatus(msg, isError = false) {
    let stat = document.getElementById('ws-status');
    if (!stat) {
        stat = document.createElement('div');
        stat.id = 'ws-status';
        stat.style.position = 'fixed';
        stat.style.top = '8px';
        stat.style.right = '8px';
        stat.style.zIndex = 9999;
        stat.style.padding = '8px 18px';
        stat.style.borderRadius = '5px';
        stat.style.background = isError ? '#c92a2a' : '#2776ea';
        stat.style.color = '#fff';
        stat.style.fontWeight = '600';
        stat.style.boxShadow = '0 2px 8px rgba(0,0,0,0.12)';
        document.body.appendChild(stat);
    }
    stat.textContent = msg;
    setTimeout(() => { if (stat) stat.remove(); }, 3500);
}

// Simple toast notifications for critical/high alerts
function showToast(message, level = 'info') {
    const colors = { info: '#2563eb', success: '#22c55e', danger: '#dc2626', warning: '#fbbf24' };
    let bg = colors[level] || colors.info;
    let toast = document.createElement('div');
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.padding = '16px 30px';
    toast.style.background = bg;
    toast.style.color = '#fff';
    toast.style.borderRadius = '7px';
    toast.style.boxShadow = '0 2px 14px rgba(30,40,100,.13)';
    toast.style.fontWeight = '500';
    toast.style.fontSize = '1.05em';
    toast.style.letterSpacing = '0.01em';
    toast.style.zIndex = 99999;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 5500);
}
