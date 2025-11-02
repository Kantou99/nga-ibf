# 🚀 QUICK START: Generate nigeria_centroids_1km.hdf5

## ⚡ Fastest Method (30 seconds)

```bash
python generate_centroids.py --method bbox
```

**Output:** `nigeria_centroids_1km.hdf5` (~150,000 points)

---

## 🎯 Most Accurate Method (2-3 minutes)

```bash
python generate_centroids.py --method boundary
```

**Output:** `nigeria_centroids_1km.hdf5` (~120,000 points, exact Nigeria shape)

---

## 🧪 Testing/Development (5 km resolution)

```bash
python generate_centroids.py --method bbox --resolution 5.0 --output nigeria_centroids_5km.hdf5
```

**Output:** `nigeria_centroids_5km.hdf5` (~5,000 points, much faster)

---

## 📊 What You Get

```
nigeria_centroids_1km.hdf5
├── 120,000-150,000 points
├── 1 km spacing
├── Covers Nigeria (4°N to 14°N, 3°E to 15°E)
├── EPSG:4326 (WGS84)
└── ~15-20 MB file size
```

---

## ✅ Verify It Works

```python
from climada.hazard import Centroids

# Load
centroids = Centroids.from_hdf5('nigeria_centroids_1km.hdf5')

# Check
print(f"Points: {len(centroids.lat):,}")
print(f"Lat: {centroids.lat.min():.2f}° to {centroids.lat.max():.2f}°")
print(f"Lon: {centroids.lon.min():.2f}° to {centroids.lon.max():.2f}°")

# ✅ If this runs without errors, you're good!
```

---

## 🎓 Complete Setup

For ALL data files (centroids + boundaries + population + events):

**See [DATA_SETUP_GUIDE.md](DATA_SETUP_GUIDE.md)** for complete instructions

---

## 🆘 Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'climada'`
```bash
pip install climada
```

**Problem:** `No module named 'geopandas'`
```bash
pip install geopandas shapely
```

**Problem:** Script too slow (>5 minutes)
```bash
# Use faster method or coarser resolution
python generate_centroids.py --method bbox --resolution 5.0
```

**Problem:** `No points found within Nigeria boundary`
```bash
# Fall back to bounding box method
python generate_centroids.py --method bbox
```

---

## 📁 Where to Put It

```bash
# Move to data directory
mkdir -p data
mv nigeria_centroids_1km.hdf5 data/

# Or update config to point to current location
# In config.py:
# centroids_file: 'nigeria_centroids_1km.hdf5'
```

---

## 🎉 Next Steps

1. ✅ Generate centroids (you're here!)
2. ⬜ Download admin boundaries ([DATA_SETUP_GUIDE.md](DATA_SETUP_GUIDE.md))
3. ⬜ Get population data ([DATA_SETUP_GUIDE.md](DATA_SETUP_GUIDE.md))
4. ⬜ Create events database ([DATA_SETUP_GUIDE.md](DATA_SETUP_GUIDE.md))
5. ⬜ Run your first forecast! ([QUICK_START.md](QUICK_START.md))

---

## 📋 Three Ways to Generate Centroids

| Method | Command | Time | Points | Use Case |
|--------|---------|------|--------|----------|
| **Fast** | `--method bbox` | 30s | 150k | Development, testing |
| **Precise** | `--method boundary` | 2-3m | 120k | Production |
| **Coarse** | `--resolution 5.0` | 5s | 5k | Quick testing |

---

## 💡 Pro Tips

1. **Start with fast method** for development
2. **Switch to precise** for production
3. **Use coarse resolution** (5-10 km) for initial testing
4. **Centroids file is reusable** - generate once, use many times
5. **File size:** 1 km = 15-20 MB, 5 km = 1-2 MB, 10 km = 0.5 MB

---

**🌍 You're ready to generate centroids! Just run the command and you'll have your file in ~30 seconds.**
