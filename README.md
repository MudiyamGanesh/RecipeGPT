# RecipeGPT

RecipeGPT is an intelligent application built to facilitate recipe generation, ingredient-based search, and meal planning. The system combines a natural language interface with an embedded vector search over a structured recipe dataset to deliver contextual and accurate culinary assistance.

## Architecture Overview

The project follows a decoupled client-server architecture:

- **Backend (Python / FastAPI):** Handles API requests, session management, and interfaces with the language model. It utilizes LangChain to orchestrate a conversational retrieval chain. Document embeddings are generated via the `sentence-transformers` library and indexed using FAISS for efficient similarity search. The primary language model is integrated via the Groq API.
- **Frontend (React / Vite):** A responsive, single-page application that provides a persistent chat interface and local session history management. It is styled with custom CSS to support dynamic layouts and modern interface design patterns.

## Core Features

- **Recipe Retrieval:** Extracts and formats recipes from the underlying dataset based on user queries.
- **Ingredient-Based Search:** Identifies recipes that match specific available ingredients.
- **Meal Planning:** Assists in structuring meals over requested timeframes.
- **Persistent Sessions:** Chat histories are stored persistently, allowing users to load and manage previous interactions.

## Repository Structure

- `main.py`: The entry point for the FastAPI server, defining all REST endpoints.
- `recipe.py`: Contains the logic for document ingestion, FAISS indexing, and LangChain initialization.
- `Dataset.csv`: The primary data source containing recipe information.
- `faiss_index/`: The persistent directory storing the generated vector embeddings.
- `frontend/`: The React application source code and deployment configuration.
- `render.yaml`: Infrastructure as code configuration for deploying the backend service.

## Local Development Setup

### Backend Environment

1. Create and activate a Python virtual environment.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your environment variables. Create a `.env` file in the root directory and add your API credentials:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Environment

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the Node package dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```

## Deployment Guidelines

- **Backend:** The repository includes a `render.yaml` configuration file for streamlined deployment to Render. The service is configured to execute `pip install -r requirements.txt` during the build phase and utilize `uvicorn` for the start command.
- **Frontend:** The React application is pre-configured for deployment to GitHub Pages. Prior to building for production, ensure the `API_BASE` variable in the application points to the live backend URL. Use the configured deployment script to publish the interface.
