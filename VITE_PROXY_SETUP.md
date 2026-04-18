# 前端如何调用后端 API

## 问题：前端（localhost:5173）如何调用后端（localhost:8000）？

## 解决方案：使用 Vite 代理配置

### 1. 配置 vite.config.ts

在前端项目的 `vite.config.ts` 文件中添加代理配置：

```typescript
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### 2. 工作原理

**关键配置：**
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

**工作流程：**

1. 前端代码发起请求：
   ```typescript
   fetch('/api/order/parse-pdf', { ... })
   ```

2. Vite 开发服务器拦截所有以 `/api` 开头的请求

3. 自动转发到后端服务器：
   ```
   /api/order/parse-pdf  →  http://localhost:8000/api/order/parse-pdf
   ```

4. 后端处理请求并返回响应

5. Vite 将响应返回给前端

### 3. 为什么需要代理？

**问题：跨域（CORS）**

如果前端直接请求 `http://localhost:8000/api/order/parse-pdf`，会遇到跨域问题：
```
Access to fetch at 'http://localhost:8000/api/order/parse-pdf' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**解决方案：**

使用 Vite 代理后：
- 前端请求的是**同源地址** `/api/order/parse-pdf`（相对路径）
- Vite 在服务器端转发请求，**不存在跨域问题**
- 浏览器认为请求来自同一个域名

### 4. 前端代码示例

**正确写法（使用相对路径）：**
```typescript
// ✅ 正确：使用相对路径，会被 Vite 代理转发
const response = await fetch('/api/order/parse-pdf', {
  method: 'POST',
  body: formData,
})
```

**错误写法（直接请求后端地址）：**
```typescript
// ❌ 错误：会遇到 CORS 跨域问题
const response = await fetch('http://localhost:8000/api/order/parse-pdf', {
  method: 'POST',
  body: formData,
})
```

### 5. 完整配置说明

```typescript
server: {
  proxy: {
    '/api': {                           // 匹配规则：所有以 /api 开头的请求
      target: 'http://localhost:8000',  // 目标服务器地址
      changeOrigin: true                // 改变请求头中的 origin 字段
    }
  }
}
```

**配置项说明：**

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `/api` | 匹配规则，拦截以此开头的请求 | `/api/order/parse-pdf` 会被拦截 |
| `target` | 后端服务器地址 | `http://localhost:8000` |
| `changeOrigin` | 修改请求头的 origin，避免后端拒绝 | `true` |

### 6. 其他代理配置示例

**多个 API 路径：**
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    },
    '/upload': {
      target: 'http://localhost:9000',
      changeOrigin: true
    }
  }
}
```

**路径重写：**
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
      // /api/order/parse-pdf → /order/parse-pdf
    }
  }
}
```

**WebSocket 支持：**
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      ws: true  // 支持 WebSocket
    }
  }
}
```

### 7. 后端 CORS 配置（可选）

虽然使用了 Vite 代理，但后端仍然配置了 CORS，以支持其他场景：

```python
# pdf_parser_service.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173'])
```

这样即使不使用代理，直接请求后端也不会有 CORS 问题。

### 8. 生产环境部署

**开发环境：**
- 前端：`http://localhost:5173`（Vite 开发服务器）
- 后端：`http://localhost:8000`（Flask 开发服务器）
- 使用 Vite 代理转发请求

**生产环境：**
- 前端：构建后的静态文件，部署到 Nginx/Apache
- 后端：使用 Gunicorn/uWSGI 部署 Flask
- 使用 Nginx 反向代理：

```nginx
# nginx.conf
server {
  listen 80;
  
  # 前端静态文件
  location / {
    root /var/www/html;
    try_files $uri $uri/ /index.html;
  }
  
  # API 代理到后端
  location /api {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

### 9. 验证配置是否生效

1. **启动后端服务：**
   ```bash
   cd /Users/markov_lee/Code/pdf-order-parser/e_print_backend
   python3 pdf_parser_service.py
   ```
   应该看到：`Running on http://localhost:8000`

2. **启动前端服务：**
   ```bash
   cd /Users/markov_lee/Code/E_Print
   npm run dev
   ```
   应该看到：`Local: http://localhost:5173/`

3. **测试代理：**
   - 打开浏览器开发者工具（F12）
   - 切换到 Network 标签
   - 上传 PDF 并点击解析按钮
   - 查看请求：
     - Request URL: `http://localhost:5173/api/order/parse-pdf`（前端地址）
     - 实际转发到: `http://localhost:8000/api/order/parse-pdf`（后端地址）
     - Status: `200 OK`

### 10. 常见问题

**Q: 修改 vite.config.ts 后不生效？**  
A: 需要重启 Vite 开发服务器（Ctrl+C 然后重新 `npm run dev`）

**Q: 仍然报 CORS 错误？**  
A: 检查：
1. 后端服务是否启动（`http://localhost:8000`）
2. vite.config.ts 配置是否正确
3. 前端代码是否使用相对路径 `/api/...`

**Q: 请求超时？**  
A: 检查后端服务是否正常运行，查看后端日志

**Q: 404 Not Found？**  
A: 检查：
1. API 路径是否正确（`/api/order/parse-pdf`）
2. 后端路由是否正确定义
3. 代理配置的 target 是否正确

## 总结

使用 Vite 代理配置，前端可以：
1. ✅ 避免 CORS 跨域问题
2. ✅ 使用相对路径调用 API
3. ✅ 开发环境和生产环境配置一致
4. ✅ 无需修改前端代码即可切换后端地址

**核心配置只需 5 行代码：**
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```
