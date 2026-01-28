# Troubleshooting Guide - Clinical Protocol AI

## Common Issues and Solutions

### 🚨 **Backend Issues**

#### **1. Ollama Connection Error**
**Error**: `Connection refused to localhost:11434`

**Solutions**:
```bash
# Check if Ollama is running
ollama list

# Start Ollama if not running
ollama serve

# Check if model is available
ollama pull llama3.1:latest

# Test Ollama directly
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:latest",
  "prompt": "Hello",
  "stream": false
}'
```

#### **2. Model Not Found Error**
**Error**: `Model 'llama3.1:latest' not found`

**Solutions**:
```bash
# Pull the required model
ollama pull llama3.1:latest

# List available models
ollama list

# If using different model, update backend/llm_client.py
MODEL = "your-model-name"
```

#### **3. ChromaDB Permission Error**
**Error**: `Permission denied: chroma_db`

**Solutions**:
```bash
# Fix permissions
sudo chown -R $USER:$USER chroma_db/
chmod -R 755 chroma_db/

# Or delete and recreate
rm -rf chroma_db/
# Restart backend to recreate
```

#### **4. PDF Upload Fails**
**Error**: `Failed to process PDF`

**Solutions**:
- Check file size (max 50MB)
- Ensure file is a valid PDF
- Check disk space
- Verify PyMuPDF installation:
```bash
pip install --upgrade PyMuPDF
```

#### **5. Memory Issues**
**Error**: `Out of memory` or slow performance

**Solutions**:
```bash
# Check memory usage
free -h

# Reduce chunk size in text_chunker.py
CHUNK_SIZE = 500  # Reduce from 1000

# Restart with fewer workers
gunicorn main:app --workers 2
```

### 🖥️ **Frontend Issues**

#### **1. CORS Error**
**Error**: `Access to fetch blocked by CORS policy`

**Solutions**:
- Ensure backend CORS is configured:
```python
# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### **2. API Connection Failed**
**Error**: `Network Error` or `Connection refused`

**Solutions**:
```bash
# Check backend is running
curl http://localhost:8000/health

# Check frontend API configuration
# In frontend/src/services/api.js
const API_BASE_URL = 'http://localhost:8000';
```

#### **3. Build Fails**
**Error**: `npm run build` fails

**Solutions**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 16+

# Fix dependency issues
npm audit fix
```

#### **4. Chat Not Responding**
**Error**: Chat interface shows loading but no response

**Solutions**:
1. Check browser console for errors
2. Verify document is uploaded
3. Check backend logs
4. Test API directly:
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'
```

#### **5. Document Analysis Timeout**
**Error**: Analysis takes too long or times out

**Solutions**:
- Increase timeout in `api.js`:
```javascript
const api = axios.create({
  timeout: 300000, // 5 minutes
});
```
- Check backend processing logs
- Ensure sufficient memory

### 🔧 **Installation Issues**

#### **1. Python Dependencies**
**Error**: `pip install` fails

**Solutions**:
```bash
# Update pip
pip install --upgrade pip

# Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install with verbose output
pip install -r requirements.txt -v
```

#### **2. Node.js Dependencies**
**Error**: `npm install` fails

**Solutions**:
```bash
# Clear npm cache
npm cache clean --force

# Use specific Node version
nvm install 16
nvm use 16

# Try yarn instead
npm install -g yarn
yarn install
```

#### **3. Ollama Installation**
**Error**: Ollama not found

**Solutions**:
```bash
# Install Ollama (Linux/Mac)
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai/download

# Verify installation
ollama --version
```

### 📊 **Performance Issues**

#### **1. Slow Response Times**
**Symptoms**: API calls take >30 seconds

**Solutions**:
1. **Check system resources**:
```bash
htop  # Check CPU/memory usage
df -h # Check disk space
```

2. **Optimize backend**:
```python
# Reduce chunk overlap in text_chunker.py
CHUNK_OVERLAP = 50  # Reduce from 200

# Use smaller embedding model
# In embeddings.py - consider lighter models
```

3. **Database optimization**:
```bash
# Reset vector database if corrupted
rm -rf chroma_db/
# Re-upload document
```

#### **2. High Memory Usage**
**Symptoms**: System becomes unresponsive

**Solutions**:
1. **Monitor memory**:
```bash
# Check memory usage
ps aux | grep python
ps aux | grep node
```

2. **Optimize settings**:
```python
# In new_rag_system.py
# Reduce concurrent processing
max_workers=2  # Instead of 3
```

3. **System limits**:
```bash
# Increase swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 🔍 **Debugging Tools**

#### **1. Backend Debugging**
```python
# Add debug logging in main.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual components
python -c "from new_rag_system import answer_question_new; print(answer_question_new('test'))"
```

#### **2. Frontend Debugging**
```javascript
// Enable debug mode in api.js
const DEBUG = true;

// Check browser console
// Open Developer Tools (F12)
// Look for errors in Console tab
```

#### **3. Network Debugging**
```bash
# Check port availability
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# Test connectivity
telnet localhost 8000
telnet localhost 11434
```

### 🚀 **Quick Fixes**

#### **Complete Reset**
If all else fails, try a complete reset:

```bash
# 1. Stop all services
pkill -f "python main.py"
pkill -f "npm start"

# 2. Clean databases
rm -rf chroma_db/
rm -rf frontend/node_modules/

# 3. Reinstall dependencies
cd backend && pip install -r requirements.txt
cd frontend && npm install

# 4. Restart services
python backend/main.py &
cd frontend && npm start
```

#### **Health Check Script**
Create `health_check.sh`:
```bash
#!/bin/bash
echo "🔍 Clinical Protocol AI Health Check"
echo "=================================="

# Check Ollama
echo -n "Ollama: "
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

# Check Backend
echo -n "Backend: "
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

# Check Frontend
echo -n "Frontend: "
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

# Check disk space
echo -n "Disk Space: "
USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $USAGE -lt 90 ]; then
    echo "✅ OK ($USAGE% used)"
else
    echo "⚠️  Low ($USAGE% used)"
fi

# Check memory
echo -n "Memory: "
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEM_USAGE -lt 90 ]; then
    echo "✅ OK ($MEM_USAGE% used)"
else
    echo "⚠️  High ($MEM_USAGE% used)"
fi
```

### 📞 **Getting Help**

#### **1. Log Collection**
Before asking for help, collect these logs:
```bash
# Backend logs
python backend/main.py > backend.log 2>&1 &

# Frontend logs (browser console)
# Right-click → Inspect → Console → Copy all

# System logs
dmesg | tail -50
journalctl --since "1 hour ago"
```

#### **2. System Information**
```bash
# Collect system info
echo "OS: $(uname -a)"
echo "Python: $(python --version)"
echo "Node: $(node --version)"
echo "Memory: $(free -h)"
echo "Disk: $(df -h)"
echo "Ollama: $(ollama --version)"
```

#### **3. Test Commands**
Run these tests and share results:
```bash
# Test 1: Basic connectivity
curl http://localhost:8000/health

# Test 2: Ollama
curl http://localhost:11434/api/tags

# Test 3: Chat API
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'

# Test 4: Frontend build
cd frontend && npm run build
```

### 🔧 **Advanced Troubleshooting**

#### **1. Database Corruption**
If ChromaDB becomes corrupted:
```bash
# Backup current database
cp -r chroma_db chroma_db_backup

# Reset database
rm -rf chroma_db

# Re-upload document to recreate
```

#### **2. Model Issues**
If LLM responses are poor:
```bash
# Try different model
ollama pull llama3.1:8b
# Update MODEL in backend/llm_client.py

# Or use different provider
# Update llm_client.py to use OpenAI/Anthropic
```

#### **3. Performance Profiling**
```python
# Add profiling to backend
import cProfile
import pstats

def profile_function():
    pr = cProfile.Profile()
    pr.enable()
    # Your code here
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats()
```

Remember: Most issues are resolved by ensuring all services are running and properly configured. When in doubt, restart everything! 🔄