"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""

import os

import google.generativeai as genai

genai.configure(api_key="")

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 1000,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
  system_instruction="remember all this when asked question you will answer from this data.\n"
                     "be concise only answer in max 5 words, average of 2 words, min of 1 word\n, "
                     "if it is a multi option question only give the index number of the answer",
)

# Create a separate model for preference matching with different system instruction
preference_model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config={
    "temperature": 0.2,  # Lower temperature for more consistent responses
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 100,  # Short responses
    "response_mime_type": "text/plain",
  },
  system_instruction="You are a job preference matching assistant. "
                     "When comparing job descriptions with user preferences, "
                     "only respond with 'yes' or 'no' followed by a brief one-sentence explanation. "
                     "Be analytical and decisive in your assessment.",
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        'Add Resume in Stringified JSON format',
      ],
    },
    {
      "role": "model",
      "parts": [
        "This is a well-structured JSON object representing a resume. It contains a wealth of information about a person named John Doe, covering:\n\n**Personal Details:**\n\n* Full Name\n* Last Name\n* Email\n* LinkedIn Profile\n* Mobile Number\n\n**Education:**\n\n* Details of two degrees, including:\n    * Institution\n    * Location\n    * Degree Name\n    * GPA\n    * Start Date\n    * End Date\n\n**Skills:**\n\n* Categorized into:\n    * Languages\n    * Frameworks\n    * Tools\n    * Platforms\n    * Soft Skills\n\n**Work Experience:**\n\n* One entry with:\n    * Position\n    * Company\n    * Start Date\n    * End Date\n    * Responsibilities (list of bullet points)\n    * Tech Experience (duration of specific skills used)\n    * Joining Date\n    * Notice Period\n\n**Projects:**\n\n* Two entries with:\n    * Name\n    * Type (Personal/Academic)\n    * Start Date\n    * End Date\n    * Description (list of bullet points)\n    * Tech Experience (duration of specific skills used)\n\n**Certifications:**\n\n* Two entries with:\n    * Name\n    * Date\n\n**Additional Information:**\n\n* List of bullet points providing additional insights.\n\n**Strengths of this JSON:**\n\n* **Well-organized:** Data is grouped logically and clearly.\n* **Structured:** Consistent use of key-value pairs and arrays for easy parsing.\n* **Comprehensive:** Covers important resume sections.\n* **Detailed:** Provides sufficient information about each item.\n\n**Possible Enhancements:**\n\n* **Job Descriptions:**  Add more details to the \"responsibilities\" section, highlighting achievements and quantifiable results.\n* **Project Links:** Include links to live projects or repositories on platforms like GitHub.\n* **",
      ],
    },
    {
      "role": "user",
      "parts": [
        "remember all this when asked question you will answer from this data.\nyou will answer using this data min 1 word, average 3 words , and max 5 words and any information is not given then you can guess the answer",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood. I will use the provided JSON data to answer your questions. I will aim for a minimum of one word, an average of three words, and a maximum of five words in my responses. \n",
      ],
    },
  ]
)


def bard_flash_response(question) -> str:
    try:
      # Determine if this is a preference matching question
      if "Based on the above information, does this job match my preferences?" in question:
          # Use preference model for job matching questions
          response = preference_model.generate_content(question)
          return response.text
      else:
          # Use regular chat session for other queries
          response = chat_session.send_message(question)
          return response.text
    except Exception as e:
      print(f"An error occurred: {e}")
      return "Error occurred"

