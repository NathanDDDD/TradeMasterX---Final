# TradeMasterX 2.0 - Desktop GUI Application

## 🖥️ Requirements

```bash
pip install streamlit
pip install pandas
pip install plotly
pip install asyncio
pip install aiohttp
```

##  Launch Application

```bash
streamlit run app.py
```

## 📁 Structure

- `app.py` - Main Streamlit application
- `components/` - UI components
- `utils/` - Utility functions
- `assets/` - Static assets

## 🎯 Features

1. **System Control Panel**
   - Start/Stop TradeMasterX
   - Dashboard launcher

2. **AI Command Chat**
   - Natural language interface
   - Claude/OpenAI integration

3. **System Status Dashboard**
   - Real-time metrics
   - Health monitoring

4. **Trade History**
   - Recent trades
   - Performance analytics

## 🔑 API Configuration

The app will prompt for API keys on first use:
- OpenAI API Key
- Claude API Key (Anthropic)

Configuration is stored securely in `.streamlit/secrets.toml`
