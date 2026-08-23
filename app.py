
import streamlit as st
from datetime import datetime, date, time, timedelta
import json

st.set_page_config(page_title="Mom of 5 Family Command Center", page_icon="💛", layout="wide")

# -------------------- STATE --------------------
def init():
    defaults = {
        "children": [
            {"name":"Child 1","age":11,"school":True,"school_start":"08:00","school_end":"15:00"},
            {"name":"Child 2","age":9,"school":True,"school_start":"08:00","school_end":"15:00"},
            {"name":"Child 3","age":7,"school":True,"school_start":"08:00","school_end":"15:00"},
            {"name":"Child 4","age":4,"school":True,"school_start":"08:30","school_end":"14:30"},
            {"name":"Baby","age":2,"school":False,"school_start":"","school_end":""},
        ],
        "tasks": [
            {"task":"Wake kids / uniforms / breakfast","category":"Morning","minutes":75,"required":True},
            {"task":"School drop-off","category":"School","minutes":45,"required":True},
            {"task":"Toddler care / morning play","category":"Toddler","minutes":60,"required":True},
            {"task":"Home reset / dishes","category":"Home","minutes":30,"required":False},
            {"task":"Cooking / dinner prep","category":"Meals","minutes":60,"required":True},
            {"task":"Toddler lunch / nap routine","category":"Toddler","minutes":75,"required":True},
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
        "appointments": [],
        "groceries": [],
        "food_lookup": [
            "Pasta","Rice","Chicken","Beans","Ground turkey","Beef stew","Fish",
            "Tacos","Soup","Sandwiches","Pizza","Eggs","Oatmeal","Cereal",
            "Pancakes","Yogurt","Fruit","Vegetables","Salad","Bread","Leftovers"
        ],
        "grocery_categories": [
            "Produce","Dairy","Meat / Protein","Bread / Bakery","Pantry",
            "Frozen","Snacks","Lunch Items","Breakfast","Beverages",
            "Household","Cleaning","Toiletries","Baby / Toddler","Other"
        ],
        "grocery_item_lookup": [
            "Milk","Eggs","Bread","Bananas","Apples","Berries","Yogurt","Cheese",
            "Chicken","Ground turkey","Rice","Pasta","Pasta sauce","Beans",
            "Cereal","Oatmeal","Juice","Water","Lunch meat","Tortillas",
            "Frozen vegetables","Fresh vegetables","Snacks","Diapers","Wipes",
            "Soap","Laundry detergent","Dish soap","Paper towels"
        ],
        "meals": {
            "Monday":{"breakfast":"Oatmeal","lunch":"Sandwiches","dinner":"Pasta"},
            "Tuesday":{"breakfast":"Eggs","lunch":"Leftovers","dinner":"Rice"},
            "Wednesday":{"breakfast":"Cereal","lunch":"Sandwiches","dinner":"Tacos"},
            "Thursday":{"breakfast":"Yogurt","lunch":"Leftovers","dinner":"Soup"},
            "Friday":{"breakfast":"Pancakes","lunch":"Sandwiches","dinner":"Pizza"},
            "Saturday":{"breakfast":"Eggs","lunch":"Sandwiches","dinner":"Leftovers"},
            "Sunday":{"breakfast":"Pancakes","lunch":"Rice","dinner":"Chicken"},
        },
        "wake_time":"06:15",
        "mom_bedtime":"22:00",
        "buffer_minutes":30,
        "target_rest_minutes":45,
        "busy_mode":False,
        "notes":"",
        "night_before":{},
        "toddler_notes":"",
        "mom_care_lookup":[
            "10 minutes of quiet","Hot shower without rushing","Tea / coffee alone",
            "Short walk","Stretching","Prayer / meditation","Read a book",
            "Listen to music or a podcast","Call a supportive friend/family member",
            "Nap / lie down","Go to bed earlier","Skincare","Hair care","Exercise",
            "Do absolutely nothing for 10 minutes"
        ],
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
    available=mins_between(st.session_state.wake_time,st.session_state.mom_bedtime)
    planned=sum(int(t["minutes"]) for t in st.session_state.tasks)
    planned+=sum(int(a.get("minutes",0)) for a in st.session_state.appointments if a.get("date")==date.today().isoformat())
    buffer=int(st.session_state.buffer_minutes)
    free=available-planned-buffer
    target=int(st.session_state.target_rest_minutes)
    return available,planned,buffer,free,target

def status_message(free,target):
    if free < 0:
        return "🔴 OVERBOOKED",f"Your plan exceeds the day by {hhmm(abs(free))}. Remove, shorten, or delegate something."
    if free < target:
        return "🟠 VERY FULL",f"You only have {hhmm(free)} unplanned. Your rest target is {hhmm(target)}."
    if free < target+45:
        return "🟡 TIGHT BUT DOABLE",f"You have about {hhmm(free)} unplanned. Protect your self-care block."
    return "🟢 BALANCED",f"You have about {hhmm(free)} available for rest, delays, or breathing room."

def export_data():
    keys=["children","tasks","appointments","groceries","food_lookup","grocery_categories",
          "grocery_item_lookup","meals","wake_time","mom_bedtime","buffer_minutes",
          "target_rest_minutes","notes","night_before","toddler_notes","mom_care_lookup"]
    return json.dumps({k:st.session_state[k] for k in keys},indent=2).encode()

def child_names(school_only=False):
    kids=[c for c in st.session_state.children if (c.get("school",False) or not school_only)]
    return [c["name"] for c in kids]

def school_children():
    return [c for c in st.session_state.children if c.get("school",False)]

def toddler_children():
    return [c for c in st.session_state.children if not c.get("school",False)]

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.header("⚙️ Family Settings")
    st.session_state.wake_time=st.text_input("Mom wake time (24h)",st.session_state.wake_time)
    st.session_state.mom_bedtime=st.text_input("Mom bedtime (24h)",st.session_state.mom_bedtime)
    st.session_state.buffer_minutes=st.number_input("Daily delay buffer (minutes)",0,180,int(st.session_state.buffer_minutes),5)
    st.session_state.target_rest_minutes=st.number_input("Minimum rest/self-care target (minutes)",0,180,int(st.session_state.target_rest_minutes),5)
    st.session_state.busy_mode=st.toggle("🆘 Busy Day Mode",value=st.session_state.busy_mode)
    st.divider()
    st.download_button("⬇️ Download family backup",export_data(),"family_planner_backup.json","application/json")
    uploaded=st.file_uploader("Restore backup",type=["json"])
    if uploaded:
        try:
            data=json.load(uploaded)
            if st.button("Restore this backup"):
                for k,v in data.items(): st.session_state[k]=v
                st.success("Backup restored."); st.rerun()
        except Exception:
            st.error("Could not read that backup.")

# -------------------- DASHBOARD --------------------
st.title("💛 Mom of 5 — Family Command Center")
st.caption("Built for four school children plus a 2-year-old at home with Mom.")

available,planned,buffer,free,target=daily_metrics()
status,status_text=status_message(free,target)

a,b,c,d=st.columns(4)
a.metric("Awake time",hhmm(available))
b.metric("Planned activities",hhmm(planned))
c.metric("Delay buffer",hhmm(buffer))
d.metric("Estimated rest/free time",hhmm(max(0,free)),delta=f"{free-target:+} min vs target")

if status.startswith("🔴"): st.error(f"### {status}\n{status_text}")
elif status.startswith("🟠") or status.startswith("🟡"): st.warning(f"### {status}\n{status_text}")
else: st.success(f"### {status}\n{status_text}")

if available>0:
    st.progress(min(1.0,planned/available),text=f"Planned activities use {planned/available*100:.0f}% of Mom's awake time")
    st.caption(f"Planned {hhmm(planned)} • Buffer {hhmm(buffer)} • Rest/free {hhmm(max(0,free))}")

tabs=st.tabs([
    "🏠 Today","👧 Kids Lookup","🌙 Night Before School","👶 Toddler at Home",
    "✅ Tasks & Time","📅 Calendar","🎒 Homework","🍽️ Food Lookup & Meals",
    "🛒 Grocery Lookup","🧹 Chores","💛 Self-Care","⏱️ Time Calculator","📊 Insights"
])

# -------------------- TODAY --------------------
with tabs[0]:
    st.header("🏠 Today's Priorities")
    if st.session_state.busy_mode:
        st.warning("Busy Day Mode is ON — essentials only.")
        essentials=[
            "Four school kids dressed, fed, and ready",
            "School drop-off and pickup",
            "2-year-old fed, supervised, rested, and cared for",
            "Urgent homework / reading",
            "Simple dinner",
            "Bath / bedtime essentials",
            "Mom eats, drinks water, and gets at least 10 quiet minutes"
        ]
        for i,x in enumerate(essentials): st.checkbox(x,key=f"ess_{i}")
    else:
        for i,t in enumerate(st.session_state.tasks):
            cols=st.columns([.5,4,1.2,1])
            cols[0].checkbox("",key=f"done_{i}")
            cols[1].write(f"**{t['task']}**"); cols[1].caption(t["category"])
            cols[2].write(hhmm(t["minutes"]))
            cols[3].write("Required" if t.get("required") else "Flexible")
    st.session_state.notes=st.text_area("One important extra thing today",st.session_state.notes)

# -------------------- KIDS LOOKUP --------------------
with tabs[1]:
    st.header("👧 Kids Lookup / Family Profiles")
    st.write("Enter each child's name once. The names are then used as lookup values throughout the app.")
    updated=[]
    for i,c in enumerate(st.session_state.children):
        with st.expander(f"{c['name']} — age {c['age']}",expanded=i<2):
            name=st.text_input("Name",c["name"],key=f"kname_{i}")
            age=st.number_input("Age",0,18,int(c["age"]),key=f"kage_{i}")
            school=st.checkbox("Attends school",value=c.get("school",True),key=f"kschool_{i}")
            if school:
                s1=st.time_input("School start",value=datetime.strptime(c.get("school_start","08:00") or "08:00","%H:%M").time(),key=f"kstart_{i}")
                s2=st.time_input("School end",value=datetime.strptime(c.get("school_end","15:00") or "15:00","%H:%M").time(),key=f"kend_{i}")
                start_s=s1.strftime("%H:%M"); end_s=s2.strftime("%H:%M")
            else:
                start_s=""; end_s=""
            updated.append({"name":name,"age":int(age),"school":school,"school_start":start_s,"school_end":end_s})
    st.session_state.children=updated

    st.subheader("Quick lookup")
    selected=st.selectbox("Select child",child_names(),key="kid_lookup")
    kid=next(c for c in st.session_state.children if c["name"]==selected)
    st.write(f"**{kid['name']}** • Age {kid['age']} • {'School child' if kid['school'] else 'Home with Mom'}")

# -------------------- NIGHT BEFORE SCHOOL --------------------
with tabs[2]:
    st.header("🌙 Night-Before Checklist — Every School Day")
    st.write("This checklist is specifically for the four children who attend school. Preparing at night reduces morning stress.")

    school_kids=school_children()
    if len(school_kids)==0:
        st.info("Mark children as 'Attends school' in Kids Lookup.")
    else:
        school_day=st.selectbox("Prepare for",["Monday","Tuesday","Wednesday","Thursday","Friday"],key="night_day")
        for i,c in enumerate(school_kids):
            with st.expander(f"🎒 {c['name']} — age {c['age']}",expanded=True):
                items=[
                    "Uniform / school clothes laid out",
                    "Underwear / socks ready",
                    "Shoes by the door",
                    "Backpack packed",
                    "Homework / folder inside backpack",
                    "Lunchbox prepared / lunch items ready",
                    "Water bottle ready",
                    "Jacket / sweater ready",
                    "Special school item checked",
                    "Hair / accessory items ready if needed",
                    "Alarm / wake-up plan set",
                ]
                for j,item in enumerate(items):
                    st.checkbox(item,key=f"night_{school_day}_{i}_{j}")
                st.text_input("Anything special tomorrow?",key=f"night_special_{school_day}_{i}",
                              placeholder="PE clothes, project, library book, picture day...")

        st.success("Best shortcut: backpacks + shoes + uniforms should all be in one predictable place before Mom goes to bed.")

# -------------------- TODDLER --------------------
with tabs[3]:
    st.header("👶 2-Year-Old Home-Day Plan")
    toddlers=toddler_children()
    if not toddlers:
        st.info("Mark the 2-year-old as not attending school in Kids Lookup.")
    else:
        toddler=st.selectbox("Child at home", [c["name"] for c in toddlers],key="tod_lookup")
        st.info("The toddler is included in the daily time budget because supervision, meals, play, diaper/toilet care, and nap routines reduce Mom's uninterrupted task time.")

        routine=[
            ("Morning wake / diaper or toilet / dress",30),
            ("Breakfast with family",30),
            ("Morning play / reading",45),
            ("Snack",15),
            ("Outside / movement / walk",30),
            ("Independent / supervised play while Mom handles a short task",30),
            ("Lunch",30),
            ("Nap / quiet time",90),
            ("Afternoon snack",15),
            ("Play / pickup transition",45),
            ("Dinner",30),
            ("Bath / pajamas",30),
            ("Bedtime routine",30),
        ]
        total=0
        for i,(name,mins) in enumerate(routine):
            cols=st.columns([.6,4,1])
            cols[0].checkbox("",key=f"tod_{i}")
            cols[1].write(name)
            cols[2].write(hhmm(mins))
            total+=mins
        st.metric("Toddler routine time represented",hhmm(total))
        st.caption("Some toddler care overlaps family activities such as breakfast and dinner; the number is a planning guide, not extra hours to add twice.")
        st.session_state.toddler_notes=st.text_area("Toddler notes",st.session_state.toddler_notes,
                                                     placeholder="Nap changes, diapers, appointments, favorite activities, supplies needed...")

# -------------------- TASKS --------------------
with tabs[4]:
    st.header("✅ Tasks & Time")
    st.write("Edit estimated durations. These values drive the overload and rest-time warnings.")
    cats=["Morning","School","Toddler","Home","Meals","Errands","Kids","Homework","Evening","Self-Care","Other"]
    for i,t in enumerate(list(st.session_state.tasks)):
        with st.expander(f"{t['task']} — {hhmm(t['minutes'])}"):
            t["task"]=st.text_input("Task",t["task"],key=f"tn_{i}")
            t["category"]=st.selectbox("Category",cats,index=cats.index(t["category"]) if t["category"] in cats else -1,key=f"tc_{i}")
            t["minutes"]=st.number_input("Estimated minutes",5,360,int(t["minutes"]),5,key=f"tm_{i}")
            t["required"]=st.checkbox("Required",value=t.get("required",False),key=f"tr_{i}")
            if st.button("Delete",key=f"td_{i}"): st.session_state.tasks.pop(i); st.rerun()
    st.subheader("Add task")
    n=st.text_input("Task name",key="newtask")
    c=st.selectbox("Category",cats,key="newcat")
    m=st.number_input("Minutes",5,360,30,5,key="newmin")
    req=st.checkbox("Required",key="newreq")
    if st.button("➕ Add task"):
        if n.strip():
            st.session_state.tasks.append({"task":n.strip(),"category":c,"minutes":int(m),"required":req})
            st.session_state.newtask=""; st.rerun()

# -------------------- CALENDAR --------------------
with tabs[5]:
    st.header("📅 Calendar / Appointments")
    st.write("Use selectable dates and times to reduce typing.")

    event_date=st.date_input("Date",value=date.today(),key="cal_date")
    event_time=st.time_input("Start time",value=time(9,0),step=900,key="cal_time")
    duration=st.number_input("Duration including travel (minutes)",5,480,60,5,key="cal_duration")
    title=st.text_input("Activity / appointment",key="cal_title",placeholder="Doctor, school event, groceries, church...")
    who=st.multiselect("Who is involved?",child_names(),key="cal_who")
    category=st.selectbox("Type",["School","Medical","Errand","Family","Activity","Church","Self-Care","Other"],key="cal_cat")
    if st.button("➕ Add to calendar",type="primary"):
        if title.strip():
            st.session_state.appointments.append({
                "title":title.strip(),
                "date":event_date.isoformat(),
                "time":event_time.strftime("%H:%M"),
                "minutes":int(duration),
                "who":who,
                "category":category
            })
            st.session_state.cal_title=""
            st.rerun()

    st.subheader("Upcoming / entered events")
    for i,a in enumerate(sorted(st.session_state.appointments,key=lambda x:(x.get("date",""),x.get("time","")))):
        c1,c2,c3,c4=st.columns([3,2,1.4,.8])
        c1.write(f"**{a['title']}**"); c1.caption(", ".join(a.get("who",[])) or "Family / Mom")
        c2.write(f"{a.get('date','')} • {a.get('time','')}")
        c3.write(hhmm(a.get("minutes",0)))
        if c4.button("Remove",key=f"arm_{i}"):
            # remove matching object from original list
            st.session_state.appointments.remove(a); st.rerun()

# -------------------- HOMEWORK --------------------
with tabs[6]:
    st.header("🎒 Homework")
    school_names=[c["name"] for c in school_children()]
    if school_names:
        kid=st.selectbox("Select child",school_names,key="hw_kid")
        st.text_input("What is due?",key=f"due_{kid}",placeholder="Math page, reading, project...")
        st.checkbox("Homework complete",key=f"hw_{kid}")
        st.checkbox("Reading complete",key=f"read_{kid}")
        st.checkbox("Backpack repacked",key=f"repack_{kid}")
    else:
        st.info("No school children are marked in Kids Lookup.")

# -------------------- FOOD LOOKUP + MEALS --------------------
with tabs[7]:
    st.header("🍽️ Food Lookup & Meal Plan")
    st.write("Enter foods once, then use them as selectable lookup values in the weekly meal plan.")

    st.subheader("Food master list")
    new_food=st.text_input("Add food / meal option",key="food_new",placeholder="Mac & cheese, lentils, chicken soup...")
    if st.button("Add food"):
        if new_food.strip() and new_food.strip() not in st.session_state.food_lookup:
            st.session_state.food_lookup.append(new_food.strip())
            st.session_state.food_new=""
            st.rerun()

    st.write("Current lookup values:")
    st.caption(" • ".join(st.session_state.food_lookup))

    st.subheader("Weekly meal plan")
    days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    for d in days:
        st.markdown(f"**{d}**")
        cols=st.columns(3)
        for idx,meal in enumerate(["breakfast","lunch","dinner"]):
            current=st.session_state.meals.get(d,{}).get(meal,"")
            options=[""]+st.session_state.food_lookup
            if current and current not in options: options.append(current)
            choice=cols[idx].selectbox(meal.title(),options,index=options.index(current) if current in options else 0,key=f"{d}_{meal}")
            st.session_state.meals.setdefault(d,{})[meal]=choice

    st.info("Tip: add all regular family meals to the master list once, then meal planning becomes mostly choosing from dropdowns.")

# -------------------- GROCERY LOOKUP --------------------
with tabs[8]:
    st.header("🛒 Grocery Lookup & List")
    st.write("Maintain reusable grocery categories and item lookup values, then build the shopping list from dropdowns.")

    c1,c2=st.columns(2)
    with c1:
        st.subheader("Grocery categories")
        new_cat=st.text_input("Add category",key="gcat_new")
        if st.button("Add category"):
            if new_cat.strip() and new_cat.strip() not in st.session_state.grocery_categories:
                st.session_state.grocery_categories.append(new_cat.strip())
                st.session_state.gcat_new=""
                st.rerun()
        st.caption(" • ".join(st.session_state.grocery_categories))

    with c2:
        st.subheader("Grocery item lookup")
        new_item=st.text_input("Add reusable grocery item",key="glookup_new")
        if st.button("Add lookup item"):
            if new_item.strip() and new_item.strip() not in st.session_state.grocery_item_lookup:
                st.session_state.grocery_item_lookup.append(new_item.strip())
                st.session_state.glookup_new=""
                st.rerun()
        st.caption(" • ".join(st.session_state.grocery_item_lookup))

    st.subheader("Build shopping list")
    gc=st.selectbox("Category",st.session_state.grocery_categories,key="grocery_cat_pick")
    gi=st.selectbox("Item",[""]+st.session_state.grocery_item_lookup,key="grocery_item_pick")
    qty=st.text_input("Quantity / note",key="grocery_qty",placeholder="2 gallons, 1 pack, large...")
    if st.button("➕ Add to shopping list",type="primary"):
        if gi:
            st.session_state.groceries.append({"category":gc,"item":gi,"qty":qty,"done":False})
            st.rerun()

    grouped={}
    for g in st.session_state.groceries:
        grouped.setdefault(g["category"],[]).append(g)
    for cat,items in grouped.items():
        st.markdown(f"### {cat}")
        for g in list(items):
            c1,c2=st.columns([5,1])
            label=f"{g['item']}" + (f" — {g['qty']}" if g.get("qty") else "")
            g["done"]=c1.checkbox(label,value=g.get("done",False),key=f"shop_{id(g)}")
            if c2.button("Remove",key=f"shoprm_{id(g)}"):
                st.session_state.groceries.remove(g); st.rerun()

# -------------------- CHORES --------------------
with tabs[9]:
    st.header("🧹 Chores / Responsibilities")
    st.write("Use the child-name lookup so responsibilities are assigned without retyping names.")
    who=st.selectbox("Child",child_names(),key="chore_kid")
    st.text_area("Responsibilities",key=f"chore_{who}",placeholder="Backpack, shoes, table, toys, laundry...")
    st.markdown("""
**Examples**
- Ages 2–4: toys in basket, clothes in hamper.
- Ages 5–7: backpack/shoes away, set table, tidy toys.
- Ages 8–9: clear dishes, fold simple laundry, prep snacks.
- Ages 10–11: dishwasher help, fold laundry, prep lunch items, help younger siblings with simple non-parent tasks.
""")

# -------------------- SELF CARE --------------------
with tabs[10]:
    st.header("💛 Mom Self-Care")
    st.metric("Estimated free/rest time today",hhmm(max(0,free)))
    st.metric("Rest target",hhmm(target))
    if free<0:
        st.error("No realistic rest time remains in the current plan. Move, shorten, or delegate something.")
    elif free<target:
        st.warning(f"You are short by {hhmm(target-free)}.")
    else:
        st.success("Your current plan meets the rest target.")

    st.subheader("Mom Care Lookup")
    st.write("Enter self-care activities once, then reuse them from the dropdown.")
    new_care=st.text_input("Add Mom-care activity",key="momcare_new",placeholder="Massage, bath, walk, journaling...")
    if st.button("Add Mom-care lookup value"):
        if new_care.strip() and new_care.strip() not in st.session_state.mom_care_lookup:
            st.session_state.mom_care_lookup.append(new_care.strip())
            st.session_state.momcare_new=""
            st.rerun()

    selected_care=st.selectbox("Choose Mom-care activity",[""]+st.session_state.mom_care_lookup,key="momcare_pick")
    care_start=st.time_input("Planned self-care start time",value=time(21,0),step=900,key="care_start")
    care_end=st.time_input("Planned self-care end time",value=time(21,20),step=900,key="care_end")

    start_dt=datetime.combine(date.today(),care_start)
    end_dt=datetime.combine(date.today(),care_end)
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    care_minutes=int((end_dt-start_dt).total_seconds()/60)

    c1,c2=st.columns(2)
    c1.metric("Mom-care duration",f"{care_minutes} minutes")
    c2.metric("In hours",f"{care_minutes/60:.2f} hours")

    if selected_care:
        st.success(f"Planned: **{selected_care}** for **{hhmm(care_minutes)}**.")

    st.subheader("Daily minimum")
    for i,x in enumerate([
        "Drink water","Eat something nourishing","Sit quietly for at least 10 minutes",
        "Stretch / walk / step outside","Do one small thing just for Mom"
    ]):
        st.checkbox(x,key=f"sc_{i}")

# -------------------- TIME CALCULATOR --------------------
with tabs[11]:
    st.header("⏱️ Time Calculator")
    st.write("Select a start and end time. The app calculates the total automatically.")

    calc_start=st.time_input("Start time",value=time(9,0),step=300,key="calc_start")
    calc_end=st.time_input("End time",value=time(10,30),step=300,key="calc_end")

    start_dt=datetime.combine(date.today(),calc_start)
    end_dt=datetime.combine(date.today(),calc_end)
    crosses_midnight=False
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
        crosses_midnight=True

    total_minutes=int((end_dt-start_dt).total_seconds()/60)
    hours=total_minutes//60
    minutes=total_minutes%60

    c1,c2,c3=st.columns(3)
    c1.metric("Total minutes",f"{total_minutes} min")
    c2.metric("Decimal hours",f"{total_minutes/60:.2f} hr")
    c3.metric("Hours + minutes",f"{hours} hr {minutes} min")

    if crosses_midnight:
        st.info("The end time is earlier than the start time, so the calculator assumes the period crosses midnight.")

    calc_activity=st.text_input("What is this time for?",key="calc_activity",placeholder="Homework, errands, bath time, Mom care...")
    if calc_activity:
        st.success(f"**{calc_activity}** takes **{hours} hr {minutes} min**.")

# -------------------- INSIGHTS --------------------
with tabs[12]:
    st.header("📊 Time & Load Insights")
    utilization=((planned+buffer)/available*100) if available else 0
    st.metric("Day utilization",f"{utilization:.0f}%")
    if utilization>100:
        st.error("The plan is above 100% of available awake time.")
    elif utilization>90:
        st.warning("Very little margin remains for toddler interruptions, traffic, spills, school calls, or rest.")
    elif utilization>80:
        st.warning("The day is fairly full. Keep at least one flexible task movable.")
    else:
        st.success("The plan has healthier breathing room.")

    st.subheader("Where time is going")
    cats={}
    for t in st.session_state.tasks:
        cats[t["category"]]=cats.get(t["category"],0)+int(t["minutes"])
    for cat,mins in sorted(cats.items(),key=lambda x:-x[1]):
        st.write(f"**{cat}:** {hhmm(mins)}")

    st.subheader("Overload rule")
    st.markdown("""
If the day is too full:
1. Keep school, toddler care, meals, safety, urgent homework, sleep, and Mom's basic needs.
2. Move non-urgent errands.
3. Use leftovers / easy dinner.
4. Shorten cleanup to 10 minutes.
5. Delegate age-appropriate responsibilities.
6. Combine errands.
7. Prepare all four school kids the night before.
""")

st.divider()
st.caption("This planner is a planning aid. Toddler care is intentionally included because it affects how much uninterrupted time Mom realistically has.")
