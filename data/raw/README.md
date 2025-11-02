# Data Directory - Raw Data

## ?? Place Your Data Files Here

This directory should contain the following datasets:

### Required Files

1. **nigeria_centroids_1km.hdf5**
   - Description: 1km resolution spatial grid (1.5M points)
   - Format: HDF5
   - Size: ~few hundred MB

2. **exposure_nigeria_lga_aggregated.***
   - Description: LGA-level population exposure
   - Format: Shapefile (.shp), GeoJSON, GeoPackage, or CSV
   - Required fields: LGA name, population

3. **dtm_displacement_data_cleaned.csv**
   - Description: Displacement event records (8,883 events)
   - Format: CSV
   - Required fields: LGA, date, individuals_displaced

4. **displacement_events_monthly.csv**
   - Description: Monthly displacement time-series (4,576 records)
   - Format: CSV
   - Required fields: month/date, displacement counts

5. **displacement_statistics_by_lga.csv**
   - Description: LGA-level vulnerability statistics (123 LGAs)
   - Format: CSV
   - Required fields: LGA, vulnerability indicators

6. **nema_flood_data_cleaned.csv**
   - Description: Historical flood events (1,029 events)
   - Format: CSV
   - Required fields: LGA, date, impacts (deaths, affected, etc.)

7. **nema_flood_risk_by_lga.csv**
   - Description: LGA-level flood risk indicators (470 LGAs)
   - Format: CSV
   - Required fields: LGA, risk indicators

---

## ?? Data Checklist

Before running the system, verify:

- [ ] All 7 datasets are present
- [ ] Files are not empty (check file sizes)
- [ ] CSV files can be opened in a text editor
- [ ] Column names match expected format (or close variations)
- [ ] Data includes Borno, Adamawa, and Yobe states

---

## ?? Verify Your Data

Run this command to check your data files:

```bash
python -c "import os; files = os.listdir('data/raw'); print('Files found:', len(files)); [print(f'  - {f}') for f in files if not f.startswith('.')]"
```

Expected output:
```
Files found: 7
  - nigeria_centroids_1km.hdf5
  - exposure_nigeria_lga_aggregated.shp
  - dtm_displacement_data_cleaned.csv
  - displacement_events_monthly.csv
  - displacement_statistics_by_lga.csv
  - nema_flood_data_cleaned.csv
  - nema_flood_risk_by_lga.csv
```

---

## ?? Data Structure Examples

### CSV Files Should Look Like:

**nema_flood_data_cleaned.csv**
```csv
State,LGA,Date,Deaths,Injured,Houses_Destroyed
Borno,Maiduguri,2022-08-15,5,12,234
Adamawa,Yola North,2022-09-03,2,8,156
...
```

**displacement_events_monthly.csv**
```csv
month,individuals_displaced,state,lga
2022-01,1500,Borno,Maiduguri
2022-02,2300,Adamawa,Yola North
...
```

### Column Name Variations

The system handles common variations:
- State/state/STATE
- LGA/lga
- Date/date/event_date
- Individuals/individuals_displaced

---

## ?? Important Notes

1. **Don't modify** original data files - the system will create processed versions
2. **Keep backups** of your original data files
3. **Check encoding**: CSV files should be UTF-8 encoded
4. **Date formats**: System accepts most common formats (YYYY-MM-DD preferred)
5. **Missing values**: System handles missing data gracefully

---

## ?? Data Security

- Add `data/raw/*.hdf5` to `.gitignore` (already done)
- Don't commit large data files to Git
- Ensure proper permissions if data is sensitive
- Use secure file transfer methods

---

## ? Need Help?

- Missing data files? Check with data providers
- Wrong format? See conversion scripts in `src/data_processing/`
- Data errors? Review logs in `data/outputs/*.log`

---

**Ready?** Once all files are here, run `python main.py` from the project root!
