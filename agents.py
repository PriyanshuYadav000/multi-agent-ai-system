from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StructuredOutputParser

from tools import web_scrape,web_search

from rich import print

llm = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0,
    max_tokens=2000,
)

#first agent 
def build_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )

#2nd agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[web_scrape]
    )

#lets create chains 
#writer chain

from langchain_core.prompts import ChatPromptTemplate


writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant that can search the web for information and provide summaries."
    ),
    (
        "human",
        """
Write a detailed summary on the topic below.

Topic:
{topic}

Research Gathered:
{research}

Structure the report as:

- Introduction
- Key Findings(minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual, and professional in your writing.
Use the research provided to support your summary.
If no research is provided, indicate that no information was found on the topic.
"""
    ),
])

writer_chain = writer_prompt | llm | StructuredOutputParser()

#critic chain

critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert research critic. Evaluate the report for accuracy, "
        "relevance, completeness, clarity, and writing quality."
    ),
    (
        "human",
        """ Review the Research Report below and evalute it strictly.
Topic:
{topic}

Research:
{research}

Report:
{report}

Provide:

Score: X/10

Strengths:
- 

Areas for Improvement:
- 

Factual Accuracy:
- 

Missing Information:
- 

Overall Feedback:
- 
"""
    ),
])

critic_chain = critic_prompt | llm | StructuredOutputParser()

