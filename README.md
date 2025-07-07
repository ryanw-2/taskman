# Reclaiming Productivity: How Embodied Interaction Shapes Our Digital Workflow

In a world dominated by clicks and keystrokes, we've overlooked a powerful, innate tool for thought and organization: our hands. Cognitive science, as highlighted by researcher David McNeill, reveals that gestures are not mere afterthoughts but integral parts of our thought processes. This project explores that forgotten connection, moving beyond the screen to create a productivity tool that leverages natural, embodied interaction to enhance focus and reduce cognitive load.

![Project Hero](background1.JPG)

## Project Summary & Achievements

This project, codenamed "Taskman," is a hands-free productivity dashboard designed to be projected onto any physical surface selected to be presented at the Meeting of the Minds Carnegie Mellon Research Symposium. It serves as an ambient, secondary workspace for managing daily tasks and calendar events without ever touching a keyboard or mouse.

The primary achievement is the creation of a fluid, low-latency control system that seamlessly translates physical actions into digital commands. Users can navigate their calendar with swipes in the air, complete checklist items with a "click" gesture, and converse with a voice-powered AI assistant to ask questions. This fosters a more intuitive and less stressful relationship with task management, directly addressing the cognitive overload common in today's fast-paced environments.

## Technology Stack

The system is built on a modern, full-stack architecture designed for real-time performance.

### Frontend: The Projected Dashboard

* **React:** The user interface is built as a dynamic single-page application using React, allowing for a component-based and easily maintainable structure.
* **Framer Motion:** All UI animations, from the expansion of grid items to the fluid transitions between views, are handled by Framer Motion to ensure a polished user experience.

### Backend: The Central Hub

* **Python & FastAPI:** A high-performance Python backend built with the FastAPI framework serves as the core of the system.
* **WebSockets:** Real-time, bidirectional communication for both gesture commands and the voice assistant is handled through WebSockets, ensuring low-latency interaction.
* **SQLAlchemy & SQLite:** A database layer managed by SQLAlchemy stores and retrieves user data for the checklist and calendar modules.

### AI & Machine Learning: The Control System

* **Hand Detection & Tracking (Gesture Control):** The system uses a Python module built with **OpenCV** to capture webcam video and the **MediaPipe** library to perform high-fidelity, real-time hand and landmark detection. This translates physical hand movements into actionable commands like "click" and "swipe."
* **Voice-Powered Assistant (Smart Search):**
   * **Google Cloud Speech-to-Text:** User speech is captured in the browser and streamed to this API for fast and accurate real-time transcription.
   * **Google Cloud Vertex AI (Gemini):** The transcribed text is sent to a Gemini model, which generates intelligent, conversational responses, transforming the feature from a simple search to a true AI assistant.

## Demo

![Project Hero](Tools.jpg)

*Demo video showing functionalities of dashboard*

## References

Britton, B. K., & Tesser, A. (1991). Effects of time-management practices on college grades. *Journal of Educational Psychology, 83*(3), 405–410.

Höök, K. (2018). *Designing with the Body: Somaesthetic Interaction Design*. MIT Press.

Macan, T. H. (1994). Time management: Test of a process model. *Journal of Applied Psychology, 79*(3), 381–391.

McNeill, D. (1992). *Hand and Mind: What Gestures Reveal About Thought*. University of Chicago Press.