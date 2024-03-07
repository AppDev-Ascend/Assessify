from pdf2image import convert_from_path
import pytesseract
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

class Converter:

    @staticmethod
    def pdf_to_text(pdf_path):
        """
        Extract text content from a PDF file.

        Parameters:
        - pdf_path (str): The path to the PDF file.

        Returns:
        str: The extracted text content from the PDF.

        Note:
        - This method uses Poppler for PDF rendering and Tesseract OCR for text extraction.
        - Ensure that the 'poppler_path' and 'tesseract_cmd' paths are correctly set for your environment.
        - The method returns the extracted text content from the PDF.
        """

        poppler_path = r'poppler-23.11.0\Library\bin'
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
        text = ''
        for i, img in enumerate(images):
            text += f'\nPage {i + 1}:\n\n'
            text += pytesseract.image_to_string(img, lang='eng')

        return text

    @staticmethod
    def quiz_to_pdf(assessment, type):
        """
        Convert a quiz assessment in JSON format to a PDF document.

        Parameters:
        - assessment (dict): The quiz assessment in dictionary format.
        - type (str): The type of assessment ("Multiple Choice", "Identification", "True or False", "Fill in the Blanks", "Essay").

        Note:
        - This method creates a PDF document with formatted content based on the quiz assessment.
        - The PDF is saved to the 'Project Files' directory with the naming convention 'assessment_{type}.pdf'.
        - The method supports different types of assessments, each with specific formatting.
        - The assessment dictionary should have the structure consistent with the expected format for the given type.
        """

        # Create a PDF document
        pdf_canvas = canvas.Canvas(rf"api\media\files\exports\quiz_{type}.pdf", pagesize=letter)

        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.drawString(50, 770, f"{type}")
        pdf_canvas.setFont("Helvetica", 12)

        # Extract information from the JSON
        questions = assessment.get("questions", [])

        # Add content to the PDF
        pdf_canvas.setFont("Helvetica", 12)

        y_position = 750  # Adjusted starting position
        x_position = 50  # Adjusted starting position on the x-axis
        line_height = 10  # Adjusted line height
        max_line_length = 80  # Adjusted maximum line length

        for index, question in enumerate(questions, start=1):
            y_position -= 2 * line_height  # Adjust the vertical position for each question

            question_text = question.get("question", "")

            if type == "multiple choice":
                options = question.get("options", [])
                pdf_canvas.drawString(x_position, y_position, f"{index}. {question_text}")

                # Add options to the PDF
                for option_index, option in enumerate(options, start=1):
                    y_position -= line_height  # Adjust the vertical position for each option
                    wrapped_option_lines = Converter.wrap_text(f"{chr(96 + option_index)}. {option}", max_line_length)
                    for i, wrapped_option_line in enumerate(wrapped_option_lines):
                        if i == 0:
                            y_position -= line_height
                            pdf_canvas.drawString(x_position + 15, y_position, wrapped_option_line)
                        else:
                            pdf_canvas.drawString(x_position + 28, y_position - 2, wrapped_option_line)
                        y_position -= line_height

            elif type == "identification":
                wrapped_text_lines = Converter.wrap_text(f"{index}. {question_text}", max_line_length)
                for i, wrapped_text_line in enumerate(wrapped_text_lines):
                    if i == 0:
                        pdf_canvas.drawString(x_position, y_position, wrapped_text_line)
                    else:
                        pdf_canvas.drawString(x_position + 15, y_position, wrapped_text_line)
                    y_position -= line_height

            elif type == "true or false":
                wrapped_text_lines = Converter.wrap_text(f"{index}. {question_text}", max_line_length)
                for i, wrapped_text_line in enumerate(wrapped_text_lines):
                    if i == 0:
                        pdf_canvas.drawString(x_position, y_position, wrapped_text_line)
                    else:
                        pdf_canvas.drawString(x_position + 15, y_position, wrapped_text_line)
                    y_position -= line_height

            elif type == "fill in the blanks":
                lines = Converter.wrap_text(f"{index}. {question_text}", max_line_length)
                for i, line in enumerate(lines):
                    if i == 0:
                        pdf_canvas.drawString(x_position, y_position, line)
                    else:
                        pdf_canvas.drawString(x_position + 15, y_position-5, line)
                    y_position -= line_height

            elif type == "essay":
                lines = Converter.wrap_text(f"{index}. {question_text}", max_line_length)
                for i, line in enumerate(lines):
                    if i == 0:
                        pdf_canvas.drawString(x_position, y_position, line)
                    else:
                        pdf_canvas.drawString(x_position + 15, y_position-5, line)
                    y_position -= line_height

            y_position -= line_height  # Adjust the vertical position for the next question

        # Save the PDF
        pdf_canvas.save()

    @staticmethod
    def quiz_answer_key(assessment, type):
        """
        Generate an answer key PDF for a quiz assessment.

        Parameters:
        - assessment (dict): The quiz assessment in dictionary format.
        - type (str): The type of assessment ("Multiple Choice", "Identification", "True or False", "Fill in the Blanks", "Essay").

        Note:
        - This method creates an answer key PDF document with correct answers for the quiz assessment.
        - The PDF is saved to the 'Files' directory with the naming convention 'answer_key_{type}.pdf'.
        - The method supports different types of assessments, each with specific formatting for correct answers.
        - The assessment dictionary should have the structure consistent with the expected format for the given type.
        """

        # Get the questions from the assessment
        questions = assessment.get("questions", [])

        # Create a PDF document for the answer key
        pdf_canvas = canvas.Canvas(fr"api\media\files\exports\quiz_answer_key_{type}.pdf", pagesize=letter)

        # Add content to the PDF
        pdf_canvas.setFont("Helvetica", 12)

        

        y_position = 780
        for index, question in enumerate(questions, start=1):
            y_position -= 15  # Adjust the vertical position for each question

            if type == "multiple choice":
                correct_answer = f"Question {index}: {question['answer']}"
            elif type == "identification":
                correct_answer = f"Question {index}: {question['answer']}"
            elif type == "true or false":
                correct_answer = f"Question {index}: {'True' if question['answer'] else 'False'}"
            elif type == "fill in the blanks":
                correct_answer = f"Question {index}: {question['answer']}"

            pdf_canvas.drawString(120, y_position, correct_answer)

            y_position -= 25  # Adjust the vertical position for the next question

        # Save the PDF
        pdf_canvas.save()

    @staticmethod
    def exam_to_pdf(exam):
        """
        Convert an exam assessment in JSON format to a PDF document.

        Parameters:
        - exam (dict): The exam assessment in dictionary format.

        Note:
        - This method creates a PDF document with formatted content based on the exam assessment.
        - The PDF is saved to the 'Files' directory with the naming convention 'exam.pdf'.
        - The method supports different types of exam sections, each with specific formatting for questions.
        - The exam dictionary should have the structure consistent with the expected format.
        - If the vertical position (y_position) exceeds the y_limit, a new page is added.
        """

        # Create a PDF document
        pdf_canvas = canvas.Canvas(r"api\media\files\exports\exam.pdf", pagesize=letter)

        # Add a header to the PDF
        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.drawString(50, 770, "Exam")
        pdf_canvas.setFont("Helvetica", 12)

        y_position = 750
        x_position = 50
        line_height = 10
        max_line_length = 80
        y_limit = 100  # Set the y_limit

        for section in exam["sections"]:
            # Add section name to the PDF
            pdf_canvas.setFont("Helvetica-Bold", 12)
            pdf_canvas.drawString(x_position, y_position, section["section_type"])
            pdf_canvas.setFont("Helvetica", 12)
            y_position -= line_height  # Adjust the vertical position for the section name

            questions = section["questions"]["questions"]
            for index, question in enumerate(questions, start=1):
                y_position -= line_height  # Adjust the vertical position for each question

                question_text = question.get("question", "")
                wrapped_question_lines = Converter.wrap_text(f"{index}. {question_text}", max_line_length)
                for i, wrapped_question_line in enumerate(wrapped_question_lines):
                    if i == 0:
                        y_position -= line_height
                        pdf_canvas.drawString(x_position, y_position, wrapped_question_line)
                    else:
                        y_position -= 5
                        pdf_canvas.drawString(x_position + 15, y_position, wrapped_question_line)
                    y_position -= line_height

                # Add options to the PDF if it's a Multiple Choice section
                if section["section_type"] == "Multiple Choice":
                    options = question.get("options", [])
                    for option_index, option in enumerate(options, start=1):
                        y_position -= line_height  # Adjust the vertical position for each option
                        wrapped_option_lines = Converter.wrap_text(f"{option}", max_line_length)
                        for i, wrapped_option_line in enumerate(wrapped_option_lines):
                            if i == 0:
                                y_position -= line_height
                            pdf_canvas.drawString(x_position + 15, y_position, wrapped_option_line)
                            y_position -= line_height

                y_position -= line_height  # Adjust the vertical position for the next question

                # Check if y_position exceeds the y_limit, add a new page if needed
                if y_position < y_limit:
                    pdf_canvas.showPage()
                    y_position = 750  # Reset y_position for the new page

            y_position -= line_height # Adjust the vertical position for the next section

        # Save the PDF
        pdf_canvas.save()

    @staticmethod
    def exam_answer_key(exam):

        """
        Generate an answer key PDF for an exam assessment.

        Parameters:
        - exam (dict): The exam assessment in dictionary format.

        Note:
        - This method creates an answer key PDF document with correct answers for the exam assessment.
        - The PDF is saved to the 'Project Files' directory with the naming convention 'exam_answer_key.pdf'.
        - The method supports different types of exam sections, each with specific formatting for correct answers.
        - The exam dictionary should have the structure consistent with the expected format.
        - If the vertical position (y_position) exceeds the y_limit, a new page is added.
        """

        # Create a PDF document for the answer key
        pdf_canvas = canvas.Canvas(r"api\media\files\exports\exam_answer_key.pdf", pagesize=letter)

        # Add content to the PDF
        pdf_canvas.setFont("Helvetica", 12)
        max_line_length = 80  # Adjusted maximum line length
        y_position = 780
        y_limit = 100  # Set the y_limit
        line_height = 10  # Set the line height
        x_position = 80  # Adjusted starting position on the x-axis

        for section in exam["sections"]:
            # Add section name to the PDF
            pdf_canvas.setFont("Helvetica-Bold", 14)
            if section["section_type"] != "Essay":
                pdf_canvas.drawString(50, y_position, section["section_type"])
            pdf_canvas.setFont("Helvetica", 12)
            y_position -= line_height  # Adjust the vertical position for the section name

            questions = section["questions"]["questions"]
            for index, question in enumerate(questions, start=1):
                y_position -= 2 * line_height  # Adjust the vertical position for each question

                # Check if y_position exceeds the y_limit, add a new page if needed
                if y_position < y_limit:
                    pdf_canvas.showPage()
                    y_position = 780  # Reset y_position for the new page

                if section["section_type"] == "Multiple Choice":
                    correct_answer = f"Question {index}: {chr(97 + question['answer'])}"
                elif section["section_type"] == "Identification":
                    correct_answer = f"Question {index}: {question['answer']}"
                elif section["section_type"] == "True or False":
                    correct_answer = f"Question {index}: {'True' if question['answer'] else 'False'}"
                elif section["section_type"] == "Fill in the Blanks":
                    correct_answer = f"Question {index}: {question['answer']}"
                elif section["section_type"] == "Essay":
                    pass
                
                if(section["section_type"] != "Essay"):
                    wrapped_correct_answer = Converter.wrap_text(correct_answer, max_line_length)
                    for i, wrapped_question_line in enumerate(wrapped_correct_answer):
                        if i == 0:
                            y_position -= line_height
                            pdf_canvas.drawString(x_position, y_position, wrapped_question_line)
                        else:
                            y_position -= 5
                            pdf_canvas.drawString(x_position + 65, y_position, wrapped_question_line)
                        y_position -= line_height

            y_position -= 2 * line_height  # Adjust the vertical position for the next section

        # Save the PDF
        pdf_canvas.save()

    @staticmethod
    def wrap_text(text, max_length):
        """Wrap text to limit the line length and return a list of strings."""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_length:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.strip())

        return lines

    @staticmethod
    def quiz_to_gift(json_data):
        """
        Convert a quiz assessment in JSON format to a GIFT (General Import Format Template) file.

        Parameters:
        - json_data (dict): The quiz assessment in dictionary format.
        - output_file (str): The path to the output GIFT file.

        Note:
        - This method supports various types of quiz questions (Multiple Choice, Identification, True or False, Fill in the Blanks, Essay).
        - The GIFT file is created based on the input JSON data and saved to the specified output file.
        """

        gift_string = ""

        for question_data in json_data["questions"]:
            question_type = json_data["type"]
            question_text = question_data["question"]

            if question_type == "Multiple Choice":
                options = question_data.get("options", [])
                correct_answer_index = question_data.get("answer", 0)

                gift_string += f"::Question::{question_text}?\n"
                for i, option in enumerate(options):
                    if i == correct_answer_index:
                        gift_string += f"= {option}\n"
                    else:
                        gift_string += f"~ {option}\n"

            elif question_type == "Identification":
                correct_answer = question_data.get("answer", "")

                gift_string += f"::Question::{question_text}?\n= {correct_answer}\n"

            elif question_type == "True or False":
                correct_answer = question_data.get("answer", False)

                gift_string += f"::Question::{question_text}?\n"
                if correct_answer:
                    gift_string += "= True\n~ False\n"
                else:
                    gift_string += "= False\n~ True\n"

            elif question_type == "Fill in the Blanks":
                correct_answer = question_data.get("answer", "")

                gift_string += f"::Question::{question_text} is ___?\n= {correct_answer}\n"

            elif question_type == "Essay":
                gift_string += f"::Question::{question_text}?\n"

        # Save the GIFT content to the specified output file
        with open(r"api\media\files\exports\quiz_gift.txt", "w") as file:
            file.write(gift_string)

    @staticmethod
    def exam_to_gift(exam, output_file):
        """
        Convert an exam assessment in JSON format to a GIFT (General Import Format Template) file.
        
        Parameters:
        - exam (dict): The exam assessment in dictionary format.

        Note:
        - This method supports various types of exam sections (Multiple Choice, Identification, True or False, Fill in the Blanks, Essay).  
        - The GIFT file is created based on the input JSON data and saved to the specified output file.
        """
        
        gift_string = ""

        for section in exam["sections"]:
            section_name = section["section_name"]
            section_type = section["section_type"]
            questions = section["questions"]

            gift_string += f"::Section::{section_name}::{section_type}::\n"

            for question_data in questions:
                question_text = question_data["question"]

                if section_type == "Multiple Choice":
                    options = question_data.get("options", [])
                    correct_answer_index = question_data.get("answer", 0)

                    gift_string += f"::Question::{question_text}?\n"
                    for i, option in enumerate(options):
                        if i == correct_answer_index:
                            gift_string += f"= {option}\n"
                        else:
                            gift_string += f"~ {option}\n"

                elif section_type == "Identification":
                    correct_answer = question_data.get("answer", "")

                    gift_string += f"::Question::{question_text}?\n= {correct_answer}\n"

                elif section_type == "True or False":
                    correct_answer = question_data.get("answer", False)

                    gift_string += f"::Question::{question_text}?\n"
                    if correct_answer:
                        gift_string += "= True\n~ False\n"
                    else:
                        gift_string += "= False\n~ True\n"

                elif section_type == "Fill in the Blanks":
                    correct_answer = question_data.get("answer", "")

                    gift_string += f"::Question::{question_text} is ___?\n= {correct_answer}\n"

                elif section_type == "Essay":
                    gift_string += f"::Question::{question_text}?\n"

        # Save the GIFT content to the specified output file
        with open(r"api\media\files\exports\exam_gift.txt", "w") as file:
            file.write(gift_string)

        return gift_string