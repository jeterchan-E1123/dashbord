# TimeInsights Dashboard

## How to run
1. Start API server
```
uvicorn api:app --host 0.0.0.0 --port 8000
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
