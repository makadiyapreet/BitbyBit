const ws = new WebSocket(`ws://${window.location.host}/ws`);

ws.onopen = () => {
    setStatus('Connected to live alerts');
};

ws.onmessage = (event) => {
    const alertArea = document.getElementById('alerts-area');
    const alert = JSON.parse(event.data);

    if (alertArea) {
        alertArea.textContent = JSON.stringify(alert, null, 2);
    }

    // Popup notification for CRITICAL/HIGH alerts
    if (alert.type === 'instant_threat' && alert.data && alert.data.threat_level) {
        if (alert.data.threat_level === 'CRITICAL') {
            showToast(`CRITICAL THREAT: ${alert.data.location}`, "danger");
        } else if (alert.data.threat_level === 'HIGH') {
            showToast(`HIGH THREAT: ${alert.data.location}`, "warning");
        }
    }
};

ws.onerror = (e) => {
    setStatus('WebSocket error occurred', true);
};

ws.onclose = () => {
    setStatus('WebSocket disconnected', true);
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

// Toast notification function (reusable)
function showToast(message, level='info') {
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
