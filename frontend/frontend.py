import streamlit as st
import httpx
import asyncio

url = "http://127.0.0.1:8000"

client = httpx.AsyncClient()

async def login(email, pwd):
    try:
        response = await client.post(f"{url}/api/User/token" , data={"username": email, "password": pwd})
        if response.status_code == 200:
            st.session_state["token"] = response.json().get("access_token")
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")
    except Exception as e:
        st.error(f"error: {e}")


def set_signup():
    st.session_state.form = "signup"
def set_login():
    st.session_state.form = "login"



async def signup(name ,email, pwd):
    try:
        response = await client.post(f"{url}/register", json = {
            "account_name":name,
            "email": email,
            "password": pwd})
        if response.status_code == 200:
            st.success("Signup successful, Now login")
            await asyncio.sleep(2)
            st.rerun()
        elif response.status_code == 409:
            st.success("already Signup, Try login")
            await asyncio.sleep(2)
            st.rerun()
    except Exception as e:
        st.error(f"error: {e}")

if "form" not in st.session_state:
    set_login()

if "token" not in st.session_state:
    st.title("login form")
    if st.session_state.form == "login":
        with st.form("login_form"):
            user_email = st.text_input("Email Address")
            pwd = st.text_input("Password", type= "password")
            btn_login = st.form_submit_button("login")
            signup= st.form_submit_button("signup",  on_click= set_signup)
            if btn_login:
                asyncio.run(login(user_email, pwd))
    elif st.session_state.form == "signup":
        with st.form("signup_form"):
            account_name = st.text_input("Name")
            user_email = st.text_input("Email Address")
            pwd = st.text_input("Password", type= "password")
            btn_signup = st.form_submit_button("signup")
            login= st.form_submit_button("login",  on_click= set_login)
            if btn_signup:
                asyncio.run(signup(account_name ,user_email, pwd))

else:
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
    st.title("📝 Your Notes")
    st.write("You are logged in. Ready to build the notes list?")