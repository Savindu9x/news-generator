from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import streamlit as st

# define the main llm
llm = LLM(model="openai/gpt-4o-mini", temperature=1.0, max_tokens=5000)

@tool("Exa Fetch Content tool")
def exa_get_contents_tool(
    url: str,
) -> str:
    """
    Fetches all text contents from the given url

    :param question: url of the website where content needs to fetch from.
    :return: The text contents of the web page.
    """
    api_key = st.secrets["EXA_API_KEY"]
    endpoint = "https://api.exa.ai/contents"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "urls": [url],
        "text": True,
        "livecrawl": "always"
    }

    response = requests.post(endpoint, headers=headers, json=payload)

    if response.ok:
        return response.json()
    else:
        return None
    # ExaSearch  = Exa(api_key=st.secrets["EXA_API_KEY"])
    # response = ExaSearch.get_contents(urls=[url], livecrawl="always",
    #                          text={"include_html_tags": False}, 
    #                          )
    # return response

search_tool = [exa_get_contents_tool]

senior_research_analyst = Agent(
    role="Senior Research Analyst",
    goal=f"Research, analyze, and synthesize comprehensive information on the given topic using content from the user-provided URLs.",
    backstory="You're an expert research analyst working for event planning company based in Netherlands helping company gather information to write article on upcoming events or key speaks."
            "You have a knack for methodically examining provided materials."
            "You excel at reading and extracting key insights from any text or reference documents you receive."
            "You can fact-check data, and provide well-organized, thorough research briefs."
            "Your analysis includes both raw data and interpreted insights, making complex information accessible and actionable."
            "You incorporate clear citations to help others trace the origins of the information.",
    allow_delegation=False,
    verbose=True,
    tools=search_tool,
    llm=llm
)

# Second Agent: Content Writer
article_writer = Agent(
    role="News Article Writer",
    goal="Transform the research findings into an in-depth, engaging news-style article that maintains factual accuracy, proper citations, and a reader-friendly structure.",
    backstory="You are an experienced news article writer working for event planning company helping to promote event, key speaks through article writing." \
            "You possess a talent to create compelling, "
            "well-structured, and accurate articles based on research briefs. Your writing"
            "style combines informational depth with a subtle promotional tone, effectively"
            "highlighting the significance of industry events or developments. You excel at"
            "weaving in critical data and citations from the Senior Research Analyst, while"
            "ensuring the piece remains accessible and engaging. You strike the perfect balance "
            "between detail and readability, using subheadings, bullet points, and expert quotes"
            "to keep readers informed and interested.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

# Research Task
research_task = Task(
    description=("""Analyze and synthesize comprehensive information on {topic} using the content from {urls}.
        Your responsibilities include:
        - Identifying key developments, trends, and innovations presented in the source materials.
        - Collecting relevant expert opinions, statistics, and market insights if available.
        - Incorporating Factual information and data from the provided URLs.
        - Evaluate source credibility and fact-check all information
        - Organizing findings into a clear, structured research brief.
        - Providing complete citations and references for all utilized sources.
    """),
    expected_output="""A well-organized research report containing:
        - Executive summary of key findings.
        - In-depth analysis of current trends and developments.
        - List of verified facts and statistics
        - All citations and links to original sources
        - Clear categorization of main themes and patterns
        Please format with clear sections and bullet points for easy reference.""",
    agent=senior_research_analyst
)

# Writing Task
writing_task = Task(
    description=("""Using the research brief provided, write an engaging **in-depth news-style article** that:
        1. Converts technical or complex information into reader-friendly language.
        2. Stays factually accurate, reflecting the data and insights from the research brief.
        3. Maintains a balanced, professional tone with a subtle promotional angle (where relevant).
        4. Follows the structure and style of the sample news articles, but approximately **twice** their length.
        5. Includes:
            - Attention-grabbing introduction
            - Organize the body into clear sections, each with its own heading.
            - Provide a concise yet engaging conclusion or outlook.
        6. Ends with a 'References' section listing all sources used (in bullet points or list form).
        5. Includes a References section at the end
    """),
    expected_output="""A polished, longer-form article in Markdown format that:
        - Do not include a title for the article.
        - Maintains a factual yet engaging style, highlighting key facts, or expert viewpoints.
        - Presents the content in well-structured sections (H1 for title, H3 for sub-sections).
        - Presents information in an accessible yet informative way.
        - Includes a final 'References' section with all sources cited in the article.
        - Delivers around 400-500 word count offering more depth and insight.""",
    agent=article_writer
)

# Create Crew
crew = Crew(
    agents=[senior_research_analyst, article_writer],
    tasks=[research_task, writing_task],
    verbose=True
)

# Run Crew
def run_agent(topic: str, links: list[str]):
    """
    Run the crew with the given topic and links.

    :param topic: The topic to research and write about.
    :param links: A list of URLs to fetch content from.
    :return: The final article generated by the crew.
    """
    # Start the crew with the given inputs
    crew_output = crew.kickoff(inputs={"topic": topic, "urls": links})
    
    # Wait for the crew to finish and return the final article
    # The crew will automatically handle the task delegation and execution
    return crew_output.raw
