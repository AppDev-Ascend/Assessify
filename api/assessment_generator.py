import openai
from dotenv import load_dotenv
import os
import json
import time
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.output_parsers import GuardrailsOutputParser
from llama_index.llm_predictor import StructuredLLMPredictor

from pydantic import BaseModel, Field
from typing import List, Optional
import guardrails as gd

from llama_index.prompts import PromptTemplate
from llama_index.prompts.default_prompts import (
    DEFAULT_TEXT_QA_PROMPT_TMPL,
    DEFAULT_REFINE_PROMPT_TMPL,
)

class Question(BaseModel):
    question: str = Field(...)
    options: List[str] = Field(...)
    answer: int = Field(...)

class Response(BaseModel):
    type: str = Field(...)
    questions: List[Question] = Field(...)

class Assessment(BaseModel):
    type: str = Field(...)
    questions: List[Question] = Field(...)

class AI:

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def get_quiz(self, assessment_type, number_of_questions, learning_outcomes) -> dict:

        print(f"\n\nGenerating {number_of_questions} {assessment_type} Quiz...\n\n")
        assessment = ""
        
        # Create a new index
        documents = SimpleDirectoryReader("Files").load_data()
        index = VectorStoreIndex.from_documents(documents)

        # Define the prompt
        prompt = """
        Query string here.

        ${gr.xml_prefix_prompt}

        ${output_schema}

        ${gr.json_suffix_prompt_v2_wo_none}
        """

        # Create a guard object
        guard = gd.Guard.from_pydantic(output_class=Response, prompt=prompt)

        # Create output parse object
        output_parser = GuardrailsOutputParser(guard)        

        fmt_qa_tmpl = output_parser.format(DEFAULT_TEXT_QA_PROMPT_TMPL)
        fmt_refine_tmpl = output_parser.format(DEFAULT_REFINE_PROMPT_TMPL)

        qa_prompt = PromptTemplate(fmt_qa_tmpl, output_parser=output_parser)
        refine_prompt = PromptTemplate(fmt_refine_tmpl, output_parser=output_parser)

        
        query_engine = index.as_query_engine(
            text_qa_template=qa_prompt,
            refine_template=refine_prompt
        )
            
        # Customize the promot
        new_summary_tmpl_str = (
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Given the context information and not prior knowledge.\n"
            "Query: {query_str}\n"
            "Answer: "
        )

        new_summary_tmpl = PromptTemplate(new_summary_tmpl_str)

        query_engine.update_prompts(
            {"response_synthesizer:summary_template": new_summary_tmpl}
        )

        # Prepare the Query
        question = "a term question" if assessment_type == "identification" else assessment_type
        formatted_learning_outcomes = "\n".join(learning_outcomes)

        response = query_engine.query(f"Create a quiz that contains {number_of_questions} {question} questions for the following learning outcomes:\n\n{formatted_learning_outcomes}\n\n")
        print(response)

        exit()
            
        # Save assessment to a json file
        with open(fr'Project Files\quiz_{assessment_type}.json', 'w') as f:
            json.dump(assessment_json, f)

        return assessment_json

    def get_exam(self, lesson, exam_format, learning_outcomes) -> dict:
         
        print("Generating an exam...\n\n")

        exam = {
            "type": "Exam",
            "sections": []
        }

        for section in exam_format:
            section_name, assessment_type, question_count = section

            print(f"Generating Section {section_name}...\n\n")

            questions = self.get_quiz(lesson, assessment_type, question_count, learning_outcomes)
            exam["sections"].append({
                "section_name": section_name,
                "section_type": assessment_type,
                "questions": questions
            })

            # for testing purposes, since OpenAI has a limit of 3 requests per minute on a free account
            time.sleep(20)

        # Save exam to a json file
        with open(fr'Project Files\exam.json', 'w') as f:
            json.dump(exam, f)
        
        return exam