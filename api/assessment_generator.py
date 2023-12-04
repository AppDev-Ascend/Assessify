from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import time

class AI:

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def get_quiz(self, lesson, assessment_type, number_of_questions, learning_outcomes) -> dict:

        """
        Generate a quiz based on the specified assessment type and learning outcomes.

        Parameters:
        - lesson (str): The lesson for which the quiz is generated.
        - assessment_type (str): The type of assessment (e.g., "Multiple Choice", "Identification").
        - number_of_questions (int): The number of questions to generate for the quiz.
        - learning_outcomes (list): A list of learning outcomes to guide question generation.

        Returns:
        dict: The generated quiz in dictionary format.

        Note:
        - The function uses GPT-3.5-turbo from OpenAI to generate quiz questions based on the provided information.
        - The generated quiz is validated against the expected JSON structure for each assessment type.
        - If the assessment generated does not match the expected format, the function prints an error message and exits.
        - The generated quiz is saved to a JSON file named 'assessment_{assessment_type}.json'.
        - The function returns the generated quiz in dictionary format.
        """

        print(f"\n\nGenerating {number_of_questions} {assessment_type} Quiz...\n\n")
        assessment = ""

        match(assessment_type):
            case "Multiple Choice":
                json_data = {
                    "type": "Multiple Choice",
                    "questions": [
                    {
                        "question": "Question",
                        "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                        "answer": 1,
                    }
                    ]
                }
            case "Identification":
                json_data = {
                    "type": "Identification",
                    "questions": [
                    {
                        "question": "Question",
                        "answer": "Answer 1",
                    }
                    ]
                }
            case "True or False":
                json_data = {
                    "type": "True or False",
                    "questions": [
                    {
                        "question": "Question",
                        "answer": True,
                    }
                    ]
                }
            case "Fill in the Blanks":
                json_data = {
                    "type": "Fill in the Blanks",
                    "questions": [
                    {
                        "question": "Question is ___",
                        "answer": "Answer 1",
                    }
                    ]
                }
            case "Essay":
                json_data = {
                    "type": "Essay",
                    "questions": [
                    {
                        "question": "Question",
                    }
                    ]
                }
            case _:
                print("Error: Invalid Assessment Type")

        json_string = json.dumps(json_data)

        question = "a flashcard question where the term is an answer" if assessment_type == "identification" else assessment_type

        is_valid = False
        while not is_valid:
            # API Call to Generate Assessment
            if json_data is not None:
                completion = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are an assessment generator who have no outside knowledge and must only generate questions based on the outputted lesson. The assessment generated should follow these learning outcomes: \n {learning_outcomes}\
                                        Lastly, You must output the assessment in JSON format."
                        },
                        {
                            "role": "user",
                            "content": f"Compose an quiz for this lesson {lesson}. \n \
                                        The quiz contains {number_of_questions} questions that is {question} \n \
                                        Lastly, the output must be a JSON in this format: {json_string}"
                        }
                    ]
                )

                assessment = completion.choices[0].message.content

                # Test the Assessment Format
                try:
                    assessment_json = json.loads(assessment)

                    if "type" in assessment_json and "questions" in assessment_json and isinstance(assessment_json["questions"], list):
                        for question in assessment_json["questions"]:
                            if assessment_json["type"] == "Multiple Choice":
                                if "question" in question and "options" in question and "answer" in question:
                                    is_valid = True
                                else:
                                    print("Error: Question in the Multiple Choice assessment does not match expected format.")
                                    is_valid = False
                                    break
                            elif assessment_json["type"] == "Identification":
                                if "question" in question and "answer" in question:
                                    is_valid = True
                                else:
                                    print("Error: Question in the Identification assessment does not match expected format.")
                                    is_valid = False
                                    break
                            elif assessment_json["type"] == "True or False":
                                if "question" in question and "answer" in question:
                                    is_valid = True
                                else:
                                    print("Error: Question in the True or False assessment does not match expected format.")
                                    is_valid = False
                                    break
                            elif assessment_json["type"] == "Fill in the Blanks":
                                if "question" in question and "answer" in question:
                                    is_valid = True
                                else:
                                    print("Error: Question in the Fill in the Blanks assessment does not match expected format.")
                                    is_valid = False
                                    break
                            elif assessment_json["type"] == "Essay":
                                if "question" in question:
                                    is_valid = True
                                else:
                                    print("Error: Question in the Essay assessment does not match expected format.")
                                    is_valid = False
                                    break
                            else:
                                print("Error: Invalid Assessment Type")
                                is_valid = False
                                break
                    else:
                        print("Error: Assessment JSON structure does not match expected format.")
                        is_valid = False

                except json.JSONDecodeError:
                    print(assessment)
                    print("Error: Assessment is not in valid JSON format")
                    is_valid = False

        return assessment_json

    def get_exam(self, lesson, exam_format, learning_outcomes) -> dict:
        """
        Generate an exam based on the specified format and learning outcomes.

        Parameters:
        - lesson (str): The lesson for which the exam is generated.
        - exam_format (list): A list of tuples specifying the sections of the exam.
          Each tuple contains:
            - section_name (str): The name of the exam section.
            - assessment_type (str): The type of assessment for the section (e.g., "Multiple Choice").
            - question_count (int): The number of questions to generate for the section.
        - learning_outcomes (list): A list of learning outcomes to guide question generation.

        Returns:
        dict: The generated exam in dictionary format.

        Note:
        - For testing purposes, there is a sleep of 60 seconds between generating sections
          to comply with OpenAI API usage limits (3 requests per minute on a free account).
        - The generated exam is also saved to a JSON file named 'assessment_exam.json'.
        """
         
        print("Generating an exam...\n\n")

        exam = {
            "type": "Exam",
            "sections": []
        }

        for section in exam_format:
            section_name, assessment_type, question_count = section

            print(f"Generating Section {section_name}...\n\n")

            # 
            questions = self.get_quiz(lesson, assessment_type, question_count, learning_outcomes)
            exam["sections"].append({
                "section_name": section_name,
                "section_type": assessment_type,
                "questions": questions
            })

            # for testing purposes, since OpenAI has a limit of 3 requests per minute on a free account
            time.sleep(20)
            
        return exam