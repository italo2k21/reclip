# ReClip Installation Guide for Ubuntu 24.04 (HP Mini-PC with M3 Mac Access)

**Version:** 1.0  
**Last Updated:** 2026-05-10  
**Target System:** Ubuntu 24.04 LTS on HP Mini-PC  
**Access:** From Apple Mac M3 and other devices on network

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Detailed Installation Steps](#detailed-installation-steps)
4. [Network Access Setup](#network-access-setup)
5. [Running as a Background Service](#running-as-a-background-service)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)
8. [Uninstall](#uninstall)

---

## 🚀 Quick Start

If you're in a hurry, run these commands in sequence on your Ubuntu Mini-PC:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv ffmpeg git

# Clone and run
cd ~
git clone https://github.com/averygan/reclip.git
cd reclip
chmod +x reclip.sh
./reclip.sh
```

Then access from your Mac: **http://[MINI-PC-IP]:8899**

---

## ✅ Prerequisites

Before you begin, ensure you have:

- **OS:** Ubuntu 24.04 LTS (or similar Debian-based distro)
- **RAM:** 2GB minimum (you have 8GB ✅)
- **Storage:** 500MB free space for installation (videos go to `downloads/` folder)
- **Network:** Connected to same network as Mac M3
- **Access:** SSH or direct terminal access to Mini-PC

### Check your specs:
```bash
# Check Ubuntu version
lsb_release -a

# Check RAM available
free -h

# Check disk space
df -h
```

---

## 📝 Detailed Installation Steps

### **Step 1: Update Your System (Important!)**

```bash
sudo apt update
sudo apt upgrade -y
```

**What this does:**
- Updates package lists
- Installs security patches
- Takes 5-10 minutes

**Expected output:**
```
Reading package lists... Done
Building dependency tree... Done
0 upgraded, 0 newly installed, 0 to remove
```

---

### **Step 2: Install Required Dependencies**

```bash
sudo apt install -y python3-pip python3-venv ffmpeg git
```

**Breakdown:**
- `python3-pip` - Python package installer
- `python3-venv` - Virtual environments for Python
- `ffmpeg` - Video conversion engine
- `git` - Version control (to clone ReClip)

**Takes:** 2-5 minutes

**Verify installation:**
```bash
python3 --version      # Should show Python 3.x.x
pip3 --version         # Should show pip version
ffmpeg -version        # Should show FFmpeg version
git --version          # Should show git version
```

---

### **Step 3: Clone ReClip Repository**

```bash
cd ~
git clone https://github.com/averygan/reclip.git
cd reclip
ls -la
```

**What this does:**
- Creates `~/reclip/` directory
- Downloads all ReClip files

**Expected files:**
```
app.py
reclip.sh
requirements.txt
templates/
Dockerfile
README.md
LICENSE
```

---

### **Step 4: Make the Script Executable**

```bash
chmod +x reclip.sh
```

---

### **Step 5: Run ReClip**

```bash
./reclip.sh
```

**What happens:**
1. Script checks for Python, ffmpeg, yt-dlp
2. Creates a virtual environment (`venv/`)
3. Installs Flask and yt-dlp via pip
4. Starts the web server

**Expected output:**
```
Setting up virtual environment...
Collecting flask
Collecting yt-dlp
Installing collected packages: flask, yt-dlp
Successfully installed flask-x.x.x yt-dlp-xxxx.xx.xx

  ReClip is running at http://localhost:8899
```

**ReClip is now RUNNING!** ✅

---

## 🌐 Network Access Setup

### **From Your Mac M3:**

#### **Step 1: Find Mini-PC IP Address**

On the Mini-PC, run:
```bash
hostname -I
```

Example output:
```
192.168.1.100
```

#### **Step 2: Access from Mac Browser**

On your Mac, open any browser and go to:
```
http://192.168.1.100:8899
```

**You should see the ReClip web interface!** 🎉

---

### **Troubleshooting Network Access**

**Can't find Mini-PC IP?**
```bash
# On Mini-PC, try:
ip addr show

# Look for lines like: inet 192.168.x.x
```

**Connection refused?**
- Ensure ReClip is still running on Mini-PC (check terminal)
- Ensure both Mac and Mini-PC are on same WiFi network
- Check firewall: `sudo ufw allow 8899`

**Wrong IP?**
- IP can change! Set a static IP in your router or:
```bash
sudo nano /etc/netplan/01-netcfg.yaml
```

---

## 🔧 Running as a Background Service (Optional)

Want ReClip to start automatically when Mini-PC boots?

### **Step 1: Create a systemd Service File**

```bash
sudo nano /etc/systemd/system/reclip.service
```

### **Step 2: Paste This Configuration**

```ini
[Unit]
Description=ReClip Video Downloader
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/reclip
ExecStart=/home/ubuntu/reclip/reclip.sh
Restart=on-failure
RestartSec=10
Environment="PORT=8899"
Environment="HOST=0.0.0.0"

[Install]
WantedBy=multi-user.target
```

### **Step 3: Enable and Start the Service**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable reclip

# Start the service
sudo systemctl start reclip

# Check status
sudo systemctl status reclip
```

**Expected output:**
```
● reclip.service - ReClip Video Downloader
   Loaded: loaded (/etc/systemd/system/reclip.service; enabled; vendor preset: enabled)
   Active: active (running) since ...
```

### **Service Commands:**

```bash
# Check if running
sudo systemctl status reclip

# Stop the service
sudo systemctl stop reclip

# Restart the service
sudo systemctl restart reclip

# View logs
sudo journalctl -u reclip -f

# Disable on boot
sudo systemctl disable reclip
```

---

## 📁 Directory Structure

```
/home/ubuntu/reclip/
├── app.py                    # Flask backend (~150 lines)
├── reclip.sh                 # Startup script
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── README.md                 # Original README
├── LICENSE                   # MIT License
├── templates/
│   └── index.html            # Web UI (single file)
├── downloads/                # Created on first run
│   ├── [video_id_1].mp4
│   ├── [video_id_2].mp3
│   └── ...
└── venv/                     # Virtual environment (created by reclip.sh)
    └── lib/python3.x/site-packages/
```

---

## 🐛 Troubleshooting

### **Issue: "yt-dlp: command not found"**

**Solution:**
```bash
pip install yt-dlp
./reclip.sh
```

---

### **Issue: "ffmpeg: command not found"**

**Solution:**
```bash
sudo apt install -y ffmpeg
./reclip.sh
```

---

### **Issue: Port 8899 already in use**

**Solution 1 - Use different port:**
```bash
PORT=9000 ./reclip.sh
# Access at http://[IP]:9000
```

**Solution 2 - Find and stop the process using port 8899:**
```bash
sudo lsof -i :8899
# Note the PID, then:
sudo kill -9 [PID]
./reclip.sh
```

---

### **Issue: Permission denied on reclip.sh**

**Solution:**
```bash
chmod +x reclip.sh
./reclip.sh
```

---

### **Issue: Can't access from Mac (connection refused)**

**Check if ReClip is running:**
```bash
curl http://localhost:8899
# Should show HTML output
```

**Check network connectivity:**
```bash
# From Mac:
ping 192.168.1.100
# Should get responses
```

**Check firewall:**
```bash
sudo ufw status
sudo ufw allow 8899
```

---

### **Issue: Storage filling up**

**Check disk usage:**
```bash
du -sh ~/reclip/downloads/
df -h
```

**Delete old downloads:**
```bash
rm -rf ~/reclip/downloads/*
```

**Or move to external storage:**
```bash
# Connect external drive, then:
mv ~/reclip/downloads/* /mnt/external-drive/
```

---

## 🧹 Maintenance

### **Update ReClip**

```bash
cd ~/reclip
git pull origin main
./reclip.sh
```

### **Update yt-dlp** (important for new site support)

```bash
pip install --upgrade yt-dlp
./reclip.sh
```

### **Check for Updates**

```bash
git log --oneline -5
# Shows recent changes
```

---

## 🗑️ Uninstall

### **Option 1: Keep Downloads, Remove Software**

```bash
# Stop if running
Ctrl + C

# Remove ReClip code only
cd ~
rm -rf reclip
```

**Keeps:** Downloaded videos  
**Removes:** ReClip application files

---

### **Option 2: Complete Uninstall (Delete Everything)**

```bash
# Stop if running
Ctrl + C

# Remove everything
cd ~
rm -rf reclip

# Optional: Remove Python dependencies
pip uninstall -y flask yt-dlp

# Optional: Remove system packages (if not used for other apps)
sudo apt remove -y ffmpeg
```

**Keeps:** Python, pip  
**Removes:** Everything related to ReClip

---

### **If Running as Service:**

```bash
# Stop the service
sudo systemctl stop reclip

# Disable on boot
sudo systemctl disable reclip

# Remove service file
sudo rm /etc/systemd/system/reclip.service
sudo systemctl daemon-reload

# Remove files
rm -rf ~/reclip
```

---

## 📊 System Resource Usage

**Typical Resource Consumption:**

| Resource | Idle | Downloading |
|----------|------|-------------|
| RAM | 50-100MB | 200-400MB |
| CPU | <1% | 30-60% |
| Disk (per video) | - | 200MB-2GB |
| Network | ~1KB/s | 1-10MB/s |

**Your Mini-PC specs (8GB RAM) is perfect!** ✅

---

## 🔐 Security Notes

1. **Local Network Only:** ReClip runs on `localhost:8899` by default
   - Not exposed to internet
   - Only accessible from your network

2. **Public Access (Advanced):**
   If you want internet access, use a reverse proxy like Nginx (not covered here)

3. **Downloaded Content:** 
   - Respect copyright laws
   - Check platform terms of service
   - Only download content you have permission to download

---

## 📞 Getting Help

**If something goes wrong:**

1. Check logs:
   ```bash
   # If running in terminal: see error messages
   # If running as service:
   sudo journalctl -u reclip -n 50
   ```

2. Check GitHub issues:
   ```
   https://github.com/averygan/reclip/issues
   ```

3. Reinstall from scratch:
   ```bash
   # Backup your downloads
   cp -r ~/reclip/downloads ~/reclip-downloads-backup
   
   # Fresh install
   rm -rf ~/reclip
   git clone https://github.com/averygan/reclip.git
   cd reclip
   ./reclip.sh
   ```

---

## 📝 Quick Reference Card

```bash
# Start ReClip
cd ~/reclip && ./reclip.sh

# Stop ReClip
Ctrl + C

# Find Mini-PC IP
hostname -I

# Access from Mac
http://[IP]:8899

# View logs (as service)
sudo journalctl -u reclip -f

# Restart service
sudo systemctl restart reclip

# Check disk usage
du -sh ~/reclip/downloads/

# Update ReClip
cd ~/reclip && git pull
```

---

## ✨ You're All Set!

Your ReClip installation on Ubuntu Mini-PC is ready to:
- ✅ Download from 1000+ websites
- ✅ Support MP4 video & MP3 audio
- ✅ Accessible from your Mac M3
- ✅ Run 24/7 without degrading your Mac
- ✅ Expand storage as needed

**Happy downloading!** 🎬🎵

---

**Version History:**
- v1.0 (2026-05-10) - Initial guide for Ubuntu 24.04 installation
