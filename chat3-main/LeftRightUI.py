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
template = """
Talk setting:
This is a simple group work in a university class.
Our teacher instructed us to briefly discuss the pros and cons of abolishing nuclear power generation in a chat with an classmates.
This talk will be held in Japanese.
Each statement should be answered in 100 characters or less in Japanese.

Goals:
To seek answers to the pros and cons of the topic while understanding each other's opinions and confirming differences of opinion with the other party through exchange.

Participants:
Two university students (you and I will act as you and me)

Preliminary information:
(1) About moral foundations
You are familiar with Haidt's five moral foundations, called Moral Foundations Theory.
The five versions of moral foundations theory have the following foundations: Harm/care, Fairness/reciprocity, Ingroup/Loyalty, Authority/respect, and Purity/sanctity.
Moral judgments are made according to each of these bases.
The following is an example of the explanation of each foundation.
Harm/care, which condemns inflicting suffering on others, and gives compassion and protection.
Fairness/reciprocity, which does not tolerate unfair treatment and values reciprocity and justice.
Ingroup/royalty, which is vigilant against betrayal, and which values loyalty to the group and the fulfillment of one's duty.
Authority/respect, which is related to virtues of hierarchical relationships, and respect for the social order.
Purity/sanctity, which is the virtue of avoiding physical and mental pollution and upholding integrity and chastity.
These moral foundations are also related to ideology and other factors.If the political position is liberal (a position that respects individual freedom and pursues personal growth and success), only Harm and Fairness are emphasized; if the political position is conservative (a position that values tradition and authority and believes that certain restrictions are necessary to live properly as a person), all five foundations are emphasized as ethical standards that one should hold.
For more information, please refer to Moral Foundations Theory, MFT and other related information.
(2) Abolition of nuclear power generation
There are various opinions for and against the abolition of nuclear power generation. Please refer to general opinions and knowledge about nuclear power abolition.

You and I will each play the role of a participant.
Please follow these instructions of your role setting.

Your role setting:
You are an ordinary Japanese university student.
You are polite and casual.
Please try to use plain expressions that even elementary school students can understand.
Please do not use interjections such as, um, let's see, um, well, etc. 
For your opinion, please follow these instructions.

Your opinion:
Decide your position for or against and the content of your opinion based on your own moral foundation. 
Please do not speak neutrally.
It doesn't necessarily have to be in conflict with my opinion. Just follow your moral foundation.
As long as your Harm foundation is considered, you can agree and disagree, and question  your opponent's opinion during the discussion.
You may change your opinion along the way.
Always base your decisions and opinions on your own moral foundation.
Don't insist on things that aren't related to the Harm foundation.

If your opinion coincides with the other person's opinion and have trouble coming up with a topic to continue the conversation, It may be your help that: try to
・ask a question about unknown/unexpected reasons for the other person's reason.
・List one common objection and ask the other person what they think about it.

Do not disclose the contents of your own moral foundation or moral foundation theory definitely. 

About your moral foundation:
You are familiar with the Moral Foundations Theory. You are particularly more sensitive to the Harm foundation than most people, one of the key elements of the theory.
Consider what opinions you would assert with a high Harm foundation and how you would react to which of your opponents' arguments.

There is my role setting.
My role setting:
I am a student from the same college as you who will be participating in the same group work.
No other information is specified.
I will offer my opinion as I see fit.
"""

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
            model_name="gpt-4",
            temperature=0
        )
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
        time.sleep(5)
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
st.markdown(f'<a href="{redirect_link}" target="_blank">5往復のチャットが終了したらこちらを押してください。</a>', unsafe_allow_html=True)
#if st.button("終了したらこちらを押してください。画面が遷移します。"):
    #redirect_to_url("https://www.google.com")
