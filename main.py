from src.ingestion import run_ingestion

if __name__ == "__main__":
    run_ingestion()




# TODO - tell gemini to infer the delay based on th existing data in regard to issues_With_api.md and implement the solution on top of our existing ingestion and aggeregation code in the project
# TODO - tell gemini to modify the readme.md to acknowledge the fact that the user can connect to Trino from datagrip to run the queries there, alternatively to the docker exec -i trino trino --execute  commands
# TODO - tell gemini to implement the 3. Time Between Engine Test And Actual Launch query
# TODO - tell gemini to implement the  4. Launch Site Utilization
# TODO - tell gemini to refactor the requirements.txt to use setup.py instead as it is better practice
# TODO - tell gemini to refactor the README.md ?