from src.aws_bedrock import get_llm_model
from langchain_core.runnables import RunnableSequence
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
from langchain.output_parsers.openai_tools import PydanticToolsParser

class SkillRecommenderModel(BaseModel):
    skills:list[str] =  Field(default=[],description="The list of skills with skill levels attached")

class SkillorMeterPromptTemplate():

    def __init__(self,system_msg_str):
        self.system_msg_str = system_msg_str
 
    def generate(self) -> ChatPromptTemplate:
        """Get the final prompt."""
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(content = self.system_msg_str),
                HumanMessagePromptTemplate.from_template("{input_params}")
            ]
        )

def create_agent(system_prompt:str):
    llm = get_llm_model()
    prompt = SkillorMeterPromptTemplate(system_prompt).generate()
    llm = llm.bind_tools([SkillRecommenderModel])
    parser = PydanticToolsParser(tools=[SkillRecommenderModel])
    agent = RunnableSequence(prompt |  llm | parser)
    return agent