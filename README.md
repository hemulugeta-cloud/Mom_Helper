# Mom of 5 Family Command Center v2

This version is designed specifically for:
- Four children who attend school
- One 2-year-old who stays home with Mom

## New in this version
- Toddler-at-home routine and toddler time included in planning
- Dedicated night-before checklist for all school children
- Child-name lookup values used across the app
- Selectable date and time controls for calendar entries
- Food master lookup list
- Meal-plan dropdowns using the food lookup
- Grocery category master list
- Grocery item lookup master list
- Grocery shopping list built from dropdowns
- Rest-time and overload metrics
- JSON backup / restore

## GitHub
Upload:
- app.py
- requirements.txt
- README.md
- .gitignore

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Persistence
Streamlit Community Cloud does not guarantee permanent local storage. Use the built-in JSON backup download/restore periodically.

## Added in v3
- Mom Care reusable lookup list
- Selectable self-care start/end times
- Automatic Mom-care duration in minutes and hours
- Dedicated Time Calculator tab
- Start/end time selection with total minutes, decimal hours, and hours + minutes
- Cross-midnight calculation support
