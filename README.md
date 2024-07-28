# VocRec

## Outline

VocRec can recommend similar vocabularies for your [Anki flashcards](https://apps.ankiweb.net/)!

VocRec can synchronize all the flash cards stored in `.anki2`, which is the [Anki database file](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure) for storing the flashcards, and provides several similar vocabularies of a specified card. 



## How It works

VocRec makes use of [vector embedding provided by OpenAI](https://platform.openai.com/docs/guides/embeddings) to create vectors of each flash card, storing them in a [pgvector, which is an extension based on PostgreSQL DB](https://github.com/pgvector/pgvector). 

1. Synchronization: Syncs your Anki flashcards with the `.anki2` database file.
2. Vector Creation: Uses OpenAI’s API to generate vector embeddings for each flashcard.
3. Storage: Stores these vectors in a pgvector PostgreSQL database.
4. Recommendation: Provides similar vocabulary recommendations based on the vectors of your flashcards.



## Prerequisites:

- Anki: Ensure you have Anki installed and your flashcards stored in the `.anki2` database file.
- OpenAI API Key: Required for generating vector embeddings.
- PostgreSQL with pgvector: Database setup to store and manage vectors.
- Docker: Recommended for running the application in a containerized environment.


## Getting Started: 

1. **Clone the repository**: Clone the repository and guide to the working folder to apply the setup:

    ```bash
    git clone https://github.com/phlin0424/AnkiVocRecommender.git
    cd AnkiVocRecommender/
    ```



2. **Setup the environment file**: Copy the `.env.example` file to `.env` in the root directory of the project.

    ```bash
    cp .env.example .env
    ```

    Then, open the `.env` file in a text editor and replace the placeholder values with your actual configuration values.

    ```dotenv
    API_KEY=your_openai_api_key
    DECK_NAME=your_anki_deck_name
    ANKI_DB_PATH=/path/to/your/collection.anki2
    ```




## Running the Application


1. **Build and Run Docker Containers**: under the root directory, execute the following command to launch the docker containers: 

    ```bash
    docker-compose up --build
    ```


2. **Run Database Migrations** (only required the first time):
    Do the migration as below: 

    ```bash
    poetry run alembic revision --autogenerate -m "Create anki_cards table"
    ```
    This will generate a `.py` script for migration under `alembic/versions`. Check that if there is anything needing justification. 

    After modifying the script, executing the following command: 

    ```bash
    poetry run alembic upgrade head
    ```
    
    You should be able to find the migrated tables in the DB then. 

    



## Usage


Once the containers are up and running, you can access the application via:

- **FastAPI App**: `http://localhost:4000`
- **Streamlit App**: `http://localhost:8501`

To synchronize your Anki flashcards, use the Streamlit interface or the FastAPI endpoints (`http://localhost:4000/sync/`).