# Mindfluence

### _Your Personal Guide to a Clearer Mind_

![Built for](https://img.shields.io/badge/Built%20for-CS%20Base%20Hack4Health-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)

Mindfluence is a web-based self-awareness toolkit designed to help users understand their thoughts, clarify their values, and build healthier mental habits. It provides a private, secure space for self-reflection powered by psychologically-grounded tools and intelligent insights.

**Crucial Disclaimer:** Mindfluence is an educational and self-help tool, not a diagnostic tool or a replacement for professional medical or therapeutic advice.

---

## 📸 Screenshots

| Landing Page                                  | Dashboard                               |
| :-------------------------------------------- | :-------------------------------------- |
| ![Landing Page](snaps/land.png)               | ![Dashboard](snaps/dash.png)            |
| **Assessments**                               | **Guided Journal**                      |
| ![Assessments Page](snaps/asses.png)          | ![Journal Page](snaps/journal.png)      |
| **Community (Concept)**                       | **Resources**                           |
| ![Community Page](snaps/community.png)        | ![Resources Page](snaps/resource.png)   |

---

## ✨ Key Features

*   🧠 **Cognitive Toolkits:** Interactive tools based on established methods like CBT and ACT to help users identify and reframe negative thought patterns.
*   📊 **Guided Assessments:** Take validated self-assessments (e.g., GAD-7) to get a private baseline of your current mental state and track changes over time.
*   ✍️ **AI-Powered Journaling:** A secure journal that uses NLP to analyze sentiment and extract recurring themes, helping you discover patterns in your thinking.
*   💡 **Personalized Insights Engine:** Connects the dots between your assessments, tool usage, and journal entries to provide a holistic view and suggest relevant resources.
*   📚 **Curated Resource Library:** Access a library of articles, guides, and strategies for managing anxiety, understanding biases, and improving well-being.
*   🔒 **Privacy First:** All user data is private. Insights are generated on our secure backend and are never shared.

---

## 🛠️ Tech Stack & Architecture

We built Mindfluence on a modern, scalable microservices architecture to ensure robustness and separation of concerns.

| Category      | Technology                                                                                                                                                                                                                                                         |
| :------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Frontend**  | ![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB) ![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)                                                |
| **Backend**   | ![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white) ![Express.js](https://img.shields.io/badge/Express.js-000000?style=for-the-badge&logo=express&logoColor=white)                                             |
| **AI/ML**     | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)                                                        |
| **Database**  | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)                                                                                                                                                   |
| **DevOps**    | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![Git](https://img.shields.io/badge/GIT-E44C30?style=for-the-badge&logo=git&logoColor=white)                                                                   |

### Architecture Diagram

graph TD
A[Client Browser] --> B{API Gateway};

text
subgraph Backend Services
    B --> C[User Service <br> (Node.js)];
    B --> D[Content Service <br> (Node.js)];
    B --> E[AI/Insights Service <br> (Python)];
end

C --> F[(PostgreSQL DB)];
D --> F;
E --> F;
text

---

## 🚀 Getting Started

Follow these instructions to get a local copy up and running for development and testing purposes.

### Prerequisites

*   [Node.js](https://nodejs.org/) (v18.x or later)
*   [Python](https://www.python.org/) (v3.9 or later)
*   [Git](https://git-scm.com/)
*   [Docker](https://www.docker.com/) (Recommended, for database)

### Installation & Setup

1.  **Clone the repository:**
    ```
    git clone https://github.com/your-username/mindfluence.git
    cd mindfluence
    ```

2.  **Set up the Database (using Docker):**
    ```
    docker run --name mindfluence-db -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the root of each service directory (e.g., `services/user-service/`, `services/ai-service/`). Use the `.env.example` files as a template.
    ```
    # Example for user-service/.env
    DATABASE_URL="postgresql://postgres:mysecretpassword@localhost:5432/mindfluence_db"
    JWT_SECRET="your-super-secret-key"
    ```

4.  **Install Backend Dependencies:**
    Navigate to each service directory and install its dependencies.
    ```
    # For Node.js services
    cd services/user-service
    npm install
    cd ../..

    # For Python services
    cd services/ai-service
    pip install -r requirements.txt
    cd ../..
    ```

5.  **Install Frontend Dependencies:**
    ```
    cd client
    npm install
    ```

### Running the Application

1.  **Start the Backend Services:**
    Open a terminal for each service, navigate to its directory, and run the start command.
    ```
    # Terminal 1: User Service
    cd services/user-service
    npm start

    # Terminal 2: AI Service
    cd services/ai-service
    uvicorn main:app --reload
    ```

2.  **Start the Frontend Development Server:**
    In a new terminal, run the React app.
    ```
    cd client
    npm start
    ```

3.  Open your browser and navigate to `http://localhost:3000`. You should see the Mindfluence landing page!

---

## 🌳 Project Structure

The project uses a monorepo structure to keep the frontend, backend services, and shared libraries organized.

/
├── client/ # React Frontend Application
│ ├── public/
│ └── src/
├── services/ # Backend Microservices
│ ├── user-service/ # Manages users, auth
│ ├── content-service/ # Manages assessments, modules
│ └── ai-service/ # NLP, insights engine
├── snaps/ # UI Screenshots for README
│ ├── land.png
│ └── ...
└── README.md

text

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📜 License

Not yet licensed.

---

## 🙏 Acknowledgments

*   This project was created for the **CS Base (csbase.org) Hack4Health** hackathon.
*   Inspiration drawn from principles of CBT, ACT, and the push for accessible mental well-being tools.
*   Thanks to all the creators of the open-source libraries used in this project.