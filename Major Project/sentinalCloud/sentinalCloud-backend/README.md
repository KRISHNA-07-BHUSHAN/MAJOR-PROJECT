# SentinelCloud Backend

This is the FastAPI backend for the SentinelCloud network security dashboard. It serves machine learning models for real-time intrusion detection, provides model explanations via SHAP, and offers a suite of APIs for statistical analysis and alert management.

## 🚀 Quickstart (Docker)

1.  **Place your assets:**
    * Put your trained `.h5` model files in the `sentinalCloud-backend/saved_models/` directory.
    * Place your saved `scaler.pkl` in the `sentinalCloud-backend/saved_models/` directory.
    * Place a small sample of your training data (e.g., `KDDTrain_preprocessed.csv`) in `sentinalCloud-backend/app/data/` for SHAP to use as a background dataset.

2.  **Navigate to the project root** (the `sentinalCloud/` directory).

3.  **Build and run the entire stack:**
    ```bash
    docker-compose up --build
    ```

4.  **Access the services:**
    * **Frontend Application:** [http://localhost:5173](http://localhost:5173)
    * **Backend API Docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API Endpoints

The API is automatically documented and interactive at the `/docs` endpoint. All routes are prefixed with `/api`.

-   `POST /api/detection/detect`: The main prediction endpoint. Accepts a list of feature vectors and returns enriched predictions.
-   `GET /api/stats/summary`: Provides key summary statistics for the dashboard.
-   `GET /api/alerts/`: Returns a paginated list of security alerts.
-   `POST /api/explain/{model_name}`: Generates a SHAP explanation for a given data sample and model.
-   `POST /api/detection/simulate-attack`: Simple endpoint for the frontend's "Simulate Attack" button.

---

*For a detailed explanation of the algorithm, see the original documentation.*