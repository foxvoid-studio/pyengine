# PyEngine

A lightweight, cross-platform Python game engine built on SDL2 and Modern OpenGL.

**⚠️ WARNING: This project is currently in the experimental stage.**
APIs are subject to change without notice. It is primarily a learning resource for building a game engine from scratch in Python.

**PyEngine** is a 2D/3D game engine designed for developers who want to understand the low-level mechanics of a game engine without leaving the comfort of Python.

Unlike frameworks like PyGame (which often relies on legacy rendering) or Kivy (which imposes a strict UI paradigm), PyEngine focuses on a **"Modern OpenGL"** approach. It combines the robustness of **SDL2** for windowing with a strict **Entity Component System (ECS)** architecture for logic.

---

## 🌟 Key Features

  - 🐍 Pure Python: Easy to read, debug, and extend.

  - ⚡ Modern OpenGL: Uses the Core Profile (3.3+), Shaders (GLSL), VBOs, and VAOs. No legacy pipeline.

  - 🧱 ECS Architecture: A strict separation of data and logic, making the engine modular and scalable.

  - 📱 Cross-Platform Ready: Built on top of SDL2, allowing potential deployment to Desktop (Windows/Linux/macOS) and Mobile (Android via Buildozer).

  - 🧮 Robust Math: Powered by PyGLM for C++ equivalent matrix and vector performance.

---

## 📦 Installation

Ensure you have Python 3.10+ installed.

Clone the repository:

```
git clone [https://github.com/foxvoid-studio/pyengine.git](https://github.com/foxvoid-studio/pyengine.git)
cd pyengine
```


Install dependencies:

```
poetry install
```

---

## 🚀 Quick Start

Here is how to create a simple window with a rotating triangle using the ECS system.

```python
from pyengine.core.app import App

if __name__ == "__main__":
    # Create the application context (800x600)
    app = App(800, 600, "My First Game")
    
    # The App automatically initializes the ECS, 
    # loads default shaders, and creates a demo scene.
    
    # Run the main loop
    app.run()
```

---

## 🏗️ Architecture

PyEngine follows a strict layered architecture to maintain performance and readability.

| Layer | Technology | Description |
| :--- | :--- | :--- |
| Windowing | `pysdl2` | Cross-platform window creation, input handling, and context management. |
| Rendering | `PyOpenGL` | Direct bindings to OpenGL 3.3 Core Profile. |
| Rendering | `Pillow` | Image loading and processing for textures. |
| Maths | `PyGLM` | Fast matrix/vector operations (GLSL compatible). |
| Logic | `ECS` | Custom Entity Component System for managing game state. |

---

## 🤝 Contributing

Contributions are welcome, but please remember this is an experimental project.

Fork the project

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See LICENSE for more information.
