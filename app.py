
import streamlit as st
import random

st.set_page_config(page_title="Early Learning Interview Prep", page_icon="🎓", layout="wide")

st.title("🎓 Early Learning Interview Prep")
st.caption("A fast, practical interview-prep app for preschool / early-learning positions.")

QUESTIONS = [
    {
        "question":"Tell me about yourself.",
        "key_points":[
            "Years of hands-on experience caring for children of different ages",
            "Patience, organization, safety, routines, behavior support",
            "Volunteer tutoring / community experience",
            "Beginning or continuing formal ECE education",
            "Interest in building a long-term early-childhood career"
        ],
        "sample":"""I have many years of hands-on experience caring for and supporting children from toddler through elementary ages. As a mother of five, I have developed strong patience, organization, responsibility, and experience supporting children's routines, learning, behavior, and emotional needs.

I also have volunteer tutoring experience working with children in a community setting. I enjoy helping children learn, become more independent, and feel safe and supported.

I am now continuing my Early Childhood Education training because I want to connect my practical experience with current early-learning practices and build a long-term career in early childhood education."""
    },
    {
        "question":"Why do you want to work in early childhood education?",
        "key_points":[
            "Early years are important for development",
            "Enjoy helping children learn through play and daily routines",
            "Like helping children build confidence and independence",
            "Want to grow professionally in ECE"
        ],
        "sample":"""I enjoy working with young children because the early years are such an important time for development. I like helping children learn through play, reading, conversation, routines, and positive encouragement.

I especially enjoy seeing a child become more confident or independent after struggling with something. I also want to continue growing professionally in early childhood education and contribute to a classroom where children feel safe, respected, and excited to learn."""
    },
    {
        "question":"What are your strengths?",
        "key_points":["Patience","Reliability","Organization","Calm under pressure","Managing children with different needs","Positive communication"],
        "sample":"""My biggest strengths are patience, reliability, organization, and staying calm when children are upset. I am comfortable managing several children's needs at the same time, and I try to understand what a child needs before reacting. I also value clear routines, preparation, and respectful communication."""
    },
    {
        "question":"What is one weakness or area you are developing?",
        "key_points":["Do not say you have no weaknesses","Avoid making the weakness sound unsafe","Connect it to professional growth","Mention formal ECE training if appropriate"],
        "sample":"""One area I am continuing to develop is my formal Early Childhood Education training. I have extensive hands-on experience with children, and I am continuing ECE coursework so I can connect that practical experience with current early-childhood education practices."""
    },
    {
        "question":"Why should we hire you?",
        "key_points":["Patience and reliability","Hands-on childcare experience","Safety and positive guidance","Willingness to support the lead teacher","Eagerness to learn"],
        "sample":"""I believe I would bring patience, reliability, maturity, and a genuine commitment to children. I have years of hands-on experience managing children of different ages and understand how important safety, consistency, positive guidance, and communication are.

I am also eager to learn from experienced teachers and continue growing in early childhood education. I would come to work ready to support the teacher and help create a safe, positive environment for the children."""
    },
]

SCENARIOS = [
    ("A child is having a tantrum.",
     "Ensure safety, stay calm, acknowledge feelings, help the child regulate, redirect or teach an appropriate response, and follow classroom procedures.",
     "Yelling, shaming, threatening, or giving the child whatever they want just to stop the behavior."),
    ("Two children are fighting over the same toy.",
     "Make sure both are safe, acknowledge both children's needs, coach them to use words, and help them take turns or find another solution.",
     "Immediately blaming one child or punishing without teaching a replacement skill."),
    ("A child refuses to participate.",
     "Try to understand why, encourage without forcing or embarrassing, offer a choice, model the activity, or allow brief observation before joining.",
     "Forcing participation, public criticism, or labeling the child."),
    ("A child falls and is bleeding.",
     "Safety and appropriate first aid come first. Follow center procedures and notify the appropriate staff.",
     "Finishing another task before addressing the injury."),
    ("A parent asks you about another child's behavior.",
     "Protect confidentiality and discuss only information you are authorized to share.",
     "Sharing private details about another child."),
    ("You suspect a developmental delay.",
     "Observe objectively, document appropriately, and communicate through the teacher/director or approved process.",
     "Diagnosing the child yourself."),
    ("A child cannot put on a jacket.",
     "Encourage the child to try, offer just enough help to get started, then let the child complete what they can.",
     "Automatically doing the entire task for the child."),
    ("The lead teacher gives you an instruction you do not understand.",
     "Ask for clarification rather than guessing.",
     "Pretending you understand and doing something incorrectly."),
    ("A child is alone near an exit.",
     "Act immediately to ensure safety, then follow classroom or center procedures.",
     "Waiting to see what happens."),
    ("A parent becomes angry with you.",
     "Stay calm, listen respectfully, avoid arguing, respond within your role, and involve the teacher/director when appropriate.",
     "Becoming defensive or sharing information you are not authorized to provide.")
]

CORE_WORDS = [
    "Safety first","Active supervision","Positive guidance","Developmentally appropriate",
    "Learning through play","Scaffolding","Teach replacement behavior","Encourage independence",
    "Protect confidentiality","Objective observation","Follow teacher/center procedures",
    "Communicate respectfully with families"
]

ASK_EMPLOYER = [
    "What would a typical day look like for someone in this position?",
    "What age group would I primarily be working with?",
    "What qualities are most important to you in someone joining your classroom team?",
    "What training or support do you provide to new staff?"
]

if "rapid_q" not in st.session_state:
    st.session_state.rapid_q = 0

tabs = st.tabs([
    "⏱️ 30-Min Plan","🙋 Interview Questions","🎯 Scenario Practice",
    "🧠 Rapid-Fire","⭐ Strengths & Weakness","❓ Questions to Ask","✅ Final 5-Min Review"
])

with tabs[0]:
    st.header("⏱️ 30-Minute Interview Plan")
    st.table({
        "Time":["0–10 min","10–20 min","20–25 min","25–30 min"],
        "What to do":[
            "Read your 5 core interview answers out loud",
            "Practice scenario questions",
            "Review strengths, weakness, and why they should hire you",
            "Review key words + questions to ask + slow your breathing"
        ],
        "Goal":[
            "Sound natural, not memorized",
            "Practice judgment and calm responses",
            "Be ready for common hiring questions",
            "Walk in focused and confident"
        ]
    })
    st.success("**Safety → Calm → Dignity → Support/Teach → Procedure → Objective Documentation**")

with tabs[1]:
    st.header("🙋 Common Interview Questions")
    for item in QUESTIONS:
        with st.expander(item["question"]):
            st.markdown("**Key points to include:**")
            for p in item["key_points"]:
                st.write("• " + p)
            st.markdown("**Sample answer:**")
            st.write(item["sample"])
    st.info("Do not memorize every word. Learn the structure, then answer naturally.")

with tabs[2]:
    st.header("🎯 Scenario Practice")
    st.write("Answer out loud before opening the suggested response.")
    for scenario, best, avoid in SCENARIOS:
        with st.expander(scenario):
            st.markdown("**Strong response:**")
            st.write(best)
            st.markdown("**Avoid:**")
            st.write(avoid)

with tabs[3]:
    st.header("🧠 Rapid-Fire Practice")
    all_prompts = [q["question"] for q in QUESTIONS] + [s[0] for s in SCENARIOS]
    if st.button("Give Me a Random Question", type="primary"):
        st.session_state.rapid_q = random.randrange(len(all_prompts))
    prompt = all_prompts[st.session_state.rapid_q % len(all_prompts)]
    st.subheader(prompt)
    st.text_area("Practice your answer here (or answer out loud)", key="rapid_answer", height=160)
    st.caption("Aim for a clear answer in about 30–90 seconds.")

with tabs[4]:
    st.header("⭐ Strengths & Weakness")
    strengths = [
        "Patience","Reliability","Organization","Calm under pressure",
        "Experience managing multiple children","Safety awareness",
        "Positive communication","Willingness to learn",
        "Consistency with routines","Supporting children's independence"
    ]
    chosen = st.multiselect("Choose 3–4 strengths you want to remember", strengths)
    if chosen:
        st.success("Your strengths: " + " • ".join(chosen))
    st.subheader("Safe weakness answer")
    st.info("Use a growth area, not something that makes you sound unsafe or unreliable.")
    st.write("""Example:  
**“One area I am continuing to develop is my formal Early Childhood Education training. I have extensive hands-on experience with children, and I am continuing ECE coursework so I can connect that practical experience with current early-childhood education practices.”**""")

with tabs[5]:
    st.header("❓ Questions to Ask the Employer")
    st.write("When they ask, **“Do you have any questions for us?”**, say yes.")
    for i, q in enumerate(ASK_EMPLOYER):
        st.checkbox(q, key=f"ask_{i}")
    st.success("Pick 2 questions. Asking thoughtful questions shows interest and professionalism.")

with tabs[6]:
    st.header("✅ Final 5-Minute Review")
    for item in CORE_WORDS:
        st.write("• **" + item + "**")
    st.warning("If you get stuck, ask: **What answer is safest, most respectful, most developmentally appropriate, and most supportive of the child?**")
    reminders = [
        "Slow down when you speak.",
        "Take 2–3 seconds to think before answering.",
        "Use real examples from caring for children whenever possible.",
        "Do not apologize for family childcare experience.",
        "Connect your hands-on experience to safety, routines, behavior guidance, learning, and independence.",
        "Smile and show warmth, but stay professional.",
        "If you do not know something, say you would ask the lead teacher or follow center procedure rather than guessing."
    ]
    for i, r in enumerate(reminders):
        st.checkbox(r, key=f"rem_{i}")
    st.success("You do not need perfect answers. You need to sound calm, safe, caring, reliable, and teachable.")

st.divider()
st.caption("Independent interview-prep tool. Customize your answers so they stay truthful to your own experience.")
