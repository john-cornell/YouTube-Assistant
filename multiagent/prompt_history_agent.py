import asyncio

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
    def __init__(self, llm, template_prompt = None, token_limit=1000):
        self.type = type
        self.history = []
        self.docs = set() #hashset to avoid dups
        self.token_limit = token_limit

        self.history_lock = asyncio.Lock()
        self.docs_lock = asyncio.Lock()

        if template_prompt==None:
            template_prompt = prompt_history_agent_prompt
        super().__init__(prompt_history_agent_types.PROMPT_HISTORY_TYPE, llm, template_prompt)           


    #format
    async def format(self):
        lines = []
        #READ LOCK, not calling self.append or self.add_summary where other instances of lock are
        async with self.history_lock:
            for context, text in self.history:
                lines.append(f"{context}: \"{text}\"")
        
        return "\n".join(lines)

    async def format_docs(self):
        lines = []
        
        async with self.docs_lock:
            for doc in self.docs:
                lines.append(doc)
        
        return "\n".join(lines)

    #update
    async def append_docs(self, docs):   
        async with self.docs_lock:     
            for d in docs:
                self.docs.add(d)
        
        return await self.schedule_summarise_docs_if_required()

    async def append(self, type: prompt_input_type, item : str):
        #Write lock, not calling format or self.add_summary where other instances of lock are
        async with self.history_lock:
            self.history.append((type.name, item))

    async def add_summary(self, summary):
        
        #NO DEADLOCK, just resetting
        async with self.history_lock:
            self.history = []    

        #locks internally
        await self.append(prompt_input_type.SUMMARY, summary)

    async def append_query(self, query):
        #locks internally
        await self.append(prompt_input_type.User, query)
        #locks internally
        await self.schedule_summarise_if_required()

    async def append_response(self, response):
        #locks internally
        await self.append(prompt_input_type.AI, response) 
        #locks internally
        await self.schedule_summarise_if_required()

    #summarise
    async def schedule_summarise_docs_if_required(self):
        asyncio.create_task(self._summarise_docs())

    async def schedule_summarise_if_required(self):
        asyncio.create_task(self._summarise())

    async def _summarise(self):

        history = await self.format()
        
        if (self.too_many_tokens(history)):    
            print("summarise chats")        
            template = PromptTemplate(input_variables=["history"], template=self.prompt)
            chain = LLMChain(llm=self.llm, prompt=template, output_key="answer")            
            self.add_summary(chain.run(history=history))
            #if just summarised, this will just be a single item, so not a performance issue to call again

            #not locking here as self.format has lock
            self.history=[await self.format()]

            print("complete")

        return history
    
    async def _summarise_docs(self):

        history = await self.format_docs()
        
        if (self.too_many_tokens(history)): 
            print("summarise docs")           
            template = PromptTemplate(input_variables=["history"], template=self.prompt)
            chain = LLMChain(llm=self.llm, prompt=template, output_key="answer")
            
            self.append_docs([chain.run(history=history)])
            #if just summarised, this will just be a single item, so not a performance issue to call again
        
            self.docs = set()
            self.docs = await self.format_docs()

            print("complete docs")
        return history
    
    def too_many_tokens(self, text : str):
        #In the ghetto 🎵
        return len(text) / 4 > self.token_limit
