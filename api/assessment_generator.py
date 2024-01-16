from dotenv import load_dotenv
import openai
import os
import json
import time
from llama_index.llms import OpenAI
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext, StorageContext, load_index_from_storage
class AssessmentGenerator:
    
    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        llm = OpenAI(model="gpt-4-1106-preview")
        self.service_context = ServiceContext.from_defaults(llm=llm)

    def read_excluded_questions(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return f.read()
        else:
            return ""
    
    def write_excluded_questions(self, file_path, questions):
        with open(file_path, 'w') as f:
            f.write(questions)

    def get_quiz(self, username, assessment_type, number_of_questions, learning_outcomes, lesson_path="", exclude_questions=False, index=None) -> dict:
        
        print("Generating Quiz...")
        print(f"Assessment Type: {assessment_type}")
        print(f"Number of Questions: {number_of_questions}")
        print(f"Learning Outcomes: {learning_outcomes}")

        assessment = ""

        if index is None:
            # Create the index
            documents = SimpleDirectoryReader(lesson_path).load_data()
            index = VectorStoreIndex.from_documents(documents, service_context=self.service_context)

        # Create response format
        match(assessment_type):
            case "Multiple Choice" | "multiple choice":
                question = "multiple choice questions with important terms as an answer"
                response_format = 'The result type should be provided in the following JSON data structure:\n\
                                {\
                                    "question": "Question", \
                                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"], \
                                    "answer": Int Index \
                                }\n\
                                Separate each question with a these symbols >>>.\n\
                                Respond only with the output in the exact format specified, with no explanation or conversation.'

            case "Identification" | "identification" | "True or False" | "true or false":
                question = "term identification question where the answer are important terms" if assessment_type == "Identification" else "true or false questions"
                response_format = 'The result type should be provided in the following JSON data structure:\n\
                                {\
                                    "question": "Question", \
                                    "answer": "Answer" \
                                }\n\
                                Do not include numbers in the questions. Separate each question with a these symbols >>>.\n\
                                Respond only with the output in the exact format specified, with no explanation or conversation.'

            case "Fill in the Blanks" | "fill in the blanks":
                question = "fill in the blanks questions term where the answer are important terms"
                response_format = 'The result type should be provided in the following JSON data structure:\n\
                                {\
                                    "question": "Question with blank", \
                                    "answer": "Answer" \
                                }\n\
                                Do not include numbers in the questions. Separate each question with a these symbols >>>.\n\
                                Respond only with the output in the exact format specified, with no explanation or conversation.'
            case "Essay" | "essay":
                question = "essay questions"
                response_format = 'The result type should be provided in the following JSON data structure:\n\
                                { \
                                    "question": "Question", \
                                }\n\
                                Do not include numbers in the questions. Separate each question with a these symbols >>>.\n\
                                Respond only with the output in the exact format specified, with no explanation or conversation.'

        # Format for the prompt
        if learning_outcomes == [] or learning_outcomes == None:
            my_prompt = f"Generate {number_of_questions} {question}.\n\n{response_format}"
        else:
            formatted_learning_outcomes = "\n".join(learning_outcomes)
            my_prompt = f"Generate {number_of_questions} {question} that is aligned with these learning outcomes: \n\n{formatted_learning_outcomes}.\n\n{response_format}"
        
        if exclude_questions == True:
            existing_excluded_questions = self.read_excluded_questions(fr'media\{username}\lessons\excluded_questions.txt')
            my_prompt = my_prompt + f"\n\nMake sure that these questions are excluded: \n\n{existing_excluded_questions}."
        
        print("Prompt: ", my_prompt)

        query_engine = index.as_query_engine()
        assessment = query_engine.query(my_prompt)
      
        assessment_str = str(assessment)
        
        lines = assessment_str.split(">>>")
        quiz = {
            "type": assessment_type,
            "questions": []
        }

        for line in lines:
            if line != "":
                question = json.loads(line)
                quiz["questions"].append(question)

                if exclude_questions == True:
                    self.write_excluded_questions(fr'media\{username}\lessons\excluded_questions.txt', question["question"])

        return quiz
    
    def get_exam(self, username, exam_format, lesson="") -> dict:

        print("Generating Exam...")

        os.makedirs(fr'media\{username}\lessons', exist_ok=True)
        
        if lesson == "":
                print("Loading the Documents")
                documents = SimpleDirectoryReader(fr"media\{username}\lessons").load_data()
        else:
            print("Storing the Lesson")
            with open(fr'media\{username}\lessons\lesson.txt', 'w') as f:
                f.write(lesson)
            documents = SimpleDirectoryReader(lesson).load_data()
        
        index = VectorStoreIndex.from_documents(documents, service_context=self.service_context)

        exam = {
            "type": "Exam",
            "sections": []
        }
        counter = 1
        for section in exam_format:
            
            assessment_type, question_count, learning_outcomes = section

            print(f"Generating Section {counter}...")

            if learning_outcomes == []:
                exclude = True
            else:
                exclude = False

            questions = self.get_quiz(username, assessment_type, question_count, learning_outcomes, exclude_questions=exclude, index=index)
            
            exam["sections"].append({
                "name": f"Section {counter}",
                "type": assessment_type,
                "questions": questions["questions"]
            })

            # # Add excluded questions
            # excluded_questions_file_path = r'media\lessons\excluded_questions.txt'
            # existing_excluded_questions = self.read_excluded_questions(excluded_questions_file_path)

            # for question in questions["questions"]:
            #     existing_excluded_questions = existing_excluded_questions + "\n" + question["question"]
            # self.write_excluded_questions(excluded_questions_file_path, existing_excluded_questions)

            counter += 1

            
        # self.write_excluded_questions(excluded_questions_file_path, "")
        print(exam)
        return exam