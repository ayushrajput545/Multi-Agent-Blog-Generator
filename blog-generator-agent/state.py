from pydantic import BaseModel, Field

class BlogState:
    # User Input
    topic:str=""
    audience:str=""

    # Researcher Output
    research:str=""
    researcher_feedback:str=""

    #Writer Output
    draft:str=""
    draft_feedback:str=""

    # Editor Output
    final_blog:str=""

    # Metadata
    revision_count:int=0 #how many attempt user takes to generate blog(Threshold)