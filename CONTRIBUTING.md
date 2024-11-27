# Contributing to **The Movie Recommendation System**

Thank you for considering contributing to **The Movie Recommendation System**! We welcome contributions that help improve this project. Whether you're reporting a bug, suggesting an enhancement, or creating a pull request, your efforts are appreciated.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [How to Contribute](#how-to-contribute)
   - [Reporting Bugs](#reporting-bugs)
   - [Suggesting Enhancements](#suggesting-enhancements)
   - [Submitting Pull Requests](#submitting-pull-requests)
3. [Important Notes on Dependencies](#important-notes-on-dependencies)

---

## Getting Started

To contribute to this project, you'll need:

- An **Anaconda setup** on your system.
- Python version **3.10** or higher (recommended).  
  > **Note**: While the project was initially designed for Python 3.6, some dependencies are no longer compatible with this version. If you encounter installation errors, switch to Python 3.10 to resolve them.  

After setting up your environment, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/se-zeus/popcorn_pal_2.0.git
   cd popcorn_pal_2.0
   ```
2. Install the necessary dependencies using:
   ```bash
   conda create --name my_env python=3.10
   conda activate my_env
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

---

## How to Contribute

### **1. Reporting Bugs**
If you encounter an issue while using the Movie Recommendation System, help us by submitting a detailed bug report.

#### How to Submit a Bug Report:
1. Navigate to the [Issues](https://github.com/se-zeus/popcorn_pal_2.0/issues) section of the repository.
2. Create a new issue and include the following:
   - **A clear and descriptive title**.
   - **Steps to reproduce the issue** with examples or code snippets (use Markdown for code blocks).
   - **Screenshots or logs** to better explain the issue.
   - Any **additional context** (e.g., environment setup, Python version).

### **2. Suggesting Enhancements**
Have an idea to improve the system? We’d love to hear it!

#### How to Suggest Enhancements:
1. Navigate to the [Issues](https://github.com/se-zeus/popcorn_pal_2.0/issues) section.
2. Create a new issue for your enhancement. Include:
   - **A descriptive title** for your suggestion.
   - **Detailed explanation** of the enhancement.
   - **Suggestions for implementation** or examples to clarify your idea.

Some examples of enhancements could be:
- Adding new features, like user interaction tracking.
- Improving recommendation algorithms.
- Optimizing the app for better performance.

### **3. Submitting Pull Requests**
Pull requests are the best way to propose changes to the project. 

#### Steps to Submit a Pull Request:
1. Fork the repository and create a new branch:
   ```bash
   git checkout -b feature-name
   ```
2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Add detailed description of your changes"
   ```
3. Push the branch to your fork:
   ```bash
   git push origin feature-name
   ```
4. Open a pull request from your forked repository to the main repository. Make sure to:
   - Clearly describe your changes.
   - Reference related issues (if any).
   - Provide tests or examples for new features.

---

## Important Notes on Dependencies

- **Python Version**: The project was initially designed for Python 3.6, but some dependencies may not install on this version. It is recommended to use **Python 3.10** to avoid errors.
- If you encounter issues with dependencies:
  - Check the error message to identify the incompatible package.
  - Attempt to use an updated version of the dependency if available.
  - Document any changes you made for compatibility in your pull request.

---

Thank you for contributing to **The Movie Recommendation System**! Let's work together to make this project better for everyone. 🎥 🍿