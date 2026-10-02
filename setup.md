# Setup Instructions

## 1. Create the Virtual Environment
To create an isolated Python virtual environment for the project, run the following command in the root of the project:
```powershell
python -m venv .venv
```

## 2. Allow Script Execution (Windows Only)
If you encounter a `PSSecurityException` when trying to activate the virtual environment on Windows, you need to update your PowerShell execution policy. Run this once:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
*(Type `Y` and press Enter if prompted).*

## 3. Activate the Virtual Environment
Activate the environment using the following command:

**PowerShell (Windows):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Command Prompt (Windows):**
```cmd
.\.venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```
You should now see `(.venv)` prefixed in your terminal prompt.

## 4. Install Dependencies
With the virtual environment activated, install the required packages from the `requirements.txt` file using:
```powershell
pip install -r requirements.txt
```

> **Note:** This installs PyTorch with CUDA 12.4 GPU support. The `--extra-index-url` in `requirements.txt` pulls the GPU-enabled wheels automatically.

## 5. Verify GPU Access
After installation, confirm that PyTorch can see your NVIDIA GPU:
```powershell
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}') if torch.cuda.is_available() else None"
```
You should see `CUDA available: True` and your GPU name (e.g. `NVIDIA GeForce GTX 1050`).

