---
title: Getting the Code
---

Rota AI is an open-source project hosted on GitHub. Follow this guide to clone the source code and prepare your workspace.

---

### Prerequisites
Before cloning, ensure you have the following version control tools installed on your development machine:
* **Git**: [git-scm.com](https://git-scm.com)
* **Git LFS (Large File Storage)**: Some model weights and binary files are stored using Git LFS. If not installed, run:
  - **macOS**: `brew install git-lfs`
  - **Linux**: `sudo apt install git-lfs` / `sudo dnf install git-lfs`
  - **Windows**: Included with the official Git installer.

---

### Cloning the Repository

Open a terminal or command prompt and clone the repository along with its submodules:

```bash
# Clone the main repository
git clone https://github.com/krthik20050/Rota-AI.git

# Navigate into the project folder
cd Rota-AI

# Initialize Git LFS (pulls down compressed files)
git lfs install
git lfs pull
```

---

### Folder Layout Reference
The project root has a double-tier layout:
* `/desktop`: The Python source codebase for the desktop application.
* `/website`: The Next.js/Tailwind CSS project for the web landing page and documentation engine.
* `/tests`: Python unit tests and functional test suites.
* `/docs`: Project developer guides and architectural specifications.
