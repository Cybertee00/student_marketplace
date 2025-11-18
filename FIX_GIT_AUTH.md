# 🔐 Fix Git Authentication Issue

## Problem
Git is trying to use credentials for `Tumelo02` but your repository is under `Cybertee00`.

## Solution Options

### **Option 1: Use SSH (Recommended)**

1. **Generate SSH key (if you don't have one):**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
   (Press Enter to accept default location)

2. **Add SSH key to GitHub:**
   - Copy your public key: `cat ~/.ssh/id_ed25519.pub` (or `id_rsa.pub`)
   - Go to GitHub → Settings → SSH and GPG keys → New SSH key
   - Paste the key and save

3. **Change remote to SSH:**
   ```bash
   git remote set-url origin git@github.com:Cybertee00/student_marketplace.git
   ```

4. **Push again:**
   ```bash
   git push -u origin main
   ```

---

### **Option 2: Use Personal Access Token (HTTPS)**

1. **Create Personal Access Token:**
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token (classic)
   - Select scopes: `repo` (full control)
   - Copy the token (you'll only see it once!)

2. **Update remote URL with token:**
   ```bash
   git remote set-url origin https://YOUR_TOKEN@github.com/Cybertee00/student_marketplace.git
   ```
   (Replace `YOUR_TOKEN` with your actual token)

3. **Push:**
   ```bash
   git push -u origin main
   ```

---

### **Option 3: Clear Cached Credentials (Windows)**

1. **Clear Windows Credential Manager:**
   - Press `Win + R`, type `control /name Microsoft.CredentialManager`
   - Go to "Windows Credentials"
   - Find any GitHub entries and remove them

2. **Push again (will prompt for credentials):**
   ```bash
   git push -u origin main
   ```
   - Username: `Cybertee00`
   - Password: Use your Personal Access Token (not your GitHub password)

---

## Quick Fix (Try This First)

If you're logged into GitHub Desktop or have GitHub CLI:

```bash
# Try using GitHub CLI
gh auth login
gh repo set-default Cybertee00/student_marketplace
git push -u origin main
```

Or manually authenticate when pushing - Git will prompt you for credentials.

