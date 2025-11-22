# FLUD Frontend

A modern, responsive web application for flood prediction and risk assessment. Built with React, TypeScript, and Tailwind CSS.

## Features

- 🗺️ **Interactive Map**: Select locations using an interactive map or enter coordinates manually
- 📊 **Risk Visualization**: Comprehensive flood risk assessment with severity levels and time-windowed forecasts
- 📈 **Weather Data Charts**: Visualize precipitation, temperature, and soil moisture data over time
- 🤖 **AI-Powered Analysis**: Get AI-generated insights and recommendations
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **React Leaflet** - Interactive maps
- **Axios** - HTTP client
- **Lucide React** - Icons

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Building for Production

```bash
npm run build
```

The production build will be in the `dist` directory.

## Configuration

### API Endpoint

By default, the frontend expects the backend API at `http://localhost:8000`. You can configure this by:

1. Creating a `.env` file in the frontend directory:
```
VITE_API_URL=http://localhost:8000
```

2. Or modify the API base URL in `src/services/api.ts`

### Mock Data Mode

The application includes a "Use Mock Data" toggle in the header. This allows you to test the interface without connecting to the backend API.

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── LocationInput.tsx
│   │   ├── RiskOverview.tsx
│   │   ├── WeatherCharts.tsx
│   │   ├── SeverityBreakdown.tsx
│   │   ├── TimeWindowForecast.tsx
│   │   ├── AIRecommendations.tsx
│   │   └── Progress.tsx
│   ├── pages/               # Page components
│   │   └── Dashboard.tsx
│   ├── services/            # API services
│   │   └── api.ts
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── index.html               # HTML template
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Features Overview

### Location Input
- Enter coordinates manually or click on the map
- Adjustable analysis period (1-30 days)
- Real-time map marker updates

### Risk Overview
- Overall risk score with color-coded severity
- Confidence intervals and uncertainty metrics
- Key risk factors display

### Weather Charts
- Precipitation time series
- Soil moisture visualization
- Weather summary statistics

### Severity Breakdown
- Minor, Moderate, and Severe flooding probabilities
- Progress bars for visual representation
- Detailed descriptions for each severity level

### Time Window Forecast
- 24-hour, 48-hour, 72-hour, and 7-day forecasts
- Interactive line chart
- Probability cards for each time window

### AI Recommendations
- Overall assessment
- Severity and temporal analysis
- Recommended actions
- Key concerns and monitoring priorities

## Backend Integration

The frontend expects a REST API endpoint at `/api/predict` that accepts:

```json
{
  "lat": 16.5062,
  "lon": 80.6480,
  "days": 7
}
```

And returns a `FloodPredictionResult` object matching the interface defined in `src/services/api.ts`.

## Development

### Linting

```bash
npm run lint
```

### Type Checking

TypeScript type checking is performed during the build process. For development, your IDE should provide real-time type checking.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

Part of the FLUD project.

