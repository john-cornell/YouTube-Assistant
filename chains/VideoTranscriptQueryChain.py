from typing import List
from dotenv import load_dotenv
from chains.AgentTypeChain import AgentTypeChain
from chains.RagPromptOptimizerChain import RagPromptOptimizerChain
from embeddings_store import Embeddings
from vectorstorage.vectorstore import get_vectorstore_for_db

from multiagent.json_extractor import extract_json, get_error_json
from typing import Any, Dict, List, Optional
import json

from langchain.chains import LLMChain
from langchain.schema import BasePromptTemplate
from langchain.schema.language_model import BaseLanguageModel
from langchain.chains.base import Chain
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun
)

from langchain.vectorstores.faiss import FAISS

load_dotenv()

class VideoTranscriptQueryChain(Chain):
    llm:BaseLanguageModel
    prompt:BasePromptTemplate
    url: str
    debug: bool
    k: int = 15
    embeddings: Embeddings = Embeddings.HUGGINGFACE

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"

    @property
    def input_keys(self) -> List[str]:
        return ["query"]

    @property
    def output_keys(self) -> List[str]:
        return ["output"]

    def _call(
            self,
            inputs: Dict[str, Any],
            run_manager: Optional[CallbackManagerForChainRun] = None
    ) -> Dict[str, str]:

        #Get query from input
        query = inputs["query"]

        if not query:
            raise ValueError("query not set")

        #Assertain prompt type - only RAG is supported for now
        process_chain = AgentTypeChain(llm=self.llm, debug=True)
        process_response = process_chain.run({"query": query})["process"]

        print(f"Process response: {process_response}")

        if process_response == "SUMMARY":
            print("SUMMARY not yet supported")
            return self.build_return("That question would require a summarisation of the whole video, which is not yet supported.", [], None)
        if process_response == "NONE":
            print("NONE not yet supported")
            return self.build_return("I don't know", [], None)

        #Optimize RAG search prompt
        optimizer_chain = RagPromptOptimizerChain(llm=self.llm, debug=True)
        optimizer_response_json = optimizer_chain.run({"query": query})

        optimizer_response = optimizer_response_json["searchprompt"]

        #Get docs from db
        db = get_vectorstore_for_db(self.url, Embeddings.HUGGINGFACE)

        docs = db.similarity_search(optimizer_response, k=self.k)
        docs_page_content = [doc.page_content for doc in docs]

        #Send prompt to LLM
        chain = LLMChain(llm=self.llm, prompt=self.prompt, output_key="answer")

        response = chain.run(query=query, docs=docs_page_content)
        response = response.replace("\r", "")

        return self.build_return(response, docs, self.prompt)

    def build_return(self, response, docs, prompt):
        return {
            "output":{
                "response": response,
                "metadata": {
                    "docs": docs,
                    "prompt": prompt
                }
            }
        }


