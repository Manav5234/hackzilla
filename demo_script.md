# TrafficAI Demo Script (2 minutes)

## Opening (15 seconds)

"India loses over $22 billion annually to traffic congestion. Millions of hours are wasted on roads every day — in Delhi, Mumbai, Bangalore, the problem is staggering. TrafficAI tackles this with real-time AI-powered congestion prediction."

## Demo Walkthrough

### 1. Traffic Prediction (30 seconds)

"Start with the prediction panel. Select a location — say Connaught Place — set vehicle count, weather, road type, and time. Hit 'Predict Congestion.' The XGBoost model instantly returns a congestion score out of 100, a risk label with color code, and the top three most congested zones in the area. This model was trained on 7070 data points across Indian cities and achieves 99.86% accuracy."

### 2. Live Heatmap (30 seconds)

"The heatmap shows 16 monitored locations across Delhi-NCR, Mumbai, Bangalore, Chennai, and Kolkata. Each marker is color-coded: green for low, yellow for medium, red for high congestion. Click any marker for real-time traffic volume, average speed, and congestion intensity. The map uses OpenStreetMap tiles and Leaflet heat layers for a live traffic feel."

### 3. Route Comparator (30 seconds)

"Pick an origin and destination. The system queries OSRM — Open Source Routing Machine — and returns three routes: Route A is the fastest, Route B is toll-free, and Route C is AI-recommended. Each shows estimated duration, distance, and congestion level with color-coded warnings. The AI route dynamically blends the best attributes of both alternatives."

### 4. Chatbot Interaction (30 seconds)

"The TrafficAI chatbot is powered by Groq's Llama 3.3 70B model. Ask about NH48 traffic, the best time to travel from Delhi to Noida, or congestion near Connaught Place — it responds with specific, data-driven answers. For quick access, try one of the example chips. With a Groq API key in the `.env` file, it unlocks the full AI engine."

## Impact Statement

"TrafficAI demonstrates how machine learning, real-time weather data, and AI-powered navigation can transform urban mobility. In 6 months, we envision city-wide deployments, integration with municipal traffic systems, and personalized commuter alerts — turning India's congestion crisis into a manageable, data-driven problem."

---

**Tips for presenting:**
- Switch between tabs smoothly
- Keep the Event Mode toggle for the end as a bonus feature
- Mute browser notifications before presenting
- Have the backend already running to avoid cold starts
