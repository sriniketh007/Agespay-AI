let totalCount = 0;
let fraudCount = 0;
let challengeCount = 0;
let totalLatency = 0;

// Connect to FastAPI WebSocket Stream
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/ws/stream`;
const ws = new WebSocket(wsUrl);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    addStreamRow(data);
    updateMetrics(data);
};

function updateMetrics(data) {
    totalCount++;
    if (data.verdict === 'DECLINED_FRAUD') fraudCount++;
    if (data.verdict === 'CHALLENGE_PUSH') challengeCount++;
    totalLatency += data.latency_ms;

    document.getElementById('stat-total').innerText = totalCount;
    document.getElementById('stat-fraud').innerText = fraudCount;
    document.getElementById('stat-challenge').innerText = challengeCount;
    document.getElementById('stat-latency').innerText = (totalLatency / totalCount).toFixed(1) + ' ms';
}

function addStreamRow(data) {
    const tbody = document.getElementById('stream-rows');
    const emptyRow = tbody.querySelector('.empty-row');
    if (emptyRow) emptyRow.remove();

    let badgeClass = 'badge-approved';
    if (data.verdict === 'CHALLENGE_PUSH') badgeClass = 'badge-challenge';
    if (data.verdict === 'DECLINED_FRAUD') badgeClass = 'badge-declined';

    const row = document.createElement('tr');
    row.innerHTML = `
        <td style="color: #64748b;">${data.eval_id}</td>
        <td>${data.account_id}</td>
        <td>₹${data.amount.toFixed(2)}</td>
        <td style="color: #00f3ff;">${(data.risk_score * 100).toFixed(1)}%</td>
        <td><span class="badge ${badgeClass}">${data.verdict}</span></td>
        <td>${data.latency_ms} ms</td>
    `;

    tbody.insertBefore(row, tbody.firstChild);

    // Keep table limited to 15 rows
    if (tbody.children.length > 15) {
        tbody.removeChild(tbody.lastChild);
    }
}

// Handle Form Submission for Quick Testing
document.getElementById('sim-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const payload = {
        transaction_id: `tx_${Date.now()}`,
        account_id: document.getElementById('sim-account').value,
        merchant: { id: document.getElementById('sim-merchant').value, category_code: 5732 },
        amount: parseFloat(document.getElementById('sim-amount').value),
        currency: "USD",
        timestamp: new Date().toISOString(),
        device: {
            device_fingerprint: "df_mock_1029",
            ip_address: document.getElementById('sim-ip').value,
            user_agent: "Mozilla/5.0"
        },
        location: { latitude: 37.77, longitude: -122.41 }
    };

    await fetch('/v1/evaluate-transaction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
});