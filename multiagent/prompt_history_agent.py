from .agents import defined_agent, agent_type
from .agent_input import Agent_Input
from .multi_agent_prompts import prompt_history_agent_prompt

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from enum import Enum

from dotenv import load_dotenv
load_dotenv()

#Helper classes

class prompt_input_type(Enum):
    User = "User",
    AI = "AI",
    SUMMARY = "Summary"

class prompt_history_agent_types(agent_type):
    PROMPT_HISTORY_TYPE = "PROMPT_HISTORY_TYPE"

#Main class
class prompt_history_agent(defined_agent):
    #token limit assumes Claude level window, but very conservative, could probably make way higher - this is for docs and query separately, 60000 on Claude 100 000 
    #until 2.1 is rolled out
    def __init__(self, llm, template_prompt = None, token_limit=30000):
        self.type = type
        self.history = []
        self.docs = set() #hashset to avoid dups
        self.token_limit = token_limit

        if template_prompt==None:
            template_prompt = prompt_history_agent_prompt
        super().__init__(prompt_history_agent_types.PROMPT_HISTORY_TYPE, llm, template_prompt)           

    def format(self):
        lines = []
        for context, text in self.history:
            lines.append(f"{context}: \"{text}\"")
        
        return "\n".join(lines)

    def format_docs(self):
        lines = []
        for doc in self.docs:
            lines.append(doc)
        
        return "\n".join(lines)

    def append_docs(self, docs):
        for d in docs:
            self.docs.add(d)
        return self.summarise_docs_if_required()

    def append(self, type: prompt_input_type, item : str):
        self.history.append((type.name, item))

    def add_summary(self, summary):
        self.history = []        
        self.append(prompt_input_type.SUMMARY, summary)

    def append_query(self, query):
        self.append(prompt_input_type.User, query)
        return self.summarise_if_required()

    def append_response(self, response):
        self.append(prompt_input_type.AI, response)
        return self.summarise_if_required()

    def summarise_if_required(self):

        history=self.format()
        
        if (self.too_many_tokens(history)):            
            template = PromptTemplate(input_variables=["history"], template=self.prompt)
            chain = LLMChain(llm=self.llm, prompt=template, output_key="answer")
            self.history = []
            self.add_summary(chain.run(history=history))
            #if just summarised, this will just be a single item, so not a performance issue to call again
            self.history=self.format()

        return history
    
    def summarise_docs_if_required(self):

        history=self.format_docs()
        
        if (self.too_many_tokens(history)):            
            template = PromptTemplate(input_variables=["history"], template=self.prompt)
            chain = LLMChain(llm=self.llm, prompt=template, output_key="answer")
            self.docs = set()
            self.append_docs([chain.run(history=history)])
            #if just summarised, this will just be a single item, so not a performance issue to call again
            history=self.format_docs()

        return history
    
    def too_many_tokens(self, text : str):
        #In the ghetto 🎵
        return len(text) / 4 > self.token_limit
