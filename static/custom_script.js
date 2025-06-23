// Dashboard JavaScript for TradeMasterX 2.0
let ws = null;
let tradingActive = false;
let emergencyStopActive = false;

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    ws = new WebSocket(wsUrl);
    ws.onopen = function() {
        addLog('WebSocket connected', 'success');
        const status = document.getElementById('connection-status');
        if (status) status.textContent = 'Connected';
    };
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };
    ws.onclose = function() {
        addLog('WebSocket disconnected', 'warning');
        const status = document.getElementById('connection-status');
        if (status) status.textContent = 'Disconnected';
        setTimeout(connectWebSocket, 5000);
    };
}

function handleMessage(data) {
    switch(data.type) {
        case 'status':
            updateStatus(data.data);
            break;
        case 'market_data':
            updateMarketData(data.data);
            break;
        case 'portfolio':
            updatePortfolio(data.data);
            break;
        case 'trades':
            updateTrades(data.data);
            break;
        case 'ai_response':
            addChatMessage(data.message, 'ai');
            break;
        case 'log':
            addLog(data.message, data.level);
            break;
    }
}

function updateStatus(data) {
    const dot = document.getElementById('status-dot');
    const text = document.getElementById('status-text');
    if (data.status === 'ACTIVE') {
        dot.className = 'status-dot status-active';
        text.textContent = 'Trading Active';
        tradingActive = true;
        emergencyStopActive = false;
    } else if (data.status === 'EMERGENCY_STOP') {
        dot.className = 'status-dot status-emergency';
        text.textContent = 'EMERGENCY STOP';
        tradingActive = false;
        emergencyStopActive = true;
    } else {
        dot.className = 'status-dot status-stopped';
        text.textContent = 'Trading Stopped';
        tradingActive = false;
        emergencyStopActive = false;
    }
    updateButtons();
}

function updateMarketData(data) {
    const container = document.getElementById('market-data');
    if (!container) return;
    let html = '';
    Object.entries(data).forEach(([symbol, info]) => {
        const changeClass = info.change >= 0 ? 'positive' : 'negative';
        const changeSymbol = info.change >= 0 ? '+' : '';
        html += `
            <div class="market-item">
                <div class="symbol">${symbol}</div>
                <div class="price">$${info.price.toLocaleString()}</div>
                <div class="change ${changeClass}">${changeSymbol}${info.change.toFixed(2)}%</div>
            </div>
        `;
    });
    container.innerHTML = html;
}

function updatePortfolio(data) {
    document.getElementById('total-value').textContent = `$${data.total_value.toLocaleString()}`;
    document.getElementById('available-balance').textContent = `$${data.available_balance.toLocaleString()}`;
    const dailyPnl = document.getElementById('daily-pnl');
    dailyPnl.textContent = `$${data.daily_pnl.toFixed(2)}`;
    dailyPnl.className = `metric-value ${data.daily_pnl >= 0 ? 'positive' : 'negative'}`;
    const totalPnl = document.getElementById('total-pnl');
    totalPnl.textContent = `$${data.total_pnl.toFixed(2)}`;
    totalPnl.className = `metric-value ${data.total_pnl >= 0 ? 'positive' : 'negative'}`;
}

function updateTrades(trades) {
    const tbody = document.getElementById('trades-body');
    if (!tbody) return;
    if (trades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #a0aec0;">No active trades</td></tr>';
        return;
    }
    let html = '';
    trades.forEach(trade => {
        const typeClass = trade.type === 'BUY' ? 'trade-buy' : 'trade-sell';
        const pnlClass = trade.pnl >= 0 ? 'positive' : 'negative';
        html += `
            <tr>
                <td>${trade.time}</td>
                <td>${trade.symbol}</td>
                <td class="${typeClass}">${trade.type}</td>
                <td>$${trade.price.toFixed(2)}</td>
                <td>${trade.quantity}</td>
                <td class="${pnlClass}">$${trade.pnl.toFixed(2)}</td>
                <td>${trade.status}</td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

function updateButtons() {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const emergencyBtn = document.getElementById('emergency-btn');
    if (emergencyStopActive) {
        startBtn.disabled = true;
        stopBtn.disabled = true;
        emergencyBtn.textContent = 'Reset Emergency Stop';
    } else if (tradingActive) {
        startBtn.disabled = true;
        stopBtn.disabled = false;
        emergencyBtn.disabled = false;
    } else {
        startBtn.disabled = false;
        stopBtn.disabled = true;
        emergencyBtn.disabled = false;
    }
}

function addLog(message, level = 'info') {
    const logs = document.getElementById('logs');
    if (!logs) return;
    const time = new Date().toLocaleTimeString();
    const levelClass = level === 'error' ? 'log-error' : level === 'warning' ? 'log-warning' : level === 'success' ? 'log-success' : 'log-info';
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.innerHTML = `
        <span class="log-time">[${time}]</span>
        <span class="${levelClass}">${message}</span>
    `;
    logs.appendChild(logEntry);
    logs.scrollTop = logs.scrollHeight;
    while (logs.children.length > 100) {
        logs.removeChild(logs.firstChild);
    }
}

function addChatMessage(message, sender) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message message-${sender}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    if (!input) return;
    const message = input.value.trim();
    if (!message) return;
    addChatMessage(message, 'user');
    input.value = '';
    try {
        const response = await fetch('/api/ai-query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: message})
        });
        const data = await response.json();
        if (data.success) {
            addChatMessage(data.response, 'ai');
        }
    } catch (error) {
        addLog('Error sending chat message: ' + error, 'error');
    }
}

async function startTrading() {
    console.log('startTrading function called');
    try {
        const response = await fetch('/api/start-trading', { method: 'POST' });
        const data = await response.json();
        console.log('startTrading response:', data);
        if (data.success) {
            addLog('Trading started successfully', 'success');
        } else {
            addLog('Failed to start trading: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('startTrading error:', error);
        addLog('Error starting trading: ' + error, 'error');
    }
}

async function stopTrading() {
    console.log('stopTrading function called');
    try {
        const response = await fetch('/api/stop-trading', { method: 'POST' });
        const data = await response.json();
        console.log('stopTrading response:', data);
        if (data.success) {
            addLog('Trading stopped successfully', 'warning');
        } else {
            addLog('Failed to stop trading: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('stopTrading error:', error);
        addLog('Error stopping trading: ' + error, 'error');
    }
}

async function emergencyStop() {
    console.log('emergencyStop function called');
    try {
        const response = await fetch('/api/emergency-stop', { method: 'POST' });
        const data = await response.json();
        console.log('emergencyStop response:', data);
        if (data.success) {
            addLog('EMERGENCY STOP ACTIVATED!', 'error');
        } else {
            addLog('Failed to activate emergency stop: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('emergencyStop error:', error);
        addLog('Error activating emergency stop: ' + error, 'error');
    }
}

async function triggerRetrain() {
    try {
        const response = await fetch('/api/trigger-retrain', { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            addLog('Model retraining triggered', 'success');
        } else {
            addLog('Failed to trigger retrain: ' + data.error, 'error');
        }
    } catch (error) {
        addLog('Error triggering retrain: ' + error, 'error');
    }
}

async function placeOrder() {
    const symbol = document.getElementById('order-symbol').value;
    const type = document.getElementById('order-type').value;
    const quantity = parseFloat(document.getElementById('order-quantity').value);
    try {
        const response = await fetch('/api/place-order', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({symbol, type, quantity})
        });
        const data = await response.json();
        if (data.success) {
            addLog(`Order placed: ${type} ${quantity} ${symbol}`, 'success');
        } else {
            addLog('Failed to place order: ' + data.error, 'error');
        }
    } catch (error) {
        addLog('Error placing order: ' + error, 'error');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    connectWebSocket();
    updateButtons();
    fetch('/api/market-data').then(r => r.json()).then(updateMarketData);
    fetch('/api/portfolio').then(r => r.json()).then(updatePortfolio);
    fetch('/api/status').then(r => r.json()).then(updateStatus);
    setInterval(() => {
        fetch('/api/market-data').then(r => r.json()).then(updateMarketData);
        fetch('/api/portfolio').then(r => r.json()).then(updatePortfolio);
    }, 30000);
});

// Expose button functions to global scope
window.startTrading = startTrading;
window.stopTrading = stopTrading;
window.emergencyStop = emergencyStop;
window.triggerRetrain = triggerRetrain;
window.placeOrder = placeOrder; 