# Google Drive Setup for ROBUST04 Notebooks

## Add This Cell at the Beginning of Each Notebook

Copy and paste this code as the **FIRST CODE CELL** in any of your ROBUST04 notebooks:

```python
# ============================================================================
# GOOGLE DRIVE SETUP - Add this as the first cell in your notebook
# ============================================================================

import os
import sys

# Check if running in Google Colab
try:
    import google.colab
    IN_COLAB = True
    print("✓ Running in Google Colab")
except:
    IN_COLAB = False
    print("✓ Running locally")

# Mount Google Drive if in Colab
if IN_COLAB:
    print("\nMounting Google Drive...")
    from google.colab import drive
    drive.mount('/content/drive')
    print("✓ Google Drive mounted")

    # Set base directory (change this to your folder path in Google Drive)
    BASE_DIR = '/content/drive/MyDrive/ROBUST04'

    # Check if directory exists
    if os.path.exists(BASE_DIR):
        print(f"✓ Found directory: {BASE_DIR}")
        os.chdir(BASE_DIR)
        print(f"✓ Changed to: {os.getcwd()}")
    else:
        print(f"⚠ Directory not found: {BASE_DIR}")
        print(f"  Current directory: {os.getcwd()}")
        print("\n📝 Please update BASE_DIR to match your Google Drive folder structure")
        print("   Example: '/content/drive/MyDrive/YourFolder/ROBUST04'")
else:
    # Running locally - files should be in current directory
    BASE_DIR = os.getcwd()
    print(f"Working directory: {BASE_DIR}")

# Define file paths
QUERIES_FILE = 'queriesROBUST.txt'
QRELS_FILE = 'qrels_50_Queries'

# Verify files exist
print("\n📁 Checking for required files...")
if os.path.exists(QUERIES_FILE):
    print(f"  ✓ Found: {QUERIES_FILE}")
else:
    print(f"  ✗ Missing: {QUERIES_FILE}")

if os.path.exists(QRELS_FILE):
    print(f"  ✓ Found: {QRELS_FILE}")
else:
    print(f"  ✗ Missing: {QRELS_FILE}")

# List files in directory
print(f"\n📂 Files in {os.getcwd()}:")
files = [f for f in os.listdir('.') if not f.startswith('.')]
for f in files[:10]:  # Show first 10 files
    print(f"  - {f}")
if len(files) > 10:
    print(f"  ... and {len(files) - 10} more files")

print("\n" + "="*70)
print("Setup complete! You can now run the notebook cells below.")
print("="*70)
```

---

## Alternative: Direct Upload Method (if files not in Drive)

If you don't have the files in Google Drive yet, use this instead:

```python
# ============================================================================
# DIRECT FILE UPLOAD - Use this if you want to upload files directly
# ============================================================================

import os

# Check if running in Colab
try:
    import google.colab
    IN_COLAB = True
    print("✓ Running in Google Colab")

    # Check if files already exist
    if not os.path.exists('queriesROBUST.txt') or not os.path.exists('qrels_50_Queries'):
        print("\n📤 Please upload your files:")
        print("  1. queriesROBUST.txt")
        print("  2. qrels_50_Queries")
        print("\nClick the button below to select files from your computer:")

        from google.colab import files
        uploaded = files.upload()

        print("\n✓ Files uploaded successfully!")
    else:
        print("✓ Files already present in workspace")

except:
    IN_COLAB = False
    print("✓ Running locally")
    print(f"Working directory: {os.getcwd()}")

# Verify files exist
print("\n📁 Checking for required files...")
QUERIES_FILE = 'queriesROBUST.txt'
QRELS_FILE = 'qrels_50_Queries'

if os.path.exists(QUERIES_FILE):
    print(f"  ✓ Found: {QUERIES_FILE}")
    with open(QUERIES_FILE, 'r') as f:
        num_lines = len(f.readlines())
    print(f"    Contains {num_lines} queries")
else:
    print(f"  ✗ Missing: {QUERIES_FILE}")

if os.path.exists(QRELS_FILE):
    print(f"  ✓ Found: {QRELS_FILE}")
    with open(QRELS_FILE, 'r') as f:
        num_lines = len(f.readlines())
    print(f"    Contains {num_lines} relevance judgments")
else:
    print(f"  ✗ Missing: {QRELS_FILE}")

print("\n" + "="*70)
print("Setup complete! You can now run the notebook cells below.")
print("="*70)
```

---

## Alternative: Download from URL (if files are hosted online)

```python
# ============================================================================
# DOWNLOAD FROM URL - Use this if files are on a web server
# ============================================================================

import os
import urllib.request

# Check if running in Colab
try:
    import google.colab
    IN_COLAB = True
    print("✓ Running in Google Colab")
except:
    IN_COLAB = False
    print("✓ Running locally")

# File URLs (replace with your actual URLs)
QUERIES_URL = "https://your-server.com/queriesROBUST.txt"
QRELS_URL = "https://your-server.com/qrels_50_Queries"

QUERIES_FILE = 'queriesROBUST.txt'
QRELS_FILE = 'qrels_50_Queries'

def download_file(url, filename):
    """Download file from URL if it doesn't exist."""
    if not os.path.exists(filename):
        print(f"📥 Downloading {filename}...")
        try:
            urllib.request.urlretrieve(url, filename)
            print(f"  ✓ Downloaded: {filename}")
            return True
        except Exception as e:
            print(f"  ✗ Error downloading {filename}: {e}")
            return False
    else:
        print(f"  ✓ File already exists: {filename}")
        return True

# Download files
print("Checking/downloading required files...\n")
download_file(QUERIES_URL, QUERIES_FILE)
download_file(QRELS_URL, QRELS_FILE)

# Verify files
print("\n📁 Verifying files...")
if os.path.exists(QUERIES_FILE) and os.path.exists(QRELS_FILE):
    print("✓ All files ready!")
else:
    print("✗ Some files are missing. Please check the URLs and try again.")

print("\n" + "="*70)
print("Setup complete! You can now run the notebook cells below.")
print("="*70)
```

---

## How to Use

### Method 1: Google Drive (Recommended for Colab)
1. Upload your files to Google Drive in a folder like `My Drive/ROBUST04/`
2. Add the first code cell above to your notebook
3. Update the `BASE_DIR` path to match your folder structure
4. Run the cell - it will mount Drive and verify files

### Method 2: Direct Upload
1. Add the second code cell to your notebook
2. Run it - you'll get an upload button
3. Select `queriesROBUST.txt` and `qrels_50_Queries` from your computer
4. Files will be uploaded to the Colab workspace

### Method 3: Download from URL
1. Host your files on a web server or cloud storage
2. Add the third code cell with your URLs
3. Run it - files will be downloaded automatically

---

## Quick Reference: Google Drive Folder Structure

```
My Drive/
└── ROBUST04/                    ← Your data folder
    ├── queriesROBUST.txt       ← 249 queries
    ├── qrels_50_Queries         ← Relevance judgments
    ├── run_1.res                ← Output (generated)
    ├── run_2.res                ← Output (generated)
    └── run_3.res                ← Output (generated)
```

**Path to use in code**: `/content/drive/MyDrive/ROBUST04`

---

## Troubleshooting

### "Directory not found"
- Check the exact path in Google Drive
- Common paths:
  - `/content/drive/MyDrive/ROBUST04`
  - `/content/drive/MyDrive/Colab Notebooks/ROBUST04`
  - `/content/drive/My Drive/ROBUST04` (with space)

### "Permission denied"
- Make sure you clicked "Connect to Google Drive" when prompted
- Try remounting: `drive.mount('/content/drive', force_remount=True)`

### Files not showing up
- Refresh your Google Drive
- Check the exact file names (case-sensitive!)
- Run: `!ls -la` to see all files in current directory

---

## Which Method Should You Use?

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Google Drive** | Regular use, multiple sessions | Persistent, easy to access | Requires Drive setup |
| **Direct Upload** | Quick testing, one-time use | Simple, no Drive needed | Lost when runtime ends |
| **URL Download** | Shared access, automation | Reproducible, no manual upload | Need to host files |

**Recommendation**: Use Google Drive method for this competition - it's the most reliable for long-running notebooks!
