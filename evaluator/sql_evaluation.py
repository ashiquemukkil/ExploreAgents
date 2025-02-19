from ragas.metrics import LLMSQLEquivalence, DataCompyScore
from ragas.dataset_schema import SingleTurnSample
import openai
import asyncio
import sqlite3

class Evaluator:
    def __init__(self, openai_model, db_connection):
        self.sql_scorer = LLMSQLEquivalence()
        self.sql_scorer.llm = openai_model
        self.data_scorer = DataCompyScore()
        self.db_connection = db_connection
    
    async def evaluate_sql(self, response_sql, reference_sql, reference_contexts):
        sample = SingleTurnSample(
            response=response_sql,
            reference=reference_sql,
            reference_contexts=reference_contexts
        )
        return await self.sql_scorer.single_turn_ascore(sample)
    
    async def evaluate_data(self, response_data, reference_data):
        sample = SingleTurnSample(
            response=response_data,
            reference=reference_data
        )
        return await self.data_scorer.single_turn_ascore(sample)
    
    def execute_sql_queries(self, queries):
        """Executes a list of SQL queries and returns their outputs."""
        results = []
        cursor = self.db_connection.cursor()
        try:
            for query in queries:
                cursor.execute(query)
                results.append(cursor.fetchall())
        except Exception as e:
            results.append(str(e))
        finally:
            cursor.close()
        return results

# Example usage:
# async def main():
#     openai_model = openai.ChatCompletion.create(model="gpt-4")
#     db_connection = sqlite3.connect(":memory:")
#     evaluator = Evaluator(openai_model, db_connection)
#     
#     sql_score = await evaluator.evaluate_sql(response_sql, reference_sql, reference_contexts)
#     data_score = await evaluator.evaluate_data(response_data, reference_data)
#     sql_outputs = evaluator.execute_sql_queries(["SELECT * FROM my_table;"])
#     
#     print("SQL Score:", sql_score)
#     print("Data Score:", data_score)
#     print("SQL Outputs:", sql_outputs)
# 
# asyncio.run(main())
