# Aukey Finance OCR 识别系统

这是一个基于FastAPI和PaddleOCR的财务文档OCR识别系统，提供高性能的文字识别服务。

## 功能特性

- 🚀 基于FastAPI的高性能API服务
- 📄 支持多种财务文档的OCR识别
- 🔒 内置API密钥认证和限流机制
- 💾 SQLite数据库存储
- 🏥 健康检查接口
- 📊 支持批量文档处理

## 系统要求

- Python 3.10
- Windows/Linux/macOS
- 至少2GB可用内存
- 网络连接（首次运行需要下载OCR模型）

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd aukey-finance-ocr-identify
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 环境配置

创建 `.env` 文件（可选）：

```bash
# 数据库配置
DB_USER=root
DB_PASSWORD=123456
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=yecai_ocr

# 结果目录
RESULT_DIR=results
```

### 5. 初始化数据库

```bash
python init_db.py
```

### 6. 配置IP白名单（可选）

使用命令行工具管理IP白名单：

```bash
# 添加IP到白名单
python manage_whitelist.py add 192.168.1.100 "内网服务器"
python manage_whitelist.py add 10.0.0.0/24 "内网段"

# 查看所有IP白名单
python manage_whitelist.py list

# 从白名单移除IP
python manage_whitelist.py remove 192.168.1.100

# 刷新缓存
python manage_whitelist.py refresh-cache

# 查看缓存信息
python manage_whitelist.py cache-info
```

### 6. 配置IP白名单（可选）

使用命令行工具管理IP白名单：

```bash
# 添加IP到白名单
python manage_whitelist.py add 192.168.1.100 "内网服务器"
python manage_whitelist.py add 10.0.0.0/24 "内网段"

# 查看所有IP白名单
python manage_whitelist.py list

# 从白名单移除IP
python manage_whitelist.py remove 192.168.1.100

# 刷新缓存
python manage_whitelist.py refresh-cache

# 查看缓存信息
python manage_whitelist.py cache-info
```

## 启动项目

### 开发模式启动

```bash
python run.py
```

或者使用uvicorn直接启动：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 生产模式启动

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 访问地址

- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health
- 交互式API文档：http://localhost:8000/redoc
- IP白名单管理：http://localhost:8000/whitelist/list
- IP白名单管理：http://localhost:8000/whitelist/list

## API 使用说明

### OCR识别接口

**POST** `/ocr/`

上传图片文件进行OCR识别

**请求参数：**
- `file`: 图片文件（支持jpg, png, bmp等格式）

**请求头：**
```
Content-Type: multipart/form-data
Authorization:Bearer your-token
```

**响应示例：**
```json
{
  "success": true,
  "data": [
    {
      "text": "识别出的文字",
      "confidence": 0.95,
      "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    }
  ]
}
```

### IP白名单管理接口

#### 获取所有IP白名单
**GET** `/whitelist/list`

#### 添加IP到白名单
**POST** `/whitelist/add`
```json
{
  "ip_address": "192.168.1.100",
  "description": "内网服务器"
}
```

#### 从白名单移除IP
**DELETE** `/whitelist/remove/{ip_address}`

#### 更新IP描述
**PUT** `/whitelist/update/{ip_address}`
```json
{
  "ip_address": "192.168.1.100",
  "description": "更新后的描述"
}
```

#### 刷新缓存
**POST** `/whitelist/refresh-cache`

#### 获取缓存信息
**GET** `/whitelist/cache-info`

### 健康检查接口

**GET** `/health`

检查服务状态

**响应示例：**
```json
{
  "status": "ok"
}
```

## 限流说明

- OCR接口限制：每分钟最多10次请求
- 超过限制将返回429状态码

## 项目结构

```
aukey-finance-ocr-identify/
├── app/
│   ├── api/                 # API路由
│   ├── core/               # 核心配置
│   ├── models/             # 数据模型
│   ├── ocr_models/         # OCR模型文件
│   └── services/           # 业务逻辑
├── init_db.py              # 数据库初始化
├── run.py                  # 启动脚本
└── requirements.txt        # 依赖包
```

## 注意事项

### 1. 首次运行
- 首次启动时会自动下载OCR模型文件，可能需要几分钟时间
- 确保网络连接正常，模型文件较大

### 2. 内存要求
- PaddleOCR模型需要较大内存，建议至少2GB可用内存
- 如果内存不足，可以考虑使用轻量级模型

### 3. 文件权限
- 确保应用有权限创建和写入`results`目录
- 上传的文件会临时存储在系统临时目录

### 4. 性能优化
- 生产环境建议使用多进程模式启动
- 可以配置反向代理（如Nginx）进行负载均衡
- 考虑使用Redis等缓存系统提升性能

### 5. 安全考虑
- 生产环境请修改默认的API密钥
- 建议配置HTTPS
- 定期更新依赖包

## 故障排除

### 常见问题

1. **模型下载失败**
   - 检查网络连接
   - 尝试手动下载模型文件到`app/ocr_models/`目录
   V3
   模型下载地址：https://github.com/PaddlePaddle/PaddleOCR/blob/e878b023c31531c701c8482b2042cdcb94e241e7/docs/version3.x/model_list.md
   https://github.com/PaddlePaddle/PaddleOCR/blob/de17179186dcb9b1ee0773578445180a48a51c7c/docs/version3.x/module_usage/text_detection.md

   V2
   https://github.com/PaddlePaddle/PaddleOCR/blob/de17179186dcb9b1ee0773578445180a48a51c7c/docs/version2.x/model/index.md

2. **内存不足**
   - 增加系统内存
   - 使用更轻量的OCR模型

3. **端口被占用**
   - 修改`run.py`中的端口号
   - 或使用`--port`参数指定其他端口

4. **依赖安装失败**
   - 确保Python版本兼容（3.10）
   - 尝试升级pip：`pip install --upgrade pip`

## 开发说明

### 添加新的API接口

1. 在`app/api/`目录下创建新的路由文件
2. 在`app/main.py`中注册路由
3. 在`app/services/`中实现业务逻辑

### 自定义OCR模型

1. 将模型文件放入`app/ocr_models/`目录
2. 修改`app/services/ocr_service.py`中的模型路径
3. 重启服务
