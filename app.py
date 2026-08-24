import streamlit as st
from datetime import date, timedelta

st.set_page_config(page_title="Mom Weekly Calendar", page_icon="📅", layout="wide")

def init_state():
    if "week_start" not in st.session_state:
        today = date.today()
        st.session_state.week_start = today - timedelta(days=today.weekday())
    if "schedule" not in st.session_state:
        st.session_state.schedule = {}

def hours_text(minutes):
    minutes = int(minutes)
    h, m = divmod(minutes, 60)
    if h and m:
        return f"{h} hr {m} min"
    if h:
        return f"{h} hr"
    return f"{m} min"

def week_dates(monday):
    return [monday + timedelta(days=i) for i in range(7)]

init_state()

DURATION_OPTIONS = [0,5,10,15,20,30,45,60,75,90,120,150,180,240,300,360,420,480]

CATEGORIES = {
    "🎒 Kids / School": [
        "Wake school kids",
        "Get kids dressed / uniforms",
        "Breakfast",
        "Pack / check lunches & backpacks",
        "School drop-off",
        "School pickup",
        "After-school snack / decompress",
        "Homework / reading",
        "Dinner with kids",
        "Bath / showers",
        "Bedtime routine",
    ],
    "👶 Toddler": [
        "Toddler morning routine",
        "Toddler breakfast",
        "Toddler play / reading",
        "Toddler snack",
        "Toddler outdoor / movement time",
        "Toddler lunch",
        "Toddler nap / quiet time",
        "Toddler afternoon play",
        "Toddler bath",
        "Toddler bedtime routine",
    ],
    "🧹 Cleaning": [
        "Morning kitchen reset",
        "General house cleaning",
        "Bathroom cleaning",
        "Bedroom pickup",
        "Living room pickup",
        "Floor sweeping / vacuuming",
        "Mopping",
        "Dinner cleanup",
        "Night-before home reset",
    ],
    "🍳 Cooking": [
        "Breakfast prep",
        "Lunch prep",
        "Meal planning",
        "Meal prep",
        "Cooking dinner",
        "Pack school lunches",
        "Prepare snacks",
        "Batch cooking / freezer prep",
        "Grocery shopping / food errands",
    ],
    "🧺 Laundry": [
        "Sort laundry",
        "Wash clothes",
        "Dry clothes",
        "Fold clothes",
        "Put clothes away",
        "School uniform laundry",
        "Bedding / towels",
    ],
    "⛪ Church": [
        "Church worship",
        "Church class",
        "Kids church / Sunday school",
        "Prayer / devotional time",
        "Church event / fellowship",
        "Travel to / from church",
    ],
    "💛 Mom Self-Care": [
        "Drink water / hydration break",
        "Eat a nourishing meal",
        "Quiet rest",
        "Nap",
        "Reading",
        "School / study time",
        "Prayer / meditation",
        "Walk / exercise",
        "Stretching",
        "Shower / personal care",
        "Tea / coffee break",
        "Listen to music / podcast",
        "Call / talk with supportive person",
        "Skincare / hair care",
        "Go to bed earlier",
        "Do nothing / mental break",
    ],
    "👨‍👩‍👧‍👦 Family Time": [
        "Eat dinner together",
        "Watch TV / movie together",
        "Go to the park",
        "Go out to eat",
        "Play games in the house",
        "Read together",
        "Family conversation",
        "Walk together",
        "Outdoor family activity",
        "Visit family / friends",
        "Go to church together",
        "Family outing / activity",
    ],
    "😴 Sleep": [
        "Mom sleep",
        "Kids bedtime supervision",
        "Toddler sleep / bedtime supervision",
    ],
}

DEFAULT_MINUTES = {
    "Wake school kids":15,
    "Get kids dressed / uniforms":30,
    "Breakfast":30,
    "Pack / check lunches & backpacks":20,
    "School drop-off":45,
    "School pickup":45,
    "After-school snack / decompress":30,
    "Homework / reading":60,
    "Dinner with kids":45,
    "Bath / showers":45,
    "Bedtime routine":45,

    "Toddler morning routine":30,
    "Toddler breakfast":30,
    "Toddler play / reading":45,
    "Toddler snack":15,
    "Toddler outdoor / movement time":30,
    "Toddler lunch":30,
    "Toddler nap / quiet time":90,
    "Toddler afternoon play":45,
    "Toddler bath":30,
    "Toddler bedtime routine":30,

    "Morning kitchen reset":20,
    "General house cleaning":60,
    "Bathroom cleaning":30,
    "Bedroom pickup":30,
    "Living room pickup":20,
    "Floor sweeping / vacuuming":30,
    "Mopping":30,
    "Dinner cleanup":30,
    "Night-before home reset":20,

    "Breakfast prep":20,
    "Lunch prep":30,
    "Meal planning":20,
    "Meal prep":30,
    "Cooking dinner":60,
    "Pack school lunches":30,
    "Prepare snacks":15,
    "Batch cooking / freezer prep":90,
    "Grocery shopping / food errands":90,

    "Sort laundry":15,
    "Wash clothes":45,
    "Dry clothes":45,
    "Fold clothes":45,
    "Put clothes away":30,
    "School uniform laundry":60,
    "Bedding / towels":60,

    "Church worship":120,
    "Church class":60,
    "Kids church / Sunday school":60,
    "Prayer / devotional time":20,
    "Church event / fellowship":90,
    "Travel to / from church":45,

    "Drink water / hydration break":5,
    "Eat a nourishing meal":30,
    "Quiet rest":20,
    "Nap":30,
    "Reading":30,
    "School / study time":60,
    "Prayer / meditation":20,
    "Walk / exercise":30,
    "Stretching":15,
    "Shower / personal care":20,
    "Tea / coffee break":15,
    "Listen to music / podcast":20,
    "Call / talk with supportive person":20,
    "Skincare / hair care":20,
    "Go to bed earlier":60,
    "Do nothing / mental break":15,

    "Eat dinner together":45,
    "Watch TV / movie together":90,
    "Go to the park":60,
    "Go out to eat":90,
    "Play games in the house":45,
    "Read together":30,
    "Family conversation":20,
    "Walk together":30,
    "Outdoor family activity":60,
    "Visit family / friends":120,
    "Go to church together":120,
    "Family outing / activity":120,

    "Mom sleep":480,
    "Kids bedtime supervision":45,
    "Toddler sleep / bedtime supervision":30,
}

st.title("📅 Mom Weekly Calendar")
st.caption("For a family with five children ages 2–12, with the 2-year-old staying home with Mom.")

c1,c2,c3 = st.columns([1,2,1])
with c1:
    if st.button("← Previous Week"):
        st.session_state.week_start -= timedelta(days=7)
        st.rerun()

with c2:
    chosen_week = st.date_input(
        "Select any date in the week",
        value=st.session_state.week_start,
        key="week_picker"
    )
    monday = chosen_week - timedelta(days=chosen_week.weekday())
    if monday != st.session_state.week_start:
        st.session_state.week_start = monday
        st.rerun()

with c3:
    if st.button("Next Week →"):
        st.session_state.week_start += timedelta(days=7)
        st.rerun()

dates = week_dates(st.session_state.week_start)
day_labels = [d.strftime("%A %b %d") for d in dates]

if st.session_state.week_start <= date.today() <= st.session_state.week_start + timedelta(days=6):
    default_idx = date.today().weekday()
else:
    default_idx = 0

selected_label = st.selectbox("Select day to plan",day_labels,index=default_idx)
selected_date = dates[day_labels.index(selected_label)]
day_key = selected_date.isoformat()

st.markdown(f"## {selected_date.strftime('%A, %B %d, %Y')}")

if day_key not in st.session_state.schedule:
    st.session_state.schedule[day_key] = {}

category_totals = {}
day_total = 0

st.info("Expand only the categories you want to plan. Check the activities Mom will do that day and choose the estimated time beside each activity.")

for category, activities in CATEGORIES.items():
    cat_total = 0

    with st.expander(category, expanded=(category in ["🎒 Kids / School","👶 Toddler"])):
        st.caption("Select activities and estimated duration.")

        for idx, activity in enumerate(activities):
            row = st.columns([0.6,4.8,2.2])
            key_base = f"{day_key}_{category}_{idx}"

            existing = st.session_state.schedule[day_key].get(
                activity,
                {"selected":False,"minutes":DEFAULT_MINUTES.get(activity,30)}
            )

            with row[0]:
                selected = st.checkbox(
                    "",
                    value=existing["selected"],
                    key=f"{key_base}_selected"
                )

            with row[1]:
                st.write(f"**{activity}**")

            with row[2]:
                default_mins = existing["minutes"]
                opts = DURATION_OPTIONS if default_mins in DURATION_OPTIONS else sorted(set(DURATION_OPTIONS+[default_mins]))
                duration = st.selectbox(
                    "Duration",
                    opts,
                    index=opts.index(default_mins),
                    format_func=hours_text,
                    key=f"{key_base}_duration",
                    label_visibility="collapsed"
                )

            st.session_state.schedule[day_key][activity] = {
                "selected":selected,
                "minutes":int(duration)
            }

            if selected:
                cat_total += int(duration)

        st.markdown(f"**Category total: {hours_text(cat_total)}**")

    category_totals[category] = cat_total
    day_total += cat_total

st.header("📊 Daily Time Summary")

m1,m2,m3 = st.columns(3)
m1.metric("Total planned time",hours_text(day_total))
m2.metric("Total minutes",f"{day_total} min")
m3.metric("Total hours",f"{day_total/60:.1f} hr")

st.subheader("Time spent by category")
cols = st.columns(4)
for i,(category,total) in enumerate(category_totals.items()):
    with cols[i % 4]:
        st.metric(category, hours_text(total))

if day_total > 1440:
    st.error(f"🔴 This plan exceeds 24 hours by {hours_text(day_total-1440)}.")
elif day_total > 1200:
    st.warning("🟠 Very full day. More than 20 hours are assigned.")
elif day_total > 960:
    st.warning("🟡 Full day. Check Mom's rest, sleep, and breathing room.")
else:
    st.success("🟢 The selected activities leave some room for transitions, interruptions, and rest.")

st.header("📈 Weekly Summary")
weekly_category = {cat:0 for cat in CATEGORIES}
weekly_total = 0

for d in dates:
    dk=d.isoformat()
    entries=st.session_state.schedule.get(dk,{})
    for category,activities in CATEGORIES.items():
        for activity in activities:
            item=entries.get(activity)
            if item and item.get("selected"):
                mins=int(item.get("minutes",0))
                weekly_category[category]+=mins
                weekly_total+=mins

st.metric("Total selected time this week",hours_text(weekly_total))

week_cols=st.columns(4)
for i,(category,total) in enumerate(weekly_category.items()):
    with week_cols[i % 4]:
        st.metric(category,hours_text(total))

st.subheader("Daily totals for the selected week")
for d in dates:
    dk=d.isoformat()
    total=0
    entries=st.session_state.schedule.get(dk,{})
    for category,activities in CATEGORIES.items():
        for activity in activities:
            item=entries.get(activity)
            if item and item.get("selected"):
                total += int(item.get("minutes",0))
    st.write(f"**{d.strftime('%A')}** — {hours_text(total)}")

st.divider()
st.caption("Only selected activities count toward the daily and weekly metrics. Each category can be expanded or collapsed.")
