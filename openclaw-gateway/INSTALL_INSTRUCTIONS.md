# Installation Instructions

## ✅ Fixed: Virtual Environment Support

The installation script has been updated to work with externally-managed Python environments (Debian/Ubuntu systems).

---

## Quick Installation

### Step 1: Run the installer

```bash
cd ~/Gemini-API/openclaw-gateway
./install.sh
```

This will:

- ✅ Create a Python virtual environment (`venv/`)
- ✅ Install parent Gemini-API dependencies
- ✅ Install gateway dependencies
- ✅ Create `.env` file from template
- ✅ Create temp directory

### Step 2: Configure your Gemini cookies

Edit the `.env` file:

```bash
nano .env
```

Add your cookies (get from gemini.google.com):

```bash
GEMINI_SECURE_1PSID=your_cookie_value_here
GEMINI_SECURE_1PSIDTS=your_cookie_value_here
```

### Step 3: Run the server

**Option A: Using the run script (easiest)**

```bash
./run.sh
```

**Option B: Manual activation**

```bash
source venv/bin/activate
python api_server.py
```

### Step 4: Test

```bash
curl http://localhost:18080/health
```

You should see:

```json
{"status":"ok","service":"gemini-openclaw-gateway","version":"1.0.0"}
```

---

## What Changed

### Before (didn't work on Ubuntu/Debian)

```bash
pip install -r requirements.txt  # ❌ Error: externally-managed-environment
```

### After (works everywhere)

```bash
./install.sh  # ✅ Creates venv automatically
```

---

## Files Created

After installation, you'll have:

```
openclaw-gateway/
├── venv/                  # Virtual environment (NEW)
│   ├── bin/
│   ├── lib/
│   └── ...
├── .env                   # Your configuration (created from template)
└── ... (other files)
```

---

## Running the Server

### Development Mode

```bash
./run.sh --reload
```

Or manually:

```bash
source venv/bin/activate
python api_server.py --reload
```

### Production Mode

```bash
./run.sh --host 0.0.0.0 --port 18080
```

### With Docker (no venv needed)

```bash
docker-compose up -d
```

---

## Troubleshooting

### "venv not found"

Run the installer:

```bash
./install.sh
```

### "Permission denied: ./install.sh"

Make it executable:

```bash
chmod +x install.sh run.sh
```

### Still getting "externally-managed-environment"

Make sure you're using the updated `install.sh` script. If you see the error, the script should handle it automatically by creating a venv.

### Import errors when running

Make sure venv is activated:

```bash
source venv/bin/activate
```

Or use the run script:

```bash
./run.sh
```

---

## Deactivating Virtual Environment

When you're done:

```bash
deactivate
```

---

## Complete Example Session

```bash
# 1. Install
cd ~/Gemini-API/openclaw-gateway
./install.sh

# 2. Configure
nano .env
# (add your cookies)

# 3. Run
./run.sh

# In another terminal:
# 4. Test
curl -X POST http://localhost:18080/v1/responses \
  -H "Content-Type: application/json" \
  -d '{"model": "gemini-3-pro", "input": "Hello!"}'

# 5. When done, stop server (Ctrl+C) and deactivate
deactivate
```

---

## Next Steps

- ✅ Installation complete
- ✅ Server running
- 📖 Read [README.md](README.md) for full documentation
- 💡 Check [EXAMPLES.md](EXAMPLES.md) for usage examples
- 🚀 Integrate with OpenClaw (see [QUICKSTART.md](QUICKSTART.md))
