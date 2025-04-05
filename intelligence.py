from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Initialize the OpenAI client with the API key from environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def news_generator(company_code, topic, audience, tone, article_length, language):
    """
    Generates a news article based on the provided parameters using OpenAI's GPT-3.5-turbo model.
    
    Parameters:
        topic (str): The topic for the news article.
        audience (str): The target audience for the article.
        tone (str): The tone of the article (e.g., formal, informal).
        article_length (str): The desired length of the article (e.g., short, medium, long).
        language (str): The language in which to generate the article.
        
    Returns:
        str: The generated news article.
    """
    # Define the prompt for the OpenAI API
    prompt = f"Generate a {article_length} news article about '{topic}' for a {audience} audience with a {tone} tone in {language}."
    if company_code == "ai@fcode"
      # Call the OpenAI API to generate the news article
      response = client.chat.completions.create(
          model="gpt-4o",
          messages=[{"role": "user", "content": prompt}],
          temperature=0.7,
          max_tokens=500  # Adjust max_tokens as needed
      )
    # Extract and return the generated text from the response
      generated_text = response.choices[0].message.content
      return generated_text
    else:
      return "Company Code does not match! Please enter correct company code.
