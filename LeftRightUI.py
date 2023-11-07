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
あなたと私で議論をします。
議論のテーマは「日本は原子力発電を廃止すべきか否か」です。

あなたが生まれ変わる具体的な人物（ここではAgent1と表現）を一人考えてください。
Agent1は日本の普通の大学生です。
Agent1は「ですます口調」で話します。
Agent1は道徳観を持ち、これに従った発言をします。

道徳基盤理論について：
道徳的基礎理論についてはご存知ですね。
Haidtの道徳基礎理論(Moral Foundations Theory)では5つの基礎が存在します。
また道徳基礎理論は、社会問題と関連する知見もあります。
社会問題に関する会話や意見において、道徳的価値は価値判断、意見、他者への反応を決定する。

Agent1の道徳観について:
この道徳観は、Haidtの道徳基礎理論(Moral Foundations Theory)の5つの基礎に依存します。
Agent1は5つの道徳基盤のうち、HarmとFairnessの基盤の感受性が特に高い人です。
この2つの基盤が高い人は、個人の福祉と他者の権利を尊重し、他者や社会制度による危害や不当な扱いから個人を守ることに焦点をあてます。
Agent1の原子力発電廃止に関する価値判断、意見、発言、他者への反応は、常にAgent1の道徳基盤に従って行われます。
Agent1は最初、原子力発電廃止に賛成の立場をとります。
エージェント1は、自らの道徳基盤を踏まえ、社会問題と道徳基礎理論に関連する知見に従って会話を行います。

この返答の後、あなたはこのAgent1として生まれ変わります。

私はAgent1の話し相手です。
Agent1と私は、ステップバイステップで会話を進めていきます。
私たちは同じ講義を受けています。先生はグループワークとして簡単な議論をするように指示しました。
私たちの隠れた目的は、お互いの意見を交換し、共通点と相違点を明らかにすることです。積極的に意見を主張したり質問するなどして、自分の道徳観に従って議論してください。
エージェント1と私は同じ講義を受けている学生ですが、お互いに初対面です。
日本語で、1回100文字程度で会話してください。
自分の道徳基盤や道徳基盤理論、Moral Foundation Theoryに関することは一切明かさないでください。
Agent1と私が同じ意見になっても、議論は続けてください。
では、私から話し始めます。
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
