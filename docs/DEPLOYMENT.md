# Deployment Guide for Different Platforms

## Standard Linux (with compilation support)

### Requirements
- Python 3.11 or 3.12
- Build tools (gcc, python-dev)

### Installation

```bash
# Clone repository
git clone https://github.com/Szumak75/qnap-img-shrink.git
cd qnap-img-shrink

# Run launcher (auto-installs dependencies)
./bin/qimgshrink --help
```

The launcher will:
1. Create virtual environment
2. Install all dependencies (including Pillow)
3. Run application

**Converter used**: Pillow-based (Converter)

---

## QNAP NAS (without compilation support)

### Prerequisites

1. **Install Entware** (if not installed):
   ```bash
   # Follow QNAP Entware installation guide
   ```

2. **Install Python 3.11+**:
   ```bash
   opkg update
   opkg install python3 python3-pip
   ```

3. **Install ImageMagick**:
   ```bash
   opkg install imagemagick
   
   # Verify installation
   which convert identify
   convert -version
   ```

### Installation

```bash
# Clone or copy project to QNAP
cd /share/homes/admin
git clone https://github.com/Szumak75/qnap-img-shrink.git
cd qnap-img-shrink

# Run launcher
./bin/qimgshrink --help
```

The launcher will:
1. Create virtual environment
2. Try to install Pillow (will fail)
3. **Automatically fallback** to requirements-minimal.txt
4. Install dependencies without Pillow
5. Run application with ImageMagick-based converter

**Converter used**: ImageMagick-based (Converter2)

### Manual Installation (if launcher fails)

```bash
cd qnap-img-shrink

# Create venv
python3 -m venv .venv
source .venv/bin/activate

# Install minimal dependencies
pip install -r requirements-minimal.txt

# Run application
python -m qimgshrink.main --help
```

---

## Docker Container

### Dockerfile with Pillow

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "-m", "qimgshrink.main"]
```

### Dockerfile with ImageMagick (Alpine)

```dockerfile
FROM python:3.11-alpine

WORKDIR /app

# Install ImageMagick and dependencies
RUN apk add --no-cache \
    imagemagick \
    git

# Copy project
COPY . /app/

# Install Python dependencies (without Pillow)
RUN pip install --no-cache-dir -r requirements-minimal.txt

ENTRYPOINT ["python", "-m", "qimgshrink.main"]
```

### Usage

```bash
# Build image
docker build -t qimgshrink .

# Run
docker run -v /path/to/images:/data qimgshrink -t

# Or use bind mount
docker run -v $(pwd)/images:/images qimgshrink
```

---

## Troubleshooting

### Pillow Installation Fails

**Symptoms:**
- Error during `pip install pillow`
- Missing compiler or headers
- Build fails with gcc errors

**Solution:**
The launcher automatically handles this by falling back to requirements-minimal.txt. Ensure ImageMagick is installed:

```bash
# Debian/Ubuntu
sudo apt-get install imagemagick

# QNAP (Entware)
opkg install imagemagick

# Alpine
apk add imagemagick

# macOS
brew install imagemagick
```

### No Converter Available

**Error message:**
```
ERROR: No image converter available!
Attempted converters:
  ✗ Pillow: No module named 'PIL'
  ✗ ImageMagick: ImageMagick 'convert' and 'identify' commands not found.
```

**Solution:**
Install either Pillow or ImageMagick:

```bash
# Option 1: Install Pillow (if build tools available)
pip install pillow

# Option 2: Install ImageMagick (no compilation needed)
apt-get install imagemagick  # or opkg/brew/apk
```

### Permission Issues on QNAP

**Symptoms:**
- Cannot create venv
- Cannot write to directories
- Permission denied errors

**Solution:**
```bash
# Ensure you're in a writable location
cd /share/homes/$(whoami)

# Or use a shared folder with proper permissions
cd /share/Public
mkdir qimgshrink
cd qimgshrink
```

### Wrong Python Version

**Error:**
```
Python 3.11 or higher not found!
```

**Solution on QNAP:**
```bash
# Install newer Python via Entware
opkg update
opkg install python3

# Or install from QNAP Club
# Visit QNAP Club store and install Python 3.11+
```

---

## Platform-Specific Notes

### QNAP QTS/QuTS

- **Location**: Use `/share/homes/admin` or shared folders
- **Persistence**: Place in a shared folder for persistence across reboots
- **Scheduler**: Use QNAP's Task Scheduler for automated runs
- **ImageMagick**: Install via Entware or QNAP Club

### Synology NAS

Similar to QNAP:
```bash
# Install Python Package via Package Center
# Install ImageMagick via Entware

cd /volume1/homes/admin
git clone ...
./bin/qimgshrink --help
```

### Raspberry Pi

Standard Linux installation works:
```bash
sudo apt-get install python3 python3-pip imagemagick
git clone ...
./bin/qimgshrink --help
```

### macOS

```bash
# Install dependencies
brew install python@3.11 imagemagick

# Clone and run
git clone ...
./bin/qimgshrink --help
```

---

## Automated Deployment

### systemd Service (Linux)

Create `/etc/systemd/system/qimgshrink.service`:

```ini
[Unit]
Description=QNAP Image Shrink Service
After=network.target

[Service]
Type=oneshot
User=imageuser
WorkingDirectory=/opt/qnap-img-shrink
ExecStart=/opt/qnap-img-shrink/bin/qimgshrink
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and run:
```bash
sudo systemctl enable qimgshrink.service
sudo systemctl start qimgshrink.service
```

### Cron Job

```bash
# Edit crontab
crontab -e

# Run daily at 2 AM
0 2 * * * /path/to/qnap-img-shrink/bin/qimgshrink >> /var/log/qimgshrink.log 2>&1
```

### QNAP Task Scheduler

1. Control Panel → System → Task Scheduler
2. Create → User Defined Script
3. Schedule: Daily at 2:00 AM
4. Script:
   ```bash
   /share/homes/admin/qnap-img-shrink/bin/qimgshrink
   ```

---

## Verification

After installation, verify setup:

```bash
# Check Python version
python3 --version

# Check converter availability
./bin/qimgshrink --help

# Test mode (no modifications)
./bin/qimgshrink -t

# Check which converter is used (in launcher output)
# Look for: "Using Pillow-based converter" or "Using ImageMagick-based converter"
```

---

## Support

For issues:
1. Check logs/error messages
2. Verify Python version (3.11+)
3. Ensure either Pillow or ImageMagick is available
4. Check file permissions
5. Open issue on GitHub with platform details

