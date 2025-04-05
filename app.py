import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_quill import st_quill
from intelligence import news_generator

import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate("fcode-newsgenerator-firebase-adminsdk-fbsvc-59634d891f.json")  # Replace with your service account file path
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Set page configuration (centered layout)
st.set_page_config(layout="centered", page_title="SwiftLens - Your News Generator")

with st.sidebar:
    #st.image("assets/logo.png", width=200)
    st.title("SwiftLens")
    st.markdown("### Your AI-Powered News Generator")
    st.markdown("Generate personalized news articles with ease.")
    st.markdown("---")
    selected_page = option_menu(
        menu_title=None,
        options=["Generator", "Editor", "My Posts", "Metrics"],
        icons=["newspaper", "pencil", "file-earmark-text", "bar-chart-line"],
        menu_icon="cast",
        default_index=0,
    )



def fetch_posts():
        try:
            posts_ref = db.collection("news_samples")  # Replace "posts" with your collection name
            docs = posts_ref.stream()
            posts_data = {doc.to_dict()["topic"]: doc.to_dict()["body"] for doc in docs}
            return posts_data # returns a dictionary of posts
        except Exception as e:
            st.error(f"Error fetching posts: {e}")
            return {}

def save_edited_text(topic, edited_body):
        try:
            db.collection("news_samples").document(topic).set({"topic": topic, "body": edited_body})
            st.success(f"Post with Topic of'{topic}' saved successfully!")
        except Exception as e:
            st.error(f"Error saving post: {e}")

if selected_page == "Generator":
    # Custom CSS for centering the main container and styling the Generate button
    st.markdown(
        """
        <style>
        .center {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        .generate-button {
            background-color: blue;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


    # Initialize session_state for each input if they don't exist already
    if "company_code" not in st.session_state:
        st.session_state.company_code = ""
    if "topic" not in st.session_state:
        st.session_state.topic = ""
    if "audience" not in st.session_state:
        st.session_state.audience = ""
    if "tone" not in st.session_state:
        st.session_state.tone = ""
    if "article_length" not in st.session_state:
        st.session_state.article_length = "short"
    if "language" not in st.session_state:
        st.session_state.language = "English"
    if "post" not in st.session_state:
        st.session_state.post = ""

    # printing the session state for debugging

    # Main container for the app content
    with st.container():
        st.markdown('<div class="center">', unsafe_allow_html=True)
        
        # Topic input
        #st.markdown("Topic")
        st.session_state.company_code = st.text_input(
            label="Company Code",
            placeholder="Enter your company code (e.g., ABC123)",
            value=st.session_state.company_code
        )
        st.session_state.topic = st.text_area(
            label="Topic",
            placeholder="Enter your topic idea (e.g., AI in healthcare)",
            height=100
        )
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Audience input
        st.session_state.audience = st.text_input(
            label="Audience",
            placeholder="Enter your target audience: Local Residents, International"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tone input
        
        st.session_state.tone = st.text_input(
            label="Tone",
            placeholder="Enter desired tone (e.g., informative, casual)"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Two columns for Article Length and Language drop-downs
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.article_length = st.selectbox(
                "Article Length",
                options=["short", "medium", "long"],
                index=["short", "medium", "long"].index(st.session_state["article_length"])
            )
        with col2:
            st.session_state.language = st.selectbox(
                "Language",
                options=["English", "Dutch", "French"],
                key="language_"
            )
        
        # Some space before the Generate button
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # # Generate button (styled)
        # generate_html = """
        # <div style="text-align: center;">
        #     <button class="generate-button" onclick="window.location.reload()">Generate</button>
        # </div>
        # """
        # st.markdown(generate_html, unsafe_allow_html=True)
        
        # st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Generate", key="generate", type="secondary"):
            st.session_state["post"] = ""  # Reset post before generating a new one
            with st.spinner("Generating post..."):
                if not (st.session_state.topic == "" or st.session_state.audience == "" or st.session_state.tone == "") :
                    response = news_generator(topic=st.session_state["topic"], audience=st.session_state["audience"],
                                            tone=st.session_state["tone"], article_length=st.session_state["article_length"],
                                            language=st.session_state["language"])
                    if response:
                        # Assuming the API returns a text string as JSON
                        st.session_state["post"] = response
                    else:
                        st.error("Failed to generate post")
                else:
                    st.error("I'm sorry, it looks like there's a missing element in your request. Could you please provide more details or clarify the topic you'd like the news article to cover?")
        
        st.markdown("</div>", unsafe_allow_html=True)
    # If a post has been generated, display it in an expander with markdown styling
    if st.session_state["post"]:
        with st.expander("View News Article", expanded=True):
            st.markdown(
                f"""
                <div style='background-color:#f0f2f6; padding: 1rem 1.5rem; border-left: 4px solid #0073b1; border-radius: 8px; color: #222; font-size: 1rem; line-height: 1.6;'>
                    {st.session_state["post"]}
                </div>
                """,
                unsafe_allow_html=True
            )
elif selected_page == "Editor":
    
    
    st.write("# Editor")
    # Button to fetch posts
    if "posts" not in st.session_state:
        st.session_state["posts"] = {}
    if "topics" not in st.session_state:
        st.session_state["topics"] = []
    if True:#st.button("Fetch Posts"):
        posts_data = fetch_posts()
        if posts_data:
            st.session_state["posts"] = posts_data
            st.session_state["topics"] = list(posts_data.keys())
    if "topics" in st.session_state and st.session_state["topics"]:
        selected_topic = st.selectbox("Select a Topic:", st.session_state["topics"])
        if selected_topic:
            initial_body = st.session_state["posts"][selected_topic]
            edited_topic = st.text_area("Edit News Article Topic:", value=selected_topic, height=70)
            edited_body = st_quill(placeholder="Edit News Article Body:",value=initial_body)
            #edited_body = st.text_area("Edit News Article Body:", value=initial_body, height=300)

            # Center the Save button using columns
            col1, col2, col3 = st.columns([0.8, 0.8, 0.5])  # Adjusted column widths to bring columns 2 and 3 closer
            with col1:
                if st.button("Save Edited Post"):
                    save_edited_text(edited_topic, edited_body)
            with col2:  # Place the button in the middle column
                # Download button for the edited post
                st.download_button(label="Download Data", data=edited_body, file_name=f'{edited_topic}.txt', mime='text/plain')
            with col3:
                #delete button for the edited post
                if st.button("Delete Post"):
                    try:
                        db.collection("news_samples").document(selected_topic).delete()
                        st.success(f"Post with Topic of'{selected_topic}' deleted successfully!")
                        # Remove the deleted topic from the session state
                        st.session_state["topics"].remove(selected_topic)
                        st.session_state["posts"].pop(selected_topic, None)  # Remove from posts as well
                    except Exception as e:
                        st.error(f"Error deleting post: {e}")
                
elif selected_page == "My Posts":
    def clean_html(text):
        import re
    # Remove HTML tags using regex
        clean_text = re.sub(r"<[^>]+>", "", text)
        return clean_text.strip()
    st.markdown("# Your Posts")
    try:
        posts_data = fetch_posts()
    except:
        st.error("Error fetching posts from the database.")
        posts_data = {}
    if 'topic_post_mapping' not in st.session_state:
        st.session_state["topic_post_mapping"] = {}
    st.session_state["topic_post_mapping"] = {topic: clean_html(body) for topic, body in posts_data.items()}
    # Display each post in an expander
    for topic in st.session_state["topic_post_mapping"].keys():
        with st.expander(f"**{topic}**", expanded=True):  # Make the topic bold
            st.markdown(
                f"""
                <div style='background-color:#f0f2f6; padding: 1rem 1.5rem; border-left: 4px solid #0073b1; border-radius: 8px; color: #222; font-size: 1rem; line-height: 1.6;'>
                    {st.session_state.topic_post_mapping[topic]}
                </div>
                """,
                unsafe_allow_html=True
            )
    if not st.session_state["topic_post_mapping"]:
        st.warning("No posts found in the database.")
elif selected_page == "Metrics":
    st.write("# Metrics")
    st.write("Please subscribe to the premium plan to access this feature.")
