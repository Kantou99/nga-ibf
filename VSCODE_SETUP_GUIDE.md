# 🎨 VS Code Setup Guide for BAY States Visualization System

This guide will help you set up VS Code to run and extend the BAY States visualization system on your local machine.

---

## 📦 Prerequisites

### **Required Software:**
1. **Python 3.9+** (Recommended: Python 3.11+)
   - Download from: https://www.python.org/downloads/
   - ✅ During installation, check "Add Python to PATH"

2. **VS Code**
   - Download from: https://code.visualstudio.com/

3. **Git** (Optional, but recommended)
   - Download from: https://git-scm.com/downloads

---

## 🛠️ Step 1: Install VS Code Extensions

Open VS Code and install these essential extensions:

### **Must-Have Extensions:**

1. **Python** (by Microsoft)
   - Extension ID: `ms-python.python`
   - Provides Python language support, debugging, linting

2. **Pylance** (by Microsoft)
   - Extension ID: `ms-python.vscode-pylance`
   - Fast, feature-rich Python language server

3. **Jupyter** (by Microsoft)
   - Extension ID: `ms-toolsai.jupyter`
   - Run Python code interactively, view plots inline

### **Recommended Extensions:**

4. **Python Indent** (by Kevin Rose)
   - Extension ID: `KevinRose.vsc-python-indent`
   - Better automatic indentation

5. **autoDocstring** (by Nils Werner)
   - Extension ID: `njpwerner.autodocstring`
   - Generate Python docstrings automatically

6. **Better Comments** (by Aaron Bond)
   - Extension ID: `aaron-bond.better-comments`
   - Highlight different types of comments

### **How to Install Extensions:**

```
Method 1: Via UI
1. Click Extensions icon (Ctrl+Shift+X)
2. Search for extension name
3. Click "Install"

Method 2: Via Command Palette
1. Press Ctrl+Shift+P (Cmd+Shift+P on Mac)
2. Type: "Extensions: Install Extensions"
3. Search and install
```

---

## 🐍 Step 2: Set Up Python Environment

### **Option A: System Python (Easiest)**

```bash
# Windows (Command Prompt or PowerShell)
python --version  # Verify Python is installed
pip install --upgrade pip

# macOS/Linux (Terminal)
python3 --version  # Verify Python is installed
pip3 install --upgrade pip
```

### **Option B: Virtual Environment (Recommended)**

```bash
# Windows
cd C:\Users\YourName\Documents\BAY_States
python -m venv venv
venv\Scripts\activate

# macOS/Linux
cd ~/Documents/BAY_States
python3 -m venv venv
source venv/bin/activate
```

**Why use virtual environment?**
- Isolates project dependencies
- Prevents package conflicts
- Easy to replicate on other machines

---

## 📚 Step 3: Install Required Packages

### **Create requirements.txt:**

Create a file called `requirements.txt` with this content:

```txt
numpy>=1.26.0
matplotlib>=3.8.0
seaborn>=0.13.0
scipy>=1.11.0
scikit-learn>=1.3.0
pandas>=2.1.0
ipython>=8.0.0
jupyter>=1.0.0
```

### **Install all packages:**

```bash
# From your project directory
pip install -r requirements.txt

# Or install individually:
pip install numpy matplotlib seaborn scipy scikit-learn pandas ipython jupyter
```

### **Verify Installation:**

```python
# Test in VS Code terminal
python -c "import numpy, matplotlib, seaborn, scipy, sklearn, pandas; print('All packages installed successfully!')"
```

---

## 📁 Step 4: Project Structure

Create this folder structure:

```
BAY_States_Project/
├── bay_states_visualizations.py    # Main script (download from outputs)
├── requirements.txt                # Package dependencies
├── outputs/                        # Generated visualizations
├── data/                          # Optional: Store data files
├── notebooks/                     # Jupyter notebooks for exploration
│   └── exploration.ipynb
├── extensions/                    # Your custom visualizations
│   └── custom_plots.py
└── README.md                      # Project documentation
```

### **Create folders:**

```bash
# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path outputs, data, notebooks, extensions

# macOS/Linux
mkdir -p outputs data notebooks extensions
```

---

## ⚙️ Step 5: Configure VS Code Settings

### **Open Settings:**
- Press `Ctrl+,` (Windows/Linux) or `Cmd+,` (Mac)
- Or click: File → Preferences → Settings

### **Configure Python:**

1. **Select Python Interpreter:**
   - Press `Ctrl+Shift+P`
   - Type: "Python: Select Interpreter"
   - Choose your Python installation or virtual environment

2. **Configure Linting (Optional):**
   ```json
   {
       "python.linting.enabled": true,
       "python.linting.pylintEnabled": true,
       "python.formatting.provider": "autopep8"
   }
   ```

3. **Configure Auto-Save:**
   ```json
   {
       "files.autoSave": "afterDelay",
       "files.autoSaveDelay": 1000
   }
   ```

### **Create `.vscode/settings.json`:**

Create a `.vscode` folder in your project and add `settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "autopep8",
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1000,
    "editor.formatOnSave": true,
    "python.analysis.typeCheckingMode": "basic",
    "[python]": {
        "editor.defaultFormatter": "ms-python.python",
        "editor.tabSize": 4,
        "editor.insertSpaces": true
    }
}
```

---

## 🚀 Step 6: Run the Visualization System

### **Method 1: Run in Terminal**

```bash
# Make sure you're in the project directory
cd BAY_States_Project

# Activate virtual environment (if using one)
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Run the script
python bay_states_visualizations.py
```

### **Method 2: Run in VS Code**

1. Open `bay_states_visualizations.py` in VS Code
2. Press `F5` or click "Run" → "Start Debugging"
3. Or right-click in editor → "Run Python File in Terminal"

### **Method 3: Interactive Mode with Jupyter**

Create a new notebook (`notebooks/exploration.ipynb`):

```python
# Cell 1: Import the analyzer
import sys
sys.path.append('..')  # Add parent directory to path

from bay_states_visualizations import BAYStatesAnalyzer

# Cell 2: Create analyzer instance
analyzer = BAYStatesAnalyzer(n_samples=1000, random_state=42)

# Cell 3: Generate all visualizations
analyzer.generate_all_visualizations()

# Cell 4: Or generate individual plots
analyzer.plot_1_state_space_3d()
analyzer.plot_13_summary_dashboard()

# Cell 5: Explore the data
print(analyzer.data.head())
print(analyzer.data.describe())

# Cell 6: Custom analysis
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
analyzer.data.boxplot(column='Activation', by='State')
plt.show()
```

---

## 🎨 Step 7: Extending the System

### **Add Your Own Visualization:**

Create `extensions/custom_plots.py`:

```python
"""
Custom BAY States Visualizations
Add your own plots here!
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from bay_states_visualizations import BAYStatesAnalyzer

def plot_custom_heatmap(analyzer):
    """Create a custom heatmap visualization"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Your custom code here
    pivot_data = analyzer.data.pivot_table(
        values='Activation',
        index='State',
        columns=pd.cut(analyzer.data['Response_Time'], bins=5),
        aggfunc='mean'
    )
    
    sns.heatmap(pivot_data, annot=True, fmt='.2f', 
                cmap='coolwarm', ax=ax)
    ax.set_title('Custom BAY States Heatmap', fontweight='bold')
    
    plt.savefig('../outputs/14_custom_heatmap.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Custom heatmap created!")

def plot_custom_scatter_matrix(analyzer):
    """Create a custom scatter matrix"""
    import pandas as pd
    from pandas.plotting import scatter_matrix
    
    fig, axes = plt.subplots(5, 5, figsize=(15, 15))
    
    scatter_matrix(analyzer.data[['Activation', 'Response_Time', 
                                  'Stability', 'Energy', 'Coherence']],
                   alpha=0.6, figsize=(15, 15), diagonal='kde',
                   ax=axes, c=analyzer.data['State'].map(
                       {'B': 0, 'A': 1, 'Y': 2}),
                   cmap='viridis')
    
    plt.suptitle('Custom Scatter Matrix', fontsize=16, fontweight='bold')
    plt.savefig('../outputs/15_custom_scatter_matrix.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Custom scatter matrix created!")

# Main execution
if __name__ == "__main__":
    # Create analyzer
    analyzer = BAYStatesAnalyzer(n_samples=1000, random_state=42)
    
    # Run custom visualizations
    plot_custom_heatmap(analyzer)
    plot_custom_scatter_matrix(analyzer)
```

### **Run your custom extensions:**

```bash
cd extensions
python custom_plots.py
```

---

## 🔍 Step 8: Debugging in VS Code

### **Set Breakpoints:**
1. Click in the left margin (gutter) next to line numbers
2. Red dot appears = breakpoint set
3. Run with `F5` - execution pauses at breakpoints

### **Debug Configuration:**

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "BAY States: Generate All",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/bay_states_visualizations.py",
            "console": "integratedTerminal",
            "args": []
        }
    ]
}
```

### **Useful Debug Actions:**
- `F5` - Start/Continue
- `F10` - Step Over
- `F11` - Step Into
- `Shift+F11` - Step Out
- `F9` - Toggle Breakpoint

---

## 📊 Step 9: View Visualizations in VS Code

### **Option 1: Image Preview Extension**

Install: **Image Preview** extension
- View images directly in editor
- Hover over image paths to see previews

### **Option 2: Jupyter Notebooks**

```python
from IPython.display import Image, display

# Display generated images inline
display(Image(filename='outputs/01_bay_3d_state_space.png'))
display(Image(filename='outputs/13_bay_summary_dashboard.png'))
```

### **Option 3: External Viewer**

```python
import os
import platform

def open_image(filepath):
    """Open image in default viewer"""
    if platform.system() == 'Darwin':  # macOS
        os.system(f'open {filepath}')
    elif platform.system() == 'Windows':
        os.startfile(filepath)
    else:  # Linux
        os.system(f'xdg-open {filepath}')

# Usage
open_image('outputs/13_bay_summary_dashboard.png')
```

---

## 🎯 Step 10: Advanced Customization

### **Modify State Parameters:**

```python
# In bay_states_visualizations.py or your custom script

class CustomBAYAnalyzer(BAYStatesAnalyzer):
    """Extended analyzer with custom parameters"""
    
    def __init__(self, n_samples=2000, random_state=42):
        # Increase sample size
        super().__init__(n_samples=n_samples, random_state=random_state)
    
    def generate_bay_data(self):
        """Override with custom data generation"""
        # Modify state characteristics
        n_per_state = self.n_samples // 3
        
        # Custom distributions
        B_f1 = np.random.normal(0, 0.3, n_per_state)  # Tighter baseline
        A_f1 = np.random.normal(4, 0.8, n_per_state)  # Higher activation
        Y_f1 = np.random.normal(2, 0.5, n_per_state)  # Different yielding
        
        # ... rest of data generation
```

### **Add New State:**

```python
def add_new_state():
    """Example: Add a fourth state 'R' (Recovering)"""
    
    # Modify state definitions
    self.bay_states['R'] = {
        'name': 'Recovering',
        'color': '#00CC99',
        'marker': 'd'  # Diamond marker
    }
    
    # Add data for R state
    # ... add R_f1, R_f2, etc.
```

### **Create Custom Feature:**

```python
def add_custom_feature(analyzer):
    """Add a computed feature to the dataset"""
    
    # Example: Activation/Stability ratio
    analyzer.data['Activation_Stability_Ratio'] = (
        analyzer.data['Activation'] / 
        (analyzer.data['Stability'] + 1e-6)  # Avoid division by zero
    )
    
    # Example: Energy efficiency
    analyzer.data['Energy_Efficiency'] = (
        analyzer.data['Activation'] / 
        (analyzer.data['Energy'] + 1e-6)
    )
    
    return analyzer
```

---

## 💡 Step 11: Productivity Tips

### **VS Code Shortcuts:**

```
Essential Shortcuts:
- Ctrl+` : Toggle terminal
- Ctrl+P : Quick file open
- Ctrl+Shift+P : Command palette
- Ctrl+/ : Toggle comment
- Alt+↑↓ : Move line up/down
- Ctrl+D : Select next occurrence
- Ctrl+Shift+K : Delete line
- F2 : Rename symbol
- Ctrl+Space : Trigger suggestions

Python-Specific:
- Shift+Enter : Run selection in terminal
- Ctrl+Enter : Run cell (in .py file with #%%)
```

### **Code Snippets:**

Create `.vscode/python.code-snippets`:

```json
{
    "BAY Plot Template": {
        "prefix": "bayplot",
        "body": [
            "def plot_${1:name}(self):",
            "    \"\"\"${2:Description}\"\"\"",
            "    fig, ax = plt.subplots(figsize=(12, 8))",
            "    ",
            "    # Your visualization code here",
            "    ${3:pass}",
            "    ",
            "    plt.tight_layout()",
            "    plt.savefig('/mnt/user-data/outputs/${4:filename}.png', ",
            "                bbox_inches='tight', dpi=300)",
            "    plt.close()",
            "    print('✅ ${1:name} created!')"
        ],
        "description": "Create a new BAY visualization method"
    }
}
```

### **Task Automation:**

Create `tasks.json` for common tasks:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Generate All Visualizations",
            "type": "shell",
            "command": "python",
            "args": ["bay_states_visualizations.py"],
            "group": {
                "kind": "build",
                "isDefault": true
            }
        },
        {
            "label": "Clean Outputs",
            "type": "shell",
            "command": "rm",
            "args": ["-rf", "outputs/*.png"]
        }
    ]
}
```

Run tasks with: `Ctrl+Shift+B`

---

## 🐛 Step 12: Common Issues & Solutions

### **Issue 1: "Module not found" error**

```bash
# Solution: Check Python interpreter
# In VS Code, press Ctrl+Shift+P
# Type: "Python: Select Interpreter"
# Choose correct interpreter

# Or reinstall packages:
pip install --force-reinstall numpy matplotlib seaborn scipy scikit-learn pandas
```

### **Issue 2: Plots not displaying**

```python
# Solution: Use non-interactive backend
import matplotlib
matplotlib.use('Agg')  # Add at the top of script
import matplotlib.pyplot as plt
```

### **Issue 3: Permission denied for outputs**

```bash
# Solution: Create outputs directory with write permissions
mkdir -p outputs
chmod 755 outputs  # On Unix systems
```

### **Issue 4: ImportError for bay_states_visualizations**

```python
# Solution: Add to Python path
import sys
sys.path.append('.')  # Current directory
sys.path.append('..')  # Parent directory

from bay_states_visualizations import BAYStatesAnalyzer
```

### **Issue 5: Slow execution**

```python
# Solution: Reduce sample size for testing
analyzer = BAYStatesAnalyzer(n_samples=100)  # Instead of 1000

# Or generate only specific plots
analyzer.plot_13_summary_dashboard()  # Just one plot
```

---

## 📝 Step 13: Version Control with Git

### **Initialize Git Repository:**

```bash
cd BAY_States_Project
git init
```

### **Create `.gitignore`:**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# VS Code
.vscode/
*.code-workspace

# Data & Outputs (optional - you might want to track these)
outputs/*.png
data/

# Jupyter
.ipynb_checkpoints/
*.ipynb

# OS
.DS_Store
Thumbs.db
```

### **First Commit:**

```bash
git add .
git commit -m "Initial commit: BAY States Visualization System"
```

---

## 🌟 Step 14: Next Steps & Resources

### **Learn More:**

1. **Python for Data Science:**
   - https://www.python.org/about/gettingstarted/
   - https://docs.python.org/3/tutorial/

2. **Matplotlib Tutorials:**
   - https://matplotlib.org/stable/tutorials/index.html

3. **Seaborn Gallery:**
   - https://seaborn.pydata.org/examples/index.html

4. **VS Code Python:**
   - https://code.visualstudio.com/docs/python/python-tutorial

### **Explore Further:**

```python
# Try these extensions:

1. Interactive plots with Plotly:
   pip install plotly
   # Create interactive 3D visualizations

2. Statistical modeling with statsmodels:
   pip install statsmodels
   # Advanced statistical tests

3. Animation with matplotlib:
   from matplotlib.animation import FuncAnimation
   # Create animated state transitions

4. Machine learning with PyTorch:
   pip install torch
   # Build neural networks for state classification
```

### **Join Communities:**

- Python Discord: https://discord.gg/python
- r/Python: https://reddit.com/r/Python
- Stack Overflow: Tag your questions with [python] [matplotlib]

---

## ✅ Checklist

Before you start, make sure you have:

- [ ] Python 3.9+ installed
- [ ] VS Code installed
- [ ] Required extensions installed (Python, Pylance, Jupyter)
- [ ] Virtual environment created (optional but recommended)
- [ ] All packages installed (`pip install -r requirements.txt`)
- [ ] Project folder structure created
- [ ] Downloaded `bay_states_visualizations.py`
- [ ] Tested basic import: `import numpy, matplotlib`
- [ ] Run the main script successfully
- [ ] Outputs folder populated with 13 PNG files

---

## 🎉 You're Ready!

You now have a complete VS Code setup for BAY States visualization!

**Next:**
1. Run `python bay_states_visualizations.py`
2. Check `outputs/` folder for visualizations
3. Open Jupyter notebook for interactive exploration
4. Start creating your own custom plots!

**Questions?** Check the documentation files in the outputs folder!

---

**Happy Visualizing! 📊✨**
