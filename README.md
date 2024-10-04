# TimeInsights Dashboard

## How to run
1. Start API server
```
uvicorn api:app --host localhost --port 8000
```
2. Start Streamlit on port 8501
```
streamlit run main.py --server.port 8501
```
3. Redirect port 8501 to 80 (HTTP)
```!
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8501
sudo iptables -t nat -A OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 8501
```
## How to use
![image](https://github.com/user-attachments/assets/48bc3ec3-6898-43df-a31f-6447415d73e5)

1. Select an entire department or a specific employee.
2. Select the date range.
3. In Working Hours chart, select individual project and task to see how much time spent on it.
4. In Project Category Ratio, select different perspective to see the proportion of time.

![image](https://github.com/user-attachments/assets/e3992d15-8050-4977-9c8a-f8eaa0674b86)

5. In Task Insights, it can generate the summary base on the selected task and its description.
6. Also, there is a summary of selected department or employee.
7. At the buttom of the page, there is an AI chat model which can answer any questions base on the timesheet data.
