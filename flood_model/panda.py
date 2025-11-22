# Mini-test for 2021 Jan only
test_grib = 'test_era5.grib'
c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': 'total_precipitation',  # Just one var
        'year': '2021',
        'month': '01',
        'day': ['01', '02'],  # Tiny subset
        'time': '00:00',
        'area': AREA,
        'format': 'grib',
    },
    test_grib
)
print(f"Test file size: {os.path.getsize(test_grib) if os.path.exists(test_grib) else 'Not created'}")