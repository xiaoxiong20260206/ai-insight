// ==================== 全局状态 ====================
let currentRole = 'all';
let highlightedNodes = new Set();
let currentAgentDesign = 'Chatbot';

// ==================== 初始化 ====================
document.addEventListener('DOMContentLoaded', () => {
    initRoleTabs();
    renderAgentCards();
    renderTables();
    renderGraph();
    initTooltip();
    initAgentDesignTabs();
    renderAgentDesign('Chatbot');
});

// ==================== 角色选择器 ====================
function initRoleTabs() {
    const tabs = document.querySelectorAll('.role-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentRole = tab.dataset.role;
            renderGraph();
            renderTables();
            updateStats();
        });
    });
}

// ==================== 更新统计数据 ====================
function updateStats() {
    const totalRolesEl = document.getElementById('totalRoles');
    const totalTasksEl = document.getElementById('totalTasks');
    
    if (currentRole === 'all') {
        totalRolesEl.textContent = '10';
        totalTasksEl.textContent = '180+';
    } else {
        totalRolesEl.textContent = '1';
        const role = roleData[currentRole];
        let taskCount = 0;
        Object.values(role.scenes).forEach(scene => {
            taskCount += scene.tasks.length;
        });
        totalTasksEl.textContent = taskCount;
    }
}

// ==================== 渲染Agent卡片 ====================
function renderAgentCards() {
    const container = document.getElementById('agentsGrid');
    container.innerHTML = '';
    
    Object.entries(agentData).forEach(([key, agent]) => {
        const card = document.createElement('div');
        card.className = 'agent-card';
        card.innerHTML = `
            <div class="agent-card-header">
                <span class="agent-card-icon">${agent.icon}</span>
                <span class="agent-card-title">${agent.name}</span>
            </div>
            <div class="agent-card-coverage">
                <div class="coverage-bar">
                    <div class="coverage-fill" style="width: ${agent.coverage}%"></div>
                </div>
                <span class="coverage-text">${agent.coverage}%</span>
            </div>
            <div class="agent-card-desc">${agent.description}</div>
            <div class="agent-card-roles">
                ${agent.roles.map(role => `<span class="role-tag">${role}</span>`).join('')}
            </div>
        `;
        container.appendChild(card);
    });
}

// ==================== 渲染表格 ====================
function renderTables() {
    const container = document.getElementById('tablesContainer');
    container.innerHTML = '';
    
    const rolesToRender = currentRole === 'all' 
        ? Object.entries(roleData) 
        : [[currentRole, roleData[currentRole]]];
    
    rolesToRender.forEach(([roleKey, role]) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'role-table-wrapper';
        
        // 表头
        const header = document.createElement('div');
        header.className = `role-table-header ${roleKey}`;
        header.innerHTML = `${role.icon} ${role.name} 工作场景（占企业${role.percentage}%）`;
        wrapper.appendChild(header);
        
        // 表格
        const table = document.createElement('table');
        table.className = 'role-table';
        
        // 表头行
        table.innerHTML = `
            <thead>
                <tr>
                    <th>工作场景</th>
                    <th>具体任务</th>
                    <th>时间占比</th>
                    <th>Agent类型</th>
                    <th>业界产品</th>
                </tr>
            </thead>
            <tbody></tbody>
        `;
        
        const tbody = table.querySelector('tbody');
        
        Object.entries(role.scenes).forEach(([sceneName, scene]) => {
            scene.tasks.forEach((task, idx) => {
                const tr = document.createElement('tr');
                const timeClass = getTimeClass(task.timePercent);
                const agentClass = getAgentClass(task.agent);
                
                tr.innerHTML = `
                    <td>${idx === 0 ? `<strong>${sceneName}</strong><br><small style="color:#64748B">(${scene.timePercent}%)</small>` : ''}</td>
                    <td>${task.name}</td>
                    <td><span class="time-badge ${timeClass}">${task.timePercent}%</span></td>
                    <td><span class="agent-badge ${agentClass}">${agentData[task.agent]?.icon || ''} ${task.agent}</span></td>
                    <td>${task.products.map(p => {
                        const link = productLinks[p];
                        return link 
                            ? `<a href="${link}" target="_blank" class="product-link">${p}</a>` 
                            : p;
                    }).join(', ')}</td>
                `;
                
                if (idx === 0) {
                    tr.querySelector('td').rowSpan = scene.tasks.length;
                } else {
                    tr.querySelector('td').remove();
                }
                
                tbody.appendChild(tr);
            });
        });
        
        wrapper.appendChild(table);
        container.appendChild(wrapper);
    });
}

function getTimeClass(percent) {
    if (percent >= 10) return 'time-high';
    if (percent >= 5) return 'time-medium';
    if (percent >= 2) return 'time-low';
    return 'time-verylow';
}

function getAgentClass(agent) {
    const classMap = {
        'Coding': 'coding',
        'Chatbot': 'chatbot',
        'Workflow': 'workflow',
        'Research': 'research',
        'Design': 'design',
        'Data': 'data',
        'Background': 'background',
        'Browser': 'browser',
        'Computer': 'computer'
    };
    return classMap[agent] || '';
}

// ==================== 渲染关系图 ====================
function renderGraph() {
    const container = document.getElementById('graphColumns');
    const svg = document.getElementById('connectionsSvg');
    container.innerHTML = '';
    svg.innerHTML = '';
    
    // 5列：角色、场景、任务、Agent、产品
    const columns = {
        roles: [],
        scenes: [],
        tasks: [],
        agents: [],
        products: []
    };
    
    // 收集数据
    const rolesToRender = currentRole === 'all' 
        ? Object.entries(roleData).slice(0, 5) // 限制显示5个角色避免过于拥挤
        : [[currentRole, roleData[currentRole]]];
    
    const usedAgents = new Set();
    const usedProducts = new Set();
    const connections = [];
    
    rolesToRender.forEach(([roleKey, role]) => {
        const roleId = `role-${roleKey}`;
        columns.roles.push({
            id: roleId,
            name: `${role.icon} ${role.name}`,
            type: 'role',
            roleKey: roleKey
        });
        
        // 限制场景数量
        const sceneEntries = Object.entries(role.scenes).slice(0, 3);
        sceneEntries.forEach(([sceneName, scene]) => {
            const sceneId = `scene-${roleKey}-${scene.id}`;
            columns.scenes.push({
                id: sceneId,
                name: sceneName,
                type: 'scene',
                roleKey: roleKey
            });
            connections.push({ from: roleId, to: sceneId });
            
            // 限制任务数量
            const taskSlice = scene.tasks.slice(0, 2);
            taskSlice.forEach(task => {
                const taskId = `task-${task.id}`;
                columns.tasks.push({
                    id: taskId,
                    name: task.name,
                    type: 'task',
                    roleKey: roleKey,
                    agent: task.agent,
                    products: task.products
                });
                connections.push({ from: sceneId, to: taskId });
                
                // Agent
                const agentId = `agent-${task.agent}`;
                usedAgents.add(task.agent);
                connections.push({ from: taskId, to: agentId });
                
                // 产品（限制数量）
                task.products.slice(0, 2).forEach(product => {
                    const productId = `product-${product.replace(/\s+/g, '-')}`;
                    usedProducts.add(product);
                    connections.push({ from: taskId, to: productId });
                });
            });
        });
    });
    
    // 添加Agent节点
    usedAgents.forEach(agentKey => {
        const agent = agentData[agentKey];
        if (agent) {
            columns.agents.push({
                id: `agent-${agentKey}`,
                name: `${agent.icon} ${agent.name}`,
                type: 'agent'
            });
        }
    });
    
    // 添加产品节点
    usedProducts.forEach(product => {
        columns.products.push({
            id: `product-${product.replace(/\s+/g, '-')}`,
            name: product,
            type: 'product',
            link: productLinks[product]
        });
    });
    
    // 创建列容器
    const columnOrder = ['roles', 'scenes', 'tasks', 'agents', 'products'];
    columnOrder.forEach(colKey => {
        const colDiv = document.createElement('div');
        colDiv.className = 'graph-column';
        colDiv.id = `col-${colKey}`;
        
        columns[colKey].forEach(node => {
            const nodeDiv = document.createElement('div');
            nodeDiv.className = `graph-node node-${node.type}`;
            nodeDiv.id = node.id;
            nodeDiv.textContent = node.name;
            
            if (node.roleKey) {
                nodeDiv.dataset.role = node.roleKey;
            }
            
            // 所有节点都支持点击高亮
            nodeDiv.addEventListener('click', (e) => {
                // 如果是产品节点且按住Ctrl/Cmd键，则跳转
                if (node.type === 'product' && node.link && (e.ctrlKey || e.metaKey)) {
                    window.open(node.link, '_blank');
                } else {
                    handleNodeClick(node.id, connections);
                }
                e.stopPropagation();
            });
            
            // 产品节点双击跳转
            if (node.type === 'product' && node.link) {
                nodeDiv.style.cursor = 'pointer';
                nodeDiv.addEventListener('dblclick', (e) => {
                    window.open(node.link, '_blank');
                    e.stopPropagation();
                });
            }
            
            // Tooltip
            nodeDiv.addEventListener('mouseenter', (e) => showTooltip(e, node));
            nodeDiv.addEventListener('mouseleave', hideTooltip);
            
            colDiv.appendChild(nodeDiv);
        });
        
        container.appendChild(colDiv);
    });
    
    // 绘制连接线（延迟执行以确保DOM已渲染）
    setTimeout(() => {
        drawConnections(connections, svg);
    }, 100);
    
    // 点击空白取消高亮
    document.querySelector('.graph-canvas').addEventListener('click', (e) => {
        if (e.target.classList.contains('graph-canvas') || e.target.id === 'connectionsSvg') {
            clearHighlight();
        }
    });
}

// ==================== 绘制连接线 ====================
function drawConnections(connections, svg) {
    const canvas = document.querySelector('.graph-canvas');
    const canvasRect = canvas.getBoundingClientRect();
    
    svg.setAttribute('width', canvas.scrollWidth);
    svg.setAttribute('height', canvas.scrollHeight);
    
    connections.forEach(conn => {
        const fromEl = document.getElementById(conn.from);
        const toEl = document.getElementById(conn.to);
        
        if (!fromEl || !toEl) return;
        
        const fromRect = fromEl.getBoundingClientRect();
        const toRect = toEl.getBoundingClientRect();
        
        const scrollLeft = canvas.scrollLeft;
        const scrollTop = canvas.scrollTop;
        
        const x1 = fromRect.right - canvasRect.left + scrollLeft;
        const y1 = fromRect.top + fromRect.height / 2 - canvasRect.top + scrollTop;
        const x2 = toRect.left - canvasRect.left + scrollLeft;
        const y2 = toRect.top + toRect.height / 2 - canvasRect.top + scrollTop;
        
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const midX = (x1 + x2) / 2;
        path.setAttribute('d', `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`);
        path.setAttribute('class', 'connection-line');
        path.dataset.from = conn.from;
        path.dataset.to = conn.to;
        
        svg.appendChild(path);
    });
}

// ==================== 节点点击高亮 ====================
function handleNodeClick(nodeId, connections) {
    clearHighlight();
    
    // 找到所有直接关联的节点（只查找直接连线的节点）
    const directlyConnected = new Set([nodeId]);
    
    // 第一层：找直接连接的节点
    connections.forEach((conn) => {
        if (conn.from === nodeId) {
            directlyConnected.add(conn.to);
        }
        if (conn.to === nodeId) {
            directlyConnected.add(conn.from);
        }
    });
    
    // 第二层：从直接连接的节点继续向两侧扩展
    const secondLevel = new Set();
    directlyConnected.forEach(connectedId => {
        if (connectedId === nodeId) return;
        connections.forEach((conn) => {
            if (conn.from === connectedId && !directlyConnected.has(conn.to)) {
                secondLevel.add(conn.to);
            }
            if (conn.to === connectedId && !directlyConnected.has(conn.from)) {
                secondLevel.add(conn.from);
            }
        });
    });
    
    // 合并所有需要高亮的节点
    const allHighlighted = new Set([...directlyConnected, ...secondLevel]);
    
    // 高亮节点
    document.querySelectorAll('.graph-node').forEach(node => {
        if (allHighlighted.has(node.id)) {
            node.classList.add('highlighted');
        } else {
            node.classList.add('dimmed');
        }
    });
    
    // 高亮连接线 - 只高亮实际连接的线
    document.querySelectorAll('.connection-line').forEach((line) => {
        const fromId = line.dataset.from;
        const toId = line.dataset.to;
        // 连接线两端的节点都需要在高亮集合中才高亮这条线
        if (allHighlighted.has(fromId) && allHighlighted.has(toId)) {
            line.classList.add('highlighted');
        } else {
            line.classList.add('dimmed');
        }
    });
    
    highlightedNodes = allHighlighted;
}

function clearHighlight() {
    document.querySelectorAll('.graph-node').forEach(node => {
        node.classList.remove('highlighted', 'dimmed');
    });
    document.querySelectorAll('.connection-line').forEach(line => {
        line.classList.remove('highlighted', 'dimmed');
    });
    highlightedNodes.clear();
}

// ==================== Tooltip ====================
function initTooltip() {
    // Tooltip已在HTML中定义
}

function showTooltip(e, node) {
    const tooltip = document.getElementById('tooltip');
    let content = '';
    
    if (node.type === 'role') {
        const role = roleData[node.roleKey];
        content = `
            <div class="tooltip-title">${node.name}</div>
            <div class="tooltip-row"><span class="tooltip-label">占企业比例:</span><span class="tooltip-value">${role.percentage}%</span></div>
            <div class="tooltip-row"><span class="tooltip-label">工作场景:</span><span class="tooltip-value">${Object.keys(role.scenes).length}个</span></div>
        `;
    } else if (node.type === 'scene') {
        content = `
            <div class="tooltip-title">${node.name}</div>
            <div class="tooltip-row"><span class="tooltip-label">类型:</span><span class="tooltip-value">工作场景</span></div>
        `;
    } else if (node.type === 'task') {
        content = `
            <div class="tooltip-title">${node.name}</div>
            <div class="tooltip-row"><span class="tooltip-label">Agent:</span><span class="tooltip-value">${node.agent}</span></div>
            <div class="tooltip-row"><span class="tooltip-label">产品:</span><span class="tooltip-value">${node.products?.slice(0, 3).join(', ') || '-'}</span></div>
        `;
    } else if (node.type === 'agent') {
        const agentKey = node.id.replace('agent-', '');
        const agent = agentData[agentKey];
        if (agent) {
            content = `
                <div class="tooltip-title">${agent.name}</div>
                <div class="tooltip-row"><span class="tooltip-label">覆盖率:</span><span class="tooltip-value">${agent.coverage}%</span></div>
                <div class="tooltip-row"><span class="tooltip-label">能力:</span><span class="tooltip-value">${agent.description}</span></div>
            `;
        }
    } else if (node.type === 'product') {
        content = `
            <div class="tooltip-title">🔗 ${node.name}</div>
            <div class="tooltip-row"><span class="tooltip-label">点击跳转官网</span></div>
            <div class="tooltip-row"><span class="tooltip-value" style="font-size:0.75rem;color:#94A3B8">${node.link || ''}</span></div>
        `;
    }
    
    tooltip.innerHTML = content;
    tooltip.classList.add('visible');
    
    // 定位
    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = rect.right + 10 + 'px';
    tooltip.style.top = rect.top + 'px';
    
    // 边界检查
    const tooltipRect = tooltip.getBoundingClientRect();
    if (tooltipRect.right > window.innerWidth) {
        tooltip.style.left = rect.left - tooltipRect.width - 10 + 'px';
    }
    if (tooltipRect.bottom > window.innerHeight) {
        tooltip.style.top = window.innerHeight - tooltipRect.height - 10 + 'px';
    }
}

function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    tooltip.classList.remove('visible');
}

// ==================== 窗口resize时重绘连接线 ====================
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        renderGraph();
    }, 200);
});

// ==================== Agent设计方案Tab ====================
function initAgentDesignTabs() {
    const tabs = document.querySelectorAll('.agent-design-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const agentType = tab.dataset.agent;
            currentAgentDesign = agentType;
            renderAgentDesign(agentType);
        });
    });
    
    // 架构图中Agent项点击
    const agentItems = document.querySelectorAll('.agent-item');
    agentItems.forEach(item => {
        item.addEventListener('click', () => {
            const agentType = item.dataset.agent;
            // 滚动到设计方案区域
            document.querySelector('.agent-design-section').scrollIntoView({ behavior: 'smooth' });
            // 切换Tab
            setTimeout(() => {
                document.querySelectorAll('.agent-design-tab').forEach(t => t.classList.remove('active'));
                document.querySelector(`.agent-design-tab[data-agent="${agentType}"]`)?.classList.add('active');
                renderAgentDesign(agentType);
            }, 300);
        });
    });
}

// ==================== 渲染Agent设计方案 ====================
function renderAgentDesign(agentType) {
    const container = document.getElementById('agentDesignContent');
    const agent = agentData[agentType];
    const design = agentDesignData[agentType];
    
    if (!agent || !design) {
        container.innerHTML = '<p>设计方案加载中...</p>';
        return;
    }
    
    container.innerHTML = `
        <div class="agent-design-header">
            <div class="agent-design-icon">${agent.icon}</div>
            <div class="agent-design-title">
                <h3>${design.productName}</h3>
                <p>${design.productDesc}</p>
            </div>
            <div class="agent-design-coverage">覆盖率 ${agent.coverage}%</div>
        </div>
        <div class="agent-design-body">
            <div class="design-card">
                <h4>🧩 功能模块</h4>
                <div class="module-grid">
                    ${design.modules.map(m => `<div class="module-item">${m}</div>`).join('')}
                </div>
            </div>
            <div class="design-card">
                <h4>📋 支撑工作场景</h4>
                <ul>
                    ${design.scenes.map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>
            <div class="design-card">
                <h4>🔧 技术栈</h4>
                <ul>
                    ${design.techStack.map(t => `<li>${t}</li>`).join('')}
                </ul>
            </div>
            <div class="design-card">
                <h4>✨ 核心特性</h4>
                <ul>
                    ${design.keyFeatures.map(f => `<li>${f}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
}
