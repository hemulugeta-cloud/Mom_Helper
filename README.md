# Mom Weekly Calendar — Full Upgrade

A professional Streamlit family planning dashboard for a mom managing five children, including a 2-year-old at home.

## Included
- Weekly calendar with selectable days
- Expandable/collapsible categories
- Select All / Clear All
- Duration and optional start time for each activity
- Category charts with labeled hours
- Planned and unplanned time
- Minimum daily Mom sleep target
- Minimum daily Mom self-care target
- Minimum breathing-room target
- Daily wellness warnings
- Weekly Balance Score
- Days sleep/self-care targets were met
- Overloaded-day detection
- Weekly meal-plan tab
- Reusable food lookup
- Breakfast/lunch/dinner dropdowns for every day
- Meal-to-grocery ingredient suggestions
- Grocery master lookup
- Shopping list grouped by category
- Google Calendar OAuth integration (optional)
- View current week's Google Calendar events
- Push planner activities with start times to Google Calendar
- JSON backup/restore
- Professional modern styling

## Google Calendar setup
The app works without Google Calendar.

To enable integration:
1. Enable Google Calendar API in Google Cloud.
2. Create OAuth 2.0 credentials for a Web application.
3. Add your Streamlit app URL as an authorized redirect URI.
4. Add this to Streamlit Secrets:

```toml
[google_oauth]
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
redirect_uri = "https://YOUR-APP.streamlit.app/"
```

Never commit OAuth secrets to GitHub.

## Deploy
Upload:
- `app.py`
- `requirements.txt`
- `README.md`
- `.gitignore`

Deploy `app.py` through Streamlit Community Cloud.
