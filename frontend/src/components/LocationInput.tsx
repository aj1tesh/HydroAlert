import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet'
import L from 'leaflet'
import { MapPin, Search } from 'lucide-react'
import 'leaflet/dist/leaflet.css'

// Fix for default marker icon in React Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

interface LocationInputProps {
  onPredict: (lat: number, lon: number, days: number) => void
  loading: boolean
}

function MapClickHandler({ onLocationSelect }: { onLocationSelect: (lat: number, lon: number) => void }) {
  useMapEvents({
    click: (e) => {
      onLocationSelect(e.latlng.lat, e.latlng.lng)
    },
  })
  return null
}

function MapUpdater({ center }: { center: [number, number] }) {
  const map = useMap()
  useEffect(() => {
    map.setView(center, map.getZoom())
  }, [center, map])
  return null
}

function LocationInput({ onPredict, loading }: LocationInputProps) {
  const [lat, setLat] = useState('16.5062')
  const [lon, setLon] = useState('80.6480')
  const [days, setDays] = useState(7)
  const [markerPosition, setMarkerPosition] = useState<[number, number]>([16.5062, 80.6480])

  const handleLocationSelect = (selectedLat: number, selectedLon: number) => {
    setLat(selectedLat.toFixed(4))
    setLon(selectedLon.toFixed(4))
    setMarkerPosition([selectedLat, selectedLon])
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const latNum = parseFloat(lat)
    const lonNum = parseFloat(lon)
    if (!isNaN(latNum) && !isNaN(lonNum) && latNum >= -90 && latNum <= 90 && lonNum >= -180 && lonNum <= 180) {
      onPredict(latNum, lonNum, days)
    }
  }

  const handleInputChange = () => {
    const latNum = parseFloat(lat)
    const lonNum = parseFloat(lon)
    if (!isNaN(latNum) && !isNaN(lonNum)) {
      setMarkerPosition([latNum, lonNum])
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <MapPin className="text-primary-600" size={24} />
        Location & Analysis Period
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Latitude
            </label>
            <input
              type="number"
              step="any"
              value={lat}
              onChange={(e) => {
                setLat(e.target.value)
                handleInputChange()
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="e.g., 16.5062"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Longitude
            </label>
            <input
              type="number"
              step="any"
              value={lon}
              onChange={(e) => {
                setLon(e.target.value)
                handleInputChange()
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="e.g., 80.6480"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Analysis Period (days)
            </label>
            <input
              type="number"
              min="1"
              max="30"
              value={days}
              onChange={(e) => setDays(parseInt(e.target.value) || 7)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>
        </div>

        <div className="map-container">
          <MapContainer
            center={markerPosition}
            zoom={10}
            style={{ height: '100%', width: '100%' }}
            scrollWheelZoom={true}
          >
            <TileLayer
              attribution='&copy; <a href="https://carto.com/">Carto</a> contributors, &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
              subdomains="abcd"
              maxZoom={20}
            />
            <MapClickHandler onLocationSelect={handleLocationSelect} />
            <MapUpdater center={markerPosition} />
            <Marker position={markerPosition} />
          </MapContainer>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full md:w-auto px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <Search size={20} />
          {loading ? 'Analyzing...' : 'Analyze Flood Risk'}
        </button>
      </form>
    </div>
  )
}

export default LocationInput

