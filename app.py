
import streamlit as st
from datetime import datetime, date, time, timedelta
import json, io

st.set_page_config(page_title="Mom of 5 Family Command Center", page_icon="💛", layout="wide")

# -------------------- STATE --------------------
def init():
    defaults = {
        "children": [
            {"name":"Child 1","age":11,"school_start":"08:00","school_end":"15:00"},
            {"name":"Child 2","age":9,"school_start":"08:00","school_end":"15:00"},
            {"name":"Child 3","age":7,"school_start":"08:00","school_end":"15:00"},
            {"name":"Child 4","age":4,"school_start":"08:30","school_end":"14:30"},
            {"name":"Child 5","age":2,"school_start":"","school_end":""},
        ],
        "tasks": [
            {"task":"Wake kids / uniforms / breakfast","category":"Morning","minutes":75,"required":True},
            {"task":"School drop-off","category":"School","minutes":45,"required":True},
            {"task":"Home reset / dishes","category":"Home","minutes":30,"required":False},
            {"task":"Cooking / dinner prep","category":"Meals","minutes":60,"required":True},
            {"task":"Groceries / errands","category":"Errands","minutes":60,"required":False},
            {"task":"School pickup","category":"School","minutes":45,"required":True},
            {"task":"Snack + decompress","category":"Kids","minutes":30,"required":True},
            {"task":"Homework / reading support","category":"Homework","minutes":60,"required":True},
            {"task":"Dinner","category":"Meals","minutes":45,"required":True},
            {"task":"Cleanup","category":"Home","minutes":30,"required":False},
            {"task":"Baths / showers","category":"Evening","minutes":45,"required":True},
            {"task":"Tomorrow prep","category":"Evening","minutes":30,"required":True},
            {"task":"Bedtime routines","category":"Evening","minutes":45,"required":True},
            {"task":"Mom self-care","category":"Self-Care","minutes":20,"required":True},
        ],
        "groceries": [],
        "appointments": [],
        "meals": {
            "Monday":"Pasta + vegetables + fruit",
            "Tuesday":"Rice + chicken/beans + vegetables",
            "Wednesday":"Tacos / wraps + fruit",
            "Thursday":"Soup / stew + bread",
            "Friday":"Easy family favorite / leftovers",
            "Saturday":"Flexible / family choice",
            "Sunday":"Cook extra for Monday",
        },
        "chores": {},
        "wake_time":"06:15",
        "mom_bedtime":"22:00",
        "buffer_minutes":30,
        "target_rest_minutes":45,
        "busy_mode":False,
        "notes":"",
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v
init()

# -------------------- HELPERS --------------------
def mins_between(start_s, end_s):
    try:
        a=datetime.strptime(start_s,"%H:%M")
        b=datetime.strptime(end_s,"%H:%M")
        if b<a: b += timedelta(days=1)
        return int((b-a).total_seconds()/60)
    except:
        return 0

def hhmm(minutes):
    minutes=max(0,int(minutes))
    h,m=divmod(minutes,60)
    if h and m: return f"{h} hr {m} min"
    if h: return f"{h} hr"
    return f"{m} min"

def daily_metrics():
    available = mins_between(st.session_state.wake_time, st.session_state.mom_bedtime)
    planned = sum(int(t["minutes"]) for t in st.session_state.tasks if t.get("today",True))
    appt = sum(int(a.get("minutes",0)) for a in st.session_state.appointments if a.get("today",True))
    planned += appt
    buffer = int(st.session_state.buffer_minutes)
    free = available - planned - buffer
    target = int(st.session_state.target_rest_minutes)
    return available, planned, buffer, free, target

def status_message(free, target):
    if free < 0:
        return "🔴 OVERBOOKED", f"Your plan exceeds the day by {hhmm(abs(free))}. Remove, shorten, or delegate something."
    if free < target:
        return "🟠 VERY FULL", f"You only have {hhmm(free)} unplanned. Your rest target is {hhmm(target)}."
    if free < target + 45:
        return "🟡 TIGHT BUT DOABLE", f"You have about {hhmm(free)} unplanned. Protect your self-care block."
    return "🟢 BALANCED", f"You have about {hhmm(free)} available for rest, delays, or breathing room."

def export_data():
    keys=["children","tasks","groceries","appointments","meals","chores","wake_time","mom_bedtime","buffer_minutes","target_rest_minutes","notes"]
    payload={k:st.session_state[k] for k in keys}
    return json.dumps(payload, indent=2).encode()

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.header("⚙️ Family Settings")
    st.caption("Adjust these anytime.")
    st.session_state.wake_time = st.text_input("Mom wake time (24h)", st.session_state.wake_time)
    st.session_state.mom_bedtime = st.text_input("Mom bedtime (24h)", st.session_state.mom_bedtime)
    st.session_state.buffer_minutes = st.number_input("Daily buffer for delays (minutes)",0,180,int(st.session_state.buffer_minutes),5)
    st.session_state.target_rest_minutes = st.number_input("Minimum rest/self-care target (minutes)",0,180,int(st.session_state.target_rest_minutes),5)
    st.session_state.busy_mode = st.toggle("🆘 Busy Day Mode", value=st.session_state.busy_mode)

    st.divider()
    st.subheader("Backup")
    st.download_button("⬇️ Download family backup", export_data(), "family_planner_backup.json", "application/json")
    uploaded=st.file_uploader("Restore backup", type=["json"])
    if uploaded is not None:
        try:
            data=json.load(uploaded)
            if st.button("Restore this backup"):
                for k,v in data.items():
                    st.session_state[k]=v
                st.success("Backup restored.")
                st.rerun()
        except Exception:
            st.error("That backup file could not be read.")

# -------------------- HEADER / METRICS --------------------
st.title("💛 Mom of 5 — Family Command Center")
st.caption("Plan the family day, see how full it is, protect rest time, and reduce mental load.")

available, planned, buffer, free, target = daily_metrics()
status, status_text = status_message(free,target)

c1,c2,c3,c4 = st.columns(4)
c1.metric("Awake time", hhmm(available))
c2.metric("Planned activities", hhmm(planned))
c3.metric("Delay buffer", hhmm(buffer))
c4.metric("Estimated free/rest time", hhmm(max(0,free)), delta=f"{free-target:+} min vs target")

if status.startswith("🔴"): st.error(f"### {status}\n{status_text}")
elif status.startswith("🟠"): st.warning(f"### {status}\n{status_text}")
elif status.startswith("🟡"): st.warning(f"### {status}\n{status_text}")
else: st.success(f"### {status}\n{status_text}")

# Visual time bar
if available > 0:
    planned_pct=min(100,max(0,planned/available*100))
    buffer_pct=min(100,max(0,buffer/available*100))
    free_pct=max(0,100-planned_pct-buffer_pct)
    st.markdown("**Today's time budget**")
    st.progress(min(1.0, planned/available), text=f"Planned activities use {planned_pct:.0f}% of Mom's awake time")
    st.caption(f"Planned: {hhmm(planned)} • Buffer: {hhmm(buffer)} • Unplanned/rest: {hhmm(max(0,free))}")

tabs=st.tabs([
    "🏠 Today","👧 Kids & School","✅ Tasks & Time","📅 Appointments",
    "🎒 Homework","🍽️ Meals","🛒 Groceries","🧹 Chores",
    "💛 Mom Self-Care","📆 Weekly Plan","📊 Insights"
])

# -------------------- TODAY --------------------
with tabs[0]:
    st.header("🏠 Today's Priorities")
    if st.session_state.busy_mode:
        st.warning("Busy Day Mode is ON. Today is about essentials, not perfection.")
        essentials=["Kids fed and dressed","School drop-off / pickup","Urgent homework","Simple dinner","Bath/bed essentials","Mom eats + drinks water + 10 minutes quiet"]
        for i,x in enumerate(essentials): st.checkbox(x,key=f"essential_{i}")
    else:
        st.write("Check off only what truly matters today.")
        for i,t in enumerate(st.session_state.tasks):
            cols=st.columns([.7,4,1.2,1.2])
            with cols[0]:
                done=st.checkbox("", key=f"today_done_{i}")
            with cols[1]:
                st.write(f"**{t['task']}**")
                st.caption(t["category"])
            with cols[2]:
                st.write(hhmm(t["minutes"]))
            with cols[3]:
                st.write("Required" if t.get("required") else "Flexible")

    st.subheader("One important thing")
    st.session_state.notes=st.text_area("If only one extra thing gets done today, what should it be?", st.session_state.notes)

    if free < target:
        st.subheader("✂️ Simplify today")
        flexible=sorted([t for t in st.session_state.tasks if not t.get("required")], key=lambda x:x["minutes"], reverse=True)
        if flexible:
            st.write("Consider shortening, moving, or delegating one of these:")
            for t in flexible[:4]:
                st.write(f"• **{t['task']}** — {hhmm(t['minutes'])}")
        st.info("A simple dinner, skipped non-urgent errand, or shorter cleanup can create real recovery time.")

# -------------------- KIDS --------------------
with tabs[1]:
    st.header("👧 Kids & School")
    st.write("Edit names, ages, and school times whenever schedules change.")
    new_children=[]
    for i,c in enumerate(st.session_state.children):
        with st.expander(f"{c['name']} — age {c['age']}", expanded=i<2):
            name=st.text_input("Name",c["name"],key=f"kid_name_{i}")
            age=st.number_input("Age",0,18,int(c["age"]),key=f"kid_age_{i}")
            s1=st.text_input("School start",c.get("school_start",""),key=f"kid_start_{i}",placeholder="08:00")
            s2=st.text_input("School end",c.get("school_end",""),key=f"kid_end_{i}",placeholder="15:00")
            new_children.append({"name":name,"age":int(age),"school_start":s1,"school_end":s2})
    st.session_state.children=new_children

    st.subheader("Morning checklist")
    for i,c in enumerate(st.session_state.children):
        with st.expander(c["name"]):
            for label in ["Awake","Uniform / clothes","Breakfast","Teeth / hair / bathroom","Lunch / water","Backpack","Shoes / jacket"]:
                st.checkbox(label,key=f"morning_{i}_{label}")

# -------------------- TASKS & TIME --------------------
with tabs[2]:
    st.header("✅ Tasks & Time")
    st.write("This is what drives the rest-time calculation. Keep estimates realistic, not perfect.")

    for i,t in enumerate(list(st.session_state.tasks)):
        with st.expander(f"{t['task']} — {hhmm(t['minutes'])}"):
            t["task"]=st.text_input("Task",t["task"],key=f"task_name_{i}")
            t["category"]=st.selectbox("Category",["Morning","School","Home","Meals","Errands","Kids","Homework","Evening","Self-Care","Other"],
                                       index=["Morning","School","Home","Meals","Errands","Kids","Homework","Evening","Self-Care","Other"].index(t["category"]) if t["category"] in ["Morning","School","Home","Meals","Errands","Kids","Homework","Evening","Self-Care","Other"] else 9,
                                       key=f"task_cat_{i}")
            t["minutes"]=st.number_input("Estimated minutes",5,360,int(t["minutes"]),5,key=f"task_min_{i}")
            t["required"]=st.checkbox("Required today",value=t.get("required",False),key=f"task_req_{i}")
            if st.button("Delete task",key=f"task_del_{i}"):
                st.session_state.tasks.pop(i); st.rerun()

    st.subheader("Add a task")
    a,b,c,d=st.columns([3,2,1,1])
    nt=a.text_input("Task name",key="new_task_name")
    nc=b.selectbox("Category",["Morning","School","Home","Meals","Errands","Kids","Homework","Evening","Self-Care","Other"],key="new_task_cat")
    nm=c.number_input("Minutes",5,360,30,5,key="new_task_min")
    nr=d.checkbox("Required",key="new_task_req")
    if st.button("➕ Add task",type="primary"):
        if nt.strip():
            st.session_state.tasks.append({"task":nt.strip(),"category":nc,"minutes":int(nm),"required":bool(nr)})
            st.session_state.new_task_name=""
            st.rerun()

# -------------------- APPOINTMENTS --------------------
with tabs[3]:
    st.header("📅 Appointments & One-Time Plans")
    for i,a in enumerate(list(st.session_state.appointments)):
        cols=st.columns([3,2,1,1])
        cols[0].write(f"**{a['title']}**")
        cols[1].write(a.get("when",""))
        cols[2].write(hhmm(a.get("minutes",0)))
        if cols[3].button("Remove",key=f"appt_rm_{i}"):
            st.session_state.appointments.pop(i); st.rerun()

    st.subheader("Add appointment")
    title=st.text_input("Appointment / event",key="appt_title")
    when=st.text_input("When",placeholder="Monday 4:30 PM",key="appt_when")
    duration=st.number_input("Duration including travel (minutes)",5,360,60,5,key="appt_min")
    if st.button("➕ Add appointment"):
        if title.strip():
            st.session_state.appointments.append({"title":title.strip(),"when":when.strip(),"minutes":int(duration),"today":True})
            st.session_state.appt_title=""
            st.rerun()
    st.caption("Tip: include travel time so the rest-time estimate is realistic.")

# -------------------- HOMEWORK --------------------
with tabs[4]:
    st.header("🎒 Homework")
    for i,c in enumerate(st.session_state.children):
        if c["age"]>=5:
            with st.expander(c["name"]):
                st.text_input("What is due?",key=f"hw_due_{i}")
                st.checkbox("Homework complete",key=f"hw_complete_{i}")
                st.checkbox("Reading complete",key=f"read_complete_{i}")
                st.checkbox("Backpack repacked",key=f"bag_complete_{i}")

# -------------------- MEALS --------------------
with tabs[5]:
    st.header("🍽️ Meals")
    days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    for d in days:
        st.session_state.meals[d]=st.text_input(d,st.session_state.meals.get(d,""),key=f"meal_{d}")
    st.info("Shortcut: plan one leftovers night, one freezer/easy night, and cook extra once or twice a week.")

# -------------------- GROCERIES --------------------
with tabs[6]:
    st.header("🛒 Groceries")
    item=st.text_input("Add grocery item",key="grocery_new")
    if st.button("Add grocery"):
        if item.strip():
            st.session_state.groceries.append({"item":item.strip(),"done":False})
            st.session_state.grocery_new=""
            st.rerun()
    for i,g in enumerate(list(st.session_state.groceries)):
        c1,c2=st.columns([5,1])
        g["done"]=c1.checkbox(g["item"],value=g.get("done",False),key=f"g_{i}")
        if c2.button("Remove",key=f"g_rm_{i}"):
            st.session_state.groceries.pop(i); st.rerun()

# -------------------- CHORES --------------------
with tabs[7]:
    st.header("🧹 Age-Appropriate Chores")
    st.write("The goal is to make family routines shared, not to have Mom do five children's routines alone.")
    suggestions = [
        ("Ages 2–4","Put toys in basket, carry clothes to hamper, place napkins on table."),
        ("Ages 5–7","Put shoes/backpack away, set table, tidy toys, help sort laundry."),
        ("Ages 8–9","Clear dishes, pack backpack, fold simple laundry, help prepare snacks."),
        ("Ages 10–11","Help load/unload dishwasher, fold laundry, prepare simple lunch items, help younger siblings with non-parent tasks.")
    ]
    for age,txt in suggestions:
        st.write(f"**{age}:** {txt}")

    for i,c in enumerate(st.session_state.children):
        with st.expander(c["name"]):
            st.text_area("Assigned responsibilities",key=f"chore_{i}",placeholder="Example: backpack, table, toys, laundry...")

# -------------------- SELF CARE --------------------
with tabs[8]:
    st.header("💛 Mom Self-Care")
    st.write("Self-care here means small protected recovery, not another complicated responsibility.")
    st.metric("Today's estimated free/rest time",hhmm(max(0,free)))
    st.metric("Your minimum rest target",hhmm(target))

    if free < 0:
        st.error("There is no realistic rest block in the current plan. Something needs to move, shrink, or be delegated.")
    elif free < target:
        st.warning(f"You are short of your rest target by {hhmm(target-free)}.")
    else:
        st.success(f"Your current plan leaves at least {hhmm(free)} unplanned.")

    st.subheader("Daily minimum")
    for i,x in enumerate([
        "Drink water after waking",
        "Eat something nourishing",
        "Sit down for at least 10 minutes",
        "Stretch / walk / step outside",
        "Take one small block of time that belongs only to Mom",
    ]):
        st.checkbox(x,key=f"selfcare_{i}")

    st.subheader("Choose one today")
    st.radio("What would help most?",[
        "10 minutes of quiet","Hot shower without rushing","Tea / coffee alone",
        "Short walk or stretch","Call someone supportive","Read or listen to something enjoyable",
        "Go to bed earlier","Do absolutely nothing for 10 minutes"
    ],index=None)

# -------------------- WEEKLY --------------------
with tabs[9]:
    st.header("📆 Weekly Plan")
    reset=[
        "Check school calendar / messages","Check appointments","Plan 5 weekday dinners",
        "Make grocery list","Wash / organize uniforms","Check shoes / jackets / backpacks",
        "Restock lunch/snack items","Check projects due","Choose one laundry block",
        "Choose one errand block","Schedule one small thing for Mom"
    ]
    for i,x in enumerate(reset): st.checkbox(x,key=f"weekly_{i}")

    st.subheader("Weekly priorities")
    a,b,c=st.columns(3)
    a.text_area("Must do",key="must_do")
    b.text_area("Would be nice",key="nice_do")
    c.text_area("Can wait",key="can_wait")

# -------------------- INSIGHTS --------------------
with tabs[10]:
    st.header("📊 Time & Load Insights")
    st.write("These estimates help spot overload before the day starts.")

    metrics=[
        ("Awake time",available),
        ("Planned activities",planned),
        ("Delay buffer",buffer),
        ("Estimated free/rest",max(0,free)),
        ("Rest target",target)
    ]
    for name,val in metrics:
        st.write(f"**{name}:** {hhmm(val)}")

    load = planned + buffer
    if available:
        utilization = load/available*100
        st.metric("Day utilization",f"{utilization:.0f}%")
        if utilization > 100:
            st.error("Your scheduled load is above 100% of your available awake time.")
        elif utilization > 90:
            st.warning("Your day is above 90% planned. Very little room remains for traffic, tantrums, spills, school calls, or simple rest.")
        elif utilization > 80:
            st.warning("Your day is fairly full. Keep at least one flexible task movable.")
        else:
            st.success("Your plan has a healthier amount of breathing room.")

    st.subheader("Where the time is going")
    cats={}
    for t in st.session_state.tasks:
        cats[t["category"]]=cats.get(t["category"],0)+int(t["minutes"])
    for cat,mins in sorted(cats.items(),key=lambda x:-x[1]):
        pct=(mins/planned*100) if planned else 0
        st.write(f"**{cat}:** {hhmm(mins)} ({pct:.0f}% of planned time)")

    st.subheader("If the day is overloaded")
    st.markdown("""
1. Protect school, meals, safety, urgent homework, and sleep.
2. Keep Mom's minimum food/water/rest needs on the list.
3. Move non-urgent errands.
4. Use an easy dinner or leftovers.
5. Shorten cleanup to a 10-minute reset.
6. Give older children age-appropriate responsibilities.
7. Combine errands into one trip.
8. Prepare uniforms, backpacks, and lunches the night before.
""")

st.divider()
st.caption("This planner is designed to reduce mental load, not create another standard of perfection. Time estimates are planning aids, not guarantees.")
