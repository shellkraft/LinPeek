

<img src="https://github.com/user-attachments/assets/8fb086f3-341d-4383-9ae8-7e8808a6142f" width="400" alt="LinPeek Banner">

# LinPeek - Linux Post-Exploitation Toolkit
---

LinPeek is a comprehensive post-exploitation toolkit for Linux systems, designed for security professionals to assess system security, identify privilege escalation vectors, harvest credentials, and establish persistence.

## Features

- **System Enumeration**
  - SUID binary detection with GTFOBins integration
  - Container/Docker environment detection
  - Cron job analysis
  - Host environment detection (WSL, VM, etc.)

- **Privilege Escalation**
  - Kernel exploit suggester
  - Sudo permission checker
  - Writable system file detection

- **Credential Harvesting**
  - /proc filesystem scanning for secrets
  - Shell history analysis
  - SSH key discovery

- **Persistence**
  - Multiple persistence mechanism installation
  - Log cleaning capabilities

---
## Installation

```bash
git clone https://github.com/shellkraft/linpeek.git
cd LinPeek
pip install -r requirements.txt
```
---

## Usage
```
python linpeek.py [options]
```

## Options:
```bash
--enum: Basic system enumeration

--privesc: Privilege escalation checks

--creds: Credential harvesting

--persist: Persistence module
```
---

## Disclaimer
This tool is intended for legal security assessment and research purposes only. Only use on systems you have permission to test. The developers assume no liability and are not responsible for any misuse or damage caused by this program.

