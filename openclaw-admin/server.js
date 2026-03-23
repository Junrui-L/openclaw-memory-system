const express = require('express');
const { exec } = require('child_process');
const path = require('path');
const app = express();
const PORT = 3000;

// 中间件
app.use(express.json());
app.use(express.static('public'));

// OpenClaw 实例配置
const INSTANCES = [
  { id: 'gateway', name: '主实例', container: 'openclaw-gateway', port: 8443, wsPort: 18789 },
  { id: 'work', name: '工作实例', container: 'openclaw-work', port: 8447, wsPort: 17789 },
  { id: 'test', name: '测试实例', container: 'openclaw-test', port: 8445, wsPort: 16789 }
];

// 执行 Docker 命令
function dockerCommand(cmd) {
  return new Promise((resolve, reject) => {
    exec(cmd, (error, stdout, stderr) => {
      if (error) {
        reject(stderr || error.message);
      } else {
        resolve(stdout.trim());
      }
    });
  });
}

// API: 获取所有实例状态
app.get('/api/instances', async (req, res) => {
  try {
    const result = await dockerCommand('docker ps --format "{{.Names}}|{{.Status}}|{{.Ports}}"');
    const containers = result.split('\n').reduce((acc, line) => {
      const [name, status, ports] = line.split('|');
      if (name) acc[name] = { status, ports };
      return acc;
    }, {});

    const instances = INSTANCES.map(inst => ({
      ...inst,
      running: containers[inst.container]?.status?.includes('Up') || false,
      status: containers[inst.container]?.status || 'stopped',
      ports: containers[inst.container]?.ports || ''
    }));

    res.json({ success: true, instances });
  } catch (error) {
    res.json({ success: false, error: error.toString() });
  }
});

// API: 控制实例
app.post('/api/instances/:id/:action', async (req, res) => {
  const { id, action } = req.params;
  const instance = INSTANCES.find(i => i.id === id);
  
  if (!instance) {
    return res.json({ success: false, error: '实例不存在' });
  }

  const validActions = ['start', 'stop', 'restart', 'logs'];
  if (!validActions.includes(action)) {
    return res.json({ success: false, error: '无效操作' });
  }

  try {
    let cmd;
    if (action === 'logs') {
      cmd = `docker logs --tail=50 ${instance.container}`;
    } else {
      cmd = `docker ${action} ${instance.container}`;
    }
    
    const result = await dockerCommand(cmd);
    res.json({ success: true, result });
  } catch (error) {
    res.json({ success: false, error: error.toString() });
  }
});

// API: 获取系统资源
app.get('/api/stats', async (req, res) => {
  try {
    const result = await dockerCommand(
      'docker stats --no-stream --format "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.NetIO}}"'
    );
    const stats = result.split('\n').map(line => {
      const [name, cpu, mem, net] = line.split('|');
      return { name, cpu, mem, net };
    }).filter(s => s.name);
    
    res.json({ success: true, stats });
  } catch (error) {
    res.json({ success: false, error: error.toString() });
  }
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`OpenClaw Admin 运行在 http://localhost:${PORT}`);
});
