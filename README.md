# Mom of 5 — Family Command Center

An upgraded Streamlit family planner for a mom managing five children.

## Major features
- Editable child profiles and school times
- Editable daily tasks and time estimates
- One-time appointments and events
- Homework tracking
- Meal planning
- Grocery list
- Age-appropriate chore guidance
- Weekly reset
- Busy Day Mode
- Mom self-care tracking
- Daily time-budget metrics
- Estimated free/rest time
- Rest target comparison
- Overbooking / overload warnings
- Daily utilization percentage
- Category-level time insights
- Suggestions for what to simplify when the day is overloaded
- JSON backup download and restore

## Important persistence note
Streamlit Community Cloud does not guarantee permanent local storage. This app therefore includes a JSON backup/restore feature. Download a family backup periodically and restore it if needed.

## GitHub deployment
Upload:
- app.py
- requirements.txt
- README.md
- .gitignore

Then deploy `app.py` with Streamlit Community Cloud.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
