# Harm
# ライブラリをインポート
# key=str(i) を各botへ忘れずに!
import streamlit as st
from streamlit_chat import message

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import pytz
import time

#現在時刻
global now
now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

# 環境変数の読み込み
#from dotenv import load_dotenv
#load_dotenv()

#プロンプトテンプレートを作成
with open('Prompt_neg_ind_euthanasia.txt', encoding = 'UTF-8', mode = 'r') as f:
    s = f.read()
    template = s

# 会話のテンプレートを作成
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(template),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}"),
])

#会話の読み込みを行う関数を定義
#@st.cache_resource
#def load_conversation():
    #llm = ChatOpenAI(
        #model_name="gpt-4",
        #temperature=0
    #)
    #memory = ConversationBufferMemory(return_messages=True)
    #conversation = ConversationChain(
        #memory=memory,
        #prompt=prompt,
        #llm=llm)
    #return conversation

# デコレータを使わない会話履歴読み込み for セッション管理
def load_conversation():
    if not hasattr(st.session_state, "conversation"):
        llm = ChatOpenAI(
            model_name="gpt-4-1106-preview",
            temperature=0)
        memory = ConversationBufferMemory(return_messages=True)
        st.session_state.conversation = ConversationChain(
            memory=memory,
            prompt=prompt,
            llm=llm)
    return st.session_state.conversation

# 質問と回答を保存するための空のリストを作成
if "generated" not in st.session_state:
    st.session_state.generated = []
if "past" not in st.session_state:
    st.session_state.past = []
    
# 会話のターン数をカウント
if 'count' not in st.session_state:
    st.session_state.count = 0
#st.write(st.session_state.count) # デバッグ用

# 送信ボタンがクリックされた後の処理を行う関数を定義
def on_input_change():
    st.session_state.count += 1
    # n往復目にプロンプトテンプレートの一部を改めて入力
    #if  st.session_state.count == 3:
    #    api_user_message = st.session_state.user_message + remind
    #elif st.session_state.count == 6:
    #    api_user_message = st.session_state.user_message + remind
    #elif st.session_state.count == 9:
    #    api_user_message = st.session_state.user_message + remind
    #else:
    #    api_user_message = st.session_state.user_message

    user_message = st.session_state.user_message
    conversation = load_conversation()
    with st.spinner("相手からの返信を待っています。。。"):
        time.sleep(1)
        answer = conversation.predict(input=user_message)
    st.session_state.generated.append(answer)
    st.session_state.past.append(user_message)
    #with st.spinner("入力中。。。"):
            # 任意時間入力中のスピナーを長引かせたい場合はこちら！
    #st.session_state.past.append(user_message)

    st.session_state.user_message = ""
    Human_Agent = "Human" 
    AI_Agent = "AI" 
    doc_ref = db.collection(user_number).document(str(now))
    doc_ref.set({
        Human_Agent: user_message,
        AI_Agent: answer
    })

# qualtricdへURL遷移
def redirect_to_url(url):
    new_tab_js = f"""<script>window.open("{url}", "_blank");</script>"""
    st.markdown(new_tab_js, unsafe_allow_html=True)

# タイトルやキャプション部分のUI
# st.title("ChatApp")
# st.caption("Q&A")
# st.write("議論を行いましょう！")
user_number = st.text_input("学籍番号を半角で入力してエンターを押してください")
if user_number:
    #st.write(f"こんにちは、{user_number}さん！")
    # 初期済みでない場合は初期化処理を行う
    if not firebase_admin._apps:
            cred = credentials.Certificate('chat3-109ec-firebase-adminsdk-2zc5h-08e4bf5e34.json') 
            default_app = firebase_admin.initialize_app(cred)
    db = firestore.client()
    #doc_ref = db.collection(user_number)
    #doc_ref = db.collection(u'tour').document(str(now))

# 会話履歴を表示するためのスペースを確保
chat_placeholder = st.empty()

# 会話履歴を表示
with chat_placeholder.container():
    for i in range(len(st.session_state.generated)):
        message(st.session_state.past[i],is_user=True, key=str(i))
        key_generated = str(i) + "keyg"
        message(st.session_state.generated[i], key=str(key_generated))

# 質問入力欄と送信ボタンを設置
with st.container():
    if  st.session_state.count == 0:
        user_message = st.text_input("「原子力発電は廃止すべき」という意見に対して、あなたの意見を入力して送信ボタンを押してください", key="user_message")
    else:
        user_message = st.text_input("あなたの意見を入力して送信ボタンを押してください", key="user_message")
    st.button("送信", on_click=on_input_change)
# 質問入力欄 上とどっちが良いか    
#if user_message := st.chat_input("聞きたいことを入力してね！", key="user_message"):
#    on_input_change()


redirect_link = "https://nagoyapsychology.qualtrics.com/jfe/form/SV_cw48jqskbAosSLY"

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown(f'<a href="{redirect_link}" target="_blank">5往復のチャットが終了したらこちらを押してください。</a>', unsafe_allow_html=True)
#if st.button("終了したらこちらを押してください。画面が遷移します。"):
    #redirect_to_url("https://www.google.com")
