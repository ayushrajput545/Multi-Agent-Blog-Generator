
from state import BlogState
from agent import research_agent , get_llm , writer_agent , editor_agent
from langgraph.types import interrupt , Command
from typing import Literal
from langgraph.graph import StateGraph , START , END
from langgraph.checkpoint.memory import InMemorySaver
 

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



# CONDTIONAL ROUTE EDGES (for HITL) -> Decided on which node , we redirect after feedback
def route_after_research_review(state:BlogState)->Literal["research","writer"]: #
    if state.researcher_feedback:
        return "research" #redirect to research node again if feedback present
    else:
        return "writer"

def route_after_draft_review(state:BlogState)->Literal["writer","editor"]:
    if state.draft_feedback and state.revision_count < MAX_REVISION: 
        return "writer"
    else:
        return "editor"

# Build and compile the graph
def build_blog_graph():
    builder = StateGraph(BlogState)

    # Add nodes
    builder.add_node("research",researcher_node)
    builder.add_node("review_research",human_review_research_node)
    builder.add_node("writer", writer_node)
    builder.add_node("review_draft",human_review_draft_node)
    builder.add_node("editor",editor_node)

    # EDGES
    builder.add_edge(START , "research")
    builder.add_edge("research" , "review_research")
    builder.add_conditional_edges("review_research", route_after_research_review)
    builder.add_edge("writer" , "review_draft")
    builder.add_conditional_edges("review_draft", route_after_draft_review)
    builder.add_edge("editor",END)


    # compile
    GRAPH = builder.compile(checkpointer=InMemorySaver())
    return GRAPH


