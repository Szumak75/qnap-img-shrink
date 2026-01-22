# QNAP Deployment Guide

## Python3 Profile Integration

QNAP systems require sourcing a specific Python3 environment profile before running Python applications. The launcher script (`bin/qimgshrink`) handles this automatically.

### How It Works

The script sources `/etc/profile.d/python3.bash` at startup (lines 25-39):

```bash
PYTHON3_PROFILE='/etc/profile.d/python3.bash'

# Source Python3 profile if exists (QNAP specific)
if [ -f "$PYTHON3_PROFILE" ]; then
    . "$PYTHON3_PROFILE"
    
    # Explicit export for maximum compatibility
    export PATH
    [ -n "$PYTHONPATH" ] && export PYTHONPATH
    [ -n "$LD_LIBRARY_PATH" ] && export LD_LIBRARY_PATH
fi
```

### What the QNAP Profile Does

The `/etc/profile.d/python3.bash` typically contains:

```bash
_PYTHON3_QPKG_CONF=/etc/config/qpkg.conf
_PYTHON3_QPKG_NAME="Python3"
_PYTHON3_QPKG_ROOT=$(/sbin/getcfg $_PYTHON3_QPKG_NAME Install_Path -f ${_PYTHON3_QPKG_CONF})
_PYTHON3_QPKG_BIN="${_PYTHON3_QPKG_ROOT}/opt/python3/bin"
echo "${PATH}" | grep -q ${_PYTHON3_QPKG_BIN} || export PATH=${_PYTHON3_QPKG_BIN}:${PATH}
```

Key points:
- Uses helper variables (`_PYTHON3_*`) to locate Python installation
- Adds Python binary directory to PATH
- Checks if already in PATH to avoid duplicates
- **Exports PATH** - makes it available to all subprocesses

### Launcher Script Protection

The launcher explicitly re-exports PATH and other variables after sourcing:
- Ensures compatibility with profiles that don't export
- Handles optional variables (PYTHONPATH, LD_LIBRARY_PATH)
- Only exports if variable is set (non-empty)

### Why Early Sourcing?

The profile **must** be sourced **before** any Python operations:
1. ✅ **Before** `find_python()` - ensures correct Python binary is found
2. ✅ **Before** `setup_venv()` - venv creation needs proper environment
3. ✅ **Before** `check_dependencies()` - pip needs correct paths
4. ✅ **Before** running the application - runtime needs all variables

### Non-QNAP Systems

On systems without `/etc/profile.d/python3.bash`:
- File check silently fails (`if [ -f ... ]`)
- Script continues normally
- No error messages
- Standard Python environment is used

### Verification

To verify the profile is loaded on QNAP:

```bash
./bin/qimgshrink --help
```

Expected output includes:
```
[INFO] QNAP Python3 profile loaded: /etc/profile.d/python3.bash
```

### Manual Override

You can override the profile path via environment variable:

```bash
PYTHON3_PROFILE='/custom/path/python3.bash' ./bin/qimgshrink
```

### Troubleshooting

**Problem:** Python not found on QNAP despite installation

**Solution:** Verify profile exists and is sourced:
```bash
ls -la /etc/profile.d/python3.bash
cat /etc/profile.d/python3.bash
```

**Problem:** Import errors despite installed packages

**Solution:** Check PYTHONPATH after sourcing:
```bash
. /etc/profile.d/python3.bash
echo $PYTHONPATH
echo $LD_LIBRARY_PATH
```

### QNAP Installation Steps

1. Install Python3 via Entware or QPKG
2. Verify profile exists: `ls /etc/profile.d/python3.bash`
3. Clone repository to `/share/homes/admin/qnap-img-shrink` (or similar)
4. Run launcher: `./bin/qimgshrink`
5. Script auto-configures venv and dependencies

### Alternative: Manual Sourcing

If you need to run Python commands manually on QNAP:

```bash
# Always source profile first
. /etc/profile.d/python3.bash

# Then run Python
cd /share/homes/admin/qnap-img-shrink
source .venv/bin/activate
python -m qimgshrink.main --help
```

## See Also

- [DEPLOYMENT.md](DEPLOYMENT.md) - General deployment guide
- [README.md](../README.md) - Main documentation
