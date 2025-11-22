# Quick Start Guide

Get the FLUD frontend up and running in minutes!

## Prerequisites

- Node.js 18 or higher
- npm, yarn, or pnpm

## Installation Steps

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

## Using Mock Data

The frontend includes a "Use Mock Data" toggle in the header. Enable it to:
- Test the interface without a backend
- See example data and visualizations
- Develop and debug frontend features

## Connecting to Backend

1. **Start your backend API** (see `BACKEND_API.md` for API requirements)

2. **Configure the API URL** (if different from default):
   - Create a `.env` file in the frontend directory
   - Add: `VITE_API_URL=http://localhost:8000`
   - Restart the dev server

3. **Disable "Use Mock Data"** toggle

4. **Enter coordinates and click "Analyze Flood Risk"**

## Troubleshooting

### Map not loading?
- Check browser console for errors
- Ensure Leaflet CSS is loaded (should be automatic)
- Try refreshing the page

### API connection errors?
- Verify backend is running on the correct port
- Check CORS settings on backend
- Review browser console for specific error messages
- Try using mock data to verify frontend works

### Build errors?
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)
- Review TypeScript errors in terminal

## Next Steps

- Read `README.md` for detailed documentation
- Check `BACKEND_API.md` for API integration details
- Customize the UI in `src/components/`
- Modify API service in `src/services/api.ts`

