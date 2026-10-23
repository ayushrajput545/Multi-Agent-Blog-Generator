
from state import BlogState
from agent import research_agent , get_llm , writer_agent , editor_agent
from langgraph.types import interrupt , Command
 

MAX_REVISION=3

# Nodes
def researcher_node(state:BlogState)->BlogState:
    """Reseacher Agent generate (or revise) the research outline"""

    llm = get_llm()
    research_data = research_agent(
        llm=llm,
        topic=state.topic,
        audience=state.audience,
        feedback=state.researcher_feedback
    )

    state.research=research_data
    state.researcher_feedback=""
    return state


def human_review_research_node(state:BlogState)->BlogState:
    """Pause and ask human to approve the research or send the feedback"""
    decision= interrupt({
        "stage":"researcher_review",
        "research":state.research,
        "instructions":(
            "Reply with 'approve' to continue the writing",
            "or describe what to change to send it back to the researcher"
        )
    })

    if isinstance(decision , dict): # if our decision is dict type like human provide feedback in dict type
        action = decision.get("action","approve") #If the key(action) doesn't exist → returns the default value:approve.
        feedback = decision.get("feedback","")
    else:                            # if user type something
        text = str(decision) 
        action = "approve" if text.lower() in ["approve", "approved" , "yes" , "ok" , "process" , ""] else "revise" #action = "approve" : "revise"
        feedback = "" if action == "approve" else text

    state.researcher_feedback = feedback
    return state


def writer_node(state:BlogState)->BlogState:
    """Writer Agent produce the full draft blog (or revise it)"""

    llm = get_llm()
    draft_data = writer_agent(
        llm=llm,
        topic=state.topic,
        audience=state.audience,
        research=state.research,
        feedback=state.draft_feedback
    )

    state.draft = draft_data
    state.draft_feedback=""
    return state

def human_review_draft_node(state:BlogState)->BlogState:
    """Pause and ask human to approve the draft or send the feedback"""
    decision= interrupt({
        "stage":"draft_review",
        "research":state.draft,
        "instructions":(
            "Reply with 'approve' to sent the editor",
            "or describe what to change to send it back to the writer"
        )
    })

    if isinstance(decision , dict): # if our decision is dict type like human provide feedback in dict type
        action = decision.get("action","approve") #If the key(action) doesn't exist → returns the default value:approve.
        feedback = decision.get("feedback","")
    else:                            # if user type something
        text = str(decision) 
        action = "approve" if text.lower() in ["approve", "approved" , "yes" , "ok" , "process" , ""] else "revise" #action = "approve" : "revise"
        feedback = "" if action == "approve" else text

    state.draft_feedback = feedback
    return state


def editor_node(state:BlogState)->BlogState:
    """ Editor Agent should produce final polished version of blog"""
    llm = get_llm()
    final = editor_agent(
        llm=llm,
        topic=state.topic,
        draft=state.draft
    )

    state.final_blog=final
    return state



