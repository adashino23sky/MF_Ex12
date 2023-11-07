from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.base import BaseCallbackHandler
import streamlit as st

model_name = 'gpt-4'


class StreamHandler(BaseCallbackHandler):
    """
    新しいトークンをテキストに追加し、コンテナ内に更新されたテキストを表示するためのコールバックハンドラ。
    """

    def __init__(self, container, init_text=""):
        self.container = container
        self.text = init_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)


def main():

    query = st.text_input("メッセージを入力してください。")
    send_button = st.button("送信")

    if send_button and query:
        send_button = False

        container = st.empty()
        stream_handler = StreamHandler(container)
        llm = ChatOpenAI(model_name=model_name, streaming=True, callbacks=[stream_handler], temperature=0)

        prompt = PromptTemplate(
            input_variables=["query"],
            template="""
                     以下の質問に答えてください。

                     質問:
                     {query}
                     """,
        )

        chain = LLMChain(llm=llm, prompt=prompt)
        chain.run(query)


if __name__ == '__main__':
    main()