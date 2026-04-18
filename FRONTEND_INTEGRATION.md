# 前端集成指南

## 按钮点击后的完整代码实现

### 1. 基础实现（Vue 3 + TypeScript）

```typescript
// 状态定义
const isParsing = ref(false)
const mainFile = ref<{ file: File | null }>({ file: null })
const orderData = reactive<IOrder>({
  // 你的订单数据对象
})

// 核心解析函数
async function ParseOrderFile() {
  if (!mainFile.file) {
    alert('请先上传 PDF 文件')
    return
  }

  try {
    isParsing.value = true
    
    // 1. 创建 FormData 对象
    const formData = new FormData()
    formData.append('file', mainFile.file)

    // 2. 发送 POST 请求到后端 API
    const response = await fetch('/api/order/parse-pdf', {
      method: 'POST',
      body: formData,
    })

    // 3. 检查响应状态
    if (!response.ok) {
      throw new Error(`解析失败: ${response.status}`)
    }

    // 4. 解析 JSON 响应
    const result = await response.json()
    
    // 5. 将解析结果填充到表单数据
    Object.assign(orderData, result)
    
    alert('解析成功，订单已自动填充')
  } catch (error) {
    console.error('Parsing error:', error)
    alert('解析失败，请检查文件格式或手动填写')
  } finally {
    isParsing.value = false
  }
}
```

### 2. 模板部分（按钮）

```vue
<template>
  <div>
    <!-- 文件上传 -->
    <input 
      type="file" 
      accept=".pdf"
      @change="handleFileChange"
    />
    
    <!-- 解析按钮 -->
    <button 
      @click="ParseOrderFile"
      :disabled="!mainFile.file || isParsing"
    >
      {{ isParsing ? '解析中...' : 'AI解析并填充表格' }}
    </button>
  </div>
</template>

<script setup lang="ts">
// 文件选择处理
function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    mainFile.file = target.files[0]
  }
}
</script>
```

### 3. 使用 axios 的实现

如果你的项目使用 axios：

```typescript
import axios from 'axios'

async function ParseOrderFile() {
  if (!mainFile.file) return

  try {
    isParsing.value = true
    
    const formData = new FormData()
    formData.append('file', mainFile.file)

    const { data } = await axios.post('/api/order/parse-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    Object.assign(orderData, data)
    alert('解析成功')
  } catch (error) {
    console.error('Parsing error:', error)
    alert('解析失败')
  } finally {
    isParsing.value = false
  }
}
```

### 4. 完整示例（包含错误处理和加载状态）

```typescript
import { ref, reactive } from 'vue'
import type { IOrder } from '@/types/Order'

// 状态
const isParsing = ref(false)
const parseError = ref<string | null>(null)
const mainFile = ref<File | null>(null)
const orderData = reactive<IOrder>({
  customer: '',
  order_id: '',
  productName: '',
  dingDanShuLiang: 0,
  chanPinMingXi: [],
  // ... 其他字段
})

// 文件选择
function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    mainFile.value = target.files[0]
    parseError.value = null // 清除之前的错误
  }
}

// 解析函数
async function ParseOrderFile() {
  if (!mainFile.value) {
    parseError.value = '请先上传 PDF 文件'
    return
  }

  // 验证文件类型
  if (!mainFile.value.name.toLowerCase().endsWith('.pdf')) {
    parseError.value = '只支持 PDF 文件'
    return
  }

  // 验证文件大小（16MB 限制）
  if (mainFile.value.size > 16 * 1024 * 1024) {
    parseError.value = '文件大小不能超过 16MB'
    return
  }

  try {
    isParsing.value = true
    parseError.value = null
    
    const formData = new FormData()
    formData.append('file', mainFile.value)

    const response = await fetch('/api/order/parse-pdf', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.error || `HTTP ${response.status}`)
    }

    const result = await response.json()
    
    // 填充数据
    Object.assign(orderData, result)
    
    console.log('解析成功，提取字段数:', Object.keys(result).length)
    alert('✅ 解析成功，订单已自动填充')
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '未知错误'
    parseError.value = `解析失败: ${errorMessage}`
    console.error('Parsing error:', error)
    alert(`❌ ${parseError.value}`)
  } finally {
    isParsing.value = false
  }
}
```

### 5. 模板（完整版）

```vue
<template>
  <div class="pdf-parser">
    <!-- 文件上传区域 -->
    <div class="upload-section">
      <input 
        id="pdf-file"
        type="file" 
        accept=".pdf"
        @change="handleFileChange"
        :disabled="isParsing"
      />
      <label for="pdf-file">
        {{ mainFile ? mainFile.name : '选择 PDF 文件' }}
      </label>
    </div>

    <!-- 错误提示 -->
    <div v-if="parseError" class="error-message">
      {{ parseError }}
    </div>

    <!-- 解析按钮 -->
    <button 
      class="parse-button"
      @click="ParseOrderFile"
      :disabled="!mainFile || isParsing"
    >
      <span v-if="isParsing">
        <i class="loading-icon"></i>
        解析中...
      </span>
      <span v-else>
        AI解析并填充表格
      </span>
    </button>

    <!-- 解析结果预览（可选） -->
    <div v-if="orderData.order_id" class="preview">
      <h3>解析结果预览</h3>
      <p>客户: {{ orderData.customer }}</p>
      <p>订单号: {{ orderData.order_id }}</p>
      <p>产品名称: {{ orderData.productName }}</p>
      <p>订单数量: {{ orderData.dingDanShuLiang }}</p>
    </div>
  </div>
</template>

<style scoped>
.pdf-parser {
  padding: 20px;
}

.upload-section {
  margin-bottom: 15px;
}

.error-message {
  color: red;
  margin-bottom: 10px;
}

.parse-button {
  padding: 10px 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.parse-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.loading-icon {
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
```

## API 响应格式

后端返回的 JSON 格式：

```json
{
  "customer": "当纳利亚洲印务有限公司",
  "order_id": "25025769",
  "productName": "绿女巫塔罗牌",
  "dingDanShuLiang": 30000,
  "chuYangShuLiang": 1,
  "guigeGaoMm": 127,
  "guigeKuanMm": 88.9,
  "guigeHouMm": 8,
  "xiaZiliaodaiRiqiPromise": "2025-10-29",
  "chuHuoRiqiPromise": "2025-11-24",
  "chanPinMingXi": [
    {
      "neiWen": "封面",
      "houDu": 0,
      "keZhong": 300,
      "chanDi": "国产",
      "pinPai": "华夏太阳",
      "zhiLei": "白卡纸（单粉卡）",
      "FSC": "FSC Mix Credit",
      "yeShu": 4,
      "yinSe": "CYMK/",
      "zhuanSe": "/",
      "biaoMianChuLi": "单面过哑胶",
      "zhuangDingGongYi": "",
      "yongZhiChiCun": "",
      "beiZhu": ""
    }
  ]
}
```

## 关键点说明

1. **FormData 必须包含 'file' 字段**
   ```typescript
   formData.append('file', mainFile.file)  // 字段名必须是 'file'
   ```

2. **不需要手动设置 Content-Type**
   浏览器会自动设置 `multipart/form-data` 和 boundary

3. **使用 Object.assign 填充数据**
   ```typescript
   Object.assign(orderData, result)  // 自动合并所有字段
   ```

4. **文件大小限制**
   后端限制 16MB，前端应该提前验证

5. **错误处理**
   后端返回的错误格式：
   ```json
   { "error": "错误信息" }
   ```

## 测试建议

1. 使用 `docs/` 目录中的示例 PDF 文件测试
2. 检查浏览器控制台的 Network 标签，确认请求正确发送
3. 验证响应数据是否正确填充到表单

## 常见问题

**Q: CORS 错误？**  
A: 确保后端已配置 CORS，允许前端域名访问

**Q: 解析很慢？**  
A: 正常情况下 1-3 秒，复杂 PDF 可能需要 5 秒

**Q: 某些字段没有填充？**  
A: 检查 PDF 格式是否与预期一致，查看后端日志

**Q: 产品明细为空？**  
A: 确保 PDF 包含"产品明细"表格，且表头包含必要字段
