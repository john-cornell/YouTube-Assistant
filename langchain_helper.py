from dotenv import load_dotenv
from embeddings_store import get_embeddings, Embeddings

from langchain.chat_models.anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from chains.VideoTranscriptQueryChain import VideoTranscriptQueryChain

load_dotenv()

embeddings = get_embeddings(Embeddings.HUGGINGFACE)

def get_response_from_query(url : str, query : str, k=20):
    chat = ChatAnthropic(temperature=0.4)
    prompt = PromptTemplate(
        input_variables=["query", "docs"],
        template="""
        You are a helpful assistant that that can answer questions about youtube videos
        based on the video's transcript.

        Answer the following user's question:
        "{query}"

        Answer by searching the following video transcript very carefully, ensuring to be as helpful and comprehensive as possible :
        Transcript: {docs}

        Only use the factual information from the transcript to answer the question.

        If you feel like you don't have enough information to answer the question, only answer "I don't know", and don't rabbit on about it.

        Your answers should be verbose and detailed, unless you are answering "I don't know", in which case you should be brief.

        Complete your sentence, don't leave it hanging.

        Answer in a friendly manner, that is easy to understand.
        """
    )

    chain = VideoTranscriptQueryChain(llm=chat, prompt=prompt, url=url, k=k, embeddings=Embeddings.HUGGINGFACE, debug=True)

    response = chain.run({"query": query})

    output = response["response"]
    metadata = response["metadata"]

    return output, metadata["docs"], metadata["prompt"]




#create_vector_db_from_youtube_url("SUpBR06sJLs")
#https://www.youtube.com/watch?v=z6bGOBKlhOs (TDIAI)
#https://www.youtube.com/watch?v=2PClFGlyEgM (1LC)