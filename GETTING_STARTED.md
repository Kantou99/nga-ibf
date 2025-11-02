# 🚀 Getting Started with BAY States Visualization in VS Code

Welcome! This guide will get you up and running in **5 minutes**.

---

## ⚡ Quick Start (3 Steps)

### **Step 1: Download Files**

Download these files from the outputs folder:
- ✅ `bay_states_visualizations.py` - Main script
- ✅ `requirements.txt` - Dependencies
- ✅ `custom_bay_visualizations.py` - Extension template
- ✅ `BAY_States_QuickStart.ipynb` - Jupyter notebook

### **Step 2: Install Dependencies**

```bash
# Open terminal in VS Code (Ctrl+`)
pip install -r requirements.txt
```

### **Step 3: Run It!**

```bash
python bay_states_visualizations.py
```

**🎉 Done!** Check the `outputs/` folder for 13 visualizations.

---

## 📚 Complete Guides Available

| Guide | Purpose | Time to Read |
|-------|---------|--------------|
| **GETTING_STARTED.md** (this file) | Quick 5-min start | 5 min |
| **VSCODE_SETUP_GUIDE.md** | Full setup & configuration | 20 min |
| **QUICK_REFERENCE_GUIDE.md** | Fast lookup tables | 5 min |
| **BAY_STATES_VISUALIZATION_INDEX.md** | Complete descriptions | 30 min |
| **TECHNICAL_SPECIFICATIONS.md** | Architecture details | 45 min |

---

## 🎯 What You Get

### **13 Ready-to-Use Visualizations:**

1. **3D State Space** - Spatial relationships
2. **Temporal Dynamics** - Time series + spectra
3. **Statistical Distributions** - Probability densities
4. **Correlation Heatmap** - Feature relationships
5. **PCA Analysis** - Dimensionality reduction
6. **Box & Violin Plots** - Distribution comparison
7. **Transition Probabilities** - Markov chains
8. **Distance Matrix** - Similarity analysis
9. **ANOVA Tests** - Statistical validation
10. **Phase Space** - Dynamical trajectories
11. **Effect Size** - Cohen's d analysis
12. **Cumulative Distributions** - ECDF with KS tests
13. **Summary Dashboard** - Executive overview

### **Complete Documentation:**
- Comprehensive guides for every level
- Code templates for extensions
- Jupyter notebook for interactive work
- VS Code configuration files

---

## 💻 System Requirements

**Minimum:**
- Python 3.9+
- VS Code
- 2 GB RAM
- 100 MB storage

**What you need to install:**
1. Python → https://python.org/downloads
2. VS Code → https://code.visualstudio.com

---

## 🔧 Installation Steps (Detailed)

### **1. Install Python**

**Windows:**
```
1. Download from python.org
2. Run installer
3. ✅ CHECK "Add Python to PATH"
4. Verify: Open CMD, type: python --version
```

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python

# Verify
python3 --version
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# Verify
python3 --version
```

### **2. Install VS Code**

Download and install from: https://code.visualstudio.com

### **3. Install VS Code Extensions**

In VS Code, press `Ctrl+Shift+X` and install:
- ✅ Python (by Microsoft)
- ✅ Pylance (by Microsoft)
- ✅ Jupyter (by Microsoft)

### **4. Set Up Project**

```bash
# Create project folder
mkdir BAY_States_Project
cd BAY_States_Project

# Copy downloaded files here
# - bay_states_visualizations.py
# - requirements.txt
# - custom_bay_visualizations.py
# - BAY_States_QuickStart.ipynb

# Create outputs folder
mkdir outputs

# Install dependencies
pip install -r requirements.txt
```

### **5. Run the System**

```bash
# Method 1: Command line
python bay_states_visualizations.py

# Method 2: In VS Code
# - Open bay_states_visualizations.py
# - Press F5
# - Or right-click → "Run Python File in Terminal"
```

---

## 📊 Verify Installation

Run this quick test:

```python
# test_installation.py
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy
import sklearn
import pandas as pd

print("✅ All packages installed successfully!")
print(f"NumPy: {np.__version__}")
print(f"Matplotlib: {plt.matplotlib.__version__}")
print(f"Seaborn: {sns.__version__}")
print(f"SciPy: {scipy.__version__}")
print(f"Scikit-learn: {sklearn.__version__}")
print(f"Pandas: {pd.__version__}")
```

Expected output:
```
✅ All packages installed successfully!
NumPy: 1.26.x
Matplotlib: 3.8.x
Seaborn: 0.13.x
SciPy: 1.11.x
Scikit-learn: 1.3.x
Pandas: 2.1.x
```

---

## 🎨 Your First Custom Visualization

After running the main script, try this:

```python
# my_first_custom.py
from bay_states_visualizations import BAYStatesAnalyzer
import matplotlib.pyplot as plt

# Create analyzer
analyzer = BAYStatesAnalyzer(n_samples=1000)

# Create a simple plot
plt.figure(figsize=(10, 6))

for state in ['B', 'A', 'Y']:
    data = analyzer.data[analyzer.data['State'] == state]['Activation']
    plt.hist(data, alpha=0.5, bins=30, 
            label=state, 
            color=analyzer.bay_states[state]['color'])

plt.xlabel('Activation', fontweight='bold')
plt.ylabel('Count', fontweight='bold')
plt.title('My First Custom Plot!', fontweight='bold')
plt.legend()
plt.savefig('outputs/my_first_plot.png', dpi=300)
plt.show()

print("✅ Your first plot created!")
```

---

## 🔥 Quick Commands Reference

```bash
# Generate all visualizations
python bay_states_visualizations.py

# Run custom extensions
python custom_bay_visualizations.py

# Start Jupyter notebook
jupyter notebook BAY_States_QuickStart.ipynb

# Check Python version
python --version

# List installed packages
pip list

# Update a package
pip install --upgrade matplotlib

# Create virtual environment (recommended)
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
```

---

## 🐛 Common Issues & Quick Fixes

### **Issue: "python not found"**
```bash
# Try python3 instead
python3 bay_states_visualizations.py

# Or add Python to PATH (Windows)
# Search "Environment Variables" → Edit PATH → Add Python folder
```

### **Issue: "Module not found"**
```bash
# Reinstall packages
pip install -r requirements.txt

# Or install individually
pip install numpy matplotlib seaborn scipy scikit-learn pandas
```

### **Issue: "Permission denied"**
```bash
# Windows: Run as administrator
# Mac/Linux: Use pip3 and python3
pip3 install -r requirements.txt
```

### **Issue: Plots not showing**
```python
# Add this at the top of your script
import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg'
import matplotlib.pyplot as plt
```

---

## 📱 Next Steps

After your first successful run:

1. **Explore the outputs** - Check all 13 generated visualizations
2. **Read Quick Reference** - Understand what each plot shows
3. **Try Jupyter notebook** - Interactive exploration
4. **Customize** - Edit `custom_bay_visualizations.py`
5. **Read full guides** - Deep dive into capabilities

---

## 💡 Pro Tips

✨ **Use Virtual Environments**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

✨ **Enable Auto-Save in VS Code**
- File → Preferences → Settings
- Search "Auto Save"
- Set to "afterDelay"

✨ **Use Jupyter for Exploration**
- Great for testing code snippets
- Visualizations show inline
- Easy to experiment

✨ **Organize Your Work**
```
BAY_States_Project/
├── outputs/           # Generated visualizations
├── notebooks/         # Jupyter notebooks
├── extensions/        # Your custom code
└── data/             # Any data files
```

---

## 🎯 Success Checklist

Before you start customizing, make sure:

- [ ] Python 3.9+ installed
- [ ] VS Code installed with Python extensions
- [ ] All packages installed (`pip install -r requirements.txt`)
- [ ] Main script runs successfully
- [ ] 13 PNG files generated in outputs/
- [ ] Can view the visualizations
- [ ] Test plot created successfully

---

## 📞 Getting Help

**Documentation:**
1. Start with this file (GETTING_STARTED.md)
2. Check QUICK_REFERENCE_GUIDE.md for fast answers
3. Read VSCODE_SETUP_GUIDE.md for detailed setup
4. See TECHNICAL_SPECIFICATIONS.md for deep dive

**Online Resources:**
- Python Documentation: https://docs.python.org
- Matplotlib Gallery: https://matplotlib.org/stable/gallery
- Seaborn Examples: https://seaborn.pydata.org/examples
- VS Code Python: https://code.visualstudio.com/docs/python

**Communities:**
- r/Python on Reddit
- Python Discord Server
- Stack Overflow (tag: python, matplotlib)

---

## 🎉 You're Ready!

**Congratulations!** You now have everything you need to:
- ✅ Generate publication-quality visualizations
- ✅ Analyze BAY states data
- ✅ Create custom plots
- ✅ Explore interactively in Jupyter
- ✅ Extend the system with your own code

---

**Time to create amazing visualizations! 🎨📊✨**

---

*Last updated: October 31, 2025*  
*Version: 1.0*
