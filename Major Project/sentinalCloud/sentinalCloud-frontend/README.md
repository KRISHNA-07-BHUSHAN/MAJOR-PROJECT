# SentinelCloud Frontend

This is the React-based frontend for the SentinelCloud network security dashboard. It provides real-time monitoring, AI-driven explanations, and a comprehensive interface for security analysis.

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Routing**: React Router
- **HTTP Client**: Axios
- **Styling**: Plain CSS with CSS Variables for theming
- **Deployment**: Docker, Nginx

## Getting Started

### Prerequisites

- Node.js (v20 or later)
- Docker Desktop

### Running Locally (Development)

1.  **Clone the repository**
2.  **Navigate to the frontend directory:**
    ```bash
    cd sentinalCloud-frontend
    ```
3.  **Install dependencies:**
    ```bash
    npm install
    ```
4.  **Run the development server:**
    *(This command will be part of the final `docker-compose` setup)*
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:5173`.

### Building for Production

To create an optimized production build, run:
```bash
npm run build