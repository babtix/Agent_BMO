# Tests Organization

## 📁 Test Structure

All test scripts have been organized into the `tests/` folder for better maintainability.

## 🔄 What Changed

### Before
```
project/
├── test_gui.py              # Root level
├── test_installation.py     # Root level
├── verify_paths.py          # Root level
└── v3/
    └── test_gui.py          # V3 specific
```

### After
```
project/
├── tests/                   # All tests organized
│   ├── __init__.py
│   ├── README.md
│   ├── run_all_tests.py    # Test runner
│   ├── test_gui_root.py    # Renamed from root test_gui.py
│   ├── test_v3_gui.py      # Moved from v3/
│   ├── test_installation.py
│   └── verify_paths.py
├── v1/
├── v2/
└── v3/                      # No more test files here
```

## 📝 Files Moved

### From Root Directory
1. **test_gui.py** → **tests/test_gui_root.py**
   - Renamed to clarify it tests root-level functionality
   - Updated imports to work from tests/ folder
   - Updated config paths to `../config.json`

2. **test_installation.py** → **tests/test_installation.py**
   - Updated all path references to use `project_root`
   - Fixed imports to work from tests/ folder
   - Added encoding parameter to file operations

3. **verify_paths.py** → **tests/verify_paths.py**
   - Updated all path references to use `project_root`
   - Fixed imports to work from tests/ folder
   - Added encoding parameter to file operations

### From v3/ Directory
4. **v3/test_gui.py** → **tests/test_v3_gui.py**
   - Updated imports to access v3/core modules
   - Updated config paths to `../v3/config.json`
   - Fixed sys.path to include v3 directory

## 🔧 Import Path Updates

### All Tests Now Use Project Root

```python
# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

### V3 Tests Access V3 Modules

```python
# Add v3 directory to path for core modules
v3_dir = Path(__file__).parent.parent / 'v3'
sys.path.insert(0, str(v3_dir))
```

### Configuration Paths

```python
# V3 config
config_path = Path(__file__).parent.parent / 'v3' / 'config.json'

# Root config
config_path = Path(__file__).parent.parent / 'config.json'

# V1/V2 config
config_path = project_root / 'v1' / 'config.json'
```

## 📚 New Files Created

### 1. tests/__init__.py
Makes tests a proper Python package.

### 2. tests/README.md
Complete documentation for the test suite:
- How to run tests
- What's tested
- Test requirements
- Troubleshooting
- Adding new tests

### 3. tests/run_all_tests.py
Automated test runner:
- Runs all tests in sequence
- Captures output
- Provides summary
- Returns proper exit codes

## 🚀 Running Tests

### Run All Tests
```cmd
python tests/run_all_tests.py
```

### Run Individual Tests
```cmd
python tests/test_v3_gui.py
python tests/test_installation.py
python tests/test_gui_root.py
python tests/verify_paths.py
```

### From Any Directory
Tests work from any directory because they use absolute paths:
```cmd
cd v3
python ../tests/test_v3_gui.py

cd tests
python test_installation.py
```

## ✅ Verification

### Test Import Paths
All tests now correctly:
- ✅ Find project root
- ✅ Import core modules
- ✅ Load configuration files
- ✅ Access version-specific code

### Test Execution
All tests can be run:
- ✅ From project root
- ✅ From tests/ directory
- ✅ From any subdirectory
- ✅ Via test runner

## 📊 Test Coverage

### What's Tested
- ✅ Package imports (PyQt6, groq, ollama, etc.)
- ✅ Configuration loading (all versions)
- ✅ Core modules (ConfigManager, AudioManager, etc.)
- ✅ GUI framework (PyQt6 QApplication)
- ✅ Path resolution (all versions)
- ✅ Environment variables (API keys)

### Test Files
1. **test_v3_gui.py** (4 tests)
   - Import verification
   - Config loading
   - Core modules
   - GUI framework

2. **test_installation.py** (3 tests)
   - V1 installation
   - V2 installation
   - Environment setup

3. **test_gui_root.py** (4 tests)
   - Root-level imports
   - Root config
   - Root core modules
   - GUI framework

4. **verify_paths.py** (3 verifications)
   - V1 path resolution
   - V2 path resolution
   - Config file access

## 🎯 Benefits

### Organization
- ✅ All tests in one place
- ✅ Easy to find
- ✅ Clear structure
- ✅ Better navigation

### Maintainability
- ✅ Single location to update
- ✅ Consistent import patterns
- ✅ Proper path handling
- ✅ Easy to add new tests

### Execution
- ✅ Test runner for all tests
- ✅ Individual test execution
- ✅ Works from any directory
- ✅ CI/CD ready

## 🔍 Code Changes

### Example: test_v3_gui.py

**Before:**
```python
sys.path.insert(0, str(Path(__file__).parent))
config_path = Path(__file__).parent / 'config.json'
```

**After:**
```python
v3_dir = Path(__file__).parent.parent / 'v3'
sys.path.insert(0, str(v3_dir))
config_path = Path(__file__).parent.parent / 'v3' / 'config.json'
```

### Example: test_installation.py

**Before:**
```python
config_path = Path("v1/config.json")
sys.path.insert(0, "v1")
```

**After:**
```python
project_root = Path(__file__).parent.parent
config_path = project_root / "v1" / "config.json"
sys.path.insert(0, str(project_root / "v1"))
```

## 📝 Updated Documentation

### Main README.md
Added testing section:
```markdown
## 🧪 Testing

Run the test suite to verify your installation:
```cmd
python tests/run_all_tests.py
```

### tests/README.md
Complete test documentation:
- Test descriptions
- Running instructions
- Requirements
- Troubleshooting
- Best practices

## 🔄 CI/CD Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pip install -r v3/requirements.txt
    python tests/run_all_tests.py
```

## 🎓 Adding New Tests

### Create New Test
1. Create file in `tests/` directory
2. Name it `test_*.py` or `*_test.py`
3. Add proper path handling:

```python
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_something():
    """Test description"""
    # Your test code
    pass

if __name__ == "__main__":
    test_something()
```

4. Add to `run_all_tests.py`:

```python
tests = [
    ("Your Test", "test_your_test.py"),
    # ... other tests
]
```

## ✅ Verification Checklist

After organization:
- [x] All test files moved to tests/
- [x] Import paths updated
- [x] Config paths updated
- [x] Tests run successfully
- [x] Test runner created
- [x] Documentation updated
- [x] README.md updated
- [x] All tests pass

## 🎉 Summary

All test scripts are now organized in the `tests/` folder with:
- ✅ 7 files (4 tests + 3 support files)
- ✅ Proper import path handling
- ✅ Updated configuration paths
- ✅ Test runner for automation
- ✅ Complete documentation
- ✅ CI/CD ready

**Run tests:** `python tests/run_all_tests.py`

---

**Organization Date**: 2026-02-20  
**Total Files Moved**: 4 files  
**New Files Created**: 3 files  
**Status**: Complete ✅
