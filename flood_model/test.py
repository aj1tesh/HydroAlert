import cdsapi

print("Initializing CDS client...")
c = cdsapi.Client()

print("Requesting test ERA5 data...")
c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'variable': '2m_temperature',
        'product_type': 'reanalysis',
        'year': '2024',
        'month': '01',
        'day': '01',
        'time': '00:00',
        'format': 'grib',
    },
    'test.grib'
)

print("\nCDS API is working ✔")
