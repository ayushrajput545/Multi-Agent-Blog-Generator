import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Get LLM
def get_llm(model_name:str="openai/gpt-oss-20b", temperature:float=0.5):
    apikey = os.getenv('GROQ_API_KEY')
    llm = ChatGroq(model=model_name, temperature=temperature, apikey=apikey)
    return llm


# Reasearcher AGENT : system prompt + user prompt ; Build Agent using chain method , will use create_agent method when we need tools
RESEARCHER_PROMPT = ChatPromptTemplate.from_messages([
    {
        "role":"system",
        "content":"""
                  "You are Research Agent. Given a blog topic and target audience produce a clear, "
                  "structured research outline. Include:\n"
                  "1. 5-7 key points the blog should cover\n"
                  "2. Important facts, stats or examples for each point\n"
                  "3. Suggested angle or hook\n"
                  "Be concise. Use bullet points. Do NOT write the full blog yet"
                  """
    },
    {
        "role":"user",
        "content":"Topic: {topic}, Audience: {audience}, {revision_hits}, write research outline now."
    }
])


def research_agent(llm:ChatGroq , topic:str , audience:str , feedback:str=""):
    revision_hits = f"The human provided this feedback on your previous research- {feedback} please address it."
    if not feedback:
        revision_hints="This is your first attempt"

    chain = RESEARCHER_PROMPT | llm

    result = chain.invoke({
        "topic":topic,
        "audience":audience,
        "revision_hits":revision_hits
    })

    return result.content

# Writer Agent
WRITER_PROMPT = ChatPromptTemplate.from_messages([
    {
        "role":"system",
        "content":"""
                  "You are a Blog Writer Agent. Using the research notes provided, write a complete, "
                  "engaging blog post. \n"
                  "Rules: \n"
                  "1. Length: should be 500-800 words\n"
                  "2. Structure: catchy title, intro hook, 3-5 sections with h2 headings, conclusion \n"
                  "3. Tone: clear friendly, suited to the target audience \n"
                  "Use markdown formatting \n"
                  "Do not add word count line at the end"
                  """
    },
    {
        "role":"user",
        "content":"Topic: {topic}, Audience: {audience}, Research Notes:{research}, {revision_hits}, Write full blog post now"
    }
])

def writer_agent(llm:ChatGroq , topic:str , audience:str , research:str, feedback:str=""):
    revision_hits = f"The human provided this feedback on your previous draft blog and asked for these changes - {feedback}. Please apply these changes while writing the blog"
    if not feedback:
        revision_hints="This is your first attempt"

    chain = WRITER_PROMPT | llm

    result = chain.invoke({
        "topic":topic,
        "audience":audience,
        "research":research,
        "revision_hits":revision_hits
    })

    return result.content


# Editor AGENT
EDITOR_PROMPT = ChatPromptTemplate.from_messages([
    {"role":"system", "content":"""
        "You are an Editor Agent - the final quality gate before publishing.\n"
        "Take the draft and produce the FINAL polished version. Specifically:\n"
        "- Fix grammar, spelling, and awkward phrasing\n"
        "- Tighten wordy sentences\n"
        "- Improve flow and transitions between sections\n"
        "- Make the title and intro more compelling if needed\n"
        "- Keep the same structure and markdown formatting\n"
        "- Blog Wordings should look like human, not a AI, and don't use any special chars and complex / fancy words.\n"
        "Output only the final polished blog post - no commentary."

    """},
    { "role":"user", "content":"""
        Topic: {topic},
        Draft:{draft}
        Return the published blog post
    """ }
])

def editor_agent(llm:ChatGroq , topic:str , draft:str):

    chain = WRITER_PROMPT | llm

    result = chain.invoke({
        "topic":topic,
        "draft":draft
    })

    return result.content
