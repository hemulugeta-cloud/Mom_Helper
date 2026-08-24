import streamlit as st
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import json

st.set_page_config(page_title="Mom Weekly Calendar", page_icon="📅", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1320px; padding-top: 1.2rem; padding-bottom: 2rem;}
h1 {font-weight: 800 !important; letter-spacing: -0.025em; margin-bottom: .2rem !important;}
h2, h3 {letter-spacing: -0.015em;}
div[data-testid="stMetric"] {
    border: 1px solid rgba(120,120,120,.18);
    border-radius: 16px;
    padding: 14px 16px;
    background: rgba(255,255,255,.72);
}
div[data-testid="stExpander"] {
    border: 1px solid rgba(120,120,120,.18);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 10px;
}
div.stButton > button {border-radius: 12px; font-weight: 650;}
div[data-testid="stAlert"] {border-radius: 14px;}
.day-banner {
    padding: 16px 18px;
    border: 1px solid rgba(120,120,120,.18);
    border-radius: 16px;
    background: rgba(255,255,255,.72);
    margin: 8px 0 14px 0;
}
.muted {opacity:.72; font-size:.92rem;}
</style>
""", unsafe_allow_html=True)

# -------------------- Defaults --------------------
CATEGORIES = {
    "🎒 Kids / School": [
        "Wake school kids","Get kids dressed / uniforms","Breakfast",
        "Pack / check lunches & backpacks","School drop-off","School pickup",
        "After-school snack / decompress","Homework / reading",
        "Dinner with kids","Bath / showers","Bedtime routine",
    ],
    "👶 Toddler": [
        "Toddler morning routine","Toddler breakfast","Toddler play / reading",
        "Toddler snack","Toddler outdoor / movement time","Toddler lunch",
        "Toddler nap / quiet time","Toddler afternoon play","Toddler bath",
        "Toddler bedtime routine",
    ],
    "🧹 Cleaning": [
        "Morning kitchen reset","General house cleaning","Bathroom cleaning",
        "Bedroom pickup","Living room pickup","Floor sweeping / vacuuming",
        "Mopping","Dinner cleanup","Night-before home reset",
    ],
    "🍳 Cooking": [
        "Breakfast prep","Lunch prep","Meal planning","Meal prep","Cooking dinner",
        "Pack school lunches","Prepare snacks","Batch cooking / freezer prep",
        "Grocery shopping / food errands",
    ],
    "🧺 Laundry": [
        "Sort laundry","Wash clothes","Dry clothes","Fold clothes","Put clothes away",
        "School uniform laundry","Bedding / towels",
    ],
    "⛪ Church": [
        "Church worship","Church class","Kids church / Sunday school",
        "Prayer / devotional time","Church event / fellowship","Travel to / from church",
    ],
    "💛 Mom Self-Care": [
        "Drink water / hydration break","Eat a nourishing meal","Quiet rest","Nap",
        "Reading","School / study time","Prayer / meditation","Walk / exercise",
        "Stretching","Shower / personal care","Tea / coffee break",
        "Listen to music / podcast","Call / talk with supportive person",
        "Skincare / hair care","Go to bed earlier","Do nothing / mental break",
    ],
    "👨‍👩‍👧‍👦 Family Time": [
        "Eat dinner together","Watch TV / movie together","Go to the park",
        "Go out to eat","Play games in the house","Read together",
        "Family conversation","Walk together","Outdoor family activity",
        "Visit family / friends","Go to church together","Family outing / activity",
    ],
    "😴 Sleep": [
        "Mom sleep","Kids bedtime supervision","Toddler sleep / bedtime supervision",
    ],
}

DEFAULT_MINUTES = {
    "Wake school kids":15,"Get kids dressed / uniforms":30,"Breakfast":30,
    "Pack / check lunches & backpacks":20,"School drop-off":45,"School pickup":45,
    "After-school snack / decompress":30,"Homework / reading":60,"Dinner with kids":45,
    "Bath / showers":45,"Bedtime routine":45,
    "Toddler morning routine":30,"Toddler breakfast":30,"Toddler play / reading":45,
    "Toddler snack":15,"Toddler outdoor / movement time":30,"Toddler lunch":30,
    "Toddler nap / quiet time":90,"Toddler afternoon play":45,"Toddler bath":30,
    "Toddler bedtime routine":30,
    "Morning kitchen reset":20,"General house cleaning":60,"Bathroom cleaning":30,
    "Bedroom pickup":30,"Living room pickup":20,"Floor sweeping / vacuuming":30,
    "Mopping":30,"Dinner cleanup":30,"Night-before home reset":20,
    "Breakfast prep":20,"Lunch prep":30,"Meal planning":20,"Meal prep":30,
    "Cooking dinner":60,"Pack school lunches":30,"Prepare snacks":15,
    "Batch cooking / freezer prep":90,"Grocery shopping / food errands":90,
    "Sort laundry":15,"Wash clothes":45,"Dry clothes":45,"Fold clothes":45,
    "Put clothes away":30,"School uniform laundry":60,"Bedding / towels":60,
    "Church worship":120,"Church class":60,"Kids church / Sunday school":60,
    "Prayer / devotional time":20,"Church event / fellowship":90,"Travel to / from church":45,
    "Drink water / hydration break":5,"Eat a nourishing meal":30,"Quiet rest":20,
    "Nap":30,"Reading":30,"School / study time":60,"Prayer / meditation":20,
    "Walk / exercise":30,"Stretching":15,"Shower / personal care":20,
    "Tea / coffee break":15,"Listen to music / podcast":20,
    "Call / talk with supportive person":20,"Skincare / hair care":20,
    "Go to bed earlier":60,"Do nothing / mental break":15,
    "Eat dinner together":45,"Watch TV / movie together":90,"Go to the park":60,
    "Go out to eat":90,"Play games in the house":45,"Read together":30,
    "Family conversation":20,"Walk together":30,"Outdoor family activity":60,
    "Visit family / friends":120,"Go to church together":120,"Family outing / activity":120,
    "Mom sleep":480,"Kids bedtime supervision":45,"Toddler sleep / bedtime supervision":30,
}

DURATION_OPTIONS = [0,5,10,15,20,30,45,60,75,90,120,150,180,240,300,360,420,480,540,600]
TIME_OPTIONS = [""] + [f"{h:02d}:{m:02d}" for h in range(24) for m in (0,15,30,45)]
DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
MEAL_TYPES = ["Breakfast","Lunch","Dinner"]

def init_state():
    today = date.today()
    defaults = {
        "week_start": today - timedelta(days=today.weekday()),
        "schedule": {},
        "sleep_target": 480,
        "selfcare_target": 45,
        "unplanned_target": 60,
        "timezone": "America/Los_Angeles",
        "food_lookup": [
            "Oatmeal","Eggs","Cereal","Pancakes","Yogurt & fruit","Sandwiches",
            "Leftovers","Pasta","Rice & chicken","Rice & beans","Tacos","Soup & bread",
            "Pizza","Chicken & vegetables","Fish & rice","Stew","Salad & protein"
        ],
        "meal_ingredients": {
            "Oatmeal":["Oatmeal","Milk","Bananas"],
            "Eggs":["Eggs","Bread"],
            "Cereal":["Cereal","Milk"],
            "Pancakes":["Pancake mix","Eggs","Milk"],
            "Yogurt & fruit":["Yogurt","Fruit"],
            "Sandwiches":["Bread","Lunch meat","Cheese"],
            "Pasta":["Pasta","Pasta sauce","Vegetables"],
            "Rice & chicken":["Rice","Chicken","Vegetables"],
            "Rice & beans":["Rice","Beans","Vegetables"],
            "Tacos":["Tortillas","Ground turkey / beef","Cheese","Lettuce"],
            "Soup & bread":["Soup ingredients","Bread"],
            "Pizza":["Pizza"],
            "Chicken & vegetables":["Chicken","Vegetables"],
            "Fish & rice":["Fish","Rice","Vegetables"],
            "Stew":["Stew meat / beans","Vegetables"],
            "Salad & protein":["Salad greens","Vegetables","Protein"],
        },
        "meal_plan": {},
        "grocery_categories": [
            "Produce","Dairy","Meat / Protein","Bread / Bakery","Pantry","Frozen",
            "Breakfast","Lunch Items","Snacks","Beverages","Toddler","Household",
            "Cleaning","Toiletries","Meal Ingredients","Other"
        ],
        "grocery_master": [
            {"item":"Milk","category":"Dairy"},{"item":"Eggs","category":"Dairy"},
            {"item":"Bread","category":"Bread / Bakery"},{"item":"Bananas","category":"Produce"},
            {"item":"Apples","category":"Produce"},{"item":"Yogurt","category":"Dairy"},
            {"item":"Cheese","category":"Dairy"},{"item":"Chicken","category":"Meat / Protein"},
            {"item":"Rice","category":"Pantry"},{"item":"Pasta","category":"Pantry"},
            {"item":"Pasta sauce","category":"Pantry"},{"item":"Beans","category":"Pantry"},
            {"item":"Cereal","category":"Breakfast"},{"item":"Oatmeal","category":"Breakfast"},
            {"item":"Lunch meat","category":"Lunch Items"},{"item":"Tortillas","category":"Bread / Bakery"},
            {"item":"Vegetables","category":"Produce"},{"item":"Fruit","category":"Produce"},
            {"item":"Diapers","category":"Toddler"},{"item":"Wipes","category":"Toddler"},
            {"item":"Laundry detergent","category":"Cleaning"},
        ],
        "shopping_list": [],
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def hours_text(minutes):
    minutes = max(0, int(minutes))
    h,m = divmod(minutes,60)
    if h and m: return f"{h} hr {m} min"
    if h: return f"{h} hr"
    return f"{m} min"

def week_dates(monday):
    return [monday + timedelta(days=i) for i in range(7)]

def clean_category(c):
    for icon in ["🎒 ","👶 ","🧹 ","🍳 ","🧺 ","⛪ ","💛 ","👨‍👩‍👧‍👦 ","😴 "]:
        c = c.replace(icon,"")
    return c

def category_minutes(day_key):
    out={c:0 for c in CATEGORIES}
    entries=st.session_state.schedule.get(day_key,{})
    for cat,activities in CATEGORIES.items():
        for a in activities:
            item=entries.get(a)
            if item and item.get("selected"):
                out[cat]+=int(item.get("minutes",0))
    return out

def day_total(day_key):
    return sum(category_minutes(day_key).values())

def get_day_wellness(day_key):
    cats=category_minutes(day_key)
    sleep=cats.get("😴 Sleep",0)
    selfcare=cats.get("💛 Mom Self-Care",0)
    unplanned=max(0,1440-sum(cats.values()))
    return sleep,selfcare,unplanned

def make_backup():
    keys=["week_start","schedule","sleep_target","selfcare_target","unplanned_target",
          "timezone","food_lookup","meal_ingredients","meal_plan","grocery_categories",
          "grocery_master","shopping_list"]
    data={}
    for k in keys:
        v=st.session_state[k]
        data[k]=v.isoformat() if k=="week_start" else v
    return json.dumps(data,indent=2).encode()

def meal_for(day_key, meal):
    return st.session_state.meal_plan.get(day_key,{}).get(meal,"")

init_state()

# -------------------- Sidebar --------------------
with st.sidebar:
    st.header("⚙️ Targets & Settings")
    st.session_state.sleep_target = st.number_input(
        "Minimum Mom sleep per day (minutes)", 0, 720, int(st.session_state.sleep_target), 15
    )
    st.caption(f"Target: {hours_text(st.session_state.sleep_target)}")
    st.session_state.selfcare_target = st.number_input(
        "Minimum Mom self-care per day (minutes)", 0, 240, int(st.session_state.selfcare_target), 5
    )
    st.caption(f"Target: {hours_text(st.session_state.selfcare_target)}")
    st.session_state.unplanned_target = st.number_input(
        "Minimum breathing-room target (minutes)", 0, 240, int(st.session_state.unplanned_target), 5
    )
    st.session_state.timezone = st.text_input("Calendar timezone", st.session_state.timezone)
    st.divider()
    st.download_button("⬇️ Download planner backup", make_backup(), "mom_weekly_calendar_backup.json", "application/json")
    uploaded=st.file_uploader("Restore planner backup",type=["json"])
    if uploaded is not None:
        try:
            data=json.load(uploaded)
            if st.button("Restore backup"):
                for k,v in data.items():
                    if k=="week_start": v=date.fromisoformat(v)
                    st.session_state[k]=v
                st.success("Backup restored.")
                st.rerun()
        except Exception:
            st.error("Could not read that backup file.")

# -------------------- Header / Week --------------------
st.title("📅 Mom Weekly Calendar")
st.caption("A modern weekly family dashboard for routines, meals, groceries, wellness, family time, church, and Google Calendar.")

nav1,nav2,nav3=st.columns([1,2,1])
with nav1:
    if st.button("← Previous week"):
        st.session_state.week_start -= timedelta(days=7); st.rerun()
with nav2:
    chosen=st.date_input("Select any date in the week",value=st.session_state.week_start)
    monday=chosen-timedelta(days=chosen.weekday())
    if monday != st.session_state.week_start:
        st.session_state.week_start=monday; st.rerun()
with nav3:
    if st.button("Next week →"):
        st.session_state.week_start += timedelta(days=7); st.rerun()

dates=week_dates(st.session_state.week_start)
day_labels=[d.strftime("%A · %b %d") for d in dates]
default_idx=date.today().weekday() if date.today() in dates else 0

tabs=st.tabs([
    "📆 Weekly Calendar","🍽️ Meal Plan","🛒 Groceries","💛 Wellness Targets",
    "📊 Weekly Balance","🗓️ Google Calendar","⚙️ Lookups"
])

# -------------------- Weekly Calendar --------------------
with tabs[0]:
    selected_label=st.selectbox("Choose day",day_labels,index=default_idx,key="calendar_day")
    selected_date=dates[day_labels.index(selected_label)]
    day_key=selected_date.isoformat()
    st.session_state.schedule.setdefault(day_key,{})

    st.markdown(
        f'<div class="day-banner"><div class="muted">Selected day</div>'
        f'<div style="font-size:1.55rem;font-weight:800;">{selected_date.strftime("%A, %B %d, %Y")}</div></div>',
        unsafe_allow_html=True
    )

    meals=st.session_state.meal_plan.get(day_key,{})
    if any(meals.get(x) for x in MEAL_TYPES):
        st.info(
            f"🍳 Breakfast: **{meals.get('Breakfast','—') or '—'}**  ·  "
            f"🥪 Lunch: **{meals.get('Lunch','—') or '—'}**  ·  "
            f"🍽️ Dinner: **{meals.get('Dinner','—') or '—'}**"
        )

    st.caption("Expand a category, select activities, set duration, and optionally choose a start time for Google Calendar sync.")

    category_totals={}
    total=0
    for category,activities in CATEGORIES.items():
        cat_total=0
        with st.expander(category, expanded=category in ["🎒 Kids / School","👶 Toddler"]):
            b1,b2,b3=st.columns([1.1,1.1,4.8])
            if b1.button("Select all",key=f"all_{day_key}_{category}"):
                for idx,a in enumerate(activities):
                    item=st.session_state.schedule[day_key].get(a,{"minutes":DEFAULT_MINUTES.get(a,30),"start":""})
                    item["selected"]=True
                    st.session_state.schedule[day_key][a]=item
                    st.session_state[f"sel_{day_key}_{category}_{idx}"]=True
                st.rerun()
            if b2.button("Clear all",key=f"clear_{day_key}_{category}"):
                for idx,a in enumerate(activities):
                    item=st.session_state.schedule[day_key].get(a,{"minutes":DEFAULT_MINUTES.get(a,30),"start":""})
                    item["selected"]=False
                    st.session_state.schedule[day_key][a]=item
                    st.session_state[f"sel_{day_key}_{category}_{idx}"]=False
                st.rerun()
            b3.caption("Start time is optional; it is only needed if you want to push the activity to Google Calendar.")

            for idx,a in enumerate(activities):
                item=st.session_state.schedule[day_key].get(
                    a, {"selected":False,"minutes":DEFAULT_MINUTES.get(a,30),"start":"","google_event_id":None}
                )
                cols=st.columns([.55,4.1,1.8,1.8])
                sel=cols[0].checkbox("",value=item.get("selected",False),key=f"sel_{day_key}_{category}_{idx}")
                cols[1].write(f"**{a}**")
                mins=item.get("minutes",DEFAULT_MINUTES.get(a,30))
                opts=DURATION_OPTIONS if mins in DURATION_OPTIONS else sorted(set(DURATION_OPTIONS+[mins]))
                dur=cols[2].selectbox(
                    "Duration",opts,index=opts.index(mins),format_func=hours_text,
                    key=f"dur_{day_key}_{category}_{idx}",label_visibility="collapsed"
                )
                current_start=item.get("start","")
                if current_start not in TIME_OPTIONS: current_start=""
                start=cols[3].selectbox(
                    "Start",TIME_OPTIONS,index=TIME_OPTIONS.index(current_start),
                    key=f"start_{day_key}_{category}_{idx}",label_visibility="collapsed"
                )
                st.session_state.schedule[day_key][a]={
                    "selected":sel,"minutes":int(dur),"start":start,
                    "google_event_id":item.get("google_event_id")
                }
                if sel: cat_total += int(dur)

            st.markdown(f"**Category total · {hours_text(cat_total)}**")
        category_totals[category]=cat_total
        total+=cat_total

    unplanned=max(0,1440-total)
    sleep=category_totals.get("😴 Sleep",0)
    selfcare=category_totals.get("💛 Mom Self-Care",0)

    st.header("📊 Daily overview")
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Planned time",hours_text(total))
    m2.metric("Unplanned time",hours_text(unplanned))
    m3.metric("Mom sleep",hours_text(sleep),delta=f"{sleep-st.session_state.sleep_target:+} min vs target")
    m4.metric("Mom self-care",hours_text(selfcare),delta=f"{selfcare-st.session_state.selfcare_target:+} min vs target")

    chart_rows=[{"Category":clean_category(c),"Hours":round(v/60,2)} for c,v in category_totals.items()]
    st.subheader("Hours by category")
    st.bar_chart(pd.DataFrame(chart_rows).set_index("Category"),y="Hours",horizontal=True)
    label_cols=st.columns(3)
    for i,row in enumerate(chart_rows):
        with label_cols[i%3]:
            st.metric(row["Category"],f'{row["Hours"]:.2f} hr')

    if total>1440:
        st.error(f"🔴 Overbooked by {hours_text(total-1440)}.")
    elif sleep<st.session_state.sleep_target:
        st.warning(f"😴 Sleep is below target by {hours_text(st.session_state.sleep_target-sleep)}.")
    elif selfcare<st.session_state.selfcare_target:
        st.warning(f"💛 Self-care is below target by {hours_text(st.session_state.selfcare_target-selfcare)}.")
    elif unplanned<st.session_state.unplanned_target:
        st.warning(f"🟡 Breathing room is below target by {hours_text(st.session_state.unplanned_target-unplanned)}.")
    else:
        st.success("🟢 This day meets the current sleep, self-care, and breathing-room targets.")

# -------------------- Meal Plan --------------------
with tabs[1]:
    st.header("🍽️ Weekly Meal Plan")
    st.write("Build a reusable food lookup once, then choose breakfast, lunch, and dinner for each day.")

    for d in dates:
        dk=d.isoformat()
        st.session_state.meal_plan.setdefault(dk,{})
        with st.expander(d.strftime("%A, %B %d"),expanded=d==date.today()):
            cols=st.columns(3)
            for i,meal in enumerate(MEAL_TYPES):
                current=st.session_state.meal_plan[dk].get(meal,"")
                options=[""]+sorted(st.session_state.food_lookup)
                if current and current not in options: options.append(current)
                choice=cols[i].selectbox(
                    meal,options,index=options.index(current) if current in options else 0,
                    key=f"meal_{dk}_{meal}"
                )
                st.session_state.meal_plan[dk][meal]=choice

    st.subheader("Weekly meal snapshot")
    rows=[]
    for d in dates:
        dk=d.isoformat()
        rows.append({
            "Day":d.strftime("%A"),
            "Breakfast":meal_for(dk,"Breakfast") or "—",
            "Lunch":meal_for(dk,"Lunch") or "—",
            "Dinner":meal_for(dk,"Dinner") or "—",
        })
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)

# -------------------- Groceries --------------------
with tabs[2]:
    st.header("🛒 Grocery List")
    st.write("Build the list from reusable grocery items or add ingredients from this week's meal plan.")

    g1,g2,g3=st.columns([2,2,1])
    categories=st.session_state.grocery_categories
    master_items=sorted([x["item"] for x in st.session_state.grocery_master])
    pick=g1.selectbox("Item",[""]+master_items,key="shop_pick")
    cat_default=next((x["category"] for x in st.session_state.grocery_master if x["item"]==pick),"Other")
    cat=g2.selectbox("Category",categories,index=categories.index(cat_default) if cat_default in categories else len(categories)-1,key="shop_cat")
    qty=g3.text_input("Qty",key="shop_qty",placeholder="2")
    if st.button("➕ Add item"):
        if pick:
            st.session_state.shopping_list.append({"item":pick,"category":cat,"qty":qty,"done":False})
            st.rerun()

    # Meal ingredient suggestions
    used_meals=set()
    for d in dates:
        for meal in MEAL_TYPES:
            val=meal_for(d.isoformat(),meal)
            if val: used_meals.add(val)
    suggested=[]
    for meal in used_meals:
        suggested.extend(st.session_state.meal_ingredients.get(meal,[]))
    suggested=sorted(set(suggested))

    with st.expander("🍽️ Suggested ingredients from this week's meal plan",expanded=True):
        if suggested:
            st.write(", ".join(suggested))
            if st.button("Add suggested ingredients to grocery list"):
                existing={x["item"].lower() for x in st.session_state.shopping_list}
                master_map={x["item"].lower():x["category"] for x in st.session_state.grocery_master}
                for item in suggested:
                    if item.lower() not in existing:
                        st.session_state.shopping_list.append({
                            "item":item,
                            "category":master_map.get(item.lower(),"Meal Ingredients"),
                            "qty":"",
                            "done":False
                        })
                st.rerun()
        else:
            st.caption("Choose meals in the Meal Plan tab to generate ingredient suggestions.")

    grouped={}
    for item in st.session_state.shopping_list:
        grouped.setdefault(item["category"],[]).append(item)
    for category,items in grouped.items():
        st.subheader(category)
        for idx,item in enumerate(list(items)):
            c1,c2=st.columns([5,1])
            label=item["item"]+(f" — {item['qty']}" if item.get("qty") else "")
            item["done"]=c1.checkbox(label,value=item.get("done",False),key=f"grocery_{category}_{idx}_{item['item']}")
            if c2.button("Remove",key=f"remove_{category}_{idx}_{item['item']}"):
                st.session_state.shopping_list.remove(item); st.rerun()

# -------------------- Wellness --------------------
with tabs[3]:
    st.header("💛 Wellness Targets")
    st.write("These minimums drive the daily warnings and weekly balance score.")
    w1,w2,w3=st.columns(3)
    w1.metric("Sleep target",hours_text(st.session_state.sleep_target))
    w2.metric("Self-care target",hours_text(st.session_state.selfcare_target))
    w3.metric("Breathing-room target",hours_text(st.session_state.unplanned_target))

    rows=[]
    for d in dates:
        sleep,selfcare,unplanned=get_day_wellness(d.isoformat())
        rows.append({
            "Day":d.strftime("%A"),
            "Sleep":hours_text(sleep),
            "Sleep target":"✅" if sleep>=st.session_state.sleep_target else "⚠️",
            "Self-care":hours_text(selfcare),
            "Self-care target":"✅" if selfcare>=st.session_state.selfcare_target else "⚠️",
            "Unplanned":hours_text(unplanned),
            "Breathing room":"✅" if unplanned>=st.session_state.unplanned_target else "⚠️",
        })
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)

# -------------------- Weekly Balance --------------------
with tabs[4]:
    st.header("📊 Weekly Balance")
    sleep_days=selfcare_days=room_days=0
    total_unplanned=0
    overloaded=[]
    balance_rows=[]

    for d in dates:
        dk=d.isoformat()
        total=day_total(dk)
        sleep,selfcare,unplanned=get_day_wellness(dk)
        sleep_ok=sleep>=st.session_state.sleep_target
        self_ok=selfcare>=st.session_state.selfcare_target
        room_ok=unplanned>=st.session_state.unplanned_target
        sleep_days+=int(sleep_ok); selfcare_days+=int(self_ok); room_days+=int(room_ok)
        total_unplanned+=unplanned
        if total>1440: overloaded.append(d.strftime("%A"))
        balance_rows.append({
            "Day":d.strftime("%A"),
            "Planned hours":round(total/60,2),
            "Unplanned hours":round(unplanned/60,2),
            "Sleep target":1 if sleep_ok else 0,
            "Self-care target":1 if self_ok else 0,
        })

    score=round(((sleep_days+selfcare_days+room_days)/(7*3))*100) if dates else 0
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Weekly balance score",f"{score}%")
    c2.metric("Sleep target met",f"{sleep_days}/7 days")
    c3.metric("Self-care target met",f"{selfcare_days}/7 days")
    c4.metric("Unplanned time",hours_text(total_unplanned))

    if overloaded:
        st.error("Overloaded days: "+", ".join(overloaded))
    elif score>=85:
        st.success("Strong weekly balance. Most wellness targets are protected.")
    elif score>=65:
        st.warning("Moderate balance. Look for one or two days where rest or breathing room can be protected.")
    else:
        st.warning("This week is heavily loaded. Consider moving errands, simplifying meals, delegating chores, or protecting sleep/self-care blocks.")

    st.subheader("Planned vs unplanned hours by day")
    balance_df=pd.DataFrame(balance_rows)
    st.bar_chart(balance_df.set_index("Day")[["Planned hours","Unplanned hours"]])

# -------------------- Google Calendar --------------------
with tabs[5]:
    st.header("🗓️ Google Calendar")
    st.write("Optional integration. The planner still works normally if Google Calendar is not connected.")
    st.info("Google requires OAuth credentials. Keep the client secret in Streamlit Secrets — never commit it to GitHub.")

    SCOPES=["https://www.googleapis.com/auth/calendar.events","https://www.googleapis.com/auth/calendar.readonly"]

    def google_config():
        try:
            cfg=st.secrets["google_oauth"]
            return {
                "web":{
                    "client_id":cfg["client_id"],
                    "client_secret":cfg["client_secret"],
                    "auth_uri":"https://accounts.google.com/o/oauth2/auth",
                    "token_uri":"https://oauth2.googleapis.com/token",
                    "redirect_uris":[cfg["redirect_uri"]],
                }
            }, cfg["redirect_uri"]
        except Exception:
            return None,None

    config,redirect_uri=google_config()
    if not config:
        st.warning("Google Calendar is not configured yet.")
        with st.expander("Setup instructions"):
            st.markdown("""
1. In Google Cloud, enable the **Google Calendar API**.
2. Create an **OAuth 2.0 Web application** client.
3. Add your Streamlit app URL as an authorized redirect URI.
4. In Streamlit Community Cloud → **App settings → Secrets**, add:

```toml
[google_oauth]
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
redirect_uri = "https://YOUR-APP.streamlit.app/"
```

5. Reboot the Streamlit app.

Do **not** put the client secret in GitHub.
""")
    else:
        try:
            from google_auth_oauthlib.flow import Flow
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            if "google_credentials" not in st.session_state:
                st.session_state.google_credentials=None

            # Handle OAuth callback
            code=st.query_params.get("code")
            if code and not st.session_state.google_credentials:
                flow=Flow.from_client_config(config,scopes=SCOPES,state=st.session_state.get("google_state"))
                flow.redirect_uri=redirect_uri
                flow.fetch_token(code=code)
                creds=flow.credentials
                st.session_state.google_credentials={
                    "token":creds.token,"refresh_token":creds.refresh_token,
                    "token_uri":creds.token_uri,"client_id":creds.client_id,
                    "client_secret":creds.client_secret,"scopes":creds.scopes
                }
                st.query_params.clear()
                st.rerun()

            if not st.session_state.google_credentials:
                flow=Flow.from_client_config(config,scopes=SCOPES)
                flow.redirect_uri=redirect_uri
                auth_url,state=flow.authorization_url(access_type="offline",include_granted_scopes="true",prompt="consent")
                st.session_state.google_state=state
                st.link_button("Connect Google Calendar",auth_url,type="primary")
            else:
                c=st.session_state.google_credentials
                creds=Credentials(
                    token=c["token"],refresh_token=c["refresh_token"],token_uri=c["token_uri"],
                    client_id=c["client_id"],client_secret=c["client_secret"],scopes=c["scopes"]
                )
                service=build("calendar","v3",credentials=creds)
                st.success("Google Calendar connected for this session.")

                if st.button("Disconnect Google Calendar"):
                    st.session_state.google_credentials=None
                    st.rerun()

                # Show calendar events this week
                tz=ZoneInfo(st.session_state.timezone)
                start_dt=datetime.combine(dates[0],time.min,tzinfo=tz)
                end_dt=datetime.combine(dates[-1]+timedelta(days=1),time.min,tzinfo=tz)
                if st.button("Refresh this week's Google Calendar events"):
                    result=service.events().list(
                        calendarId="primary",
                        timeMin=start_dt.isoformat(),
                        timeMax=end_dt.isoformat(),
                        singleEvents=True,
                        orderBy="startTime"
                    ).execute()
                    st.session_state.google_week_events=result.get("items",[])

                if st.session_state.get("google_week_events"):
                    rows=[]
                    for e in st.session_state.google_week_events:
                        start=e.get("start",{}).get("dateTime") or e.get("start",{}).get("date","")
                        rows.append({"Start":start,"Event":e.get("summary","(No title)")})
                    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)

                st.subheader("Push planner activities to Google Calendar")
                sync_day=st.selectbox("Day to sync",[d.strftime("%A, %b %d") for d in dates],key="sync_day")
                sync_date=dates[[d.strftime("%A, %b %d") for d in dates].index(sync_day)]
                dk=sync_date.isoformat()
                entries=st.session_state.schedule.get(dk,{})
                syncable=[]
                for cat,acts in CATEGORIES.items():
                    for a in acts:
                        item=entries.get(a)
                        if item and item.get("selected") and item.get("start"):
                            syncable.append((a,item))
                if syncable:
                    choices=st.multiselect("Choose activities", [x[0] for x in syncable], default=[x[0] for x in syncable])
                    if st.button("Add selected activities to Google Calendar",type="primary"):
                        created=0
                        for a,item in syncable:
                            if a not in choices: continue
                            hh,mm=map(int,item["start"].split(":"))
                            start=datetime.combine(sync_date,time(hh,mm),tzinfo=tz)
                            end=start+timedelta(minutes=int(item["minutes"]))
                            body={
                                "summary":a,
                                "description":"Created from Mom Weekly Calendar",
                                "start":{"dateTime":start.isoformat(),"timeZone":st.session_state.timezone},
                                "end":{"dateTime":end.isoformat(),"timeZone":st.session_state.timezone},
                            }
                            service.events().insert(calendarId="primary",body=body).execute()
                            created+=1
                        st.success(f"Added {created} activities to Google Calendar.")
                else:
                    st.caption("Select activities in Weekly Calendar and give them start times before syncing.")

        except Exception as e:
            st.error("Google Calendar connection could not be completed.")
            st.caption(str(e))

# -------------------- Lookups --------------------
with tabs[6]:
    st.header("⚙️ Lookup Tables")

    with st.expander("🍽️ Food / meal lookup",expanded=True):
        f1,f2=st.columns([2,3])
        new_food=f1.text_input("New meal / food",key="new_food")
        ingredients=f2.text_input("Ingredients (comma separated)",key="new_food_ingredients")
        if st.button("Add food lookup value"):
            if new_food.strip() and new_food.strip() not in st.session_state.food_lookup:
                st.session_state.food_lookup.append(new_food.strip())
                st.session_state.meal_ingredients[new_food.strip()]=[x.strip() for x in ingredients.split(",") if x.strip()]
                st.rerun()

        selected_food=st.selectbox("Review / edit meal ingredients",sorted(st.session_state.food_lookup),key="edit_food")
        existing=", ".join(st.session_state.meal_ingredients.get(selected_food,[]))
        edited=st.text_input("Ingredients",value=existing,key="edit_ingredients")
        if st.button("Save ingredients"):
            st.session_state.meal_ingredients[selected_food]=[x.strip() for x in edited.split(",") if x.strip()]
            st.success("Ingredients updated.")

    with st.expander("🛒 Grocery master lookup"):
        g1,g2=st.columns(2)
        item=g1.text_input("New grocery item",key="new_grocery_master")
        category=g2.selectbox("Category",st.session_state.grocery_categories,key="new_grocery_category")
        if st.button("Add grocery lookup value"):
            if item.strip() and item.strip().lower() not in {x["item"].lower() for x in st.session_state.grocery_master}:
                st.session_state.grocery_master.append({"item":item.strip(),"category":category})
                st.rerun()

        st.dataframe(pd.DataFrame(st.session_state.grocery_master).sort_values(["category","item"]),hide_index=True,use_container_width=True)

st.divider()
st.caption("Time totals are planning estimates. Some family activities overlap naturally, so use the metrics as a workload guide rather than a stopwatch.")
