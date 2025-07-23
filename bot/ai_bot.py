#...

import os

from decouple import config

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

os.environ['GROQ_API_KEY'] = config('GROQ_API_KEY')

#...llama-3.3-70b-versatile

class AIBot:

    def __init__(self):
        self.__chat = ChatGroq(model='llama-3.3-70b-versatile')
        self.__retriever = self.__build_retriever()

    def __build_retriever(self):
        persist_directory = '/app/chroma_data'
        embedding = HuggingFaceEmbeddings()

        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding,
        )
        return vector_store.as_retriever(
            search_kwargs={'k': 30},
        )

    def __build_messages(self, history_messages, question):
        messages = []
        for message in history_messages:
            message_class = HumanMessage if message.get('fromMe') else AIMessage
            messages.append(message_class(content=message.get('body')))
        messages.append(HumanMessage(content=question))
        return messages

    def invoke(self, history_messages, question):
        SYSTEM_TEMPLATE = '''
        Responda às perguntas dos responsáveis sobre a Clínica Sapere de maneira espontânea e acolhedora.
    Você é o assistente virtual oficial da Sapere, um centro transdisciplinar de atendimento infantil em Manaus.
    Explique sobre nossas terapias para crianças e adolescentes: fisioterapia, psicomotricidade, neuropsicologia,
    psicologia, psicopedagogia, terapia ocupacional, fonoaudiologia, nutrição, musicoterapia e pediatria.
    Forneça informações claras sobre horários de atendimento e endereço (Rua Cometa Halley, 08 – Morada do Sol, Manaus‑AM).
    Explique que não atendemos convênios diretamente; o atendimento só pode ocorrer via reembolso por liminar judicial.
    Use sempre português brasileiro e inclua emojis adequados para transmitir carinho e simpatia 😊.
    Seja objetivo, mas humano e acolhedor; nunca forneça diagnósticos médicos ou informações confidenciais.
    Quando a pergunta não estiver relacionada às nossas especialidades, sugira encaminhar para um atendente humano.
      

        <context>
        {context}
        </context>
        '''

        docs = self.__retriever.invoke(question)
        question_answering_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    SYSTEM_TEMPLATE,
                ),
                MessagesPlaceholder(variable_name='messages'),
            ]
        )
        document_chain = create_stuff_documents_chain(self.__chat, question_answering_prompt)
        response = document_chain.invoke(
            {
                'context': docs,
                'messages': self.__build_messages(history_messages, question),
            }
        )
        return response
